import logging
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
import json

from models import User, UserSession, db

class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.failed_login_attempts = {}  # Track failed login attempts
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
        
    def authenticate_user(self, username: str, password: str, 
                         user_agent: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Authenticate user with enhanced security"""
        try:
            # Check for account lockout
            if self._is_account_locked(username):
                return {
                    'success': False,
                    'error': 'Account temporarily locked due to too many failed login attempts',
                    'lockout_remaining_minutes': self._get_lockout_remaining_minutes(username)
                }
            
            # Find user
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.is_active:
                self._record_failed_login(username)
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check password
            if not user.check_password(password):
                self._record_failed_login(username)
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Reset failed login attempts on successful login
            self._reset_failed_login_attempts(username)
            
            # Update last login
            user.update_last_login()
            
            # Create tokens
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'role': user.role,
                    'username': user.username,
                    'permissions': self._get_user_permissions(user.role)
                }
            )
            
            refresh_token = create_refresh_token(identity=user.id)
            
            # Create user session
            session = self._create_user_session(
                user.id, 
                access_token, 
                user_agent, 
                ip_address
            )
            
            self.logger.info(f"User {username} successfully authenticated from {ip_address}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'session_id': session.id if session else None,
                'permissions': self._get_user_permissions(user.role)
            }
            
        except Exception as e:
            self.logger.error(f"Authentication failed for {username}: {str(e)}")
            return {'success': False, 'error': 'Authentication service error'}
    
    def refresh_token(self, refresh_token_identity: int) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            user = User.query.get(refresh_token_identity)
            
            if not user or not user.is_active:
                return {'success': False, 'error': 'User not found or inactive'}
            
            # Create new access token
            new_access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'role': user.role,
                    'username': user.username,
                    'permissions': self._get_user_permissions(user.role)
                }
            )
            
            return {
                'success': True,
                'access_token': new_access_token,
                'permissions': self._get_user_permissions(user.role)
            }
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {str(e)}")
            return {'success': False, 'error': 'Token refresh failed'}
    
    def logout_user(self, user_id: int, session_token: str = None) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            # Invalidate user session if provided
            if session_token:
                session = UserSession.query.filter_by(
                    user_id=user_id,
                    session_token=session_token
                ).first()
                
                if session:
                    session.is_active = False
                    db.session.commit()
            
            # In a production system, you would also blacklist the JWT token
            # For now, we'll just log the logout
            self.logger.info(f"User {user_id} logged out")
            
            return {'success': True, 'message': 'Successfully logged out'}
            
        except Exception as e:
            self.logger.error(f"Logout failed for user {user_id}: {str(e)}")
            return {'success': False, 'error': 'Logout failed'}
    
    def validate_permissions(self, user_role: str, required_permission: str) -> bool:
        """Validate user permissions for specific actions"""
        try:
            user_permissions = self._get_user_permissions(user_role)
            return required_permission in user_permissions
            
        except Exception as e:
            self.logger.error(f"Permission validation failed: {str(e)}")
            return False
    
    def _get_user_permissions(self, role: str) -> List[str]:
        """Get permissions based on user role"""
        permission_map = {
            'admin': [
                'read_all_devices',
                'write_all_devices',
                'manage_users',
                'manage_settings',
                'view_system_logs',
                'manage_alerts',
                'export_data',
                'manage_maintenance',
                'view_analytics',
                'manage_notifications'
            ],
            'operator': [
                'read_all_devices',
                'write_assigned_devices',
                'view_alerts',
                'acknowledge_alerts',
                'export_data',
                'view_analytics',
                'manage_maintenance'
            ],
            'viewer': [
                'read_assigned_devices',
                'view_alerts',
                'view_analytics'
            ]
        }
        
        return permission_map.get(role, permission_map['viewer'])
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed login attempts"""
        try:
            if username not in self.failed_login_attempts:
                return False
            
            attempts_data = self.failed_login_attempts[username]
            
            # Check if lockout period has expired
            lockout_end = attempts_data['lockout_time'] + timedelta(minutes=self.lockout_duration_minutes)
            
            if datetime.now(timezone.utc) > lockout_end:
                # Lockout expired, reset attempts
                del self.failed_login_attempts[username]
                return False
            
            return attempts_data['attempts'] >= self.max_login_attempts
            
        except Exception as e:
            self.logger.error(f"Account lockout check failed: {str(e)}")
            return False
    
    def _get_lockout_remaining_minutes(self, username: str) -> int:
        """Get remaining lockout time in minutes"""
        try:
            if username not in self.failed_login_attempts:
                return 0
            
            attempts_data = self.failed_login_attempts[username]
            lockout_end = attempts_data['lockout_time'] + timedelta(minutes=self.lockout_duration_minutes)
            remaining = lockout_end - datetime.now(timezone.utc)
            
            return max(0, int(remaining.total_seconds() / 60))
            
        except Exception as e:
            self.logger.error(f"Lockout time calculation failed: {str(e)}")
            return 0
    
    def _record_failed_login(self, username: str) -> None:
        """Record failed login attempt"""
        try:
            current_time = datetime.now(timezone.utc)
            
            if username not in self.failed_login_attempts:
                self.failed_login_attempts[username] = {
                    'attempts': 1,
                    'first_attempt_time': current_time,
                    'lockout_time': current_time
                }
            else:
                self.failed_login_attempts[username]['attempts'] += 1
                self.failed_login_attempts[username]['lockout_time'] = current_time
            
            attempts = self.failed_login_attempts[username]['attempts']
            
            if attempts >= self.max_login_attempts:
                self.logger.warning(f"Account {username} locked after {attempts} failed login attempts")
            else:
                self.logger.info(f"Failed login attempt {attempts} for {username}")
                
        except Exception as e:
            self.logger.error(f"Failed to record login attempt: {str(e)}")
    
    def _reset_failed_login_attempts(self, username: str) -> None:
        """Reset failed login attempts on successful login"""
        try:
            if username in self.failed_login_attempts:
                del self.failed_login_attempts[username]
                
        except Exception as e:
            self.logger.error(f"Failed to reset login attempts: {str(e)}")
    
    def _create_user_session(self, user_id: int, session_token: str, 
                           user_agent: str = None, ip_address: str = None) -> Optional[UserSession]:
        """Create a new user session record"""
        try:
            # Generate unique session token hash
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()
            
            session = UserSession(
                user_id=user_id,
                session_token=token_hash,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            
            db.session.add(session)
            db.session.commit()
            
            return session
            
        except Exception as e:
            self.logger.error(f"Session creation failed: {str(e)}")
            return None
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get active sessions for a user"""
        try:
            sessions = UserSession.query.filter_by(
                user_id=user_id,
                is_active=True
            ).filter(
                UserSession.expires_at > datetime.now(timezone.utc)
            ).all()
            
            return [session.to_dict() for session in sessions]
            
        except Exception as e:
            self.logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    def invalidate_user_session(self, user_id: int, session_id: int) -> Dict[str, Any]:
        """Invalidate a specific user session"""
        try:
            session = UserSession.query.filter_by(
                id=session_id,
                user_id=user_id
            ).first()
            
            if not session:
                return {'success': False, 'error': 'Session not found'}
            
            session.is_active = False
            db.session.commit()
            
            return {'success': True, 'message': 'Session invalidated'}
            
        except Exception as e:
            self.logger.error(f"Session invalidation failed: {str(e)}")
            return {'success': False, 'error': 'Session invalidation failed'}
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime.now(timezone.utc)
            )
            
            count = expired_sessions.count()
            expired_sessions.delete()
            db.session.commit()
            
            if count > 0:
                self.logger.info(f"Cleaned up {count} expired sessions")
            
            return count
            
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {str(e)}")
            return 0
    
    def change_password(self, user_id: int, current_password: str, 
                       new_password: str) -> Dict[str, Any]:
        """Change user password with validation"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Verify current password
            if not user.check_password(current_password):
                return {'success': False, 'error': 'Current password is incorrect'}
            
            # Validate new password strength
            password_validation = self._validate_password_strength(new_password)
            if not password_validation['valid']:
                return {'success': False, 'error': password_validation['message']}
            
            # Set new password
            user.set_password(new_password)
            db.session.commit()
            
            # Invalidate all user sessions to force re-login
            UserSession.query.filter_by(user_id=user_id).update({'is_active': False})
            db.session.commit()
            
            self.logger.info(f"Password changed for user {user.username}")
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            self.logger.error(f"Password change failed: {str(e)}")
            return {'success': False, 'error': 'Password change failed'}
    
    def _validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        try:
            if len(password) < 8:
                return {'valid': False, 'message': 'Password must be at least 8 characters long'}
            
            if not any(c.isupper() for c in password):
                return {'valid': False, 'message': 'Password must contain at least one uppercase letter'}
            
            if not any(c.islower() for c in password):
                return {'valid': False, 'message': 'Password must contain at least one lowercase letter'}
            
            if not any(c.isdigit() for c in password):
                return {'valid': False, 'message': 'Password must contain at least one digit'}
            
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return {'valid': False, 'message': 'Password must contain at least one special character'}
            
            return {'valid': True, 'message': 'Password is strong'}
            
        except Exception as e:
            self.logger.error(f"Password validation failed: {str(e)}")
            return {'valid': False, 'message': 'Password validation error'}
    
    def create_user(self, username: str, email: str, password: str, 
                   role: str = 'viewer', created_by: int = None) -> Dict[str, Any]:
        """Create a new user with validation"""
        try:
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                return {'success': False, 'error': 'Username already exists'}
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                return {'success': False, 'error': 'Email already exists'}
            
            # Validate password
            password_validation = self._validate_password_strength(password)
            if not password_validation['valid']:
                return {'success': False, 'error': password_validation['message']}
            
            # Validate role
            valid_roles = ['admin', 'operator', 'viewer']
            if role not in valid_roles:
                return {'success': False, 'error': 'Invalid role specified'}
            
            # Create user
            user = User(
                username=username,
                email=email,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            self.logger.info(f"User {username} created with role {role}")
            
            return {'success': True, 'user': user.to_dict()}
            
        except Exception as e:
            self.logger.error(f"User creation failed: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': 'User creation failed'}
    
    def update_user(self, user_id: int, updates: Dict[str, Any], 
                   updated_by: int = None) -> Dict[str, Any]:
        """Update user information"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Update allowed fields
            if 'email' in updates:
                # Check if email is already in use by another user
                existing_user = User.query.filter_by(email=updates['email']).first()
                if existing_user and existing_user.id != user_id:
                    return {'success': False, 'error': 'Email already in use'}
                user.email = updates['email']
            
            if 'role' in updates:
                valid_roles = ['admin', 'operator', 'viewer']
                if updates['role'] in valid_roles:
                    user.role = updates['role']
                else:
                    return {'success': False, 'error': 'Invalid role specified'}
            
            if 'is_active' in updates:
                user.is_active = bool(updates['is_active'])
            
            db.session.commit()
            
            self.logger.info(f"User {user.username} updated")
            
            return {'success': True, 'user': user.to_dict()}
            
        except Exception as e:
            self.logger.error(f"User update failed: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': 'User update failed'}
    
    def get_auth_statistics(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        try:
            # Count active sessions
            active_sessions = UserSession.query.filter(
                UserSession.is_active == True,
                UserSession.expires_at > datetime.now(timezone.utc)
            ).count()
            
            # Count users by role
            users_by_role = {}
            for role in ['admin', 'operator', 'viewer']:
                count = User.query.filter_by(role=role, is_active=True).count()
                users_by_role[role] = count
            
            # Count total users
            total_users = User.query.filter_by(is_active=True).count()
            
            # Count failed login attempts
            current_failed_attempts = len(self.failed_login_attempts)
            
            return {
                'total_active_users': total_users,
                'users_by_role': users_by_role,
                'active_sessions': active_sessions,
                'current_failed_login_attempts': current_failed_attempts,
                'account_lockout_threshold': self.max_login_attempts,
                'lockout_duration_minutes': self.lockout_duration_minutes
            }
            
        except Exception as e:
            self.logger.error(f"Auth statistics failed: {str(e)}")
            return {'error': str(e)}
