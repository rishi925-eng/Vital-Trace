import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Box,
  Chip,
  Stack,
  Avatar,
  Alert,
  Collapse,
  Switch,
  FormControlLabel,
  Slider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  useTheme
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Warning,
  Error,
  BatteryAlert,
  Thermostat,
  Gps,
  Security,
  FlashOn,
  CloudOff,
  AcUnit,
  LocalHospital,
  Science,
  Replay
} from '@mui/icons-material';

const DemoControls = ({ devices, selectedDevice, onSendCommand }) => {
  const theme = useTheme();
  const [activeScenario, setActiveScenario] = useState(null);
  const [demoMode, setDemoMode] = useState(false);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [customTemp, setCustomTemp] = useState(4.0);
  const [selectedScenarioDevice, setSelectedScenarioDevice] = useState('');

  const scenarios = [
    {
      id: 'temp_excursion',
      title: 'Temperature Excursion',
      description: 'Simulate critical temperature breach (>8°C)',
      icon: <Thermostat />,
      color: '#d32f2f',
      severity: 'critical',
      commands: [
        { command: 'temp_override', value: '12.5' },
        { command: 'cooling_override', value: 'off' }
      ]
    },
    {
      id: 'battery_critical',
      title: 'Battery Critical',
      description: 'Low battery warning (<15%)',
      icon: <BatteryAlert />,
      color: '#f57c00',
      severity: 'warning',
      commands: [
        { command: 'battery_override', value: '12' },
        { command: 'solar_disable', value: 'true' }
      ]
    },
    {
      id: 'tamper_detected',
      title: 'Tamper Detection',
      description: 'Unauthorized box opening detected',
      icon: <Security />,
      color: '#9c27b0',
      severity: 'info',
      commands: [
        { command: 'lid_trigger', value: 'true' },
        { command: 'security_alert', value: 'tamper' }
      ]
    },
    {
      id: 'power_failure',
      title: 'Power System Failure',
      description: 'Complete power system malfunction',
      icon: <FlashOn />,
      color: '#d32f2f',
      severity: 'critical',
      commands: [
        { command: 'power_failure', value: 'true' },
        { command: 'emergency_mode', value: 'on' }
      ]
    },
    {
      id: 'connectivity_loss',
      title: 'Connectivity Loss',
      description: 'Lost connection to monitoring system',
      icon: <CloudOff />,
      color: '#757575',
      severity: 'warning',
      commands: [
        { command: 'disconnect_simulate', value: 'true' }
      ]
    },
    {
      id: 'extreme_weather',
      title: 'Extreme Weather',
      description: 'High ambient temperature stress test',
      icon: <AcUnit />,
      color: '#ed6c02',
      severity: 'warning',
      commands: [
        { command: 'ambient_temp', value: '45' },
        { command: 'weather_mode', value: 'extreme' }
      ]
    }
  ];

  const emergencyScenarios = [
    {
      id: 'earthquake_response',
      title: 'Earthquake Emergency',
      description: 'Rapid deployment for disaster response',
      icon: <LocalHospital />,
      color: '#d32f2f'
    },
    {
      id: 'outbreak_control',
      title: 'Disease Outbreak',
      description: 'Mass vaccination campaign deployment',
      icon: <Science />,
      color: '#1976d2'
    },
    {
      id: 'border_crisis',
      title: 'Border Health Crisis',
      description: 'Cross-border vaccination effort',
      icon: <LocalHospital />,
      color: '#9c27b0'
    }
  ];

  const handleScenarioTrigger = (scenario) => {
    if (!selectedDevice) {
      alert('Please select a device first!');
      return;
    }

    setActiveScenario(scenario.id);
    
    // Send commands to selected device
    scenario.commands?.forEach(cmd => {
      if (onSendCommand) {
        onSendCommand(selectedDevice, cmd.command, cmd.value);
      }
    });

    // Auto-clear scenario after 30 seconds
    setTimeout(() => {
      setActiveScenario(null);
    }, 30000);
  };

  const handleResetAll = () => {
    if (selectedDevice && onSendCommand) {
      onSendCommand(selectedDevice, 'reset_all', 'true');
      setActiveScenario(null);
    }
  };

  const handleCustomCommand = (command, value) => {
    if (selectedDevice && onSendCommand) {
      onSendCommand(selectedDevice, command, value);
    }
  };

  const ScenarioCard = ({ scenario, isActive }) => (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        elevation={isActive ? 8 : 3}
        sx={{
          height: '100%',
          border: isActive ? `3px solid ${scenario.color}` : `1px solid ${scenario.color}30`,
          background: isActive 
            ? `linear-gradient(135deg, ${scenario.color}20 0%, ${scenario.color}10 100%)`
            : `linear-gradient(135deg, ${scenario.color}10 0%, ${scenario.color}03 100%)`,
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onClick={() => handleScenarioTrigger(scenario)}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: scenario.color, mr: 2 }}>
              {scenario.icon}
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {scenario.title}
              </Typography>
              <Chip 
                label={scenario.severity.toUpperCase()} 
                size="small" 
                color={scenario.severity === 'critical' ? 'error' : scenario.severity === 'warning' ? 'warning' : 'info'}
                sx={{ mt: 0.5 }}
              />
            </Box>
          </Box>
          <Typography variant="body2" color="textSecondary">
            {scenario.description}
          </Typography>
          
          {isActive && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Alert severity={scenario.severity} sx={{ mt: 2 }}>
                <strong>SCENARIO ACTIVE:</strong> {scenario.title} is now running on {selectedDevice}
              </Alert>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, color: 'primary.main' }}>
        🎮 Demo Control Center
      </Typography>

      {/* Demo Settings */}
      <Card elevation={3} sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
            ⚙️ Demo Settings
          </Typography>
          
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Target Device</InputLabel>
                <Select
                  value={selectedDevice || ''}
                  onChange={(e) => setSelectedScenarioDevice(e.target.value)}
                  label="Target Device"
                >
                  {devices.map((device) => (
                    <MenuItem key={device.device_id} value={device.device_id}>
                      {device.name} ({device.device_id})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={demoMode} 
                    onChange={(e) => setDemoMode(e.target.checked)}
                    color="primary"
                  />
                }
                label="Demo Mode"
              />
              <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                Enhanced visual effects for presentations
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={alertsEnabled} 
                    onChange={(e) => setAlertsEnabled(e.target.checked)}
                    color="warning"
                  />
                }
                label="Real Alerts"
              />
              <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                Send actual alerts during scenarios
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Active Scenario Status */}
      <AnimatePresence>
        {activeScenario && (
          <motion.div
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -50, opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Alert 
              severity="info" 
              sx={{ 
                mb: 3, 
                backgroundColor: theme.palette.info.main + '20',
                border: `2px solid ${theme.palette.info.main}`
              }}
              action={
                <Button color="inherit" size="small" onClick={handleResetAll}>
                  RESET
                </Button>
              }
            >
              <Typography variant="h6">
                🎬 DEMO SCENARIO ACTIVE: {scenarios.find(s => s.id === activeScenario)?.title}
              </Typography>
              <Typography variant="body2">
                Scenario will auto-reset in 30 seconds or click RESET to stop now.
              </Typography>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scenario Triggers */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        🚨 Alert Scenarios
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {scenarios.map((scenario) => (
          <Grid item xs={12} sm={6} md={4} key={scenario.id}>
            <ScenarioCard 
              scenario={scenario} 
              isActive={activeScenario === scenario.id}
            />
          </Grid>
        ))}
      </Grid>

      {/* Emergency Scenarios */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        🚑 Emergency Response Scenarios
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {emergencyScenarios.map((scenario) => (
          <Grid item xs={12} sm={4} key={scenario.id}>
            <Card 
              elevation={3} 
              sx={{ 
                border: `2px solid ${scenario.color}30`,
                cursor: 'pointer',
                '&:hover': { 
                  border: `2px solid ${scenario.color}`,
                  transform: 'translateY(-4px)',
                  transition: 'all 0.3s ease'
                }
              }}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar sx={{ bgcolor: scenario.color, width: 56, height: 56, mx: 'auto', mb: 2 }}>
                  {scenario.icon}
                </Avatar>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  {scenario.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {scenario.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
      <Card elevation={3}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3 }}>
            ⚡ Quick Actions
          </Typography>
          
          <Stack direction="row" spacing={2} flexWrap="wrap" gap={2}>
            <Button
              variant="contained"
              startIcon={<Thermostat />}
              color="error"
              onClick={() => handleCustomCommand('temp_alert', '10.5')}
              disabled={!selectedDevice}
            >
              Trigger Temp Alert
            </Button>
            
            <Button
              variant="contained"
              startIcon={<BatteryAlert />}
              color="warning"
              onClick={() => handleCustomCommand('battery_low', '15')}
              disabled={!selectedDevice}
            >
              Low Battery
            </Button>
            
            <Button
              variant="contained"
              startIcon={<Security />}
              color="info"
              onClick={() => handleCustomCommand('lid_open', 'true')}
              disabled={!selectedDevice}
            >
              Box Opened
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<Replay />}
              onClick={handleResetAll}
              disabled={!selectedDevice}
            >
              Reset All
            </Button>
          </Stack>

          {/* Custom Controls */}
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle2" sx={{ mb: 2 }}>
              Custom Temperature Control
            </Typography>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={8}>
                <Slider
                  value={customTemp}
                  onChange={(e, value) => setCustomTemp(value)}
                  min={-10}
                  max={15}
                  step={0.5}
                  marks={[
                    { value: 2, label: 'Min Safe' },
                    { value: 4, label: 'Optimal' },
                    { value: 8, label: 'Max Safe' }
                  ]}
                  valueLabelDisplay="on"
                  valueLabelFormat={(value) => `${value}°C`}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => handleCustomCommand('temp_set', customTemp.toString())}
                  disabled={!selectedDevice}
                >
                  Set Temperature
                </Button>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DemoControls;
