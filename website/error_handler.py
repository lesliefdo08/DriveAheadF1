"""
Enhanced Error Handling and Resilience System for DriveAhead
Provides comprehensive error handling, graceful degradation, and user-friendly error responses
"""

import logging
import traceback
import functools
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from flask import jsonify, render_template, request
from dataclasses import dataclass
from enum import Enum
import json

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error category classification"""
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    AUTHENTICATION_ERROR = "auth_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    ML_MODEL_ERROR = "ml_model_error"
    CACHE_ERROR = "cache_error"

@dataclass
class ErrorDetails:
    """Structured error information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: Dict[str, Any]
    timestamp: datetime
    request_info: Dict[str, Any]
    suggested_actions: List[str]
    
class ErrorTracker:
    """Track and analyze error patterns"""
    
    def __init__(self, max_errors: int = 1000):
        self.max_errors = max_errors
        self.errors = []
        self.error_counts = {}
        self.error_patterns = {}
        
    def record_error(self, error: ErrorDetails):
        """Record an error for analysis"""
        self.errors.append(error)
        
        # Maintain size limit
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]
        
        # Update error counts
        error_key = f"{error.category.value}:{error.severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Analyze patterns (simplified)
        hour = error.timestamp.hour
        pattern_key = f"{error.category.value}:hour_{hour}"
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors if e.timestamp > cutoff_time]
        
        category_counts = {}
        severity_counts = {}
        
        for error in recent_errors:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "most_common_patterns": dict(sorted(self.error_patterns.items(), 
                                               key=lambda x: x[1], 
                                               reverse=True)[:5]),
            "timeframe_hours": hours
        }

class GracefulDegradationManager:
    """Manage graceful service degradation during errors"""
    
    def __init__(self):
        self.service_states = {
            "api_requests": True,
            "ml_predictions": True,
            "cache_system": True,
            "telemetry_data": True,
            "live_updates": True
        }
        self.degradation_levels = {
            "full": 0,    # All features available
            "limited": 1, # Some features disabled
            "minimal": 2, # Only essential features
            "offline": 3  # Fallback mode only
        }
        self.current_level = 0
        
    def assess_degradation_level(self, error_summary: Dict[str, Any]) -> int:
        """Assess required degradation level based on error patterns"""
        total_errors = error_summary.get("total_errors", 0)
        critical_errors = error_summary.get("by_severity", {}).get("critical", 0)
        
        if critical_errors > 5 or total_errors > 50:
            return self.degradation_levels["offline"]
        elif critical_errors > 2 or total_errors > 20:
            return self.degradation_levels["minimal"]
        elif total_errors > 10:
            return self.degradation_levels["limited"]
        else:
            return self.degradation_levels["full"]
    
    def get_available_features(self) -> Dict[str, bool]:
        """Get list of currently available features"""
        if self.current_level == 0:  # Full
            return {k: True for k in self.service_states.keys()}
        elif self.current_level == 1:  # Limited
            return {
                "api_requests": True,
                "ml_predictions": False,
                "cache_system": True,
                "telemetry_data": True,
                "live_updates": False
            }
        elif self.current_level == 2:  # Minimal
            return {
                "api_requests": True,
                "ml_predictions": False,
                "cache_system": False,
                "telemetry_data": False,
                "live_updates": False
            }
        else:  # Offline
            return {k: False for k in self.service_states.keys()}

class EnhancedErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self):
        self.error_tracker = ErrorTracker()
        self.degradation_manager = GracefulDegradationManager()
        self.fallback_responses = self._initialize_fallbacks()
        
    def _initialize_fallbacks(self) -> Dict[str, Any]:
        """Initialize fallback responses for different error scenarios"""
        return {
            "race_predictions": {
                "predictions": [
                    {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "probability": 0.65},
                    {"position": 2, "driver": "Charles Leclerc", "team": "Ferrari", "probability": 0.58},
                    {"position": 3, "driver": "Lando Norris", "team": "McLaren", "probability": 0.52}
                ],
                "note": "Fallback predictions - live data unavailable"
            },
            "race_calendar": [
                {
                    "round": "23",
                    "raceName": "Abu Dhabi Grand Prix",
                    "date": "2025-12-07",
                    "Circuit": {
                        "circuitName": "Yas Marina Circuit",
                        "Location": {
                            "locality": "Abu Dhabi",
                            "country": "UAE"
                        }
                    }
                }
            ],
            "driver_standings": [
                {"position": "1", "Driver": {"givenName": "Max", "familyName": "Verstappen"}, 
                 "Constructors": [{"name": "Red Bull Racing"}], "points": "575"},
                {"position": "2", "Driver": {"givenName": "Charles", "familyName": "Leclerc"}, 
                 "Constructors": [{"name": "Ferrari"}], "points": "456"}
            ]
        }
    
    def handle_api_error(self, error: Exception, endpoint: str, fallback_key: Optional[str] = None) -> tuple:
        """Handle API-related errors with appropriate fallbacks"""
        error_details = ErrorDetails(
            error_id=f"api_error_{int(time.time())}",
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message=str(error),
            user_message="Service temporarily unavailable. Using cached data.",
            technical_details={
                "endpoint": endpoint,
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc()
            },
            timestamp=datetime.now(),
            request_info={
                "endpoint": request.endpoint if request else "unknown",
                "method": request.method if request else "unknown",
                "user_agent": request.headers.get('User-Agent', 'unknown') if request else "unknown"
            },
            suggested_actions=[
                "Check API service status",
                "Verify network connectivity",
                "Try again in a few minutes"
            ]
        )
        
        self.error_tracker.record_error(error_details)
        logger.error(f"API Error [{error_details.error_id}]: {error_details.message}")
        
        # Return fallback data if available
        if fallback_key and fallback_key in self.fallback_responses:
            return jsonify({
                "status": "degraded",
                "data": self.fallback_responses[fallback_key],
                "message": "Using fallback data due to service issues",
                "error_id": error_details.error_id
            }), 206  # Partial Content
        
        return jsonify({
            "status": "error",
            "message": error_details.user_message,
            "error_id": error_details.error_id
        }), 503  # Service Unavailable
    
    def handle_ml_model_error(self, error: Exception, model_operation: str) -> tuple:
        """Handle ML model-related errors"""
        error_details = ErrorDetails(
            error_id=f"ml_error_{int(time.time())}",
            category=ErrorCategory.ML_MODEL_ERROR,
            severity=ErrorSeverity.HIGH,
            message=str(error),
            user_message="Prediction service temporarily unavailable. Using historical data.",
            technical_details={
                "operation": model_operation,
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc()
            },
            timestamp=datetime.now(),
            request_info={
                "endpoint": request.endpoint if request else "unknown",
                "method": request.method if request else "unknown"
            },
            suggested_actions=[
                "Check ML model status",
                "Verify model file integrity",
                "Restart ML prediction service"
            ]
        )
        
        self.error_tracker.record_error(error_details)
        logger.error(f"ML Model Error [{error_details.error_id}]: {error_details.message}")
        
        return jsonify({
            "status": "degraded",
            "data": self.fallback_responses.get("race_predictions", {}),
            "message": "Using fallback predictions due to model issues",
            "error_id": error_details.error_id
        }), 206
    
    def handle_validation_error(self, error: Exception, input_data: Any) -> tuple:
        """Handle input validation errors"""
        error_details = ErrorDetails(
            error_id=f"validation_error_{int(time.time())}",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.LOW,
            message=str(error),
            user_message="Invalid input provided. Please check your request.",
            technical_details={
                "input_data": str(input_data),
                "error_type": type(error).__name__
            },
            timestamp=datetime.now(),
            request_info={
                "endpoint": request.endpoint if request else "unknown",
                "method": request.method if request else "unknown"
            },
            suggested_actions=[
                "Verify input format",
                "Check API documentation",
                "Contact support if issue persists"
            ]
        )
        
        self.error_tracker.record_error(error_details)
        logger.warning(f"Validation Error [{error_details.error_id}]: {error_details.message}")
        
        return jsonify({
            "status": "error",
            "message": error_details.user_message,
            "error_id": error_details.error_id,
            "details": "Please check your input and try again"
        }), 400  # Bad Request
    
    def get_error_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive error data for monitoring dashboard"""
        error_summary_24h = self.error_tracker.get_error_summary(24)
        error_summary_1h = self.error_tracker.get_error_summary(1)
        
        degradation_level = self.degradation_manager.assess_degradation_level(error_summary_24h)
        available_features = self.degradation_manager.get_available_features()
        
        return {
            "current_status": {
                "degradation_level": degradation_level,
                "available_features": available_features,
                "last_updated": datetime.now().isoformat()
            },
            "error_summary": {
                "last_24_hours": error_summary_24h,
                "last_hour": error_summary_1h
            },
            "system_health": {
                "overall_health": "good" if degradation_level == 0 else 
                                 "degraded" if degradation_level < 3 else "critical",
                "critical_errors_24h": error_summary_24h.get("by_severity", {}).get("critical", 0),
                "total_errors_24h": error_summary_24h.get("total_errors", 0)
            }
        }

# Decorators for automatic error handling
def handle_api_errors(fallback_key: Optional[str] = None):
    """Decorator to automatically handle API errors"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_api_error(e, func.__name__, fallback_key)
        return wrapper
    return decorator

def handle_ml_errors(model_operation: str):
    """Decorator to automatically handle ML model errors"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_ml_model_error(e, model_operation)
        return wrapper
    return decorator

def handle_validation_errors():
    """Decorator to automatically handle validation errors"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ValueError, TypeError, KeyError) as e:
                return error_handler.handle_validation_error(e, kwargs.get('input_data', args))
            except Exception as e:
                # Re-raise non-validation errors
                raise e
        return wrapper
    return decorator

# Global error handler instance
error_handler = EnhancedErrorHandler()

def register_error_handlers(app):
    """Register Flask error handlers"""
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        if request.path.startswith('/api/'):
            return jsonify({
                "status": "error",
                "message": "API endpoint not found",
                "error_code": 404,
                "available_endpoints": [
                    "/api/race-calendar",
                    "/api/predictions", 
                    "/api/standings",
                    "/api/system-performance"
                ]
            }), 404
        else:
            return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        error_details = ErrorDetails(
            error_id=f"server_error_{int(time.time())}",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.CRITICAL,
            message=str(error),
            user_message="Internal server error occurred",
            technical_details={"traceback": traceback.format_exc()},
            timestamp=datetime.now(),
            request_info={
                "endpoint": request.endpoint,
                "method": request.method
            },
            suggested_actions=["Contact system administrator"]
        )
        
        error_handler.error_tracker.record_error(error_details)
        
        if request.path.startswith('/api/'):
            return jsonify({
                "status": "error",
                "message": "Internal server error",
                "error_id": error_details.error_id
            }), 500
        else:
            return render_template('500.html', error_id=error_details.error_id), 500
    
    @app.errorhandler(503)
    def handle_service_unavailable(error):
        """Handle 503 errors"""
        return jsonify({
            "status": "service_unavailable",
            "message": "Service temporarily unavailable",
            "retry_after": 60,
            "fallback_available": True
        }), 503