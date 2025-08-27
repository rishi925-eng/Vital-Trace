import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Pagination,
  useTheme,
  CircularProgress,
  Chip
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { motion } from 'framer-motion';
import {
  History,
  Download,
  DateRange,
  Assessment
} from '@mui/icons-material';

const DataHistory = ({ selectedDevice, socket }) => {
  const theme = useTheme();
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [rowsPerPage] = useState(10);
  const [timeRange, setTimeRange] = useState('24h');
  const [startDate, setStartDate] = useState(new Date(Date.now() - 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState(new Date());
  const [customDateRange, setCustomDateRange] = useState(false);

  useEffect(() => {
    if (selectedDevice) {
      fetchHistoricalData();
    }
  }, [selectedDevice, timeRange, startDate, endDate, customDateRange]);

  const fetchHistoricalData = () => {
    if (!selectedDevice) return;

    setLoading(true);
    let url = `http://localhost:5000/api/data/${selectedDevice}`;

    if (customDateRange) {
      url += `/range?start=${startDate.toISOString()}&end=${endDate.toISOString()}`;
    } else {
      const limit = getRowsForTimeRange(timeRange);
      url += `?limit=${limit}`;
    }

    fetch(url)
      .then(response => response.json())
      .then(data => {
        setHistoricalData(data);
        setLoading(false);
        setPage(1);
      })
      .catch(error => {
        console.error('Error fetching historical data:', error);
        setLoading(false);
      });
  };

  const getRowsForTimeRange = (range) => {
    const rangeMap = {
      '1h': 60,
      '6h': 360,
      '24h': 1440,
      '7d': 10080,
      '30d': 43200
    };
    return rangeMap[range] || 100;
  };

  const handleTimeRangeChange = (event) => {
    const newRange = event.target.value;
    setTimeRange(newRange);
    
    if (newRange === 'custom') {
      setCustomDateRange(true);
    } else {
      setCustomDateRange(false);
      const now = new Date();
      const hours = {
        '1h': 1,
        '6h': 6,
        '24h': 24,
        '7d': 168,
        '30d': 720
      };
      setStartDate(new Date(now - hours[newRange] * 60 * 60 * 1000));
      setEndDate(now);
    }
  };

  const exportToCSV = () => {
    const csvContent = [
      ['Timestamp', 'Device ID', 'Temperature', 'Humidity', 'Pressure', 'Light', 'Motion', 'Voltage'],
      ...historicalData.map(row => [
        row.timestamp,
        row.device_id,
        row.temperature || '',
        row.humidity || '',
        row.pressure || '',
        row.light || '',
        row.motion !== null ? row.motion : '',
        row.voltage || ''
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedDevice}_data_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getValueColor = (type, value) => {
    if (value === null || value === undefined) return 'text.secondary';
    
    const colorRules = {
      temperature: value > 30 ? 'error.main' : value < 10 ? 'info.main' : 'success.main',
      humidity: value > 70 ? 'warning.main' : value < 30 ? 'error.main' : 'success.main',
      motion: value ? 'error.main' : 'success.main',
      voltage: value < 3.0 ? 'error.main' : value < 3.5 ? 'warning.main' : 'success.main'
    };
    
    return colorRules[type] || 'text.primary';
  };

  const formatValue = (type, value) => {
    if (value === null || value === undefined) return '-';
    
    if (type === 'motion') {
      return value ? 'Yes' : 'No';
    }
    
    if (typeof value === 'number') {
      return value.toFixed(2);
    }
    
    return value;
  };

  const getUnit = (type) => {
    const units = {
      temperature: '°C',
      humidity: '%',
      pressure: ' hPa',
      light: ' lux',
      voltage: ' V'
    };
    return units[type] || '';
  };

  if (!selectedDevice) {
    return (
      <Card elevation={3}>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <History sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            📊 Select a device to view historical data
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const paginatedData = historicalData.slice((page - 1) * rowsPerPage, page * rowsPerPage);
  const totalPages = Math.ceil(historicalData.length / rowsPerPage);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card elevation={3}>
        <CardContent>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <History sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              📊 Data History - {selectedDevice}
            </Typography>
            <Box sx={{ ml: 'auto', display: 'flex', gap: 2, alignItems: 'center' }}>
              <Chip
                label={`${historicalData.length} records`}
                size="small"
                color="primary"
                variant="outlined"
              />
              <Button
                size="small"
                startIcon={<Download />}
                onClick={exportToCSV}
                disabled={historicalData.length === 0}
                variant="outlined"
                sx={{ textTransform: 'none' }}
              >
                Export CSV
              </Button>
            </Box>
          </Box>

          {/* Controls */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Time Range</InputLabel>
                <Select
                  value={customDateRange ? 'custom' : timeRange}
                  label="Time Range"
                  onChange={handleTimeRangeChange}
                >
                  <MenuItem value="1h">Last Hour</MenuItem>
                  <MenuItem value="6h">Last 6 Hours</MenuItem>
                  <MenuItem value="24h">Last 24 Hours</MenuItem>
                  <MenuItem value="7d">Last 7 Days</MenuItem>
                  <MenuItem value="30d">Last 30 Days</MenuItem>
                  <MenuItem value="custom">Custom Range</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {customDateRange && (
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <Grid item xs={12} sm={6} md={3}>
                  <DateTimePicker
                    label="Start Date"
                    value={startDate}
                    onChange={setStartDate}
                    slotProps={{ textField: { size: 'small', fullWidth: true } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <DateTimePicker
                    label="End Date"
                    value={endDate}
                    onChange={setEndDate}
                    slotProps={{ textField: { size: 'small', fullWidth: true } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={fetchHistoricalData}
                    startIcon={<Assessment />}
                    sx={{ height: '40px', textTransform: 'none' }}
                  >
                    Apply Filter
                  </Button>
                </Grid>
              </LocalizationProvider>
            )}
          </Grid>

          {/* Data Table */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <TableContainer component={Paper} elevation={0} sx={{ border: `1px solid ${theme.palette.divider}` }}>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)' }}>
                      <TableCell sx={{ fontWeight: 600 }}>Timestamp</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Temperature</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Humidity</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Pressure</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Light</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 600 }}>Motion</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Voltage</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paginatedData.map((row, index) => (
                      <motion.tr
                        key={row.id}
                        component={TableRow}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        sx={{
                          '&:hover': {
                            backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)'
                          }
                        }}
                      >
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {new Date(row.timestamp).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography 
                            variant="body2" 
                            sx={{ color: getValueColor('temperature', row.temperature) }}
                          >
                            {formatValue('temperature', row.temperature)}{getUnit('temperature')}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography 
                            variant="body2" 
                            sx={{ color: getValueColor('humidity', row.humidity) }}
                          >
                            {formatValue('humidity', row.humidity)}{getUnit('humidity')}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatValue('pressure', row.pressure)}{getUnit('pressure')}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatValue('light', row.light)}{getUnit('light')}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography 
                            variant="body2" 
                            sx={{ color: getValueColor('motion', row.motion) }}
                          >
                            {formatValue('motion', row.motion)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography 
                            variant="body2" 
                            sx={{ color: getValueColor('voltage', row.voltage) }}
                          >
                            {formatValue('voltage', row.voltage)}{getUnit('voltage')}
                          </Typography>
                        </TableCell>
                      </motion.tr>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(e, newPage) => setPage(newPage)}
                    color="primary"
                    size="small"
                  />
                </Box>
              )}

              {historicalData.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" color="textSecondary">
                    📊 No historical data found
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Data will appear here once your device starts sending information
                  </Typography>
                </Box>
              )}
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default DataHistory;
