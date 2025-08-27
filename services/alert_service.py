# import logging
# from datetime import datetime, timezone, timedelta
# from typing import Dict, List, Any, Optional
# from collections import defaultdict, deque
# import json

# from models import Alert, Device, User, db

# class AlertService:
#     """Advanced alert service for intelligent alert management"""
    
#     def __init__(self):
#         self.alert_cache = deque(maxlen=1000)
#         self.alert_rules = self._initialize_alert_rules()
#         self.alert_frequencies = defaultdict(int)  # Track alert frequency per device
#         self.suppressed_alerts = set()  # Track suppressed alerts
#         self.escalation_rules = self._initialize_escalation_rules()
#         self.logger = logging.getLogger(__name__)
        
#     def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
#         """Initialize alert rules and thresholds"""
#         return {
#             'temperature_critical': {
#                 'threshold': {'min': -5.0, 'max': 15.0},
#                 'severity': 'critical',
#                 'cooldown_minutes': 15,
#                 'escalate_after_minutes': 5,
#                 'auto_resolve': False
#             },
#             'temperature_high': {
#                 'threshold': {'max': 8.0},
#                 'severity': 'high',
#                 'cooldown_minutes': 30,
#                 'escalate_after_minutes': 30,
#                 'auto_resolve': True
#             },
#             'temperature_low': {
#                 'threshold': {'min': 2.0},
#                 'severity': 'high',
#                 'cooldown_minutes': 30,
#                 'escalate_after_minutes': 30,
#                 'auto_resolve': True
#             },
#             'battery_critical': {
#                 'threshold': {'max': 5},
#                 'severity': 'critical',
#                 'cooldown_minutes': 60,
#                 'escalate_after_minutes': 10,
#                 'auto_resolve': False
#             },
#             'battery_low': {
#                 'threshold': {'max': 20},
#                 'severity': 'medium',
#                 'cooldown_minutes': 120,
#                 'escalate_after_minutes': 60,
#                 'auto_resolve': True
#             },
#             'door_open': {
#                 'duration_threshold': 300,  # 5 minutes
#                 'severity': 'medium',
#                 'cooldown_minutes': 60,
#                 'escalate_after_minutes': 30,
#                 'auto_resolve': True
#             },
#             'connectivity_loss': {
#                 'duration_threshold': 600,  # 10 minutes
#                 'severity': 'high',
#                 'cooldown_minutes': 30,
#                 'escalate_after_minutes': 20,
#                 'auto_resolve': True
#             },
#             'power_failure': {
#                 'severity': 'critical',
#                 'cooldown_minutes': 10,
#                 'escalate_after_minutes': 5,
#                 'auto_resolve': True
#             },
#             'tamper_detected': {
#                 'severity': 'critical',
#                 'cooldown_minutes': 5,
#                 'escalate_after_minutes': 0,
#                 'auto_resolve': False
#             },
#             'sensor_malfunction': {
#                 'severity': 'high',
#                 'cooldown_minutes': 60,
#                 'escalate_after_minutes': 30,
#                 'auto_resolve': False
#             },
#             'maintenance_due': {
#                 'severity': 'medium',
#                 'cooldown_minutes': 1440,  # 24 hours
#                 'escalate_after_minutes': 480,  # 8 hours
#                 'auto_resolve': False
#             },
#             'anomaly_detected': {
#                 'severity': 'medium',
#                 'cooldown_minutes': 60,
#                 'escalate_after_minutes': 120,
#                 'auto_resolve': True
#             }
#         }
    
#     def _initialize_escalation_rules(self) -> Dict[str, List[str]]:
#         """Initialize alert escalation rules"""
#         return {
#             'critical': ['admin', 'operator'],
#             'high': ['operator', 'admin'],
#             'medium': ['operator'],
#             'low': ['operator']
#         }
    
#     def evaluate_alert_conditions(self, device_id: str, sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Evaluate sensor data against alert conditions"""
#         try:
#             alerts_to_create = []
#             device = Device.query.filter_by(device_id=device_id).first()
            
