import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Avatar,
  useTheme
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  Thermostat,
  Opacity,
  Speed,
  Lightbulb,
  DirectionsRun,
  Battery90
} from '@mui/icons-material';

const Dashboard = ({ selectedDevice, realTimeData }) => {
  const theme = useTheme();

  const getSensorIcon = (type) => {
    const iconMap = {
      temperature: <Thermostat sx={{ fontSize: 32 }} />,
      humidity: <Opacity sx={{ fontSize: 32 }} />,
      pressure: <Speed sx={{ fontSize: 32 }} />,
      light: <Lightbulb sx={{ fontSize: 32 }} />,
      motion: <DirectionsRun sx={{ fontSize: 32 }} />,
      voltage: <Battery90 sx={{ fontSize: 32 }} />
    };
    return iconMap[type] || <Thermostat sx={{ fontSize: 32 }} />;
  };

  const getSensorColor = (type, value) => {
    const colorMap = {
      temperature: value > 30 ? 'error' : value > 20 ? 'warning' : 'primary',
      humidity: value > 70 ? 'info' : value < 30 ? 'warning' : 'success',
      pressure: 'secondary',
      light: value > 500 ? 'warning' : 'info',
      motion: value ? 'error' : 'success',
      voltage: value < 3.0 ? 'error' : value < 3.5 ? 'warning' : 'success'
    };
    return colorMap[type] || 'primary';
  };

  const getSensorUnit = (type) => {
    const unitMap = {
      temperature: '°C',
      humidity: '%',
      pressure: 'hPa',
      light: 'lux',
      motion: '',
      voltage: 'V'
    };
    return unitMap[type] || '';
  };

  const formatValue = (type, value) => {
    if (type === 'motion') {
      return value ? 'Detected' : 'None';
    }
    return typeof value === 'number' ? value.toFixed(1) : value;
  };

  const getProgressValue = (type, value) => {
    const rangeMap = {
      temperature: { min: -10, max: 50 },
      humidity: { min: 0, max: 100 },
      pressure: { min: 980, max: 1030 },
      light: { min: 0, max: 1000 },
      voltage: { min: 2.5, max: 4.2 }
    };
    
    if (type === 'motion') return value ? 100 : 0;
    
    const range = rangeMap[type];
    if (!range) return 50;
    
    return Math.min(100, Math.max(0, ((value - range.min) / (range.max - range.min)) * 100));
  };

  if (!selectedDevice) {
    return (
      <Card elevation={3}>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="textSecondary">
            📱 Select a device to view real-time data
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!realTimeData) {
    return (
      <Card elevation={3}>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="textSecondary">
            ⏳ Waiting for data from {selectedDevice}...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const sensorData = [
    { type: 'temperature', value: realTimeData.temperature, label: 'Temperature' },
    { type: 'humidity', value: realTimeData.humidity, label: 'Humidity' },
    { type: 'pressure', value: realTimeData.pressure, label: 'Pressure' },
    { type: 'light', value: realTimeData.light, label: 'Light' },
    { type: 'motion', value: realTimeData.motion, label: 'Motion' },
    { type: 'voltage', value: realTimeData.voltage, label: 'Voltage' }
  ].filter(sensor => sensor.value !== undefined && sensor.value !== null);

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        📊 Real-time Data - {selectedDevice}
      </Typography>
      
      <Grid container spacing={3}>
        {sensorData.map((sensor, index) => (
          <Grid item xs={12} sm={6} md={4} key={sensor.type}>
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <Card 
                elevation={3} 
                sx={{ 
                  height: '100%',
                  background: theme.palette.mode === 'dark' 
                    ? 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%)'
                    : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${theme.palette.divider}20`
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar 
                      sx={{ 
                        bgcolor: `${getSensorColor(sensor.type, sensor.value)}.main`,
                        mr: 2,
                        width: 48,
                        height: 48
                      }}
                    >
                      {getSensorIcon(sensor.type)}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" component="div" sx={{ fontWeight: 500 }}>
                        {sensor.label}
                      </Typography>
                      <Chip 
                        label={selectedDevice} 
                        size="small" 
                        variant="outlined" 
                        sx={{ mt: 0.5 }}
                      />
                    </Box>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 700, mb: 1 }}>
                      {formatValue(sensor.type, sensor.value)}
                      <Typography variant="h6" component="span" sx={{ ml: 1, color: 'text.secondary' }}>
                        {getSensorUnit(sensor.type)}
                      </Typography>
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Level
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {getProgressValue(sensor.type, sensor.value).toFixed(0)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={getProgressValue(sensor.type, sensor.value)}
                      color={getSensorColor(sensor.type, sensor.value)}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
                      }}
                    />
                  </Box>

                  <Typography variant="caption" color="text.secondary">
                    Updated: {new Date(realTimeData.timestamp).toLocaleTimeString()}
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Dashboard;
