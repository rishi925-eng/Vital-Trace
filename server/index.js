const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const moment = require('moment');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../client/build')));

// Initialize SQLite Database
const db = new sqlite3.Database('iot_data.db');

// Create tables if they don't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    timestamp TEXT,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    light REAL,
    motion BOOLEAN,
    voltage REAL
  )`);
  
  db.run(`CREATE TABLE IF NOT EXISTS device_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    command TEXT,
    value TEXT,
    timestamp TEXT,
    status TEXT DEFAULT 'pending'
  )`);
});

// Store connected devices
const connectedDevices = new Map();
const connectedClients = new Map();

// WebSocket handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  connectedClients.set(socket.id, socket);

  // Handle device registration
  socket.on('device_register', (data) => {
    console.log('Device registered:', data);
    connectedDevices.set(data.device_id, {
      socket: socket,
      info: data,
      lastSeen: new Date()
    });
    
    // Broadcast device list to all clients
    io.emit('devices_updated', Array.from(connectedDevices.keys()).map(id => ({
      device_id: id,
      ...connectedDevices.get(id).info,
      status: 'online'
    })));
  });

  // Handle sensor data from devices
  socket.on('sensor_data', (data) => {
    console.log('Received sensor data:', data);
    
    // Store in database
    const stmt = db.prepare(`INSERT INTO sensor_data 
      (device_id, timestamp, temperature, humidity, pressure, light, motion, voltage) 
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
    
    stmt.run(
      data.device_id,
      moment().toISOString(),
      data.temperature || null,
      data.humidity || null,
      data.pressure || null,
      data.light || null,
      data.motion || null,
      data.voltage || null
    );
    
    stmt.finalize();

    // Update device last seen
    if (connectedDevices.has(data.device_id)) {
      connectedDevices.get(data.device_id).lastSeen = new Date();
    }

    // Broadcast to all connected clients
    io.emit('real_time_data', data);
  });

  // Handle commands from dashboard to devices
  socket.on('device_command', (data) => {
    console.log('Command received:', data);
    
    // Store command in database
    const stmt = db.prepare(`INSERT INTO device_commands 
      (device_id, command, value, timestamp) 
      VALUES (?, ?, ?, ?)`);
    
    stmt.run(
      data.device_id,
      data.command,
      data.value,
      moment().toISOString()
    );
    
    stmt.finalize();

    // Send to specific device
    const device = connectedDevices.get(data.device_id);
    if (device) {
      device.socket.emit('command', {
        command: data.command,
        value: data.value,
        timestamp: moment().toISOString()
      });
    }
  });

  // Handle disconnect
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    
    // Remove from devices if it was a device
    for (const [deviceId, device] of connectedDevices.entries()) {
      if (device.socket.id === socket.id) {
        connectedDevices.delete(deviceId);
        // Update device list
        io.emit('devices_updated', Array.from(connectedDevices.keys()).map(id => ({
          device_id: id,
          ...connectedDevices.get(id).info,
          status: 'online'
        })));
        break;
      }
    }
    
    connectedClients.delete(socket.id);
  });
});

// REST API endpoints
app.get('/api/devices', (req, res) => {
  const devices = Array.from(connectedDevices.keys()).map(id => ({
    device_id: id,
    ...connectedDevices.get(id).info,
    status: 'online',
    lastSeen: connectedDevices.get(id).lastSeen
  }));
  res.json(devices);
});

app.get('/api/data/:deviceId', (req, res) => {
  const deviceId = req.params.deviceId;
  const limit = req.query.limit || 100;
  
  db.all(
    `SELECT * FROM sensor_data WHERE device_id = ? ORDER BY timestamp DESC LIMIT ?`,
    [deviceId, limit],
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      res.json(rows.reverse());
    }
  );
});

app.get('/api/data/:deviceId/range', (req, res) => {
  const deviceId = req.params.deviceId;
  const start = req.query.start;
  const end = req.query.end;
  
  db.all(
    `SELECT * FROM sensor_data 
     WHERE device_id = ? AND timestamp BETWEEN ? AND ? 
     ORDER BY timestamp ASC`,
    [deviceId, start, end],
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      res.json(rows);
    }
  );
});

app.post('/api/command', (req, res) => {
  const { device_id, command, value } = req.body;
  
  io.emit('device_command', { device_id, command, value });
  
  res.json({ success: true, message: 'Command sent' });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
});

// Start server
const PORT = process.env.PORT || 5001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Dashboard available at http://localhost:${PORT}`);
});

// Cleanup on exit
process.on('SIGINT', () => {
  console.log('Shutting down server...');
  db.close();
  server.close();
  process.exit(0);
});