#             if not device:
#                 self.logger.warning(f"Device {device_id} not found in database")
#                 return alerts_to_create
            
#             # Temperature alerts
#             temperature = sensor_data.get('temperature')
#             if temperature is not None:
#                 temp_alerts = self._evaluate_temperature_alerts(device, temperature, sensor_data)
#                 alerts_to_create.extend(temp_alerts)
            
#             # Battery alerts
#             battery_level = sensor_data.get('battery_level')
#             if battery_level is not None:
#                 battery_alerts = self._evaluate_battery_alerts(device, battery_level, sensor_data)
#                 alerts_to_create.extend(battery_alerts)
            
#             # Door alerts
#             door_open = sensor_data.get('door_open', False)
#             if door_open:
#                 door_alerts = self._evaluate_door_alerts(device, sensor_data)
#                 alerts_to_create.extend(door_alerts)
            
#             # Power alerts
#             power_status = sensor_data.get('power_status', 'normal')
#             if power_status != 'normal':
#                 power_alerts = self._evaluate_power_alerts(device, power_status, sensor_data)
#                 alerts_to_create.extend(power_alerts)
            
#             # Connectivity alerts (based on signal strength)
#             signal_strength = sensor_data.get('signal_strength')
#             if signal_strength is not None and signal_strength < 20:
#                 connectivity_alerts = self._evaluate_connectivity_alerts(device, signal_strength, sensor_data)
#                 alerts_to_create.extend(connectivity_alerts)
            
#             return alerts_to_create
            
#         except Exception as e:
#             self.logger.error(f"Alert evaluation failed for device {device_id}: {str(e)}")
#             return []
    
#     def _evaluate_temperature_alerts(self, device: Device, temperature: float, 
#                                    sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Evaluate temperature-based alerts"""
#         alerts = []
        
#         # Critical temperature alert
#         if temperature < -5.0 or temperature > 15.0:
#             if not self._is_alert_suppressed(device.device_id, 'temperature_critical'):
#                 alerts.append({
#                     'device_id': device.device_id,
#                     'alert_type': 'temperature_critical',
#                     'severity': 'critical',
#                     'title': f'Critical Temperature Alert - {device.name}',
#                     'message': f'Temperature {temperature}°C is critically out of range. Immediate action required!',
#                     'metadata': sensor_data
#                 })
        
#         # High temperature alert
#         elif temperature > device.target_temp_max:
#             if not self._is_alert_suppressed(device.device_id, 'temperature_high'):
#                 alerts.append({
#                     'device_id': device.device_id,
#                     'alert_type': 'temperature_high',
#                     'severity': 'high',
#                     'title': f'High Temperature Alert - {device.name}',
#                     'message': f'Temperature {temperature}°C exceeds target maximum of {device.target_temp_max}°C',
#                     'metadata': sensor_data
#                 })
        
#         # Low temperature alert
#         elif temperature < device.target_temp_min:
#             if not self._is_alert_suppressed(device.device_id, 'temperature_low'):
#                 alerts.append({
#                     'device_id': device.device_id,
#                     'alert_type': 'temperature_low',
#                     'severity': 'high',
#                     'title': f'Low Temperature Alert - {device.name}',
#                     'message': f'Temperature {temperature}°C is below target minimum of {device.target_temp_min}°C',
#                     'metadata': sensor_data
#                 })
        
#         return alerts
    
#     def _evaluate_battery_alerts(self, device: Device, battery_level: int, 
#                                sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Evaluate battery-based alerts"""
#         alerts = []
        
#         # Critical battery alert
#         if battery_level <= 5:
#             if not self._is_alert_suppressed(device.device_id, 'battery_critical'):
#                 alerts.append({
#                     'device_id': device.device_id,
#                     'alert_type': 'battery_critical',
#                     'severity': 'critical',
#                     'title': f'Critical Battery Alert - {device.name}',
#                     'message': f'Battery level {battery_level}% is critically low. Device may shut down soon!',
#                     'metadata': sensor_data
#                 })
        
