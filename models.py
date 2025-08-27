# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from datetime import datetime, timezone
# import json
# from typing import Dict, Any, Optional

# db = SQLAlchemy()
# bcrypt = Bcrypt()

# class User(db.Model):
#     """User model for authentication and authorization"""
#     __tablename__ = 'users'
    
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)
#     role = db.Column(db.String(20), default='viewer', nullable=False)  # admin, operator, viewer
#     is_active = db.Column(db.Boolean, default=True, nullable=False)
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     last_login = db.Column(db.DateTime)
    
#     # Relationships
#     sessions = db.relationship('UserSession', backref='user', lazy='dynamic')
#     alerts = db.relationship('Alert', backref='assigned_user', lazy='dynamic')
    
#     def set_password(self, password: str) -> None:
#         """Hash and set the user's password"""
#         self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
#     def check_password(self, password: str) -> bool:
#         """Check if the provided password matches the stored hash"""
#         return bcrypt.check_password_hash(self.password_hash, password)
    
#     def update_last_login(self) -> None:
#         """Update the last login timestamp"""
#         self.last_login = datetime.now(timezone.utc)
#         db.session.commit()
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             'id': self.id,
#             'username': self.username,
#             'email': self.email,
#             'role': self.role,
#             'is_active': self.is_active,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'last_login': self.last_login.isoformat() if self.last_login else None
#         }

# class Device(db.Model):
#     """IoT device model for vaccine storage boxes"""
#     __tablename__ = 'devices'
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.String(50), unique=True, nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     location = db.Column(db.String(200), nullable=False)
#     latitude = db.Column(db.Float)
#     longitude = db.Column(db.Float)
#     target_temp_min = db.Column(db.Float, default=2.0)
#     target_temp_max = db.Column(db.Float, default=8.0)
#     battery_capacity = db.Column(db.Integer, default=100)
#     status = db.Column(db.String(20), default='active')
#     priority = db.Column(db.String(10), default='medium')
#     firmware_version = db.Column(db.String(20), default='1.0.0')
#     last_maintenance = db.Column(db.DateTime)
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
#     # Relationships
#     sensor_data = db.relationship('SensorData', backref='device', lazy='dynamic', cascade='all, delete-orphan')
#     alerts = db.relationship('Alert', backref='device', lazy='dynamic', cascade='all, delete-orphan')
#     maintenance_logs = db.relationship('MaintenanceLog', backref='device', lazy='dynamic')
    
#     def to_dict(self) -> Dict[str, Any]:
#         latest_data = self.sensor_data.order_by(SensorData.timestamp.desc()).first()
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'name': self.name,
#             'location': self.location,
#             'latitude': self.latitude,
#             'longitude': self.longitude,
#             'target_temp_min': self.target_temp_min,
#             'target_temp_max': self.target_temp_max,
#             'battery_capacity': self.battery_capacity,
#             'status': self.status,
#             'priority': self.priority,
#             'firmware_version': self.firmware_version,
#             'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None,
#             'latest_data': latest_data.to_dict() if latest_data else None
#         }

# class SensorData(db.Model):
#     """Sensor data model for storing IoT measurements"""
#     __tablename__ = 'sensor_data'
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
#     temperature = db.Column(db.Float, nullable=False)
#     humidity = db.Column(db.Float)
#     battery_level = db.Column(db.Integer)
#     door_open = db.Column(db.Boolean, default=False)
#     power_status = db.Column(db.String(20), default='normal')
#     signal_strength = db.Column(db.Integer)
#     timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
#     # Indexes for performance
#     __table_args__ = (
#         db.Index('idx_device_timestamp', 'device_id', 'timestamp'),
#     )
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'temperature': self.temperature,
#             'humidity': self.humidity,
#             'battery_level': self.battery_level,
#             'door_open': self.door_open,
#             'power_status': self.power_status,
#             'signal_strength': self.signal_strength,
#             'timestamp': self.timestamp.isoformat() if self.timestamp else None
#         }

# class Alert(db.Model):
#     """Alert model for storing system alerts and notifications"""
#     __tablename__ = 'alerts'
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
#     alert_type = db.Column(db.String(50), nullable=False)  # temp_high, temp_low, battery_low, door_open, etc.
#     severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
#     title = db.Column(db.String(200), nullable=False)
#     message = db.Column(db.Text, nullable=False)
#     status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
#     assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     acknowledged_at = db.Column(db.DateTime)
#     resolved_at = db.Column(db.DateTime)
#     metadata = db.Column(db.Text)  # JSON string for additional alert data
    
#     def set_metadata(self, data: Dict[str, Any]) -> None:
#         """Set metadata as JSON string"""
#         self.metadata = json.dumps(data) if data else None
    
#     def get_metadata(self) -> Optional[Dict[str, Any]]:
#         """Get metadata as dictionary"""
#         return json.loads(self.metadata) if self.metadata else None
    
#     def acknowledge(self, user_id: int) -> None:
#         """Acknowledge the alert"""
#         self.status = 'acknowledged'
#         self.assigned_user_id = user_id
#         self.acknowledged_at = datetime.now(timezone.utc)
#         db.session.commit()
    
