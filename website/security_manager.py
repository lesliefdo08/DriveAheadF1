"""
Security Hardening Module for DriveAhead F1 Analytics
Implements comprehensive security features including rate limiting, input sanitization,
CSRF protection, secure headers, and API authentication
"""

import time
import hashlib
import hmac
import secrets
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from collections import defaultdict, deque
from flask import request, jsonify, session, g, abort
from werkzeug.security import safe_str_cmp
import ipaddress
import json
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for different endpoints"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ADMIN = "admin"

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_requests: int
    window_seconds: int
    burst_allowance: int = 0

class AdvancedRateLimiter:
    """
    Advanced rate limiter with sliding window, burst allowance, and IP-based tracking
    """
    
    def __init__(self):
        # Default rate limits for different endpoint types
        self.rate_limits = {
            'api': RateLimitConfig(max_requests=100, window_seconds=60, burst_allowance=20),
            'predictions': RateLimitConfig(max_requests=30, window_seconds=60, burst_allowance=10),
            'telemetry': RateLimitConfig(max_requests=50, window_seconds=60, burst_allowance=15),
            'admin': RateLimitConfig(max_requests=10, window_seconds=60, burst_allowance=2)
        }
        
        # Track requests per IP
        self.request_tracking = defaultdict(lambda: deque())
        self.burst_tracking = defaultdict(int)
        self.blocked_ips = {}
        
        # Suspicious activity tracking
        self.suspicious_activity = defaultdict(int)
        
    def _get_client_identifier(self) -> str:
        """Get unique client identifier"""
        # Try to get real IP from headers (for proxy/load balancer scenarios)
        real_ip = request.headers.get('X-Real-IP') or \
                 request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or \
                 request.remote_addr
        
        # Add user agent as additional identifier to prevent easy bypassing
        user_agent_hash = hashlib.md5(
            request.headers.get('User-Agent', '').encode()
        ).hexdigest()[:8]
        
        return f"{real_ip}:{user_agent_hash}"
    
    def _is_ip_blocked(self, client_id: str) -> bool:
        """Check if IP is temporarily blocked"""
        ip = client_id.split(':')[0]
        if ip in self.blocked_ips:
            if time.time() > self.blocked_ips[ip]:
                # Block expired, remove it
                del self.blocked_ips[ip]
                return False
            return True
        return False
    
    def _block_ip(self, client_id: str, duration_minutes: int = 15):
        """Temporarily block an IP address"""
        ip = client_id.split(':')[0]
        self.blocked_ips[ip] = time.time() + (duration_minutes * 60)
        logger.warning(f"IP {ip} blocked for {duration_minutes} minutes due to rate limit violations")
    
    def is_allowed(self, endpoint_type: str = 'api') -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limits
        Returns: (is_allowed, rate_limit_info)
        """
        client_id = self._get_client_identifier()
        
        # Check if IP is blocked
        if self._is_ip_blocked(client_id):
            return False, {
                'error': 'IP temporarily blocked',
                'retry_after': int(self.blocked_ips[client_id.split(':')[0]] - time.time()),
                'reason': 'Rate limit violations'
            }
        
        config = self.rate_limits.get(endpoint_type, self.rate_limits['api'])
        current_time = time.time()
        
        # Clean old requests (sliding window)
        cutoff_time = current_time - config.window_seconds
        client_requests = self.request_tracking[client_id]
        
        while client_requests and client_requests[0] <= cutoff_time:
            client_requests.popleft()
        
        # Check rate limit
        requests_in_window = len(client_requests)
        remaining_requests = config.max_requests - requests_in_window
        
        # Check burst allowance
        burst_used = self.burst_tracking[client_id]
        total_allowed = config.max_requests + config.burst_allowance
        
        if requests_in_window >= total_allowed:
            # Exceeded limits, track suspicious activity
            self.suspicious_activity[client_id] += 1
            
            # Block IP if too many violations
            if self.suspicious_activity[client_id] >= 5:
                self._block_ip(client_id, duration_minutes=30)
                return False, {
                    'error': 'IP blocked due to repeated violations',
                    'retry_after': 1800  # 30 minutes
                }
            
            return False, {
                'error': 'Rate limit exceeded',
                'limit': config.max_requests,
                'window_seconds': config.window_seconds,
                'retry_after': int(config.window_seconds - (current_time - client_requests[0])) if client_requests else config.window_seconds,
                'requests_made': requests_in_window
            }
        
        # Allow request and track it
        client_requests.append(current_time)
        
        # Update burst tracking
        if requests_in_window > config.max_requests:
            self.burst_tracking[client_id] += 1
        
        return True, {
            'limit': config.max_requests,
            'remaining': max(0, remaining_requests),
            'reset_time': int(current_time + config.window_seconds),
            'burst_remaining': max(0, config.burst_allowance - burst_used)
        }
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics for monitoring"""
        current_time = time.time()
        active_clients = len([
            client for client, requests in self.request_tracking.items()
            if requests and requests[-1] > (current_time - 300)  # Active in last 5 minutes
        ])
        
        blocked_ips = len([
            ip for ip, blocked_until in self.blocked_ips.items()
            if blocked_until > current_time
        ])
        
        return {
            'active_clients_5min': active_clients,
            'blocked_ips': blocked_ips,
            'total_clients_tracked': len(self.request_tracking),
            'suspicious_activity_instances': len(self.suspicious_activity),
            'rate_limit_violations': sum(self.suspicious_activity.values())
        }

