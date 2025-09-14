"""
DriveAhead Configuration Management
Centralized configuration to minimize hardcoding across the application
"""

import os
from datetime import datetime
from typing import Dict, List, Any

class Config:
    """Main configuration class with environment-based settings"""
    
    # Environment Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'driveahead-f1-analytics-2025-secret-key')
    
    # API Configuration
    JOLPICA_API_BASE = os.getenv('JOLPICA_API_BASE', 'http://api.jolpi.ca/ergast/f1')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))
    API_CACHE_TTL = int(os.getenv('API_CACHE_TTL', '300'))  # 5 minutes
    API_RETRY_ATTEMPTS = int(os.getenv('API_RETRY_ATTEMPTS', '3'))
    API_RETRY_DELAY = float(os.getenv('API_RETRY_DELAY', '1.0'))
    
    # Performance Configuration
    DATA_REFRESH_INTERVAL = int(os.getenv('DATA_REFRESH_INTERVAL', '30000'))  # 30 seconds
    LOADING_TIMEOUT = int(os.getenv('LOADING_TIMEOUT', '5000'))  # 5 seconds
    CHART_ANIMATION_DURATION = int(os.getenv('CHART_ANIMATION_DURATION', '1000'))  # 1 second
    
    # Current Season Configuration
    CURRENT_SEASON = int(os.getenv('CURRENT_SEASON', str(datetime.now().year)))
    SEASON_START_MONTH = int(os.getenv('SEASON_START_MONTH', '3'))  # March
    SEASON_END_MONTH = int(os.getenv('SEASON_END_MONTH', '12'))  # December
    
    @staticmethod
    def get_current_season():
        """Determine current F1 season based on date"""
        current_date = datetime.now()
        year = current_date.year
        
        # If before season start, use previous year
        if current_date.month < Config.SEASON_START_MONTH:
            year -= 1
        
        return year