#         # Low battery alert
#         elif battery_level <= 20:
#             if not self._is_alert_suppressed(device.device_id, 'battery_low'):
#                 alerts.append({
#                     'device_id': device.device_id,
#                     'alert_type': 'battery_low',
#                     'severity': 'medium',
#                     'title': f'Low Battery Alert - {device.name}',
#                     'message': f'Battery level {battery_level}% is low. Consider charging or replacement.',
#                     'metadata': sensor_data
#                 })
        
#         return alerts
    
#     def _evaluate_door_alerts(self, device: Device, sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Evaluate door open alerts"""
#         alerts = []
        
#         # This would require tracking door open duration in a real implementation
#         # For now, we'll create a simple door open alert
#         if not self._is_alert_suppressed(device.device_id, 'door_open'):
#             alerts.append({
#                 'device_id': device.device_id,
#                 'alert_type': 'door_open',
#                 'severity': 'medium',
#                 'title': f'Door Open Alert - {device.name}',
#                 'message': f'Storage door is open. Ensure it is closed to maintain temperature.',
#                 'metadata': sensor_data
#             })
        
#         return alerts
    
#     def _evaluate_power_alerts(self, device: Device, power_status: str, 
#                              sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Evaluate power-related alerts"""
#         alerts = []
        
#         if power_status in ['failure', 'low', 'backup']:
#             if not self._is_alert_suppressed(device.device_id, 'power_failure'):
#                 severity = 'critical' if power_status == 'failure' else 'high'
#                 alerts.append({
#                     'device_id': device.device_id,
#                     'alert_type': 'power_failure',
#                     'severity': severity,
#                     'title': f'Power Issue Alert - {device.name}',
#                     'message': f'Power status: {power_status}. Check power supply immediately.',
#                     'metadata': sensor_data
#                 })
        
#         return alerts
    
#     def _evaluate_connectivity_alerts(self, device: Device, signal_strength: int, 
#                                     sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Evaluate connectivity alerts"""
#         alerts = []
        
#         if signal_strength < 20:
#             if not self._is_alert_suppressed(device.device_id, 'connectivity_loss'):
#                 alerts.append({
#                     'device_id': device.device_id,
#                     'alert_type': 'connectivity_loss',
#                     'severity': 'high',
#                     'title': f'Poor Connectivity Alert - {device.name}',
#                     'message': f'Signal strength {signal_strength}% is very low. Check network connection.',
#                     'metadata': sensor_data
#                 })
        
#         return alerts
    
#     def _is_alert_suppressed(self, device_id: str, alert_type: str) -> bool:
#         """Check if alert should be suppressed due to cooldown or frequency limits"""
#         try:
#             # Check cooldown period
#             cooldown_key = f"{device_id}:{alert_type}"
            
#             # Get the last alert of this type for this device
#             last_alert = Alert.query.filter_by(
#                 device_id=device_id,
#                 alert_type=alert_type
#             ).order_by(Alert.created_at.desc()).first()
            
#             if last_alert:
#                 alert_rule = self.alert_rules.get(alert_type, {})
#                 cooldown_minutes = alert_rule.get('cooldown_minutes', 30)
                
#                 time_since_last = datetime.now(timezone.utc) - last_alert.created_at
#                 if time_since_last < timedelta(minutes=cooldown_minutes):
#                     return True  # Suppress due to cooldown
            
#             # Check frequency limits
#             self.alert_frequencies[cooldown_key] += 1
#             if self.alert_frequencies[cooldown_key] > 5:  # Max 5 alerts of same type per hour
#                 return True
            
#             return False
            
#         except Exception as e:
#             self.logger.error(f"Alert suppression check failed: {str(e)}")
#             return False
    
