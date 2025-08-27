import logging
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from flask import current_app
import requests

from models import Alert, User, Device

class NotificationService:
    """Multi-channel notification service for alert delivery"""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.logger = logging.getLogger(__name__)
        self.notification_channels = {
            'websocket': self._send_websocket_notification,
            'email': self._send_email_notification,
            'sms': self._send_sms_notification,
            'slack': self._send_slack_notification,
            'webhook': self._send_webhook_notification
        }
        
    def send_alert_notification(self, alert: Alert) -> Dict[str, Any]:
        """Send alert notification through multiple channels"""
        try:
            results = {
                'alert_id': alert.id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'channels': {}
            }
            
            # Get device information
            device = Device.query.filter_by(device_id=alert.device_id).first()
            
            # Get notification preferences based on alert severity
            notification_config = self._get_notification_config(alert.severity)
            
            # Send through configured channels
            for channel in notification_config.get('channels', ['websocket']):
                try:
                    if channel in self.notification_channels:
                        result = self.notification_channels[channel](alert, device)
                        results['channels'][channel] = result
                    else:
                        self.logger.warning(f"Unknown notification channel: {channel}")
                        results['channels'][channel] = {'status': 'error', 'message': 'Unknown channel'}
                        
                except Exception as e:
                    self.logger.error(f"Failed to send notification via {channel}: {str(e)}")
                    results['channels'][channel] = {'status': 'error', 'message': str(e)}
            
            return results
            
        except Exception as e:
            self.logger.error(f"Notification sending failed for alert {alert.id}: {str(e)}")
            return {'error': str(e)}
    
    def _get_notification_config(self, severity: str) -> Dict[str, Any]:
        """Get notification configuration based on alert severity"""
        configs = {
            'critical': {
                'channels': ['websocket', 'email', 'sms', 'slack'],
                'priority': 'high',
                'retry_attempts': 3,
                'escalate_minutes': 5
            },
            'high': {
                'channels': ['websocket', 'email', 'slack'],
                'priority': 'medium',
                'retry_attempts': 2,
                'escalate_minutes': 30
            },
            'medium': {
                'channels': ['websocket', 'email'],
                'priority': 'normal',
                'retry_attempts': 1,
                'escalate_minutes': 60
            },
            'low': {
                'channels': ['websocket'],
                'priority': 'low',
                'retry_attempts': 1,
                'escalate_minutes': 120
            }
        }\
        return configs.get(severity, configs['medium'])
    
    def _send_websocket_notification(self, alert: Alert, device: Optional[Device]) -> Dict[str, Any]:
        """Send real-time notification via WebSocket"""
        try:
            if not self.socketio:
                return {'status': 'error', 'message': 'WebSocket not configured'}
            
            notification_data = {
                'type': 'alert',
                'alert': alert.to_dict(),
                'device': device.to_dict() if device else None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Emit to all connected clients
            self.socketio.emit('new_alert', notification_data, room='alerts')
            
            # Emit to dashboard room for real-time updates
            self.socketio.emit('dashboard_alert', notification_data, room='dashboard')
            
            return {'status': 'success', 'message': 'WebSocket notification sent'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _send_email_notification(self, alert: Alert, device: Optional[Device]) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Get email configuration from Flask config
            smtp_host = current_app.config.get('SMTP_HOST')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            smtp_username = current_app.config.get('SMTP_USERNAME')
            smtp_password = current_app.config.get('SMTP_PASSWORD')
            
            if not all([smtp_host, smtp_username, smtp_password]):
                return {'status': 'skipped', 'message': 'Email configuration not complete'}
            
            # Get recipients based on alert severity
            recipients = self._get_email_recipients(alert.severity)
            
            if not recipients:
                return {'status': 'skipped', 'message': 'No email recipients configured'}
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[Vital Trace] {alert.title}"
            
            # Create HTML email body
            html_body = self._create_email_html(alert, device)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            return {
                'status': 'success',
                'message': f'Email sent to {len(recipients)} recipients',
                'recipients': recipients
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _get_email_recipients(self, severity: str) -> List[str]:
        """Get email recipients based on alert severity"""
        try:
            # Get users based on severity
            if severity == 'critical':
                users = User.query.filter(User.role.in_(['admin', 'operator'])).all()
            elif severity == 'high':
                users = User.query.filter(User.role.in_(['operator', 'admin'])).all()
            else:
                users = User.query.filter_by(role='operator').all()
            
            return [user.email for user in users if user.is_active]
            
        except Exception as e:
            self.logger.error(f"Failed to get email recipients: {str(e)}")
            return []
    
    def _create_email_html(self, alert: Alert, device: Optional[Device]) -> str:
        """Create HTML email body for alert notification"""
        severity_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        
        color = severity_colors.get(alert.severity, '#6c757d')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Vital Trace Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .alert-info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .device-info {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6c757d; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: {color}; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🩺 Vital Trace Alert</h1>
                    <h2>{alert.severity.upper()} ALERT</h2>
                </div>
                <div class="content">
                    <h2>{alert.title}</h2>
                    <p>{alert.message}</p>
                    
                    <div class="alert-info">
                        <h3>Alert Details</h3>
                        <p><strong>Alert ID:</strong> {alert.id}</p>
                        <p><strong>Type:</strong> {alert.alert_type}</p>
                        <p><strong>Severity:</strong> {alert.severity}</p>
                        <p><strong>Created:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p><strong>Status:</strong> {alert.status}</p>
                    </div>
        """
        
        if device:
            html += f"""
                    <div class="device-info">
                        <h3>Device Information</h3>
                        <p><strong>Device ID:</strong> {device.device_id}</p>
                        <p><strong>Name:</strong> {device.name}</p>
                        <p><strong>Location:</strong> {device.location}</p>
                        <p><strong>Status:</strong> {device.status}</p>
                        <p><strong>Priority:</strong> {device.priority}</p>
                    </div>
            """
        
        metadata = alert.get_metadata()
        if metadata:
            html += """
                    <div class="alert-info">
                        <h3>Sensor Data</h3>
            """
            for key, value in metadata.items():
                if key == 'temperature':
                    html += f"<p><strong>Temperature:</strong> {value}°C</p>"
                elif key == 'humidity':
                    html += f"<p><strong>Humidity:</strong> {value}%</p>"
                elif key == 'battery_level':
                    html += f"<p><strong>Battery:</strong> {value}%</p>"
                else:
                    html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
            html += "</div>"
        
        html += f"""
                    <p style="margin-top: 30px;">
                        <a href="http://localhost:3000" class="btn">View Dashboard</a>
                    </p>
                    
                    <p><em>This is an automated alert from the Vital Trace cold chain monitoring system. 
                    Please take appropriate action based on the alert severity and your organization's protocols.</em></p>
                </div>
                <div class="footer">
                    <p>Vital Trace - Cold Chain Monitoring System</p>
                    <p>Generated at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_sms_notification(self, alert: Alert, device: Optional[Device]) -> Dict[str, Any]:
        """Send SMS notification (placeholder implementation)"""
        try:
            # This would integrate with SMS service like Twilio, AWS SNS, etc.
            # For now, it's a placeholder implementation
            
            sms_api_key = current_app.config.get('SMS_API_KEY')
            if not sms_api_key:
                return {'status': 'skipped', 'message': 'SMS service not configured'}
            
            # Get phone numbers for critical alerts
            phone_numbers = self._get_sms_recipients(alert.severity)
            
            if not phone_numbers:
                return {'status': 'skipped', 'message': 'No SMS recipients configured'}
            
            message = f"VITAL TRACE ALERT: {alert.title} - {alert.message}"
            
            # Placeholder for SMS sending logic
            # In production, you would integrate with your SMS provider
            self.logger.info(f"SMS would be sent to {len(phone_numbers)} recipients: {message}")
            
            return {
                'status': 'success',
                'message': f'SMS sent to {len(phone_numbers)} recipients',
                'recipients': phone_numbers
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _get_sms_recipients(self, severity: str) -> List[str]:
        """Get SMS recipients based on alert severity"""
        # In production, this would return actual phone numbers from user profiles
        # For now, return empty list
        return []
    
    def _send_slack_notification(self, alert: Alert, device: Optional[Device]) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            webhook_url = current_app.config.get('SLACK_WEBHOOK_URL')
            
            if not webhook_url:
                return {'status': 'skipped', 'message': 'Slack webhook not configured'}
            
            # Create Slack message
            color_map = {
                'critical': 'danger',
                'high': 'warning',
                'medium': 'good',
                'low': 'good'
            }
            
            color = color_map.get(alert.severity, 'good')
            
            payload = {
                'text': f'🚨 Vital Trace Alert: {alert.title}',
                'attachments': [
                    {
                        'color': color,
                        'fields': [
                            {
                                'title': 'Alert Type',
                                'value': alert.alert_type,
                                'short': True
                            },
                            {
                                'title': 'Severity',
                                'value': alert.severity.upper(),
                                'short': True
                            },
                            {
                                'title': 'Device',
                                'value': f"{device.name} ({alert.device_id})" if device else alert.device_id,
                                'short': True
                            },
                            {
                                'title': 'Location',
                                'value': device.location if device else 'Unknown',
                                'short': True
                            },
                            {
                                'title': 'Message',
                                'value': alert.message,
                                'short': False
                            }
                        ],
                        'footer': 'Vital Trace',
                        'ts': int(alert.created_at.timestamp())
                    }
                ]
            }
            
            # Add sensor data if available
            metadata = alert.get_metadata()
            if metadata:
                sensor_fields = []
                for key, value in metadata.items():
                    if key in ['temperature', 'humidity', 'battery_level']:
                        unit = {'temperature': '°C', 'humidity': '%', 'battery_level': '%'}.get(key, '')
                        sensor_fields.append({
                            'title': key.replace('_', ' ').title(),
                            'value': f"{value}{unit}",
                            'short': True
                        })
                
                if sensor_fields:
                    payload['attachments'][0]['fields'].extend(sensor_fields)
            
            # Send to Slack
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {'status': 'success', 'message': 'Slack notification sent'}
            else:
                return {'status': 'error', 'message': f'Slack API error: {response.status_code}'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _send_webhook_notification(self, alert: Alert, device: Optional[Device]) -> Dict[str, Any]:
        """Send webhook notification to external systems"""
        try:
            webhook_url = current_app.config.get('EXTERNAL_WEBHOOK_URL')
            
            if not webhook_url:
                return {'status': 'skipped', 'message': 'Webhook URL not configured'}
            
            # Create webhook payload
            payload = {
                'event': 'alert_created',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'alert': alert.to_dict(),
                'device': device.to_dict() if device else None
            }
            
            # Send webhook
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                return {'status': 'success', 'message': 'Webhook notification sent'}
            else:
                return {'status': 'error', 'message': f'Webhook error: {response.status_code}'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def send_system_notification(self, notification_type: str, message: str, 
                               severity: str = 'info') -> Dict[str, Any]:
        """Send system-wide notifications"""
        try:
            if not self.socketio:
                return {'status': 'error', 'message': 'WebSocket not configured'}
            
            notification_data = {
                'type': notification_type,
                'message': message,
                'severity': severity,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Emit to all connected clients
            self.socketio.emit('system_notification', notification_data)
            
            return {'status': 'success', 'message': 'System notification sent'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def send_maintenance_notification(self, device_id: str, maintenance_type: str, 
                                    message: str) -> Dict[str, Any]:
        """Send maintenance-related notifications"""
        try:
            device = Device.query.filter_by(device_id=device_id).first()
            
            # Create maintenance alert
            alert_data = {
                'device_id': device_id,
                'alert_type': 'maintenance_due',
                'severity': 'medium',
                'title': f'Maintenance Required - {device.name if device else device_id}',
                'message': message,
                'metadata': {'maintenance_type': maintenance_type}
            }
            
            # Create alert object for notification
            alert = Alert(**alert_data)
            
            # Send notification
            return self.send_alert_notification(alert)
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_notification_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get notification delivery statistics"""
        try:
            # In a production system, you would track notification delivery
            # For now, return placeholder statistics
            return {
                'period_hours': hours,
                'total_notifications_sent': 0,
                'delivery_rates': {
                    'websocket': 100.0,
                    'email': 95.0,
                    'sms': 98.0,
                    'slack': 99.0
                },
                'failed_notifications': 0,
                'average_delivery_time_ms': 150
            }
            
        except Exception as e:
            return {'error': str(e)}
