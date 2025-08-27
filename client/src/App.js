import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Fade,
  useMediaQuery,
  Tabs,
  Tab
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import io from 'socket.io-client';

import Dashboard from './components/Dashboard';
import DeviceList from './components/DeviceList';
import DataVisualization from './components/DataVisualization';
import DeviceControl from './components/DeviceControl';
import DataHistory from './components/DataHistory';
import BusinessMetrics from './components/BusinessMetrics';
import ExecutiveSummary from './components/ExecutiveSummary';
import DemoControls from './components/DemoControls';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [socket, setSocket] = useState(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [realTimeData, setRealTimeData] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [notification, setNotification] = useState(null);
  const [currentTab, setCurrentTab] = useState(0);
  
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: darkMode ? '#4fc3f7' : '#0277bd', // Medical blue
      },
      secondary: {
        main: darkMode ? '#81c784' : '#2e7d32', // Healthcare green
      },
      background: {
        default: darkMode ? '#0a1929' : '#f5f5f5',
        paper: darkMode ? '#1e293b' : '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h4: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 500,
      },
    },
    shape: {
      borderRadius: 12,
    },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
    },
  });

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    // Socket event handlers
    newSocket.on('connect', () => {
      setConnectionStatus('connected');
      setNotification({ type: 'success', message: 'Connected to server!' });
    });

    newSocket.on('disconnect', () => {
      setConnectionStatus('disconnected');
      setNotification({ type: 'error', message: 'Disconnected from server!' });
    });

    newSocket.on('devices_updated', (deviceList) => {
      setDevices(deviceList);
      if (!selectedDevice && deviceList.length > 0) {
        setSelectedDevice(deviceList[0].device_id);
      }
    });

    newSocket.on('real_time_data', (data) => {
      setRealTimeData(prevData => ({
        ...prevData,
        [data.device_id]: {
          ...data,
          timestamp: new Date().toISOString()
        }
      }));
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const handleThemeToggle = () => {
    setDarkMode(!darkMode);
  };

  const handleNotificationClose = () => {
    setNotification(null);
  };

  const sendCommand = (deviceId, command, value) => {
    if (socket) {
      socket.emit('device_command', {
        device_id: deviceId,
        command,
        value
      });
      setNotification({ 
        type: 'info', 
        message: `Command "${command}" sent to device ${deviceId}` 
      });
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
          <AppBar 
            position="sticky" 
            elevation={0}
            sx={{ 
              backdropFilter: 'blur(20px)',
              backgroundColor: theme => theme.palette.mode === 'dark' 
                ? 'rgba(26, 32, 53, 0.8)' 
                : 'rgba(255, 255, 255, 0.8)'
            }}
          >
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
                🩺 Vital Trace
              </Typography>
              <Typography variant="body2" sx={{ mr: 2, opacity: 0.8 }}>
                Cold Chain Monitoring
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <motion.div
                  animate={{ 
                    scale: connectionStatus === 'connected' ? [1, 1.1, 1] : 1,
                    color: connectionStatus === 'connected' ? '#4caf50' : '#f44336'
                  }}
                  transition={{ duration: 0.5, repeat: connectionStatus === 'connected' ? Infinity : 0, repeatDelay: 2 }}
                >
                  <Typography variant="body2">
                    {connectionStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
                  </Typography>
                </motion.div>
                <FormControlLabel
                  control={<Switch checked={darkMode} onChange={handleThemeToggle} />}
                  label={darkMode ? '🌙' : '☀️'}
                />
              </Box>
            </Toolbar>
          </AppBar>

          {/* Navigation Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3 }}>
            <Tabs 
              value={currentTab} 
              onChange={(e, newValue) => setCurrentTab(newValue)}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="📊 Dashboard" />
              <Tab label="💼 Business Metrics" />
              <Tab label="🎯 Executive Summary" />
              <Tab label="🎮 Demo Controls" />
            </Tabs>
          </Box>

          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            {/* Tab Content */}
            <AnimatePresence mode="wait">
              {currentTab === 0 && (
                <motion.div
                  key="dashboard"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Grid container spacing={3}>
                    {/* Device List */}
                    <Grid item xs={12} md={3}>
                      <DeviceList
                        devices={devices}
                        selectedDevice={selectedDevice}
                        onDeviceSelect={setSelectedDevice}
                        realTimeData={realTimeData}
                      />
                    </Grid>

                    {/* Main Dashboard */}
                    <Grid item xs={12} md={9}>
                      <Grid container spacing={3}>
                        {/* Real-time Data Cards */}
                        <Grid item xs={12}>
                          <Dashboard
                            selectedDevice={selectedDevice}
                            realTimeData={realTimeData[selectedDevice]}
                          />
                        </Grid>

                        {/* Data Visualization */}
                        <Grid item xs={12} lg={8}>
                          <DataVisualization
                            selectedDevice={selectedDevice}
                            socket={socket}
                          />
                        </Grid>

                        {/* Device Controls */}
                        <Grid item xs={12} lg={4}>
                          <DeviceControl
                            selectedDevice={selectedDevice}
                            onSendCommand={sendCommand}
                          />
                        </Grid>

                        {/* Data History */}
                        <Grid item xs={12}>
                          <DataHistory
                            selectedDevice={selectedDevice}
                            socket={socket}
                          />
                        </Grid>
                      </Grid>
                    </Grid>
                  </Grid>
                </motion.div>
              )}

              {currentTab === 1 && (
                <motion.div
                  key="business"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <BusinessMetrics 
                    devices={devices}
                    realTimeData={realTimeData}
                  />
                </motion.div>
              )}

              {currentTab === 2 && (
                <motion.div
                  key="executive"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ExecutiveSummary />
                </motion.div>
              )}

              {currentTab === 3 && (
                <motion.div
                  key="demo"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={3}>
                      <DeviceList
                        devices={devices}
                        selectedDevice={selectedDevice}
                        onDeviceSelect={setSelectedDevice}
                        realTimeData={realTimeData}
                      />
                    </Grid>
                    <Grid item xs={12} md={9}>
                      <DemoControls 
                        devices={devices}
                        selectedDevice={selectedDevice}
                        onSendCommand={sendCommand}
                      />
                    </Grid>
                  </Grid>
                </motion.div>
              )}
            </AnimatePresence>
          </Container>
        </Box>

        {/* Notifications */}
        <Snackbar
          open={!!notification}
          autoHideDuration={4000}
          onClose={handleNotificationClose}
          TransitionComponent={Fade}
        >
          {notification && (
            <Alert 
              onClose={handleNotificationClose} 
              severity={notification.type}
              sx={{ width: '100%' }}
            >
              {notification.message}
            </Alert>
          )}
        </Snackbar>
      </motion.div>
    </ThemeProvider>
  );
}

export default App;