#     def create_alert(self, alert_data: Dict[str, Any]) -> Optional[Alert]:
#         """Create a new alert with intelligent processing"""
#         try:
#             # Check if alert should be suppressed
#             if self._is_alert_suppressed(alert_data['device_id'], alert_data['alert_type']):
#                 return None
            
#             # Create the alert
#             alert = Alert(
#                 device_id=alert_data['device_id'],
#                 alert_type=alert_data['alert_type'],
#                 severity=alert_data['severity'],
#                 title=alert_data['title'],
#                 message=alert_data['message']
#             )
            
#             if 'metadata' in alert_data:
#                 alert.set_metadata(alert_data['metadata'])
            
#             db.session.add(alert)
#             db.session.commit()
            
#             # Add to cache
#             self.alert_cache.append(alert.to_dict())
            
#             # Schedule escalation if needed
#             self._schedule_escalation(alert)
            
#             self.logger.info(f"Alert created: {alert.alert_type} for device {alert.device_id}")
            
#             return alert
            
#         except Exception as e:
#             self.logger.error(f"Alert creation failed: {str(e)}")
#             db.session.rollback()
#             return None
    
#     def _schedule_escalation(self, alert: Alert) -> None:
#         """Schedule alert escalation based on rules"""
#         try:
#             alert_rule = self.alert_rules.get(alert.alert_type, {})
#             escalate_after_minutes = alert_rule.get('escalate_after_minutes', 60)
            
#             # In a production system, this would use a task queue like Celery
#             # For now, we'll just log the escalation schedule
#             self.logger.info(f"Alert {alert.id} scheduled for escalation in {escalate_after_minutes} minutes")
            
#         except Exception as e:
#             self.logger.error(f"Alert escalation scheduling failed: {str(e)}")
    
#     def process_alert_resolution(self, device_id: str, alert_type: str, 
#                                current_sensor_data: Dict[str, Any]) -> List[Alert]:
#         """Process automatic alert resolution based on current conditions"""
#         try:
#             resolved_alerts = []
            
#             # Find active alerts that might be resolved
#             active_alerts = Alert.query.filter_by(
#                 device_id=device_id,
#                 alert_type=alert_type,
#                 status='active'
#             ).all()
            
#             for alert in active_alerts:
#                 if self._should_auto_resolve(alert, current_sensor_data):
#                     alert.resolve()
#                     resolved_alerts.append(alert)
#                     self.logger.info(f"Auto-resolved alert {alert.id} for device {device_id}")
            
#             return resolved_alerts
            
#         except Exception as e:
#             self.logger.error(f"Alert resolution processing failed: {str(e)}")
#             return []
    
#     def _should_auto_resolve(self, alert: Alert, current_data: Dict[str, Any]) -> bool:
#         """Determine if an alert should be automatically resolved"""
#         try:
#             alert_rule = self.alert_rules.get(alert.alert_type, {})
            
#             if not alert_rule.get('auto_resolve', False):
#                 return False
            
#             # Check resolution conditions based on alert type
#             if alert.alert_type.startswith('temperature'):
#                 temperature = current_data.get('temperature')
#                 if temperature is not None:
#                     device = Device.query.filter_by(device_id=alert.device_id).first()
#                     if device and device.target_temp_min <= temperature <= device.target_temp_max:
#                         return True
            
#             elif alert.alert_type.startswith('battery'):
#                 battery_level = current_data.get('battery_level')
#                 if battery_level is not None:
#                     if alert.alert_type == 'battery_critical' and battery_level > 10:
#                         return True
#                     elif alert.alert_type == 'battery_low' and battery_level > 30:
#                         return True
            
#             elif alert.alert_type == 'door_open':
#                 door_open = current_data.get('door_open', False)
#                 if not door_open:
#                     return True
            
#             elif alert.alert_type == 'power_failure':
#                 power_status = current_data.get('power_status', 'normal')
#                 if power_status == 'normal':
#                     return True
            
#             elif alert.alert_type == 'connectivity_loss':
#                 signal_strength = current_data.get('signal_strength', 100)
#                 if signal_strength >= 50:
#                     return True
            
