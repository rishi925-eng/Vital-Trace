/*
 * Vital Trace Cold Chain Simulator
 * 
 * This script simulates Vital Trace boxes in the field for 
 * cold chain monitoring demonstration. Each box represents 
 * a real-world vaccine storage unit being transported by 
 * health workers in remote areas.
 */

const io = require('socket.io-client');

const SERVER_URL = 'http://localhost:5000';

// Simulate 25 Vital Trace boxes across different regions and use cases
const vitalTraceBoxes = [
  // === NORTHERN INDIA ===
  {
    device_id: 'VIT_BOX_001',
    name: 'Delhi Primary Health Center - COVID Vaccines',
    type: 'vital_trace_box',
    location: { lat: 28.6139, lng: 77.2090, name: 'New Delhi' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'active_cooling',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_002',
    name: 'Punjab Rural Clinic - Hepatitis B',
    type: 'vital_trace_box',
    location: { lat: 31.3260, lng: 75.5762, name: 'Jalandhar, Punjab' },
    targetTemp: 5.0,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'medium'
  },
  {
    device_id: 'VIT_BOX_003',
    name: 'Himachal Mobile Unit - Child Vaccines',
    type: 'vital_trace_box',
    location: { lat: 32.2431, lng: 77.1892, name: 'Shimla, Himachal' },
    targetTemp: 3.5,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_004',
    name: 'Haryana Health Worker - Measles',
    type: 'vital_trace_box',
    location: { lat: 29.0588, lng: 76.0856, name: 'Karnal, Haryana' },
    targetTemp: 4.5,
    batteryCapacity: 8000,
    status: 'standby',
    priority: 'medium'
  },

  // === EASTERN INDIA ===
  {
    device_id: 'VIT_BOX_005',
    name: 'Kolkata Metro Health - Flu Vaccines',
    type: 'vital_trace_box',
    location: { lat: 22.5726, lng: 88.3639, name: 'Kolkata, West Bengal' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'active_cooling',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_006',
    name: 'Bhubaneswar Clinic - Polio Campaign',
    type: 'vital_trace_box',
    location: { lat: 20.2961, lng: 85.8245, name: 'Bhubaneswar, Odisha' },
    targetTemp: 5.5,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'critical'
  },
  {
    device_id: 'VIT_BOX_007',
    name: 'Assam Tea Garden - Rural Outreach',
    type: 'vital_trace_box',
    location: { lat: 26.2006, lng: 92.9376, name: 'Guwahati, Assam' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'medium'
  },
  {
    device_id: 'VIT_BOX_008',
    name: 'Patna District Hospital - Emergency Stock',
    type: 'vital_trace_box',
    location: { lat: 25.5941, lng: 85.1376, name: 'Patna, Bihar' },
    targetTemp: 3.0,
    batteryCapacity: 8000,
    status: 'critical_temp',
    priority: 'critical'
  },

  // === WESTERN INDIA ===
  {
    device_id: 'VIT_BOX_009',
    name: 'Mumbai Slum Outreach - TB Vaccines',
    type: 'vital_trace_box',
    location: { lat: 19.0760, lng: 72.8777, name: 'Mumbai, Maharashtra' },
    targetTemp: 4.5,
    batteryCapacity: 8000,
    status: 'active_cooling',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_010',
    name: 'Pune Rural Health - Typhoid',
    type: 'vital_trace_box',
    location: { lat: 18.5204, lng: 73.8567, name: 'Pune, Maharashtra' },
    targetTemp: 5.0,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'medium'
  },
  {
    device_id: 'VIT_BOX_011',
    name: 'Gujarat Tribal Area - Multi-dose',
    type: 'vital_trace_box',
    location: { lat: 23.0225, lng: 72.5714, name: 'Ahmedabad, Gujarat' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_012',
    name: 'Rajasthan Desert Unit - Cholera',
    type: 'vital_trace_box',
    location: { lat: 26.9124, lng: 75.7873, name: 'Jaipur, Rajasthan' },
    targetTemp: 6.0,
    batteryCapacity: 8000,
    status: 'high_temp_alert',
    priority: 'critical'
  },

  // === SOUTHERN INDIA ===
  {
    device_id: 'VIT_BOX_013',
    name: 'Bangalore Tech Hub - Employee Health',
    type: 'vital_trace_box',
    location: { lat: 12.9716, lng: 77.5946, name: 'Bangalore, Karnataka' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'active_cooling',
    priority: 'medium'
  },
  {
    device_id: 'VIT_BOX_014',
    name: 'Chennai Coastal Clinic - Dengue Prevention',
    type: 'vital_trace_box',
    location: { lat: 13.0827, lng: 80.2707, name: 'Chennai, Tamil Nadu' },
    targetTemp: 5.0,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_015',
    name: 'Kerala Backwater Health - Malaria',
    type: 'vital_trace_box',
    location: { lat: 9.9312, lng: 76.2673, name: 'Kochi, Kerala' },
    targetTemp: 4.5,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'medium'
  },
  {
    device_id: 'VIT_BOX_016',
    name: 'Hyderabad Metro - COVID Boosters',
    type: 'vital_trace_box',
    location: { lat: 17.3850, lng: 78.4867, name: 'Hyderabad, Telangana' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'standby',
    priority: 'high'
  },

  // === CENTRAL INDIA ===
  {
    device_id: 'VIT_BOX_017',
    name: 'Bhopal Tribal Outreach - Multi-vaccine',
    type: 'vital_trace_box',
    location: { lat: 23.2599, lng: 77.4126, name: 'Bhopal, Madhya Pradesh' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_018',
    name: 'Nagpur Rural Circuit - Encephalitis',
    type: 'vital_trace_box',
    location: { lat: 21.1458, lng: 79.0882, name: 'Nagpur, Maharashtra' },
    targetTemp: 3.5,
    batteryCapacity: 8000,
    status: 'low_battery',
    priority: 'critical'
  },
  {
    device_id: 'VIT_BOX_019',
    name: 'Indore Industrial Area - Hepatitis A',
    type: 'vital_trace_box',
    location: { lat: 22.7196, lng: 75.8577, name: 'Indore, Madhya Pradesh' },
    targetTemp: 5.5,
    batteryCapacity: 8000,
    status: 'active_cooling',
    priority: 'medium'
  },

  // === SPECIAL OPERATIONS ===
  {
    device_id: 'VIT_BOX_020',
    name: 'Emergency Response Unit - Multi-vaccine',
    type: 'vital_trace_box',
    location: { lat: 26.7606, lng: 83.3732, name: 'Gorakhpur, UP' },
    targetTemp: 2.5,
    batteryCapacity: 8000,
    status: 'emergency_deployment',
    priority: 'critical'
  },
  {
    device_id: 'VIT_BOX_021',
    name: 'Border Health Post - International',
    type: 'vital_trace_box',
    location: { lat: 32.7302, lng: 74.8570, name: 'Jammu, J&K' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'in_transit',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_022',
    name: 'Disaster Relief Unit - Emergency Stock',
    type: 'vital_trace_box',
    location: { lat: 15.2993, lng: 74.1240, name: 'Goa' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'standby',
    priority: 'high'
  },
  {
    device_id: 'VIT_BOX_023',
    name: 'Tribal Research Center - Experimental',
    type: 'vital_trace_box',
    location: { lat: 11.0168, lng: 76.9558, name: 'Coimbatore, Tamil Nadu' },
    targetTemp: 3.0,
    batteryCapacity: 8000,
    status: 'research_mode',
    priority: 'low'
  },
  {
    device_id: 'VIT_BOX_024',
    name: 'Island Health Service - Remote Access',
    type: 'vital_trace_box',
    location: { lat: 11.7401, lng: 92.6586, name: 'Port Blair, A&N Islands' },
    targetTemp: 5.0,
    batteryCapacity: 8000,
    status: 'satellite_mode',
    priority: 'medium'
  },
  {
    device_id: 'VIT_BOX_025',
    name: 'Mountain Rescue Unit - High Altitude',
    type: 'vital_trace_box',
    location: { lat: 34.0837, lng: 74.7973, name: 'Srinagar, Kashmir' },
    targetTemp: 4.0,
    batteryCapacity: 8000,
    status: 'extreme_conditions',
    priority: 'high'
  }
];

class VitalTraceSimulator {
  constructor(boxConfig) {
    this.config = boxConfig;
    this.socket = null;
    this.isConnected = false;
    this.dataInterval = null;
    
    // Cold chain specific states
    this.currentTemp = boxConfig.targetTemp + (Math.random() - 0.5) * 2;
    this.lidOpenings = 0;
    this.lastLidOpen = null;
    this.coolingActive = false;
    this.batteryLevel = 95 + Math.random() * 5; // Start with high battery
    this.journeyDistance = 0;
    this.lastLocation = { ...boxConfig.location };
    this.temperatureExcursions = [];
    
    this.connect();
  }

  connect() {
    console.log(`📦 Connecting Vital Trace Box: ${this.config.name}...`);
    
    this.socket = io(SERVER_URL, {
      transports: ['websocket', 'polling']
    });

    this.socket.on('connect', () => {
      console.log(`✅ ${this.config.name} - ONLINE`);
      this.isConnected = true;
      this.registerBox();
      this.startMonitoring();
    });

    this.socket.on('disconnect', () => {
      console.log(`❌ ${this.config.name} - OFFLINE`);
      this.isConnected = false;
      if (this.dataInterval) {
        clearInterval(this.dataInterval);
      }
    });

    this.socket.on('command', (command) => {
      this.handleCommand(command);
    });
  }

  registerBox() {
    const deviceInfo = {
      device_id: this.config.device_id,
      name: this.config.name,
      type: 'vital_trace_box',
      firmware_version: '2.1.0-field',
      capabilities: [
        'temperature_monitoring', 
        'gps_tracking', 
        'tamper_detection',
        'active_cooling',
        'solar_charging',
        'cold_chain_compliance'
      ],
      location: this.config.location
    };

    this.socket.emit('device_register', deviceInfo);
    console.log(`🩺 Registered: ${this.config.name}`);
  }

  generateColdChainData() {
    const now = Date.now();
    const timeOfDay = new Date().getHours();
    
    // === TEMPERATURE CONTROL SIMULATION ===
    let targetTemp = this.config.targetTemp;
    let ambientTemp = 25 + Math.sin((timeOfDay - 12) * Math.PI / 12) * 8; // 17-33°C ambient
    
    // === STATUS-SPECIFIC BEHAVIORS ===
    // Apply realistic temperature variations based on operational status
    switch(this.config.status) {
      case 'critical_temp':
        // Force temperature excursions for demonstration
        if (Math.random() < 0.3) {
          this.currentTemp += (Math.random() - 0.5) * 4; // More volatile
        }
        break;
      case 'high_temp_alert':
        // Simulate desert conditions
        ambientTemp += 8; // Hotter environment
        break;
      case 'low_battery':
        // Reduce cooling effectiveness
        this.batteryLevel = Math.max(10, this.batteryLevel - 0.1);
        break;
      case 'emergency_deployment':
        // Emergency boxes operate in extreme conditions
        ambientTemp += Math.random() * 10;
        break;
      case 'extreme_conditions':
        // High altitude/extreme weather
        ambientTemp -= 10; // Mountain conditions
        if (Math.random() < 0.1) {
          this.currentTemp += (Math.random() - 0.5) * 2;
        }
        break;
    }
    
    // Cooling system logic
    if (this.currentTemp > targetTemp + 1) {
      this.coolingActive = true;
    } else if (this.currentTemp < targetTemp - 0.5) {
      this.coolingActive = false;
    }
    
    // Temperature physics simulation
    if (this.coolingActive && this.batteryLevel > 10) {
      // Active cooling brings temperature down
      this.currentTemp += (targetTemp - this.currentTemp) * 0.3;
      this.batteryLevel -= 0.05; // Cooling uses battery
    } else {
      // Passive warming towards ambient
      this.currentTemp += (ambientTemp - this.currentTemp) * 0.02;
    }
    
    // Add small random variations
    this.currentTemp += (Math.random() - 0.5) * 0.2;
    
    // === GPS & MOVEMENT SIMULATION ===
    // Simulate movement for 'in_transit' boxes
    if (this.config.status === 'in_transit') {
      const movementRange = 0.001; // ~100m variance
      this.lastLocation.lat += (Math.random() - 0.5) * movementRange;
      this.lastLocation.lng += (Math.random() - 0.5) * movementRange;
      this.journeyDistance += Math.random() * 0.1; // km
    }
    
    // === BATTERY & SOLAR SIMULATION ===
    // Solar charging during day (6 AM - 6 PM)
    if (timeOfDay >= 6 && timeOfDay <= 18) {
      this.batteryLevel += 0.02; // Solar recharging
    } else {
      this.batteryLevel -= 0.01; // Night consumption
    }
    this.batteryLevel = Math.max(5, Math.min(100, this.batteryLevel));
    
    // === LID OPENING SIMULATION ===
    let lidOpened = false;
    if (Math.random() < 0.008) { // 0.8% chance - rare events
      lidOpened = true;
      this.lidOpenings++;
      this.lastLidOpen = now;
      console.log(`🚪 BOX OPENED: ${this.config.name} - Total openings: ${this.lidOpenings}`);
      
      // Opening lid causes temperature excursion
      this.currentTemp += Math.random() * 3;
    }
    
    // === COLD CHAIN COMPLIANCE ===
    const tempInRange = this.currentTemp >= 2 && this.currentTemp <= 8;
    const batteryOK = this.batteryLevel > 15;
    const coolingStatus = this.coolingActive ? 'active' : 'standby';
    
    // Track temperature excursions
    if (!tempInRange) {
      this.temperatureExcursions.push({
        timestamp: now,
        temperature: this.currentTemp,
        duration: 1 // minutes
      });
    }
    
    // === ALERT CONDITIONS ===
    let alertLevel = 'normal';
    let alertMessage = null;
    
    if (this.currentTemp > 8) {
      alertLevel = 'critical';
      alertMessage = `CRITICAL: Temperature exceeded safe range (${this.currentTemp.toFixed(1)}°C)`;
    } else if (this.currentTemp < 2) {
      alertLevel = 'warning';  
      alertMessage = `WARNING: Temperature below optimal range (${this.currentTemp.toFixed(1)}°C)`;
    } else if (this.batteryLevel < 20) {
      alertLevel = 'warning';
      alertMessage = `LOW BATTERY: ${this.batteryLevel.toFixed(1)}% remaining`;
    } else if (lidOpened) {
      alertLevel = 'info';
      alertMessage = `Lid opened - Check authorized access`;
    }

    return {
      device_id: this.config.device_id,
      
      // Core cold chain metrics
      temperature: Math.round(this.currentTemp * 100) / 100,
      target_temperature: targetTemp,
      temperature_in_range: tempInRange,
      
      // Location & movement
      latitude: Math.round(this.lastLocation.lat * 10000) / 10000,
      longitude: Math.round(this.lastLocation.lng * 10000) / 10000,
      location_name: this.lastLocation.name,
      journey_distance: Math.round(this.journeyDistance * 100) / 100,
      
      // Power & cooling system
      battery_percentage: Math.round(this.batteryLevel * 10) / 10,
      cooling_active: this.coolingActive,
      cooling_status: coolingStatus,
      solar_charging: timeOfDay >= 6 && timeOfDay <= 18,
      
      // Security & tamper detection
      lid_opened: lidOpened,
      lid_open_count: this.lidOpenings,
      last_lid_open: this.lastLidOpen,
      
      // Compliance & alerts
      cold_chain_compliant: tempInRange && batteryOK,
      alert_level: alertLevel,
      alert_message: alertMessage,
      excursion_count: this.temperatureExcursions.length,
      
      // Standard IoT fields
      timestamp: new Date().toISOString(),
      signal_strength: -40 + Math.random() * 15,
      firmware_version: '2.1.0',
      
      // Additional context
      ambient_temperature: Math.round(ambientTemp * 10) / 10,
      status: this.config.status,
      voltage: 3.3 + (this.batteryLevel / 100) * 0.9 // 3.3V - 4.2V range
    };
  }

  startMonitoring() {
    const sendData = () => {
      if (this.isConnected) {
        const coldChainData = this.generateColdChainData();
        this.socket.emit('sensor_data', coldChainData);
        
        // Log important events
        if (coldChainData.alert_level !== 'normal') {
          console.log(`🚨 ${this.config.name}: ${coldChainData.alert_message}`);
        } else if (Math.random() < 0.05) { // 5% chance for normal status
          console.log(`✅ ${this.config.name}: ${coldChainData.temperature}°C, Battery: ${coldChainData.battery_percentage}%`);
        }
      }
      
      // Send data every 30-60 seconds (more realistic for field conditions)
      const nextInterval = 30000 + Math.random() * 30000;
      this.dataInterval = setTimeout(sendData, nextInterval);
    };

    // Start monitoring after brief delay
    setTimeout(sendData, 2000 + Math.random() * 3000);
  }

  handleCommand(command) {
    console.log(`🎮 ${this.config.name} received command:`, command);
    
    const { command: cmd, value } = command;
    
    switch (cmd) {
      case 'cooling_override':
        this.coolingActive = value === 'on';
        console.log(`❄️ ${this.config.name}: Cooling ${value === 'on' ? 'FORCED ON' : 'AUTO'}`);
        break;
        
      case 'status_check':
        console.log(`📊 ${this.config.name}: Status check requested`);
        // Send immediate data update
        if (this.isConnected) {
          const statusData = this.generateColdChainData();
          this.socket.emit('sensor_data', statusData);
        }
        break;
        
      case 'emergency_alert':
        console.log(`🚨 ${this.config.name}: EMERGENCY ALERT TRIGGERED`);
        break;
        
      case 'reset':
        console.log(`🔄 ${this.config.name}: System reset`);
        this.lidOpenings = 0;
        this.temperatureExcursions = [];
        break;
        
      default:
        console.log(`❓ ${this.config.name}: Unknown command: ${cmd}`);
    }
  }
}

// === STARTUP SEQUENCE ===
console.log('🩺 VITAL TRACE COLD CHAIN SIMULATOR');
console.log('===================================');
console.log('Simulating real-world vaccine storage boxes in the field...\n');

const simulators = [];

// Start all Vital Trace boxes with staggered connections
vitalTraceBoxes.forEach((boxConfig, index) => {
  setTimeout(() => {
    const simulator = new VitalTraceSimulator(boxConfig);
    simulators.push(simulator);
  }, index * 2000); // 2-second delays between connections
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down Vital Trace simulators...');
  simulators.forEach(sim => {
    if (sim.socket) {
      sim.socket.close();
    }
  });
  process.exit(0);
});

console.log(`\nStarting ${vitalTraceBoxes.length} Vital Trace boxes...`);
console.log('Press Ctrl+C to stop the simulation\n');
