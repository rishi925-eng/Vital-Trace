import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Chip,
  Avatar,
  Badge,
  useTheme,
  Divider
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  DeviceHub,
  Circle,
  Wifi,
  WifiOff,
  TrendingUp
} from '@mui/icons-material';

const DeviceList = ({ devices, selectedDevice, onDeviceSelect, realTimeData }) => {
  const theme = useTheme();

  const getDeviceIcon = (deviceType) => {
    const iconMap = {
      'vital_trace_box': '🩺',
      'cold_chain_monitor': '❄️',
      'vaccine_storage': '💉',
      'esp32': '🔷',
      'arduino': '🟦',
      'sensor': '📡'
    };
    return iconMap[deviceType] || '📦';
  };

  const getConnectionStrength = (deviceId) => {
    // Simulate connection strength based on recent data
    const data = realTimeData[deviceId];
    if (!data) return 0;
    
    const now = new Date();
    const lastUpdate = new Date(data.timestamp);
    const timeDiff = now - lastUpdate;
    
    if (timeDiff < 5000) return 3; // Excellent
    if (timeDiff < 15000) return 2; // Good
    if (timeDiff < 30000) return 1; // Weak
    return 0; // No signal
  };

  const getSignalIcon = (strength) => {
    if (strength >= 3) return <Wifi color="success" />;
    if (strength >= 2) return <Wifi color="warning" />;
    if (strength >= 1) return <Wifi color="error" />;
    return <WifiOff color="disabled" />;
  };

  if (devices.length === 0) {
    return (
      <Card elevation={3}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <DeviceHub sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            📦 No Vital Trace boxes online
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Waiting for cold chain monitoring boxes to connect...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card elevation={3}>
      <CardContent sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <DeviceHub sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Vital Trace Boxes
          </Typography>
          <Chip
            label={devices.length}
            size="small"
            color="primary"
            sx={{ ml: 'auto' }}
          />
        </Box>
        
        <List sx={{ pt: 0 }}>
          {devices.map((device, index) => {
            const isSelected = device.device_id === selectedDevice;
            const signalStrength = getConnectionStrength(device.device_id);
            const hasRecentData = realTimeData[device.device_id];
            
            return (
              <motion.div
                key={device.device_id}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ x: 5 }}
              >
                <ListItem 
                  disablePadding
                  sx={{ mb: 1 }}
                >
                  <ListItemButton
                    selected={isSelected}
                    onClick={() => onDeviceSelect(device.device_id)}
                    sx={{
                      borderRadius: 2,
                      border: isSelected ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent',
                      backgroundColor: isSelected 
                        ? theme.palette.mode === 'dark' 
                          ? 'rgba(144, 202, 249, 0.1)' 
                          : 'rgba(25, 118, 210, 0.1)'
                        : 'transparent',
                      '&:hover': {
                        backgroundColor: theme.palette.mode === 'dark' 
                          ? 'rgba(255, 255, 255, 0.05)' 
                          : 'rgba(0, 0, 0, 0.05)',
                      }
                    }}
                  >
                    <ListItemIcon>
                      <Badge
                        overlap="circular"
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        badgeContent={
                          <Circle
                            sx={{
                              fontSize: 12,
                              color: device.status === 'online' ? '#4caf50' : '#f44336'
                            }}
                          />
                        }
                      >
                        <Avatar
                          sx={{
                            width: 40,
                            height: 40,
                            bgcolor: isSelected ? 'primary.main' : 'grey.600',
                            fontSize: '1.2rem'
                          }}
                        >
                          {getDeviceIcon(device.type)}
                        </Avatar>
                      </Badge>
                    </ListItemIcon>
                    
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                            {device.name || device.device_id}
                          </Typography>
                          {hasRecentData && (
                            <motion.div
                              animate={{ scale: [1, 1.2, 1] }}
                              transition={{ duration: 2, repeat: Infinity }}
                            >
                              <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
                            </motion.div>
                          )}
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                            {device.device_id}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            {getSignalIcon(signalStrength)}
                            <Chip
                              label={device.status}
                              size="small"
                              color={device.status === 'online' ? 'success' : 'error'}
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        </Box>
                      }
                    />
                  </ListItemButton>
                </ListItem>
                
                {index < devices.length - 1 && (
                  <Divider sx={{ mx: 2, opacity: 0.3 }} />
                )}
              </motion.div>
            );
          })}
        </List>
      </CardContent>
    </Card>
  );
};

export default DeviceList;