#             return False
            
#         except Exception as e:
#             self.logger.error(f"Auto-resolution check failed: {str(e)}")
#             return False
    
#     def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
#         """Get alert statistics for the specified time period"""
#         try:
#             end_time = datetime.now(timezone.utc)
#             start_time = end_time - timedelta(hours=hours)
            
#             # Query alerts in time range
#             alerts = Alert.query.filter(
#                 Alert.created_at >= start_time,
#                 Alert.created_at <= end_time
#             ).all()
            
#             # Calculate statistics
#             total_alerts = len(alerts)
#             alerts_by_severity = defaultdict(int)
#             alerts_by_type = defaultdict(int)
#             alerts_by_status = defaultdict(int)
            
#             for alert in alerts:
#                 alerts_by_severity[alert.severity] += 1
#                 alerts_by_type[alert.alert_type] += 1
#                 alerts_by_status[alert.status] += 1
            
#             # Calculate resolution rate
#             resolved_alerts = alerts_by_status.get('resolved', 0)
#             resolution_rate = (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 100
            
#             # Find most problematic devices
#             device_alert_counts = defaultdict(int)
#             for alert in alerts:
#                 device_alert_counts[alert.device_id] += 1
            
#             most_problematic_devices = sorted(
#                 device_alert_counts.items(),
#                 key=lambda x: x[1],
#                 reverse=True
#             )[:5]
            
#             return {
#                 'period_hours': hours,
#                 'total_alerts': total_alerts,
#                 'alerts_by_severity': dict(alerts_by_severity),
#                 'alerts_by_type': dict(alerts_by_type),
#                 'alerts_by_status': dict(alerts_by_status),
#                 'resolution_rate': float(resolution_rate),
#                 'most_problematic_devices': [
#                     {'device_id': device_id, 'alert_count': count}
#                     for device_id, count in most_problematic_devices
#                 ],
#                 'analysis_timestamp': datetime.now(timezone.utc).isoformat()
#             }
            
#         except Exception as e:
#             self.logger.error(f"Alert statistics calculation failed: {str(e)}")
#             return {'error': str(e)}
    
#     def get_alert_recommendations(self, device_id: str) -> List[Dict[str, Any]]:
#         """Get recommendations based on alert patterns"""
#         try:
#             recommendations = []
            
#             # Analyze recent alerts for this device
#             recent_alerts = Alert.query.filter_by(device_id=device_id).filter(
#                 Alert.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
#             ).all()
            
#             if not recent_alerts:
#                 return [{'message': 'No recent alerts. System appears to be functioning normally.'}]
            
#             # Analyze patterns
#             alert_types = defaultdict(int)
#             for alert in recent_alerts:
#                 alert_types[alert.alert_type] += 1
            
#             # Generate recommendations
#             for alert_type, count in alert_types.items():
#                 if count >= 3:  # Recurring alert
#                     if alert_type.startswith('temperature'):
#                         recommendations.append({
#                             'priority': 'high',
#                             'message': f'Recurring temperature alerts ({count}). Check cooling system, insulation, and door seals.',
#                             'action': 'maintenance_required'
#                         })
#                     elif alert_type.startswith('battery'):
#                         recommendations.append({
#                             'priority': 'medium',
#                             'message': f'Recurring battery alerts ({count}). Consider battery replacement or power optimization.',
#                             'action': 'battery_maintenance'
#                         })
#                     elif alert_type == 'connectivity_loss':
#                         recommendations.append({
#                             'priority': 'medium',
#                             'message': f'Recurring connectivity issues ({count}). Check network infrastructure and device antenna.',
#                             'action': 'network_check'
#                         })
            
#             # Device-specific recommendations
#             device = Device.query.filter_by(device_id=device_id).first()
#             if device and device.status != 'active':
#                 recommendations.append({
#                     'priority': 'high',
#                     'message': 'Device status is not active. Verify device operation and update status.',
#                     'action': 'status_check'
#                 })
            