#     def resolve(self) -> None:
#         """Mark the alert as resolved"""
#         self.status = 'resolved'
#         self.resolved_at = datetime.now(timezone.utc)
#         db.session.commit()
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'alert_type': self.alert_type,
#             'severity': self.severity,
#             'title': self.title,
#             'message': self.message,
#             'status': self.status,
#             'assigned_user_id': self.assigned_user_id,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
#             'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
#             'metadata': self.get_metadata()
#         }

# class UserSession(db.Model):
#     """User session model for tracking login sessions"""
#     __tablename__ = 'user_sessions'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     session_token = db.Column(db.String(255), unique=True, nullable=False)
#     ip_address = db.Column(db.String(50))
#     user_agent = db.Column(db.String(500))
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     expires_at = db.Column(db.DateTime, nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             'id': self.id,
#             'user_id': self.user_id,
#             'ip_address': self.ip_address,
#             'user_agent': self.user_agent,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'expires_at': self.expires_at.isoformat() if self.expires_at else None,
#             'is_active': self.is_active
#         }

# class MaintenanceLog(db.Model):
#     """Maintenance log model for tracking device maintenance"""
#     __tablename__ = 'maintenance_logs'
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
#     maintenance_type = db.Column(db.String(50), nullable=False)  # scheduled, emergency, repair, etc.
#     description = db.Column(db.Text, nullable=False)
#     technician_name = db.Column(db.String(100))
#     cost = db.Column(db.Float)
#     duration_hours = db.Column(db.Float)
#     scheduled_date = db.Column(db.DateTime)
#     completed_date = db.Column(db.DateTime)
#     status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
#     notes = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'maintenance_type': self.maintenance_type,
#             'description': self.description,
#             'technician_name': self.technician_name,
#             'cost': self.cost,
#             'duration_hours': self.duration_hours,
#             'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
#             'completed_date': self.completed_date.isoformat() if self.completed_date else None,
#             'status': self.status,
#             'notes': self.notes,
#             'created_at': self.created_at.isoformat() if self.created_at else None
#         }

# class SystemMetrics(db.Model):
#     """System metrics model for storing performance and business metrics"""
#     __tablename__ = 'system_metrics'
    
#     id = db.Column(db.Integer, primary_key=True)
#     metric_type = db.Column(db.String(50), nullable=False)  # uptime, alerts_count, devices_online, etc.
#     metric_value = db.Column(db.Float, nullable=False)
#     unit = db.Column(db.String(20))  # percentage, count, hours, etc.
#     timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     metadata = db.Column(db.Text)  # JSON string for additional metric data
    
#     def set_metadata(self, data: Dict[str, Any]) -> None:
#         """Set metadata as JSON string"""
#         self.metadata = json.dumps(data) if data else None
    
#     def get_metadata(self) -> Optional[Dict[str, Any]]:
#         """Get metadata as dictionary"""
#         return json.loads(self.metadata) if self.metadata else None
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             'id': self.id,
#             'metric_type': self.metric_type,
#             'metric_value': self.metric_value,
#             'unit': self.unit,
#             'timestamp': self.timestamp.isoformat() if self.timestamp else None,
#             'metadata': self.get_metadata()
#         }


from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import uuid
import json
from typing import Dict, Any, Optional

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True)
    alerts = db.relationship('Alert', backref='assigned_user', lazy=True)
    
    def get_id(self):
        """Return the user ID for Flask-Login compatibility"""
        return str(self.id)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

db = SQLAlchemy()

from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True)
    alerts = db.relationship('Alert', backref='assigned_user', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import uuid
import json
from typing import Dict, Any, Optional

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True)
    alerts = db.relationship('Alert', backref='assigned_user', lazy=True)
    
    def get_id(self):
        """Return the user ID for Flask-Login compatibility"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import uuid
import json
from typing import Dict, Any, Optional

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True)
    alerts = db.relationship('Alert', backref='assigned_user', lazy=True)
    
    def get_id(self):
        """Return the user ID for Flask-Login compatibility"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Device(db.Model):
    """Device model for IoT devices"""
    __tablename__ = 'devices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    target_temp_min = db.Column(db.Float, default=2.0)
    target_temp_max = db.Column(db.Float, default=8.0)
    battery_capacity = db.Column(db.Integer, default=100)
    device_type = db.Column(db.String(50), nullable=False)
    mac_address = db.Column(db.String(17), unique=True)
    ip_address = db.Column(db.String(15))
    status = db.Column(db.String(20), default='active')
    priority = db.Column(db.String(10), default='medium')
    firmware_version = db.Column(db.String(20), default='1.0.0')
    last_maintenance = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    sensor_data = db.relationship('SensorData', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        latest_data = self.sensor_data.order_by(SensorData.timestamp.desc()).first()
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'target_temp_min': self.target_temp_min,
            'target_temp_max': self.target_temp_max,
            'battery_capacity': self.battery_capacity,
            'device_type': self.device_type,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'status': self.status,
            'priority': self.priority,
            'firmware_version': self.firmware_version,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'latest_data': latest_data.to_dict() if latest_data else None
        }

