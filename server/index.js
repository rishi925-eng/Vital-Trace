const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const connectDB = require('./config/db');
const dataRoutes = require('./routes/dataRoutes');

// Initialize app
const app = express();
const server = http.createServer(app);

// Connect to MongoDB
connectDB();

// CORS configuration for Socket.IO
const io = new Server(server, {
  cors: {
    origin: "http://localhost:3000", // Allow React client
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());

// API Routes
app.use('/api/data', dataRoutes);

// In-memory store for connected devices. In production, use Redis or a similar store.
let connectedDevices = [];

// Function to broadcast the updated device list to all frontend clients
const broadcastDeviceList = () => {
  const deviceList = connectedDevices.map(d => ({
    device_id: d.deviceId,
    name: d.name,
  }));
  io.to('frontend_clients').emit('device-list-update', deviceList);
  console.log('Broadcasted device list to frontend clients:', deviceList);
};

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log(`New client connected: ${socket.id}`);

  // A flag to determine if the client is a device or a frontend app
  let isDevice = false;

  // Initially, all clients join the frontend room. Devices will be moved later.
  socket.join('frontend_clients');
  
  // Send the current device list to the newly connected frontend client
  socket.emit('device-list-update', connectedDevices.map(d => ({ device_id: d.deviceId, name: d.name })));

  // Listen for device registration from simulators/hardware
  socket.on('register-device', (deviceInfo) => {
    isDevice = true;
    socket.leave('frontend_clients'); // Device should not receive frontend broadcasts
    socket.join(deviceInfo.deviceId); // Device joins a room named after its ID to receive commands
    console.log(`Device registered: ${deviceInfo.deviceId} (${deviceInfo.name}) with socket ${socket.id}`);

    // Add or update the device in our list
    const existingDeviceIndex = connectedDevices.findIndex(d => d.deviceId === deviceInfo.deviceId);
    if (existingDeviceIndex !== -1) {
      connectedDevices[existingDeviceIndex].socketId = socket.id;
    } else {
      connectedDevices.push({
        deviceId: deviceInfo.deviceId,
        name: deviceInfo.name,
        socketId: socket.id
      });
    }
    // Announce the new/updated device list to all frontend clients
    broadcastDeviceList();
  });

  // Listen for data from devices and forward it to all frontend clients
  socket.on('device-data', (data) => {
    // We only process data from registered devices
    if (isDevice && data.deviceId) {
      io.to('frontend_clients').emit('device-data', data);
    }
  });

  // Listen for commands from the frontend and forward to the specific device
  socket.on('device-command', ({ deviceId, command, value }) => {
    console.log(`Command received for ${deviceId}: ${command}=${value}. Sending to room ${deviceId}`);
    // Send command to the specific device's room
    io.to(deviceId).emit('command', { command, value });
  });

  // Handle disconnection for both devices and frontend clients
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
    // If the disconnected client was a device, remove it from the list
    const disconnectedDeviceIndex = connectedDevices.findIndex(d => d.socketId === socket.id);
    if (disconnectedDeviceIndex !== -1) {
      const deviceId = connectedDevices[disconnectedDeviceIndex].deviceId;
      console.log(`Device ${deviceId} disconnected.`);
      connectedDevices.splice(disconnectedDeviceIndex, 1);
      // Announce the updated device list
      broadcastDeviceList();
    }
  });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