class InputValidator:
    """
    Advanced input validation and sanitization
    """
    
    def __init__(self):
        # Regex patterns for validation
        self.patterns = {
            'driver_name': re.compile(r'^[a-zA-Z\s\-\.]{1,50}$'),
            'team_name': re.compile(r'^[a-zA-Z0-9\s\-\.]{1,50}$'),
            'circuit_name': re.compile(r'^[a-zA-Z0-9\s\-\.]{1,100}$'),
            'season': re.compile(r'^(19|20)\d{2}$'),
            'round_number': re.compile(r'^[1-9]\d{0,1}$'),  # 1-99
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'alphanumeric': re.compile(r'^[a-zA-Z0-9]+$')
        }
        
        # Dangerous patterns to block
        self.dangerous_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'(union|select|drop|delete|insert|update)\s+', re.IGNORECASE),
            re.compile(r'[<>"\']', re.IGNORECASE)  # Basic XSS prevention
        ]
    
    def validate_f1_data(self, data_type: str, value: Any) -> tuple[bool, str]:
        """
        Validate F1-specific data inputs
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Check for dangerous patterns first
        for pattern in self.dangerous_patterns:
            if pattern.search(value):
                return False, f"Invalid characters detected in {data_type}"
        
        # Type-specific validation
        if data_type in self.patterns:
            if not self.patterns[data_type].match(value):
                return False, f"Invalid {data_type} format"
        
        # Additional validation for specific types
        if data_type == 'season':
            try:
                year = int(value)
                if year < 1950 or year > datetime.now().year + 1:
                    return False, "Invalid season year"
            except ValueError:
                return False, "Season must be a valid year"
        
        return True, "Valid"
    
    def sanitize_input(self, value: str) -> str:
        """
        Sanitize input by removing/escaping dangerous characters
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove HTML tags
        value = re.sub(r'<[^>]+>', '', value)
        
        # Escape special characters
        value = value.replace('<', '&lt;').replace('>', '&gt;')
        value = value.replace('"', '&quot;').replace("'", '&#x27;')
        
        # Remove null bytes and control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in ['\n', '\t'])
        
        return value.strip()

class CSRFProtection:
    """
    CSRF protection implementation
    """
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
    
    def generate_token(self) -> str:
        """Generate CSRF token"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_urlsafe(32)
        
        # Create signature
        message = f"{timestamp}:{random_part}".encode()
        signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        
        token = f"{timestamp}:{random_part}:{signature}"
        return token
    
    def validate_token(self, token: str, max_age: int = 3600) -> bool:
        """Validate CSRF token"""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            timestamp, random_part, signature = parts
            
            # Check age
            token_time = int(timestamp)
            if time.time() - token_time > max_age:
                return False
            
            # Verify signature
            message = f"{timestamp}:{random_part}".encode()
            expected_signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        except (ValueError, TypeError):
            return False

class APIKeyAuth:
    """
    API key authentication system
    """
    
    def __init__(self):
        # In production, these would come from a secure database
        self.api_keys = {
            # Generate with: secrets.token_urlsafe(32)
            'driveahead_admin_key': {
                'name': 'Admin Access',
                'level': SecurityLevel.ADMIN,
                'rate_limit': 'admin',
                'created': datetime.now(),
                'last_used': None
            },
            'driveahead_app_key': {
                'name': 'Application Access',
                'level': SecurityLevel.AUTHENTICATED,
                'rate_limit': 'api',
                'created': datetime.now(),
                'last_used': None
            }
        }
    
    def validate_api_key(self, api_key: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Validate API key and return key info"""
        if not api_key:
            return False, None
        
        key_info = self.api_keys.get(api_key)
        if not key_info:
            return False, None
        
        # Update last used
        key_info['last_used'] = datetime.now()
        
        return True, key_info