class SensorData(db.Model):
    """Sensor data model"""
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float)
    battery_level = db.Column(db.Integer)
    door_open = db.Column(db.Boolean, default=False)
    power_status = db.Column(db.String(20), default='normal')
    signal_strength = db.Column(db.Integer)
    sensor_type = db.Column(db.String(50))
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_device_timestamp', 'device_id', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'battery_level': self.battery_level,
            'door_open': self.door_open,
            'power_status': self.power_status,
            'signal_strength': self.signal_strength,
            'sensor_type': self.sensor_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

from datetime import datetime, timezone
import uuid
import json
from typing import Dict, Any, Optional

# ... existing code from models.py (User, Device, SensorData classes)

class Alert(db.Model):
    """Alert model"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium') # medium, high, critical
    status = db.Column(db.String(20), default='active') # active, acknowledged, resolved
    assigned_user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    metadata = db.Column(db.Text)
    
    def set_metadata(self, data: Dict[str, Any]) -> None:
        self.metadata = json.dumps(data) if data else None
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        return json.loads(self.metadata) if self.metadata else None
    
    def acknowledge(self, user_id: str = None) -> None:
        """Mark the alert as acknowledged"""
        if self.status == 'active':
            self.status = 'acknowledged'
            self.acknowledged_at = datetime.now(timezone.utc)
            if user_id:
                self.assigned_user_id = user_id
            db.session.commit()
    
    def resolve(self) -> None:
        """Mark the alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.get_metadata()
        }

# ... other models if any

class SensorData(db.Model):
    """Sensor data model"""
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float)
    battery_level = db.Column(db.Integer)
    door_open = db.Column(db.Boolean, default=False)
    power_status = db.Column(db.String(20), default='normal')
    signal_strength = db.Column(db.Integer)
    sensor_type = db.Column(db.String(50))
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_device_timestamp', 'device_id', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'battery_level': self.battery_level,
            'door_open': self.door_open,
            'power_status': self.power_status,
            'signal_strength': self.signal_strength,
            'sensor_type': self.sensor_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Alert(db.Model):
    """Alert model"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='active')
    assigned_user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    metadata = db.Column(db.Text)
    
    def set_metadata(self, data: Dict[str, Any]) -> None:
        """Set metadata as JSON string"""
        self.metadata = json.dumps(data) if data else None
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get metadata as dictionary"""
        return json.loads(self.metadata) if self.metadata else None
    
    def acknowledge(self, user_id: str = None) -> None:
        """Mark the alert as acknowledged"""
        self.status = 'acknowledged'
        if user_id:
            self.assigned_user_id = user_id
        self.acknowledged_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def resolve(self) -> None:
        """Mark the alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.get_metadata()
        }

class SensorData(db.Model):
    """Sensor data model"""
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float)
    battery_level = db.Column(db.Integer)
    door_open = db.Column(db.Boolean, default=False)
    power_status = db.Column(db.String(20), default='normal')
    signal_strength = db.Column(db.Integer)
    sensor_type = db.Column(db.String(50))
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_device_timestamp', 'device_id', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'battery_level': self.battery_level,
            'door_open': self.door_open,
            'power_status': self.power_status,
            'signal_strength': self.signal_strength,
            'sensor_type': self.sensor_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Alert(db.Model):
    """Alert model"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(50), db.ForeignKey('devices.device_id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='active')
    assigned_user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    metadata = db.Column(db.Text)
    
    def set_metadata(self, data: Dict[str, Any]) -> None:
        """Set metadata as JSON string"""
        self.metadata = json.dumps(data) if data else None
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get metadata as dictionary"""
        return json.loads(self.metadata) if self.metadata else None
    
    def acknowledge(self, user_id: str = None) -> None:
        """Mark the alert as acknowledged"""
        self.status = 'acknowledged'
        if user_id:
            self.assigned_user_id = user_id
        self.acknowledged_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def resolve(self) -> None:
        """Mark the alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.get_metadata()
        }

class Device(db.Model):
    """Device model for IoT devices"""
    __tablename__ = 'devices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    ip_address = db.Column(db.String(15))
    status = db.Column(db.String(20), default='offline')
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    sensor_data = db.relationship('SensorData', backref='device', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='device', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SensorData(db.Model):
    """Sensor data model"""
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    device_id = db.Column(db.String(36), db.ForeignKey('devices.id'), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'sensor_type': self.sensor_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'device_id': self.device_id
        }

class Alert(db.Model):
    """Alert model"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='info')  # info, warning, error, critical
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # Foreign Keys
    device_id = db.Column(db.String(36), db.ForeignKey('devices.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    def acknowledge(self) -> None:
        """Mark the alert as acknowledged"""
        self.status = 'acknowledged'
        self.acknowledged_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def resolve(self) -> None:
        """Mark the alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'device_id': self.device_id,
            'user_id': self.user_id
        }