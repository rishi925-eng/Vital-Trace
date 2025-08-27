import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  ToggleButtonGroup,
  ToggleButton,
  useTheme,
  CircularProgress
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts';
import {
  ShowChart,
  BarChart as BarChartIcon,
  Timeline
} from '@mui/icons-material';

const DataVisualization = ({ selectedDevice, socket }) => {
  const theme = useTheme();
  const [chartType, setChartType] = useState('line');
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedDevice) {
      setLoading(true);
      setHistoricalData([]); // Clear previous data
      
      // Fetch historical data
      fetch(`http://localhost:5000/api/data/${selectedDevice}?limit=50`)
        .then(response => response.json())
        .then(data => {
          const processedData = data.map(item => ({
            ...item,
            time: new Date(item.timestamp).toLocaleTimeString('en-US', {
              hour12: false,
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
            })
          })).reverse(); // Reverse to show oldest first
          setHistoricalData(processedData);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
          setLoading(false);
        });
    }
  }, [selectedDevice]);

  useEffect(() => {
    if (socket && selectedDevice) {
      const handleDeviceData = (data) => {
        if (data.deviceId === selectedDevice) {
          const newDataPoint = {
            ...data,
            time: new Date(data.timestamp).toLocaleTimeString('en-US', {
              hour12: false,
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
            })
          };

          setHistoricalData(prevData => {
            const updatedData = [...prevData, newDataPoint];
            // Keep the data array size limited to the last 50 points for performance
            if (updatedData.length > 50) {
              return updatedData.slice(updatedData.length - 50);
            }
            return updatedData;
          });
        }
      };

      socket.on('device-data', handleDeviceData);

      return () => {
        socket.off('device-data', handleDeviceData);
      };
    }
  }, [socket, selectedDevice]);

  const handleChartTypeChange = (event, newChartType) => {
    if (newChartType !== null) {
      setChartType(newChartType);
    }
  };

  const getLineColor = (key) => {
    const colors = {
      temperature: theme.palette.error.main,
      humidity: theme.palette.info.main,
      pressure: theme.palette.secondary.main,
      light: theme.palette.warning.main,
      voltage: theme.palette.success.main
    };
    return colors[key] || theme.palette.primary.main;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Card sx={{ p: 1, minWidth: 200 }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Time: {label}
          </Typography>
          {payload.map((entry) => (
            <Typography
              key={entry.dataKey}
              variant="body2"
              sx={{ color: entry.color }}
            >
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
              {entry.dataKey === 'temperature' && '°C'}
              {entry.dataKey === 'humidity' && '%'}
              {entry.dataKey === 'pressure' && ' hPa'}
              {entry.dataKey === 'light' && ' lux'}
              {entry.dataKey === 'voltage' && ' V'}
            </Typography>
          ))}
        </Card>
      );
    }
    return null;
  };

  const renderChart = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <CircularProgress />
        </Box>
      );
    }

    if (historicalData.length === 0) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <Typography variant="h6" color="textSecondary">
            📊 No data available yet
          </Typography>
        </Box>
      );
    }

    const commonProps = {
      data: historicalData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    const chartComponents = {
      line: (
        <LineChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis 
            dataKey="time" 
            stroke={theme.palette.text.secondary}
            tick={{ fontSize: 12 }}
          />
          <YAxis stroke={theme.palette.text.secondary} tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {historicalData.some(d => d.temperature !== null) && (
            <Line
              type="monotone"
              dataKey="temperature"
              stroke={getLineColor('temperature')}
              strokeWidth={2}
              dot={{ fill: getLineColor('temperature'), strokeWidth: 2, r: 3 }}
              activeDot={{ r: 6, stroke: getLineColor('temperature'), strokeWidth: 2 }}
              name="Temperature"
            />
          )}
          
          {historicalData.some(d => d.humidity !== null) && (
            <Line
              type="monotone"
              dataKey="humidity"
              stroke={getLineColor('humidity')}
              strokeWidth={2}
              dot={{ fill: getLineColor('humidity'), strokeWidth: 2, r: 3 }}
              activeDot={{ r: 6, stroke: getLineColor('humidity'), strokeWidth: 2 }}
              name="Humidity"
            />
          )}
          
          {historicalData.some(d => d.light !== null) && (
            <Line
              type="monotone"
              dataKey="light"
              stroke={getLineColor('light')}
              strokeWidth={2}
              dot={{ fill: getLineColor('light'), strokeWidth: 2, r: 3 }}
              activeDot={{ r: 6, stroke: getLineColor('light'), strokeWidth: 2 }}
              name="Light"
            />
          )}
          
          {historicalData.some(d => d.voltage !== null) && (
            <Line
              type="monotone"
              dataKey="voltage"
              stroke={getLineColor('voltage')}
              strokeWidth={2}
              dot={{ fill: getLineColor('voltage'), strokeWidth: 2, r: 3 }}
              activeDot={{ r: 6, stroke: getLineColor('voltage'), strokeWidth: 2 }}
              name="Voltage"
            />
          )}
        </LineChart>
      ),
      
      area: (
        <AreaChart {...commonProps}>
          <defs>
            <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={getLineColor('temperature')} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={getLineColor('temperature')} stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorHumidity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={getLineColor('humidity')} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={getLineColor('humidity')} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis dataKey="time" stroke={theme.palette.text.secondary} />
          <YAxis stroke={theme.palette.text.secondary} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {historicalData.some(d => d.temperature !== null) && (
            <Area
              type="monotone"
              dataKey="temperature"
              stroke={getLineColor('temperature')}
              fillOpacity={1}
              fill="url(#colorTemp)"
              name="Temperature"
            />
          )}
          
          {historicalData.some(d => d.humidity !== null) && (
            <Area
              type="monotone"
              dataKey="humidity"
              stroke={getLineColor('humidity')}
              fillOpacity={1}
              fill="url(#colorHumidity)"
              name="Humidity"
            />
          )}
        </AreaChart>
      ),
      
      bar: (
        <BarChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis dataKey="time" stroke={theme.palette.text.secondary} />
          <YAxis stroke={theme.palette.text.secondary} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {historicalData.some(d => d.temperature !== null) && (
            <Bar
              dataKey="temperature"
              fill={getLineColor('temperature')}
              name="Temperature"
              radius={[4, 4, 0, 0]}
            />
          )}
          
          {historicalData.some(d => d.humidity !== null) && (
            <Bar
              dataKey="humidity"
              fill={getLineColor('humidity')}
              name="Humidity"
              radius={[4, 4, 0, 0]}
            />
          )}
        </BarChart>
      )
    };

    return (
      <ResponsiveContainer width="100%" height={400}>
        {chartComponents[chartType]}
      </ResponsiveContainer>
    );
  };

  if (!selectedDevice) {
    return (
      <Card elevation={3}>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <ShowChart sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            📈 Select a device to view data visualization
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              📈 Data Visualization - {selectedDevice}
            </Typography>
            
            <ToggleButtonGroup
              value={chartType}
              exclusive
              onChange={handleChartTypeChange}
              size="small"
            >
              <ToggleButton value="line">
                <ShowChart sx={{ mr: 1 }} />
                Line
              </ToggleButton>
              <ToggleButton value="area">
                <Timeline sx={{ mr: 1 }} />
                Area
              </ToggleButton>
              <ToggleButton value="bar">
                <BarChartIcon sx={{ mr: 1 }} />
                Bar
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>
          
          {renderChart()}
          
          <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
            Showing last 50 data points • Real-time updates
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default DataVisualization;