class SecurityManager:
    """
    Main security manager that coordinates all security features
    """
    
    def __init__(self, app_secret_key: str):
        self.rate_limiter = AdvancedRateLimiter()
        self.input_validator = InputValidator()
        self.csrf_protection = CSRFProtection(app_secret_key)
        self.api_auth = APIKeyAuth()
        
        # Security headers configuration
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
    
    def apply_security_headers(self, response):
        """Apply security headers to response"""
        for header, value in self.security_headers.items():
            response.headers[header] = value
        return response
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'rate_limiting': self.rate_limiter.get_security_stats(),
            'api_keys': {
                'total_keys': len(self.api_auth.api_keys),
                'active_keys': len([
                    k for k in self.api_auth.api_keys.values()
                    if k['last_used'] and k['last_used'] > (datetime.now() - timedelta(days=7))
                ])
            },
            'security_level': 'enhanced',
            'features_enabled': [
                'rate_limiting',
                'input_validation', 
                'csrf_protection',
                'api_key_auth',
                'security_headers',
                'xss_protection',
                'sql_injection_protection'
            ]
        }

# Initialize global security manager
security_manager = None

def init_security_manager(app_secret_key: str):
    """Initialize security manager"""
    global security_manager
    security_manager = SecurityManager(app_secret_key)
    logger.info("✅ Security manager initialized")

# Decorators for easy security implementation
def rate_limit(endpoint_type: str = 'api'):
    """Rate limiting decorator"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if security_manager:
                is_allowed, rate_info = security_manager.rate_limiter.is_allowed(endpoint_type)
                if not is_allowed:
                    response = jsonify({
                        'error': 'Rate limit exceeded',
                        'rate_limit_info': rate_info
                    })
                    response.status_code = 429
                    response.headers['Retry-After'] = str(rate_info.get('retry_after', 60))
                    return response
                
                # Add rate limit headers
                response = func(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(rate_info.get('limit', 0))
                    response.headers['X-RateLimit-Remaining'] = str(rate_info.get('remaining', 0))
                    response.headers['X-RateLimit-Reset'] = str(rate_info.get('reset_time', 0))
                return response
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_api_key(required_level: SecurityLevel = SecurityLevel.AUTHENTICATED):
    """API key authentication decorator"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if security_manager:
                api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
                
                is_valid, key_info = security_manager.api_auth.validate_api_key(api_key)
                if not is_valid:
                    return jsonify({
                        'error': 'Invalid or missing API key',
                        'message': 'Please provide a valid API key in the X-API-Key header'
                    }), 401
                
                # Check authorization level
                if key_info['level'] != SecurityLevel.ADMIN and required_level == SecurityLevel.ADMIN:
                    return jsonify({
                        'error': 'Insufficient privileges',
                        'required_level': required_level.value,
                        'current_level': key_info['level'].value
                    }), 403
                
                # Store key info in request context
                g.api_key_info = key_info
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_input(**validators):
    """Input validation decorator"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if security_manager:
                # Validate request parameters
                for param_name, data_type in validators.items():
                    value = request.args.get(param_name) or request.json.get(param_name) if request.is_json else None
                    
                    if value:
                        is_valid, message = security_manager.input_validator.validate_f1_data(data_type, value)
                        if not is_valid:
                            return jsonify({
                                'error': 'Invalid input',
                                'parameter': param_name,
                                'message': message
                            }), 400
                        
                        # Sanitize the input
                        sanitized_value = security_manager.input_validator.sanitize_input(str(value))
                        
                        # Update the request data with sanitized value
                        if request.args.get(param_name):
                            # For URL parameters, we can't modify request.args directly
                            # Store sanitized values in g for access in the function
                            if not hasattr(g, 'sanitized_params'):
                                g.sanitized_params = {}
                            g.sanitized_params[param_name] = sanitized_value
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def register_security_handlers(app):
    """Register security-related Flask handlers"""
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        if security_manager:
            return security_manager.apply_security_headers(response)
        return response
    
    @app.before_request
    def security_check():
        """Perform security checks before each request"""
        # Log suspicious requests
        if request.path.startswith('/api/admin') or 'script' in request.path.lower():
            logger.warning(f"Suspicious request: {request.method} {request.path} from {request.remote_addr}")
    
    logger.info("✅ Security handlers registered")