#             return recommendations if recommendations else [{
#                 'priority': 'low',
#                 'message': 'Alert patterns are within normal ranges. Continue monitoring.',
#                 'action': 'continue_monitoring'
#             }]
            
#         except Exception as e:
#             self.logger.error(f"Alert recommendations failed for device {device_id}: {str(e)}")
#             return [{'message': 'Unable to generate recommendations due to system error.'}]
    
#     def cleanup_old_alerts(self, days: int = 30) -> int:
#         """Clean up old resolved alerts"""
#         try:
#             cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
#             old_alerts = Alert.query.filter(
#                 Alert.status == 'resolved',
#                 Alert.resolved_at < cutoff_date
#             )
            
#             count = old_alerts.count()
#             old_alerts.delete()
#             db.session.commit()
            
#             self.logger.info(f"Cleaned up {count} old alerts")
#             return count
            
#         except Exception as e:
#             self.logger.error(f"Alert cleanup failed: {str(e)}")
#             db.session.rollback()
#             return 0


from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
import logging
from models import Alert, Device, User, db

class AlertService:
    """Service for managing alerts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_alert(self, device_id: str, user_id: str, title: str, 
                    message: str, severity: str = 'info') -> Optional[Alert]:
        """Create a new alert"""
        try:
            alert = Alert(
                device_id=device_id,
                user_id=user_id,
                title=title,
                message=message,
                severity=severity
            )
            
            db.session.add(alert)
            db.session.commit()
            
            self.logger.info(f"Alert created: {alert.id}")
            return alert
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {str(e)}")
            db.session.rollback()
            return None
    
    def get_alerts(self, user_id: str, status: Optional[str] = None, 
                  device_id: Optional[str] = None, limit: int = 100) -> List[Alert]:
        """Get alerts for a user"""
        try:
            query = Alert.query.filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            if device_id:
                query = query.filter_by(device_id=device_id)
            
            alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get alerts: {str(e)}")
            return []
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
            
            if not alert:
                self.logger.warning(f"Alert not found: {alert_id}")
                return False
            
            alert.acknowledge()
            self.logger.info(f"Alert acknowledged: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert: {str(e)}")
            return False
    
    def resolve_alert(self, alert_id: str, user_id: str) -> bool:
        """Resolve an alert"""
        try:
            alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
            
            if not alert:
                self.logger.warning(f"Alert not found: {alert_id}")
                return False
            
            alert.resolve()
            self.logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resolve alert: {str(e)}")
            return False
    
    def cleanup_old_alerts(self, days: int = 30) -> int:
        """Clean up old resolved alerts"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            old_alerts = Alert.query.filter(
                Alert.status == 'resolved',
                Alert.resolved_at < cutoff_date
            )
            
            count = old_alerts.count()
            old_alerts.delete()
            db.session.commit()
            
            self.logger.info(f"Cleaned up {count} old alerts")
            return count
            
        except Exception as e:
            self.logger.error(f"Alert cleanup failed: {str(e)}")
            db.session.rollback()
            return 0
    
    def get_alert_statistics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get alert statistics for a user"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            total_alerts = Alert.query.filter(
                Alert.user_id == user_id,
                Alert.created_at >= start_date
            ).count()
            
            active_alerts = Alert.query.filter(
                Alert.user_id == user_id,
                Alert.status == 'active',
                Alert.created_at >= start_date
            ).count()
            
            resolved_alerts = Alert.query.filter(
                Alert.user_id == user_id,
                Alert.status == 'resolved',
                Alert.created_at >= start_date
            ).count()
            
            critical_alerts = Alert.query.filter(
                Alert.user_id == user_id,
                Alert.severity == 'critical',
                Alert.created_at >= start_date
            ).count()
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'critical_alerts': critical_alerts,
                'period_days': days
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get alert statistics: {str(e)}")
            return {}

# Create a singleton instance
alert_service = AlertService()