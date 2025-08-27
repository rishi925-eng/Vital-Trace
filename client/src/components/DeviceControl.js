import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Slider,
  Switch,
  TextField,
  FormControlLabel,
  Divider,
  Grid,
  Chip,
  IconButton,
  useTheme
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  PowerSettingsNew,
  Lightbulb,
  Speed,
  Refresh,
  Settings,
  Send,
  VolumeUp,
  Wifi,
  Bluetooth
} from '@mui/icons-material';

const DeviceControl = ({ selectedDevice, onSendCommand }) => {
  const theme = useTheme();
  const [ledBrightness, setLedBrightness] = useState(50);
  const [motorSpeed, setMotorSpeed] = useState(30);
  const [customCommand, setCustomCommand] = useState('');
  const [devicePower, setDevicePower] = useState(true);
  const [wifiEnabled, setWifiEnabled] = useState(true);
  const [bluetoothEnabled, setBluetoothEnabled] = useState(false);

  const handleSliderCommand = (command, value) => {
    if (selectedDevice && onSendCommand) {
      onSendCommand(selectedDevice, command, value.toString());
    }
  };

  const handleSwitchCommand = (command, checked) => {
    if (selectedDevice && onSendCommand) {
      onSendCommand(selectedDevice, command, checked ? 'on' : 'off');
    }
  };

  const handleCustomCommand = () => {
    if (selectedDevice && onSendCommand && customCommand.trim()) {
      const [cmd, ...valueParts] = customCommand.trim().split(' ');
      const value = valueParts.join(' ') || 'true';
      onSendCommand(selectedDevice, cmd, value);
      setCustomCommand('');
    }
  };

  const quickCommands = [
    { label: 'Reset', command: 'reset', icon: <Refresh />, color: 'warning' },
    { label: 'Status', command: 'status', icon: <Settings />, color: 'info' },
    { label: 'Calibrate', command: 'calibrate', icon: <Speed />, color: 'success' },
    { label: 'Test LED', command: 'test_led', icon: <Lightbulb />, color: 'secondary' }
  ];

  if (!selectedDevice) {
    return (
      <Card elevation={3}>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Settings sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            🎮 Select a device to control
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Settings sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              🎮 Device Control
            </Typography>
            <Chip
              label={selectedDevice}
              size="small"
              color="primary"
              sx={{ ml: 'auto' }}
            />
          </Box>

          {/* Power Control */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 500 }}>
                ⚡ Power Management
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={devicePower}
                        onChange={(e) => {
                          setDevicePower(e.target.checked);
                          handleSwitchCommand('power', e.target.checked);
                        }}
                        color="success"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <PowerSettingsNew sx={{ mr: 1, fontSize: 20 }} />
                        Device Power
                      </Box>
                    }
                  />
                </Grid>
              </Grid>
            </Box>
          </motion.div>

          <Divider sx={{ my: 2 }} />

          {/* LED Control */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 500 }}>
                💡 LED Brightness
              </Typography>
              <Box sx={{ px: 2 }}>
                <Slider
                  value={ledBrightness}
                  onChange={(e, value) => setLedBrightness(value)}
                  onChangeCommitted={(e, value) => handleSliderCommand('led_brightness', value)}
                  min={0}
                  max={100}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${value}%`}
                  sx={{
                    color: theme.palette.warning.main,
                    '& .MuiSlider-thumb': {
                      backgroundColor: theme.palette.warning.main,
                    },
                    '& .MuiSlider-rail': {
                      backgroundColor: theme.palette.divider,
                    }
                  }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                  <Typography variant="caption">0%</Typography>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>
                    {ledBrightness}%
                  </Typography>
                  <Typography variant="caption">100%</Typography>
                </Box>
              </Box>
            </Box>
          </motion.div>

          <Divider sx={{ my: 2 }} />

          {/* Motor Speed Control */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 500 }}>
                🔧 Motor Speed
              </Typography>
              <Box sx={{ px: 2 }}>
                <Slider
                  value={motorSpeed}
                  onChange={(e, value) => setMotorSpeed(value)}
                  onChangeCommitted={(e, value) => handleSliderCommand('motor_speed', value)}
                  min={0}
                  max={100}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${value}%`}
                  sx={{
                    color: theme.palette.info.main,
                    '& .MuiSlider-thumb': {
                      backgroundColor: theme.palette.info.main,
                    },
                    '& .MuiSlider-rail': {
                      backgroundColor: theme.palette.divider,
                    }
                  }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                  <Typography variant="caption">0%</Typography>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>
                    {motorSpeed}%
                  </Typography>
                  <Typography variant="caption">100%</Typography>
                </Box>
              </Box>
            </Box>
          </motion.div>

          <Divider sx={{ my: 2 }} />

          {/* Connectivity */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 500 }}>
                📡 Connectivity
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={wifiEnabled}
                        onChange={(e) => {
                          setWifiEnabled(e.target.checked);
                          handleSwitchCommand('wifi', e.target.checked);
                        }}
                        color="primary"
                        size="small"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', fontSize: '0.9rem' }}>
                        <Wifi sx={{ mr: 0.5, fontSize: 16 }} />
                        WiFi
                      </Box>
                    }
                  />
                </Grid>
                <Grid item xs={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={bluetoothEnabled}
                        onChange={(e) => {
                          setBluetoothEnabled(e.target.checked);
                          handleSwitchCommand('bluetooth', e.target.checked);
                        }}
                        color="secondary"
                        size="small"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', fontSize: '0.9rem' }}>
                        <Bluetooth sx={{ mr: 0.5, fontSize: 16 }} />
                        BLE
                      </Box>
                    }
                  />
                </Grid>
              </Grid>
            </Box>
          </motion.div>

          <Divider sx={{ my: 2 }} />

          {/* Quick Commands */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 500 }}>
                ⚡ Quick Commands
              </Typography>
              <Grid container spacing={1}>
                {quickCommands.map((cmd, index) => (
                  <Grid item xs={6} key={cmd.command}>
                    <motion.div
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Button
                        fullWidth
                        variant="outlined"
                        color={cmd.color}
                        size="small"
                        startIcon={cmd.icon}
                        onClick={() => onSendCommand(selectedDevice, cmd.command, 'true')}
                        sx={{
                          borderRadius: 2,
                          textTransform: 'none',
                          fontWeight: 500
                        }}
                      >
                        {cmd.label}
                      </Button>
                    </motion.div>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </motion.div>

          <Divider sx={{ my: 2 }} />

          {/* Custom Command */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <Box>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 500 }}>
                💻 Custom Command
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="e.g., servo_angle 90"
                  value={customCommand}
                  onChange={(e) => setCustomCommand(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleCustomCommand();
                    }
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                />
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <IconButton
                    color="primary"
                    onClick={handleCustomCommand}
                    disabled={!customCommand.trim()}
                    sx={{
                      bgcolor: theme.palette.primary.main + '10',
                      '&:hover': {
                        bgcolor: theme.palette.primary.main + '20',
                      }
                    }}
                  >
                    <Send />
                  </IconButton>
                </motion.div>
              </Box>
            </Box>
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default DeviceControl;