class APIEndpoints:
    """Centralized API endpoint configuration"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or Config.JOLPICA_API_BASE
    
    def season_races(self, season: str = "current") -> str:
        return f"{self.base_url}/{season}.json"
    
    def driver_standings(self, season: str = "current") -> str:
        return f"{self.base_url}/{season}/driverStandings.json"
    
    def constructor_standings(self, season: str = "current") -> str:
        return f"{self.base_url}/{season}/constructorStandings.json"
    
    def race_results(self, season: str = "current", round_num: str = "last") -> str:
        return f"{self.base_url}/{season}/{round_num}/results.json"
    
    def qualifying_results(self, season: str = "current", round_num: str = "last") -> str:
        return f"{self.base_url}/{season}/{round_num}/qualifying.json"
    
    def drivers(self, season: str = "current") -> str:
        return f"{self.base_url}/{season}/drivers.json"
    
    def constructors(self, season: str = "current") -> str:
        return f"{self.base_url}/{season}/constructors.json"

class FallbackData:
    """Centralized fallback data configuration"""
    
    RACE_SCHEDULE = [
        {
            "round": 17,
            "name": "Qatar Airways Azerbaijan Grand Prix",
            "circuit": "Baku City Circuit",
            "country": "Azerbaijan",
            "date": "2025-09-21",
            "race_time_ist": "17:00"
        },
        {
            "round": 18,
            "name": "Singapore Grand Prix",
            "circuit": "Marina Bay Street Circuit",
            "country": "Singapore",
            "date": "2025-10-05",
            "race_time_ist": "17:30"
        },
        {
            "round": 19,
            "name": "United States Grand Prix",
            "circuit": "Circuit of the Americas",
            "country": "United States",
            "date": "2025-10-19",
            "race_time_ist": "01:00"
        },
        {
            "round": 20,
            "name": "Mexican Grand Prix",
            "circuit": "Autódromo Hermanos Rodríguez",
            "country": "Mexico",
            "date": "2025-10-26",
            "race_time_ist": "01:30"
        },
        {
            "round": 21,
            "name": "Brazilian Grand Prix",
            "circuit": "Interlagos",
            "country": "Brazil",
            "date": "2025-11-02",
            "race_time_ist": "19:30"
        },
        {
            "round": 22,
            "name": "Las Vegas Grand Prix",
            "circuit": "Las Vegas Street Circuit",
            "country": "United States",
            "date": "2025-11-23",
            "race_time_ist": "08:30"
        },
        {
            "round": 23,
            "name": "Qatar Grand Prix",
            "circuit": "Losail International Circuit",
            "country": "Qatar",
            "date": "2025-11-30",
            "race_time_ist": "19:30"
        },
        {
            "round": 24,
            "name": "Abu Dhabi Grand Prix",
            "circuit": "Yas Marina Circuit",
            "country": "United Arab Emirates",
            "date": "2025-12-07",
            "race_time_ist": "20:30"
        }
    ]
    
    CONSTRUCTOR_STANDINGS = [
        {"position": 1, "team": "McLaren", "points": 640},
        {"position": 2, "team": "Ferrari", "points": 619},
        {"position": 3, "team": "Red Bull Racing", "points": 581},
        {"position": 4, "team": "Mercedes", "points": 468},
        {"position": 5, "team": "Aston Martin", "points": 86},
        {"position": 6, "team": "Alpine", "points": 59},
        {"position": 7, "team": "Haas", "points": 58},
        {"position": 8, "team": "RB", "points": 46},
        {"position": 9, "team": "Williams", "points": 17},
        {"position": 10, "team": "Kick Sauber", "points": 4}
    ]
    
    DRIVER_STANDINGS = [
        {"position": 1, "driver": "Lando Norris", "team": "McLaren", "points": 374},
        {"position": 2, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 362},
        {"position": 3, "driver": "Charles Leclerc", "team": "Ferrari", "points": 356},
        {"position": 4, "driver": "Oscar Piastri", "team": "McLaren", "points": 266},
        {"position": 5, "driver": "Carlos Sainz", "team": "Ferrari", "points": 263},
        {"position": 6, "driver": "George Russell", "team": "Mercedes", "points": 245},
        {"position": 7, "driver": "Lewis Hamilton", "team": "Mercedes", "points": 223},
        {"position": 8, "driver": "Sergio Perez", "team": "Red Bull Racing", "points": 219},
        {"position": 9, "driver": "Fernando Alonso", "team": "Aston Martin", "points": 70},
        {"position": 10, "driver": "Nico Hulkenberg", "team": "Haas", "points": 37}
    ]
    
    CHAMPIONSHIP_INSIGHTS = {
        "leader": "McLaren",
        "pointsGap": 337,
        "titleFight": "Clear Leader",
        "trend": "Rising"
    }
    
    MODEL_PERFORMANCE = {
        "accuracy": 89.2,
        "precision": 91.5,
        "recall": 87.3,
        "f1_score": 89.3,
        "total_predictions": 1247,
        "correct_predictions": 1112
    }

class UIConstants:
    """UI and styling constants"""
    
    # Timing Constants (in milliseconds)
    LOADING_DELAYS = {
        'critical_data': 0,
        'race_winner_prediction': 500,
        'race_schedule': 800,
        'dashboard_predictions': 1000,
        'mini_predictions': 1200,
        'constructor_championship': 1500,
        'model_performance': 2000,
        'live_f1_data': 2500,
        'real_time_insights': 3000,
        'completed_races': 3500
    }
    
    CHAMPIONSHIP_UPDATE_INTERVALS = {
        'immediate': 0,
        'fallback_primary': 2000,
        'fallback_secondary': 4000
    }
    
    # Chart Configuration
    CHART_COLORS = {
        'primary': '#dc143c',
        'secondary': '#ffffff',
        'accent': '#ff6b6b',
        'background': 'rgba(220, 20, 60, 0.1)',
        'grid': 'rgba(255, 255, 255, 0.1)',
        'text': '#888888'
    }
    
    TEAM_COLORS = {
        'McLaren': '#ff8000',
        'Ferrari': '#dc143c',
        'Red Bull Racing': '#0600ef',
        'Mercedes': '#00d2be',
        'Aston Martin': '#006f62',
        'Alpine': '#0090ff',
        'Haas': '#ffffff',
        'RB': '#6692ff',
        'Williams': '#005aff',
        'Kick Sauber': '#52c41a'
    }
    
    # Container and Layout
    CONTAINER_CONFIG = {
        'max_width': '1400px',
        'mobile_padding': '20px',
        'insights_grid_gap': '40px'
    }
    
    # Animation and Transitions
    ANIMATION_CONFIG = {
        'chart_duration': 1000,
        'fade_duration': 300,
        'slide_duration': 500
    }

class MessageTemplates:
    """Centralized message templates"""
    
    LOADING_MESSAGES = {
        'driver_standings': 'Loading driver standings...',
        'constructor_standings': 'Loading constructor standings...',
        'race_results': 'Loading race results...',
        'predictions': 'Loading predictions...',
        'telemetry': 'Loading telemetry data...',
        'championship_insights': 'Loading championship insights...'
    }
    
    ERROR_MESSAGES = {
        'api_unavailable': 'Unable to load data. Please try again later.',
        'network_error': 'Network error. Check your connection.',
        'data_format_error': 'Invalid data format received.',
        'timeout_error': 'Request timed out. Please try again.',
        'generic_error': 'An error occurred. Please refresh the page.'
    }
    
    SUCCESS_MESSAGES = {
        'data_loaded': 'Data loaded successfully',
        'standings_updated': 'Standings updated',
        'predictions_loaded': 'Predictions loaded'
    }

class EnvironmentConfig:
    """Environment-specific configuration"""
    
    @staticmethod
    def get_config():
        """Get configuration based on environment"""
        env = Config.FLASK_ENV
        
        if env == 'production':
            return ProductionConfig()
        elif env == 'testing':
            return TestingConfig()
        else:
            return DevelopmentConfig()

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    API_CACHE_TTL = 60  # Shorter cache for development
    DATA_REFRESH_INTERVAL = 10000  # More frequent updates

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    API_CACHE_TTL = 600  # Longer cache for production
    DATA_REFRESH_INTERVAL = 60000  # Less frequent updates

class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    API_CACHE_TTL = 1  # Minimal cache for testing
    DATA_REFRESH_INTERVAL = 1000  # Very frequent updates for testing

# Global configuration instances
api_endpoints = APIEndpoints()
fallback_data = FallbackData()
ui_constants = UIConstants()
message_templates = MessageTemplates()

# Export commonly used configurations
__all__ = [
    'Config',
    'APIEndpoints', 
    'FallbackData',
    'UIConstants',
    'MessageTemplates',
    'EnvironmentConfig',
    'api_endpoints',
    'fallback_data',
    'ui_constants',
    'message_templates'
]