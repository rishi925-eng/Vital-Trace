from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token
from flask_migrate import Migrate
import os
import logging
import json
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict, deque

from config import config
from models import db, bcrypt, User, Device, SensorData, Alert, UserSession, MaintenanceLog, SystemMetrics
from services.analytics_service import AnalyticsService
from services.alert_service import AlertService
from services.notification_service import NotificationService
from services.auth_service import AuthService

def create_app(config_name: str = 'development') -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler(app.config['LOG_FILE'])
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Vital Trace startup')
    
    return app

# Create application instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Initialize SocketIO with enhanced configuration
socketio = SocketIO(
    app,
    cors_allowed_origins=app.config['CORS_ORIGINS'],
    logger=True,
    engineio_logger=True,
    async_mode='threading'
)

# Global data storage for real-time operations
devices_data = {}
connected_clients = set()
device_rooms = defaultdict(set)
alert_history = deque(maxlen=1000)
performance_metrics = defaultdict(lambda: deque(maxlen=100))

# Initialize services
analytics_service = AnalyticsService()
alert_service = AlertService()
notification_service = NotificationService(socketio)
auth_service = AuthService()

class VitalTraceBackend:
    """Enhanced backend service for Vital Trace IoT monitoring"""
    
    def __init__(self):
        self.devices = {}
        self.real_time_data = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.data_buffer = defaultdict(lambda: deque(maxlen=50))
        self.alert_rules = self._initialize_alert_rules()
        self.performance_tracker = {}
        
    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize alert rules for different scenarios"""
        return {
            'temperature_high': {
                'threshold': 8.0,
                'severity': 'high',
                'message': 'Temperature above safe range'
            },
            'temperature_low': {
                'threshold': 2.0,
                'severity': 'high', 
                'message': 'Temperature below safe range'
            },
            'temperature_critical': {
                'threshold': 10.0,
                'severity': 'critical',
                'message': 'Critical temperature excursion'
            },
            'battery_low': {
                'threshold': 20,
                'severity': 'medium',
                'message': 'Battery level is low'
            },
            'battery_critical': {
                'threshold': 5,
                'severity': 'critical',
                'message': 'Battery level critically low'
            },
            'door_open': {
                'duration_threshold': 300,  # 5 minutes
                'severity': 'medium',
                'message': 'Storage door has been open too long'
            },
            'connectivity_loss': {
                'duration_threshold': 600,  # 10 minutes
                'severity': 'high',
                'message': 'Device connectivity lost'
            }
        }
    
    def register_device(self, device_data: Dict[str, Any]) -> bool:
        """Register a new IoT device"""
        try:
            device_id = device_data.get('device_id')
            if not device_id:
                return False
            
            # Check if device exists in database
            device = Device.query.filter_by(device_id=device_id).first()
            
            if not device:
                # Create new device
                device = Device(
                    device_id=device_id,
                    name=device_data.get('name', f'Device {device_id}'),
                    location=device_data.get('location', 'Unknown'),
                    latitude=device_data.get('latitude'),
                    longitude=device_data.get('longitude'),
                    target_temp_min=device_data.get('target_temp_min', 2.0),
                    target_temp_max=device_data.get('target_temp_max', 8.0),
                    battery_capacity=device_data.get('battery_capacity', 100),
                    status=device_data.get('status', 'active'),
                    priority=device_data.get('priority', 'medium')
                )
                db.session.add(device)
                db.session.commit()
            
            self.devices[device_id] = device.to_dict()
            app.logger.info(f'Device {device_id} registered successfully')
            return True
            
        except Exception as e:
            app.logger.error(f'Failed to register device: {str(e)}')
            return False
    
    def process_sensor_data(self, data: Dict[str, Any]) -> None:
        """Process incoming sensor data with advanced analytics"""
        try:
            device_id = data.get('device_id')
            if not device_id or device_id not in self.devices:
                app.logger.warning(f'Unknown device: {device_id}')
                return
            
            # Store in database
            sensor_data = SensorData(
                device_id=device_id,
                temperature=data.get('temperature'),
                humidity=data.get('humidity'),
                battery_level=data.get('battery_level'),
                door_open=data.get('door_open', False),
                power_status=data.get('power_status', 'normal'),
                signal_strength=data.get('signal_strength')
            )
            db.session.add(sensor_data)
            db.session.commit()
            
            # Update real-time data
            self.real_time_data[device_id] = data
            self.data_buffer[device_id].append(data)
            
            # Perform analytics
            self._analyze_data(device_id, data)
            
            # Check for alerts
            self._check_alerts(device_id, data)
            
            # Emit real-time update
            socketio.emit('real_time_data', data, room='dashboard')
            
            app.logger.debug(f'Processed sensor data for device {device_id}')
            
        except Exception as e:
            app.logger.error(f'Failed to process sensor data: {str(e)}')
    
    def _analyze_data(self, device_id: str, data: Dict[str, Any]) -> None:
        """Perform advanced analytics on sensor data"""
        try:
            # Anomaly detection
            if len(self.data_buffer[device_id]) >= 10:
                values = [[d.get('temperature', 0), d.get('humidity', 0), 
                          d.get('battery_level', 0)] for d in self.data_buffer[device_id]]
                
                try:
                    anomaly_score = self.anomaly_detector.fit_predict([values[-1]])[0]
                    if anomaly_score == -1:  # Anomaly detected
                        self._create_alert(device_id, 'anomaly', 'medium', 
                                         'Anomalous sensor reading detected', data)
                except Exception as e:
                    app.logger.warning(f'Anomaly detection failed: {str(e)}')
            
            # Trend analysis
            analytics_service.analyze_trends(device_id, list(self.data_buffer[device_id]))
            
            # Update performance metrics
            self._update_performance_metrics(device_id, data)
            
        except Exception as e:
            app.logger.error(f'Analytics failed for device {device_id}: {str(e)}')
    
    def _check_alerts(self, device_id: str, data: Dict[str, Any]) -> None:
        """Check for alert conditions"""
        try:
            temperature = data.get('temperature', 0)
            battery_level = data.get('battery_level', 100)
            door_open = data.get('door_open', False)
            
            # Temperature alerts
            if temperature > self.alert_rules['temperature_critical']['threshold']:
                self._create_alert(device_id, 'temperature_critical', 'critical',
                                 f'Critical temperature: {temperature}°C', data)
            elif temperature > self.alert_rules['temperature_high']['threshold']:
                self._create_alert(device_id, 'temperature_high', 'high',
                                 f'High temperature: {temperature}°C', data)
            elif temperature < self.alert_rules['temperature_low']['threshold']:
                self._create_alert(device_id, 'temperature_low', 'high',
                                 f'Low temperature: {temperature}°C', data)
            
            # Battery alerts
            if battery_level <= self.alert_rules['battery_critical']['threshold']:
                self._create_alert(device_id, 'battery_critical', 'critical',
                                 f'Critical battery: {battery_level}%', data)
            elif battery_level <= self.alert_rules['battery_low']['threshold']:
                self._create_alert(device_id, 'battery_low', 'medium',
                                 f'Low battery: {battery_level}%', data)
            
            # Door open alert (if door has been open too long)
            if door_open:
                # This would require tracking door open duration
                # Implementation would track state over time
                pass
                
        except Exception as e:
            app.logger.error(f'Alert checking failed for device {device_id}: {str(e)}')
    
    def _create_alert(self, device_id: str, alert_type: str, severity: str, 
                     message: str, data: Dict[str, Any]) -> None:
        """Create and store an alert"""
        try:
            # Check if similar alert already exists and is active
            existing_alert = Alert.query.filter_by(
                device_id=device_id,
                alert_type=alert_type,
                status='active'
            ).first()
            
            if existing_alert:
                return  # Don't create duplicate alerts
            
            # Create new alert
            alert = Alert(
                device_id=device_id,
                alert_type=alert_type,
                severity=severity,
                title=f'{alert_type.replace("_", " ").title()} - {self.devices[device_id]["name"]}',
                message=message
            )
            alert.set_metadata(data)
            db.session.add(alert)
            db.session.commit()
            
            # Add to history
            alert_history.append(alert.to_dict())
            
            # Emit alert to connected clients
            socketio.emit('new_alert', alert.to_dict(), room='alerts')
            
            # Send notifications
            notification_service.send_alert_notification(alert)
            
            app.logger.info(f'Alert created: {alert_type} for device {device_id}')
            
        except Exception as e:
            app.logger.error(f'Failed to create alert: {str(e)}')
    
    def _update_performance_metrics(self, device_id: str, data: Dict[str, Any]) -> None:
        """Update system performance metrics"""
        try:
            timestamp = datetime.now(timezone.utc)
            
            # Device-specific metrics
            performance_metrics[f'{device_id}_temperature'].append({
                'value': data.get('temperature', 0),
                'timestamp': timestamp
            })
            
            performance_metrics[f'{device_id}_battery'].append({
                'value': data.get('battery_level', 0),
                'timestamp': timestamp
            })
            
            # System-wide metrics
            active_devices = len([d for d in self.devices.values() if d.get('status') == 'active'])
            performance_metrics['active_devices'].append({
                'value': active_devices,
                'timestamp': timestamp
            })
            
        except Exception as e:
            app.logger.error(f'Failed to update performance metrics: {str(e)}')
    
    def get_device_analytics(self, device_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get advanced analytics for a specific device"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            # Get sensor data from database
            sensor_data = SensorData.query.filter(
                SensorData.device_id == device_id,
                SensorData.timestamp >= start_time
            ).order_by(SensorData.timestamp).all()
            
            if not sensor_data:
                return {'error': 'No data available'}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame([d.to_dict() for d in sensor_data])
            
            analytics = {
                'device_id': device_id,
                'period': f'{hours} hours',
                'total_readings': len(df),
                'temperature_stats': {
                    'mean': float(df['temperature'].mean()),
                    'min': float(df['temperature'].min()),
                    'max': float(df['temperature'].max()),
                    'std': float(df['temperature'].std())
                },
                'battery_trend': {
                    'start_level': float(df['battery_level'].iloc[0]) if len(df) > 0 else 0,
                    'end_level': float(df['battery_level'].iloc[-1]) if len(df) > 0 else 0,
                    'average_drain_rate': self._calculate_battery_drain_rate(df)
                },
                'alerts_count': Alert.query.filter(
                    Alert.device_id == device_id,
                    Alert.created_at >= start_time
                ).count(),
                'uptime_percentage': self._calculate_uptime(device_id, hours),
                'compliance_score': self._calculate_compliance_score(df),
                'predictions': analytics_service.predict_maintenance(device_id)
            }
            
            return analytics
            
        except Exception as e:
            app.logger.error(f'Failed to get analytics for device {device_id}: {str(e)}')
            return {'error': str(e)}
    
    def _calculate_battery_drain_rate(self, df: pd.DataFrame) -> float:
        """Calculate battery drain rate per hour"""
        try:
            if len(df) < 2:
                return 0.0
            
            time_diff = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds() / 3600
            battery_diff = df['battery_level'].iloc[0] - df['battery_level'].iloc[-1]
            
            return float(battery_diff / time_diff) if time_diff > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_uptime(self, device_id: str, hours: int) -> float:
        """Calculate device uptime percentage"""
        try:
            # This is a simplified calculation
            # In production, you'd track connection/disconnection events
            expected_readings = hours * 60 / 5  # Assuming 5-minute intervals
            actual_readings = len(self.data_buffer[device_id])
            
            return min(100.0, (actual_readings / expected_readings) * 100)
        except:
            return 100.0
    
    def _calculate_compliance_score(self, df: pd.DataFrame) -> float:
        """Calculate cold chain compliance score"""
        try:
            if df.empty:
                return 100.0
            
            # Check how many readings are within acceptable range (2-8°C)
            compliant_readings = df[
                (df['temperature'] >= 2.0) & (df['temperature'] <= 8.0)
            ]
            
            compliance_percentage = (len(compliant_readings) / len(df)) * 100
            return float(compliance_percentage)
        except:
            return 100.0

# Initialize backend service
backend_service = VitalTraceBackend()

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role', 'viewer')
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and user.check_password(data.get('password')):
            user.update_last_login()
            
            access_token = create_access_token(
                identity=user.id,
                additional_claims={'role': user.role}
            )
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh JWT token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        new_token = create_access_token(
            identity=current_user_id,
            additional_claims={'role': user.role}
        )
        
        return jsonify({'access_token': new_token}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Device Management Routes
@app.route('/api/devices', methods=['GET'])
@jwt_required()
def get_devices():
    """Get all registered devices"""
    try:
        devices = Device.query.all()
        return jsonify([device.to_dict() for device in devices]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<device_id>/analytics', methods=['GET'])
@jwt_required()
def get_device_analytics(device_id):
    """Get analytics for specific device"""
    try:
        hours = request.args.get('hours', 24, type=int)
        analytics = backend_service.get_device_analytics(device_id, hours)
        return jsonify(analytics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Alert Management Routes
@app.route('/api/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get system alerts"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status', 'active')
        
        alerts = Alert.query.filter_by(status=status)\
                          .order_by(Alert.created_at.desc())\
                          .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts.items],
            'total': alerts.total,
            'pages': alerts.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@jwt_required()
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        current_user_id = get_jwt_identity()
        alert = Alert.query.get_or_404(alert_id)
        
        alert.acknowledge(current_user_id)
        
        return jsonify({'message': 'Alert acknowledged'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        connected_clients.add(request.sid)
        join_room('dashboard')
        
        # Send current devices and data
        emit('devices_updated', list(backend_service.devices.values()))
        
        for device_id, data in backend_service.real_time_data.items():
            emit('real_time_data', data)
        
        app.logger.info(f'Client {request.sid} connected')
        
    except Exception as e:
        app.logger.error(f'Connection error: {str(e)}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        connected_clients.discard(request.sid)
        app.logger.info(f'Client {request.sid} disconnected')
        
    except Exception as e:
        app.logger.error(f'Disconnection error: {str(e)}')

@socketio.on('device_data')
def handle_device_data(data):
    """Handle incoming device data"""
    try:
        backend_service.process_sensor_data(data)
        
    except Exception as e:
        app.logger.error(f'Device data handling error: {str(e)}')
        emit('error', {'message': 'Failed to process device data'})

@socketio.on('device_registration')
def handle_device_registration(data):
    """Handle device registration"""
    try:
        if backend_service.register_device(data):
            emit('devices_updated', list(backend_service.devices.values()), broadcast=True)
            emit('registration_success', {'device_id': data.get('device_id')})
        else:
            emit('registration_failed', {'device_id': data.get('device_id')})
            
    except Exception as e:
        app.logger.error(f'Device registration error: {str(e)}')
        emit('registration_failed', {'device_id': data.get('device_id')})

@socketio.on('subscribe_alerts')
def handle_subscribe_alerts():
    """Subscribe to alert notifications"""
    join_room('alerts')
    emit('subscribed', {'room': 'alerts'})

@socketio.on('device_command')
def handle_device_command(data):
    """Handle device control commands"""
    try:
        device_id = data.get('device_id')
        command = data.get('command')
        value = data.get('value')
        
        # Process command (this would send to actual device in production)
        app.logger.info(f'Command {command} sent to device {device_id} with value {value}')
        
        # Emit confirmation
        emit('command_sent', {
            'device_id': device_id,
            'command': command,
            'value': value,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        app.logger.error(f'Command handling error: {str(e)}')
        emit('command_error', {'message': 'Failed to send command'})

# Background Tasks
def background_tasks():
    """Run background maintenance tasks"""
    with app.app_context():
        while True:
            try:
                # Clean up old data
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
                old_data = SensorData.query.filter(SensorData.timestamp < cutoff_date)
                count = old_data.count()
                old_data.delete()
                db.session.commit()
                
                if count > 0:
                    app.logger.info(f'Cleaned up {count} old sensor data records')
                
                # Update system metrics
                active_devices = Device.query.filter_by(status='active').count()
                total_alerts = Alert.query.filter_by(status='active').count()
                
                # Store metrics
                metrics = [
                    SystemMetrics(metric_type='active_devices', metric_value=active_devices, unit='count'),
                    SystemMetrics(metric_type='active_alerts', metric_value=total_alerts, unit='count'),
                ]
                
                for metric in metrics:
                    db.session.add(metric)
                
                db.session.commit()
                
                # Emit system status
                socketio.emit('system_status', {
                    'active_devices': active_devices,
                    'active_alerts': total_alerts,
                    'connected_clients': len(connected_clients),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, room='dashboard')
                
                time.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                app.logger.error(f'Background task error: {str(e)}')
                time.sleep(60)  # Wait 1 minute on error

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@vitaltrace.com',
                role='admin'
            )
            admin_user.set_password('VitalTrace2024!')
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info('Default admin user created')
    
    # Start background tasks
    background_thread = threading.Thread(target=background_tasks)
    background_thread.daemon = True
    background_thread.start()
    
    # Run the application
    socketio.run(
        app, 
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=5000,
        use_reloader=False  # Disable reloader when using background threads
    )
