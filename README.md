# 🔌 Interactive IoT Dashboard

A complete, modern, and interactive IoT dashboard built with React, Node.js, and WebSocket for real-time data visualization and device control. Perfect for monitoring and controlling PlatformIO devices like ESP32, Arduino, and Raspberry Pi.

![Dashboard Preview](https://img.shields.io/badge/Dashboard-Interactive-blue) ![Real-time](https://img.shields.io/badge/Real--time-WebSocket-green) ![Responsive](https://img.shields.io/badge/UI-Responsive-purple)

## ✨ Features

### 🎨 **Modern UI/UX**
- **Dark/Light Theme Toggle** with smooth transitions
- **Responsive Design** for desktop, tablet, and mobile
- **Material Design** with Framer Motion animations
- **Interactive Components** with hover effects and micro-interactions
- **Glass-morphism Effects** for a modern aesthetic

### 📊 **Real-time Data Visualization**
- **Live Charts** with multiple chart types (Line, Area, Bar)
- **Interactive Tooltips** with detailed sensor information
- **Color-coded Sensors** for quick status identification
- **Auto-updating Graphs** with smooth animations
- **Historical Data Analysis** with time-series charts

### 🎮 **Device Control**
- **Remote Control Panel** for LED brightness, motor speed
- **Quick Commands** for reset, calibration, status checks
- **Custom Command Interface** for advanced operations
- **Power Management** controls
- **Connectivity Settings** (WiFi, Bluetooth toggle)

### 📈 **Data Management**
- **SQLite Database** for persistent data storage
- **Historical Data Viewer** with pagination
- **Data Export** to CSV format
- **Time Range Filtering** (1h, 6h, 24h, 7d, 30d, custom)
- **Real-time Status Monitoring**

### 🔗 **Device Integration**
- **Multi-device Support** with automatic discovery
- **WebSocket Communication** for real-time updates
- **Device Status Monitoring** with connection indicators
- **Signal Strength Monitoring**
- **Auto-reconnection** for lost connections

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- PlatformIO (for ESP32/Arduino development)

### 1. Install Dependencies

```bash
# Install backend dependencies
npm install

# Install frontend dependencies
cd client
npm install
cd ..
```

### 2. Start the Development Server

```bash
# Start both backend and frontend in development mode
npm run dev
```

This will start:
- **Backend Server** on `http://localhost:5000`
- **React Frontend** on `http://localhost:3000`

### 3. Configure Your Device

1. Copy the example code from `platformio-examples/esp32_iot_dashboard.ino`
2. Update WiFi credentials and server IP address
3. Install required libraries listed in `platformio.ini`
4. Upload to your ESP32/Arduino device

### 4. Access the Dashboard

Open your browser and navigate to `http://localhost:3000` to see the interactive dashboard!

## 📱 Device Setup

### ESP32 Hardware Connections

| Component | GPIO Pin | Description |
|-----------|----------|-------------|
| DHT22 (Temp/Humidity) | GPIO 4 | Temperature and humidity sensor |
| BMP280 (Pressure) | I2C (SDA: 21, SCL: 22) | Barometric pressure sensor |
| LDR (Light) | GPIO 36 (A0) | Light sensor |
| PIR (Motion) | GPIO 2 | Motion detection sensor |
| Built-in LED | GPIO 2 | Status LED |
| Motion LED | GPIO 5 | Motion indicator LED |

### Required Libraries (PlatformIO)

```ini
lib_deps = 
    ArduinoWebsockets @ ^0.5.3
    ArduinoJson @ ^6.21.3
    DHT sensor library @ ^1.4.4
    Adafruit BMP280 Library @ ^2.6.8
    Adafruit Unified Sensor @ ^1.1.9
```

### Device Configuration

1. **Update WiFi Settings**:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

2. **Set Server IP**:
   ```cpp
   const char* websocket_server = "ws://YOUR_SERVER_IP:5000/socket.io/?EIO=4&transport=websocket";
   ```

3. **Customize Device Info**:
   ```cpp
   const char* device_id = "ESP32_001";
   const char* device_name = "Living Room Sensor";
   ```

## 🎯 Dashboard Features

### 📊 **Real-time Data Cards**
- **Temperature** with color-coded status (°C)
- **Humidity** with percentage indicators (%)
- **Pressure** in hPa units
- **Light Level** in lux
- **Motion Detection** with visual alerts
- **Voltage Monitoring** for battery status

### 📈 **Interactive Charts**
- **Line Charts** for trend analysis
- **Area Charts** for filled visualizations
- **Bar Charts** for discrete data points
- **Zoom and Pan** functionality
- **Real-time Updates** every 5 seconds
- **Custom Time Ranges** with date picker

### 🎮 **Control Panel**
- **LED Brightness Slider** (0-100%)
- **Motor Speed Control** (0-100%)
- **Power Toggle** for device on/off
- **Quick Action Buttons** (Reset, Status, Calibrate, Test LED)
- **Custom Command Interface** for advanced control
- **Connectivity Toggles** (WiFi, Bluetooth)

### 📊 **Data History**
- **Tabular View** with sortable columns
- **Time Range Selection** (predefined and custom)
- **Data Export** to CSV format
- **Pagination** for large datasets
- **Color-coded Values** based on sensor ranges
- **Search and Filter** capabilities

## 🔧 API Endpoints

### Device Management
- `GET /api/devices` - List all connected devices
- `POST /api/command` - Send command to device

### Data Retrieval
- `GET /api/data/:deviceId?limit=100` - Get recent data
- `GET /api/data/:deviceId/range?start=START&end=END` - Get data in range

### WebSocket Events
- `device_register` - Register new device
- `sensor_data` - Receive sensor data
- `device_command` - Send commands to device
- `real_time_data` - Broadcast real-time data
- `devices_updated` - Device list changes

## 🎨 Customization

### Theme Customization

The dashboard supports extensive theme customization:

```javascript
const theme = createTheme({
  palette: {
    mode: darkMode ? 'dark' : 'light',
    primary: { main: '#90caf9' },
    secondary: { main: '#f48fb1' },
    background: {
      default: darkMode ? '#0a1929' : '#f5f5f5',
      paper: darkMode ? '#1e293b' : '#ffffff',
    },
  },
  // ... more theme options
});
```

### Adding New Sensors

1. **Update ESP32 Code**:
   ```cpp
   // Add new sensor reading
   currentData.newSensor = readNewSensor();
   
   // Update JSON payload
   doc["newSensor"] = currentData.newSensor;
   ```

2. **Update Dashboard Components**:
   ```javascript
   // Add to sensor data processing
   { type: 'newSensor', value: realTimeData.newSensor, label: 'New Sensor' }
   ```

## 🚀 Production Deployment

### Backend (Node.js)

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Frontend (React)

```bash
# Build React app
cd client
npm run build

# Serve static files through Express
# (Already configured in server/index.js)
```

### Environment Variables

Create a `.env` file:

```bash
NODE_ENV=production
PORT=5000
DATABASE_URL=sqlite:./iot_data.db
```

## 📊 Performance Features

- **Efficient WebSocket Communication** with heartbeat monitoring
- **Database Indexing** for fast queries
- **React Optimization** with memo and lazy loading
- **Responsive Images** and optimized assets
- **Progressive Web App** capabilities
- **Service Worker** for offline functionality

## 🔒 Security Features

- **CORS Protection** with configurable origins
- **Input Validation** for all API endpoints
- **SQL Injection Prevention** with prepared statements
- **Rate Limiting** for API calls
- **Device Authentication** via device ID

## 🐛 Troubleshooting

### Common Issues

1. **Device Not Connecting**:
   - Check WiFi credentials
   - Verify server IP address
   - Ensure WebSocket port (5000) is accessible

2. **No Data Appearing**:
   - Check device serial monitor for errors
   - Verify WebSocket connection status
   - Check browser developer console

3. **Charts Not Updating**:
   - Refresh the page
   - Check network connectivity
   - Verify WebSocket connection

### Debug Mode

Enable debug logging in the ESP32 code:

```cpp
#define DEBUG_MODE 1
// Adds detailed serial output for troubleshooting
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Material-UI** for the beautiful React components
- **Recharts** for interactive data visualization
- **Framer Motion** for smooth animations
- **Socket.IO** for real-time communication
- **ESP32 Community** for excellent hardware documentation

---

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the [troubleshooting guide](#-troubleshooting)
- Review the [API documentation](#-api-endpoints)

**Made with ❤️ for the IoT community**
