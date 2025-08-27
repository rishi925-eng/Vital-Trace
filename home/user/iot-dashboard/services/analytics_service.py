
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
import numpy as np
import pandas as pd
from sqlalchemy import func, and_, or_, text
from collections import defaultdict
import json
from models import SensorData, Device, Alert, db

class AnalyticsService:
    """Service for analytics and data processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection
        self.trend_window = 10  # Number of points for trend analysis
    
    def get_device_statistics(self, device_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive statistics for a device"""
        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Get sensor data for the time period
            sensor_data = SensorData.query.filter(
                SensorData.device_id == device_id,
                SensorData.timestamp >= start_time
            ).order_by(SensorData.timestamp).all()
            
            if not sensor_data:
                return {
                    'device_id': device_id,
                    'period_hours': hours,
                    'total_readings': 0,
                    'statistics': {},
                    'message': 'No data available for the specified period'
                }
            
            # Group by sensor type
            stats_by_type = defaultdict(list)
            timestamps = []
            
            for data in sensor_data:
                stats_by_type[data.sensor_type].append({
                    'value': data.value,
                    'timestamp': data.timestamp,
                    'unit': data.unit
                })
                timestamps.append(data.timestamp)
            
            # Calculate statistics for each sensor type
            statistics = {}
            for sensor_type, values in stats_by_type.items():
                numeric_values = [v['value'] for v in values if v['value'] is not None]
                
                if numeric_values:
                    statistics[sensor_type] = {
                        'count': len(numeric_values),
                        'min': float(min(numeric_values)),
                        'max': float(max(numeric_values)),
                        'avg': float(np.mean(numeric_values)),
                        'median': float(np.median(numeric_values)),
                        'std': float(np.std(numeric_values)) if len(numeric_values) > 1 else 0.0,
                        'latest': numeric_values[-1],
                        'unit': values[-1]['unit'] if values else None,
                        'trend': self._calculate_trend(numeric_values),
                        'anomalies': self._detect_anomalies(numeric_values),
                        'data_quality': self._assess_data_quality(values)
                    }
            
            return {
                'device_id': device_id,
                'period_hours': hours,
                'total_readings': len(sensor_data),
                'statistics': statistics,
                'data_range': {
                    'start': min(timestamps).isoformat() if timestamps else None,
                    'end': max(timestamps).isoformat() if timestamps else None
                },
                'health_score': self._calculate_device_health_score(statistics)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get device statistics: {str(e)}")
            return {'error': str(e)}
    
    def get_trend_data(self, device_id: str, sensor_type: str, 
                      hours: int = 24, interval_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get trend data for a specific sensor with time intervals"""
        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Get raw data and group manually for better compatibility
            sensor_data = SensorData.query.filter(
                SensorData.device_id == device_id,
                SensorData.sensor_type == sensor_type,
                SensorData.timestamp >= start_time
            ).order_by(SensorData.timestamp).all()
            
            if not sensor_data:
                return []
            
            # Group data by intervals
            interval_data = defaultdict(list)
            
            for data in sensor_data:
                # Round timestamp to nearest interval
                minutes = data.timestamp.minute
                rounded_minutes = (minutes // interval_minutes) * interval_minutes
                interval_key = data.timestamp.replace(minute=rounded_minutes, second=0, microsecond=0)
                
                interval_data[interval_key].append(data.value)
            
            # Calculate statistics for each interval
            trend_data = []
            for timestamp, values in sorted(interval_data.items()):
                if values:
                    trend_data.append({
                        'timestamp': timestamp.isoformat(),
                        'avg_value': float(np.mean(values)),
                        'min_value': float(min(values)),
                        'max_value': float(max(values)),
                        'count': len(values),
                        'unit': sensor_data[0].unit if sensor_data else None
                    })
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"Failed to get trend data: {str(e)}")
            return []
    
    def analyze_trends(self, device_id: str, data_buffer: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in real-time data buffer"""
        try:
            if len(data_buffer) < self.trend_window:
                return {'status': 'insufficient_data', 'required_points': self.trend_window}
            
            # Extract recent data points
            recent_data = data_buffer[-self.trend_window:]
            
            trends = {}
            for key in ['temperature', 'humidity', 'battery_level', 'pressure']:
                if key in recent_data[0]:
                    values = [d.get(key, 0) for d in recent_data if d.get(key) is not None]
                    if values:
                        trends[key] = self._analyze_single_trend(values)
            
            return {
                'device_id': device_id,
                'analysis_window': self.trend_window,
                'trends': trends,
                'overall_trend': self._determine_overall_trend(trends),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze trends: {str(e)}")
            return {'error': str(e)}
    
    def predict_maintenance(self, device_id: str) -> Dict[str, Any]:
        """Predict maintenance needs based on historical data"""
        try:
            # Get last 30 days of data
            start_time = datetime.now(timezone.utc) - timedelta(days=30)
            
            sensor_data = SensorData.query.filter(
                SensorData.device_id == device_id,
                SensorData.timestamp >= start_time
            ).order_by(SensorData.timestamp).all()
            
            if len(sensor_data) < 100:  # Need sufficient data for prediction
                return {
                    'prediction': 'insufficient_data',
                    'confidence': 0,
                    'message': 'Need at least 100 data points for reliable prediction'
                }
            
            # Analyze battery degradation
            battery_data = [d for d in sensor_data if d.sensor_type == 'battery_level']
            battery_prediction = self._predict_battery_maintenance(battery_data)
            
            # Analyze sensor drift
            sensor_drift = self._analyze_sensor_drift(sensor_data)
            
            # Calculate overall maintenance score
            maintenance_score = self._calculate_maintenance_score(
                battery_prediction, sensor_drift, sensor_data
            )
            
            return {
                'device_id': device_id,
                'maintenance_score': maintenance_score,
                'battery_prediction': battery_prediction,
                'sensor_drift': sensor_drift,
                'recommendations': self._generate_maintenance_recommendations(
                    maintenance_score, battery_prediction, sensor_drift
                ),
                'next_check_date': self._calculate_next_maintenance_date(maintenance_score)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to predict maintenance: {str(e)}")
            return {'error': str(e)}
    
    def get_comparative_analysis(self, device_ids: List[str], 
                               hours: int = 24) -> Dict[str, Any]:
        """Compare performance across multiple devices"""
        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            comparison_data = {}
            
            for device_id in device_ids:
                device_stats = self.get_device_statistics(device_id, hours)
                if 'error' not in device_stats:
                    comparison_data[device_id] = device_stats
            
            if not comparison_data:
                return {'error': 'No valid data for comparison'}
            
            # Perform comparative analysis
            comparative_metrics = self._calculate_comparative_metrics(comparison_data)
            
            return {
                'comparison_period_hours': hours,
                'devices_analyzed': len(comparison_data),
                'individual_stats': comparison_data,
                'comparative_metrics': comparative_metrics,
                'rankings': self._rank_devices(comparison_data),
                'outliers': self._identify_outlier_devices(comparison_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to perform comparative analysis: {str(e)}")
            return {'error': str(e)}
    
    def get_alert_analytics(self, device_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze alert patterns for a device"""
        try:
            start_time = datetime.now(timezone.utc) - timedelta(days=days)
            
            alerts = Alert.query.filter(
                Alert.device_id == device_id,
                Alert.created_at >= start_time
            ).order_by(Alert.created_at).all()
            
            if not alerts:
                return {
                    'device_id': device_id,
                    'period_days': days,
                    'total_alerts': 0,
                    'patterns': {}
                }
            
            # Analyze alert patterns
            alert_patterns = self._analyze_alert_patterns(alerts)
            
            return {
                'device_id': device_id,
                'period_days': days,
                'total_alerts': len(alerts),
                'patterns': alert_patterns,
                'severity_distribution': self._get_severity_distribution(alerts),
                'resolution_times': self._calculate_resolution_times(alerts),
                'peak_hours': self._identify_peak_alert_hours(alerts)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze alerts: {str(e)}")
            return {'error': str(e)}
    
    def export_analytics_data(self, device_id: str, start_date: datetime, 
                            end_date: datetime, format: str = 'json') -> Dict[str, Any]:
        """Export analytics data in specified format"""
        try:
            sensor_data = SensorData.query.filter(
                SensorData.device_id == device_id,
                SensorData.timestamp >= start_date,
                SensorData.timestamp <= end_date
            ).order_by(SensorData.timestamp).all()
            
            if not sensor_data:
                return {'error': 'No data found for the specified period'}
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame([{
                'timestamp': d.timestamp.isoformat(),
                'sensor_type': d.sensor_type,
                'value': d.value,
                'unit': d.unit
            } for d in sensor_data])
            
            if format.lower() == 'csv':
                csv_data = df.to_csv(index=False)
                return {
                    'format': 'csv',
                    'data': csv_data,
                    'filename': f'analytics_{device_id}_{start_date.date()}_{end_date.date()}.csv'
                }
            else:
                # Default to JSON
                return {
                    'format': 'json',
                    'data': df.to_dict('records'),
                    'summary': self.get_device_statistics(
                        device_id, 
                        int((end_date - start_date).total_seconds() / 3600)
                    )
                }
                
        except Exception as e:
            self.logger.error(f"Failed to export analytics data: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength"""
        if len(values) < 2:
            return {'direction': 'stable', 'strength': 0, 'slope': 0}
        
        try:
            # Simple linear regression
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Determine trend direction and strength
            if abs(slope) < 0.01:
                direction = 'stable'
            elif slope > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            strength = min(abs(slope) * 100, 100)  # Normalize to 0-100
            
            return {
                'direction': direction,
                'strength': float(strength),
                'slope': float(slope)
            }
        except Exception:
            return {'direction': 'stable', 'strength': 0, 'slope': 0}
    
    def _detect_anomalies(self, values: List[float]) -> Dict[str, Any]:
        """Detect anomalies using statistical methods"""
        if len(values) < 3:
            return {'count': 0, 'indices': []}
        
        try:
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if std_val == 0:
                return {'count': 0, 'indices': []}
            
            anomaly_indices = []
            for i, value in enumerate(values):
                z_score = abs((value - mean_val) / std_val)
                if z_score > self.anomaly_threshold:
                    anomaly_indices.append(i)
            
            return {
                'count': len(anomaly_indices),
                'indices': anomaly_indices,
                'threshold': self.anomaly_threshold
            }
        except Exception:
            return {'count': 0, 'indices': []}
    
    def _assess_data_quality(self, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of sensor data"""
        if not data_points:
            return {'score': 0, 'issues': ['no_data']}
        
        try:
            issues = []
            score = 100
            
            # Check for missing values
            values = [d['value'] for d in data_points if d['value'] is not None]
            if len(values) < len(data_points):
                missing_ratio = (len(data_points) - len(values)) / len(data_points)
                score -= missing_ratio * 30
                issues.append(f'missing_values: {missing_ratio:.2%}')
            
            # Check for constant values (potential sensor failure)
            if len(set(values)) == 1 and len(values) > 1:
                score -= 20
                issues.append('constant_values')
            
            # Check for extreme outliers
            if len(values) > 3:
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [v for v in values if v < lower_bound or v > upper_bound]
                if outliers:
                    outlier_ratio = len(outliers) / len(values)
                    score -= outlier_ratio * 20
                    issues.append(f'outliers: {outlier_ratio:.2%}')
            
            # Ensure score is between 0 and 100
            score = max(0, min(100, score))
            
            return {
                'score': round(score, 2),
                'issues': issues
            }
        except Exception as e:
            self.logger.error(f"Error assessing data quality: {str(e)}")
            return {'score': 0, 'issues': ['quality_assessment_error']}
    
    def _calculate_device_health_score(self, statistics: Dict[str, Any]) -> float:
        """Calculate overall health score for device"""
        if not statistics:
            return 0.0
        
        total_score = 0
        total_weight = 0
        
        for sensor_type, stats in statistics.items():
            # Weight based on sensor importance (can be adjusted)
            weight = 1.0
            if sensor_type in ['battery_level']:
                weight = 1.5  # Battery is critical
            elif sensor_type in ['temperature', 'humidity']:
                weight = 1.2  # Environmental sensors
            elif sensor_type in ['pressure']:
                weight = 1.0  # General sensors
            
            # Base score from data quality
            quality_score = stats.get('data_quality', {}).get('score', 0)
            data_quality_weight = 0.4
            
            # Trend score (positive trend = good)
            trend_direction = stats.get('trend', {}).get('direction', 'stable')
            trend_score = 100 if trend_direction != 'decreasing' else 50
            trend_weight = 0.3
            
            # Anomaly score (fewer anomalies = better)
            anomaly_count = stats.get('anomalies', {}).get('count', 0)
            anomaly_score = max(0, 100 - (anomaly_count * 10))
            anomaly_weight = 0.3
            
            # Calculate weighted score for this sensor
            sensor_score = (
                quality_score * data_quality_weight +
                trend_score * trend_weight +
                anomaly_score * anomaly_weight
            )
            
            total_score += sensor_score * weight
            total_weight += weight
        
        return round(total_score / total_weight if total_weight > 0 else 0, 2)
    
    def _analyze_single_trend(self, values: List[float]) -> Dict[str, Any]:
        """Analyze trend for a single sensor"""
        if len(values) < 2:
            return {'direction': 'stable', 'strength': 0}
        
        try:
            # Use linear regression to determine trend
            x = np.arange(len(values))
            slope, _ = np.polyfit(x, values, 1)
            
            # Determine direction
            if abs(slope) < 0.01:
                direction = 'stable'
            elif slope > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            # Calculate strength (normalized)
            strength = min(abs(slope) * 100, 100)
            
            return {
                'direction': direction,
                'strength': round(strength, 2),
                'slope': round(slope, 4)
            }
        except Exception:
            return {'direction': 'stable', 'strength': 0}
    
    def _determine_overall_trend(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """Determine overall trend from individual sensor trends"""
        if not trends:
            return {'direction': 'stable', 'strength': 0}
        
        directions = [t['direction'] for t in trends.values()]
        strengths = [t['strength'] for t in trends.values()]
        
        # Count occurrences of each direction
        direction_counts = defaultdict(int)
        for direction in directions:
            direction_counts[direction] += 1
        
        # Determine dominant direction
        dominant_direction = max(direction_counts, key=direction_counts.get)
        
        # Calculate average strength
        avg_strength = sum(strengths) / len(strengths) if strengths else 0
        
        return {
            'direction': dominant_direction,
            'strength': round(avg_strength, 2)
        }
    
    def _predict_battery_maintenance(self, battery_data: List[SensorData]) -> Dict[str, Any]:
        """Predict battery maintenance needs"""
        if len(battery_data) < 10:
            return {'prediction': 'insufficient_data', 'confidence': 0}
        
        try:
            # Extract battery levels
            battery_levels = [d.value for d in battery_data if d.value is not None]
            
            if len(battery_levels) < 10:
                return {'prediction': 'insufficient_data', 'confidence': 0}
            
            # Simple linear regression to predict battery degradation
            x = np.arange(len(battery_levels))
            slope, intercept = np.polyfit(x, battery_levels, 1)
            
            # Predict when battery will reach critical level (e.g., 10%)
            critical_level = 10.0
            if slope < 0:  # Battery is degrading
                predicted_degradation = (critical_level - battery_levels[-1]) / slope
                predicted_degradation_days = predicted_degradation * 24  # Assuming hourly readings
                
                # Confidence based on how far we are from critical level
                confidence = max(0, min(100, (battery_levels[-1] - critical_level) / (battery_levels[0] - critical_level) * 100))
                
                return {
                    'prediction': 'degrading',
                    'predicted_days_remaining': round(predicted_degradation_days, 2),
                    'confidence': round(confidence, 2),
                    'current_rate_of_degradation': round(slope, 4)
                }
            else:
                return {
                    'prediction': 'stable',
                    'confidence': 80,
                    'current_rate_of_degradation': round(slope, 4)
                }
        except Exception as e:
            self.logger.error(f"Error predicting battery maintenance: {str(e)}")
            return {'prediction': 'error', 'confidence': 0}
    
    def _analyze_sensor_drift(self, sensor_data: List[SensorData]) -> Dict[str, Any]:
        """Analyze for sensor drift"""
        try:
            # Group by sensor type
            sensor_groups = defaultdict(list)
            for data in sensor_data:
                sensor_groups[data.sensor_type].append(data)
            
            drift_results = {}
            for sensor_type, data_list in sensor_groups.items():
                if len(data_list) < 10:
                    drift_results[sensor_type] = {'status': 'insufficient_data'}
                    continue
                
                # Extract values
                values = [d.value for d in data_list if d.value is not None]
                if len(values) < 10:
                    drift_results[sensor_type] = {'status': 'insufficient_data'}
                    continue
                
                # Calculate standard deviation and mean
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                # Detect significant drift (more than 2 standard deviations from mean)
                drift_points = [i for i, val in enumerate(values) 
                              if abs(val - mean_val) > 2 * std_val]
                
                drift_results[sensor_type] = {
                    'status': 'drift_detected' if len(drift_points) > 0 else 'stable',
                    'drift_count': len(drift_points),
                    'drift_percentage': round(len(drift_points) / len(values) * 100, 2),
                    'mean': round(mean_val, 2),
                    'std_deviation': round(std_val, 2)
                }
            
            return drift_results
        except Exception as e:
            self.logger.error(f"Error analyzing sensor drift: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_maintenance_score(self, battery_prediction: Dict[str, Any], 
                                   sensor_drift: Dict[str, Any], 
                                   sensor_data: List[SensorData]) -> float:
        """Calculate overall maintenance score"""
        try:
            score = 100.0
            
            # Battery degradation impact
            if battery_prediction.get('prediction') == 'degrading':
                degradation_score = max(0, 100 - battery_prediction.get('predicted_days_remaining', 0) * 0.5)
                score = min(score, degradation_score)
            
            # Sensor drift impact
            drift_impact = 0
            for sensor_type, drift_info in sensor_drift.items():
                if isinstance(drift_info, dict) and drift_info.get('status') == 'drift_detected':
                    drift_impact += drift_info.get('drift_percentage', 0) * 0.5
            
            score = max(0, score - drift_impact)
            
            # Data quality impact
            total_quality = 0
            quality_count = 0
            for data in sensor_data:
                if hasattr(data, 'quality_score'):
                    total_quality += data.quality_score
                    quality_count += 1
            
            if quality_count > 0:
                avg_quality = total_quality / quality_count
                score = max(0, score - (100 - avg_quality) * 0.5)
            
            return round(score, 2)
        except Exception as e:
            self.logger.error(f"Error calculating maintenance score: {str(e)}")
            return 0.0
    
    def _generate_maintenance_recommendations(self, maintenance_score: float, 
                                           battery_prediction: Dict[str, Any], 
                                           sensor_drift: Dict[str, Any]) -> List[str]:
        """Generate maintenance recommendations based on scores"""
        recommendations = []
        
        if maintenance_score < 50:
            recommendations.append("Immediate maintenance required")
        elif maintenance_score < 70:
            recommendations.append("Schedule maintenance check soon")
        else:
            recommendations.append("Maintenance not urgent")
        
        if battery_prediction.get('prediction') == 'degrading':
            recommendations.append(f"Battery replacement recommended in {battery_prediction.get('predicted_days_remaining', 0)} days")
        
        for sensor_type, drift_info in sensor_drift.items():
            if isinstance(drift_info, dict) and drift_info.get('status') == 'drift_detected':
                recommendations.append(f"Sensor drift detected in {sensor_type}, consider recalibration")
        
        return recommendations
    
    def _calculate_next_maintenance_date(self, maintenance_score: float) -> str:
        """Calculate next maintenance date based on score"""
        try:
            base_date = datetime.now(timezone.utc)
            
            if maintenance_score < 30:
                # Very high risk - next maintenance in 1 week
                return (base_date + timedelta(weeks=1)).isoformat()
            elif maintenance_score < 60:
                # Moderate risk - next maintenance in 1 month
                return (base_date + timedelta(days=30)).isoformat()
            else:
                # Low risk - next maintenance in 3 months
                return (base_date + timedelta(days=90)).isoformat()
        except Exception:
            return base_date.isoformat()
    
    def _calculate_comparative_metrics(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comparative metrics across devices"""
        try:
            if len(comparison_data) < 2:
                return {}
            
            # Collect all statistics
            all_stats = []
            for device_id, stats in comparison_data.items():
                if 'statistics' in stats:
                    all_stats.extend(stats['statistics'].values())
            
            if not all_stats:
                return {}
            
            # Calculate overall averages
            metrics = {}
            for stat in all_stats:
                if 'avg' in stat:
                    metrics['avg_' + stat.get('sensor_type', 'unknown')] = stat['avg']
                if 'std' in stat:
                    metrics['std_' + stat.get('sensor_type', 'unknown')] = stat['std']
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating comparative metrics: {str(e)}")
            return {}
    
    def _rank_devices(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rank devices by health score"""
        try:
            rankings = []
            for device_id, stats in comparison_data.items():
                health_score = stats.get('health_score', 0)
                rankings.append((device_id, health_score))
            
            # Sort by health score descending
            rankings.sort(key=lambda x: x[1], reverse=True)
            
            return {
                'ranked_devices': [{'device_id': d[0], 'health_score': d[1]} for d in rankings],
                'top_device': rankings[0][0] if rankings else None
            }
        except Exception as e:
            self.logger.error(f"Error ranking devices: {str(e)}")
            return {}
    
    def _identify_outlier_devices(self, comparison_data: Dict[str, Any]) -> List[str]:
        """Identify outlier devices based on health scores"""
        try:
            if len(comparison_data) < 3:
                return []
            
            scores = [stats.get('health_score', 0) for stats in comparison_data.values()]
            if not scores:
                return []
            
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            
            # Identify outliers (more than 2 standard deviations from mean)
            outliers = []
            for device_id, stats in comparison_data.items():
                score = stats.get('health_score', 0)
                if abs(score - mean_score) > 2 * std_score:
                    outliers.append(device_id)
            
            return outliers
        except Exception as e:
            self.logger.error(f"Error identifying outlier devices: {str(e)}")
            return []
    
    def _analyze_alert_patterns(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Analyze patterns in alerts"""
        try:
            if not alerts:
                return {}
            
            # Group by alert type
            alert_types = defaultdict(list)
            for alert in alerts:
                alert_types[alert.alert_type].append(alert)
            
            patterns = {}
            for alert_type, alert_list in alert_types.items():
                patterns[alert_type] = {
                    'count': len(alert_list),
                    'first_occurrence': alert_list[0].created_at.isoformat(),
                    'last_occurrence': alert_list[-1].created_at.isoformat(),
                    'frequency': len(alert_list) / ((alerts[-1].created_at - alerts[0].created_at).total_seconds() / 3600) if len(alerts) > 1 else 0
                }
            
            return patterns
        except Exception as e:
            self.logger.error(f"Error analyzing alert patterns: {str(e)}")
            return {}
    
    def _get_severity_distribution(self, alerts: List[Alert]) -> Dict[str, int]:
        """Get distribution of alert severities"""
        try:
            severity_counts = defaultdict(int)
            for alert in alerts:
                severity_counts[alert.severity] += 1
            
            return dict(severity_counts)
        except Exception as e:
            self.logger.error(f"Error getting severity distribution: {str(e)}")
            return {}
    
    def _calculate_resolution_times(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Calculate resolution times for alerts"""
        try:
            if not alerts:
                return {}
            
            # For simplicity, assume all alerts were resolved immediately
            # In a real implementation, you'd need resolved_at timestamps
            return {
                'average_resolution_time_hours': 0,
                'total_alerts': len(alerts),
                'resolved_alerts': 0
            }
        except Exception as e:
            self.logger.error(f"Error calculating resolution times: {str(e)}")
            return {}
    
    def _identify_peak_alert_hours(self, alerts: List[Alert]) -> Dict[str, int]:
        """Identify peak alert hours"""
        try:
            hour_counts = defaultdict(int)
            for alert in alerts:
                hour_counts[alert.created_at.hour] += 1
            
            if not hour_counts:
                return {}
            
            # Find peak hour(s)
            max_count = max(hour_counts.values())
            peak_hours = [hour for hour, count in hour_counts.items() if count == max_count]
            
            return {
                'peak_hours': peak_hours,
                'peak_count': max_count
            }
        except Exception as e:
            self.logger.error(f"Error identifying peak alert hours: {str(e)}")
            return {}
