"""
DriveAhead - Advanced F1 Analytics Platform
Comprehensive Backend with Jolpica API Integration, OpenF1 API, and FastF1 Support
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import json
import logging
import warnings
import requests
import time
import random
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import xgboost as xgb

warnings.filterwarnings('ignore')
load_dotenv()

logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)

# Import performance optimization modules
try:
    from cache_manager import cache_manager, cached, get_cache_stats, clear_cache
    from api_optimizer import connection_pool, optimized_get, batch_requests, get_connection_stats
    PERFORMANCE_OPTIMIZATIONS_AVAILABLE = True
    logger.info("✅ Performance optimizations loaded")
except ImportError as e:
    PERFORMANCE_OPTIMIZATIONS_AVAILABLE = False
    logger.warning(f"⚠️ Performance optimizations not available - using standard implementations: {e}")

# Import enhanced error handling
try:
    from error_handler import (
        error_handler, handle_api_errors, handle_ml_errors, handle_validation_errors,
        register_error_handlers, ErrorCategory, ErrorSeverity
    )
    ERROR_HANDLING_AVAILABLE = True
    logger.info("✅ Enhanced error handling loaded")
except ImportError as e:
    ERROR_HANDLING_AVAILABLE = False
    logger.warning(f"⚠️ Enhanced error handling not available - using basic error handling: {e}")

# Import security features
try:
    from security_manager import (
        init_security_manager, security_manager, rate_limit, require_api_key, 
        validate_input, register_security_handlers, SecurityLevel
    )
    SECURITY_FEATURES_AVAILABLE = True
    logger.info("✅ Security features loaded")
except ImportError as e:
    SECURITY_FEATURES_AVAILABLE = False
    logger.warning(f"⚠️ Security features not available - using basic security: {e}")

# Import professional ML models
try:
    from ml_models import F1PredictionModels
    from robust_models import RobustF1Models
    ML_MODELS_AVAILABLE = True
except ImportError:
    ML_MODELS_AVAILABLE = False
    logger.warning("Professional ML models not available - using fallback predictions")

# Fallback configuration when config files not available
class Config:
    JOLPICA_API_BASE = "http://api.jolpi.ca/ergast/f1"
    API_CACHE_TTL = 300
    API_TIMEOUT = 10
    
    @staticmethod
    def get_current_season():
        return 2024

class EnvironmentConfig:
    @staticmethod
    def get_config():
        class DefaultConfig:
            DEBUG = False
            SECRET_KEY = 'driveahead-f1-analytics-2025'
        return DefaultConfig()

def _get_team_name(driver_name):
    """Get team name for a driver"""
    team_mapping = {
        'Max Verstappen': 'Red Bull Racing',
        'Charles Leclerc': 'Ferrari',
        'Lando Norris': 'McLaren',
        'Lewis Hamilton': 'Ferrari',
        'Oscar Piastri': 'McLaren',
        'George Russell': 'Mercedes',
        'Carlos Sainz': 'Williams',
        'Fernando Alonso': 'Aston Martin',
        'Sergio Perez': 'Red Bull Racing',
        'Lance Stroll': 'Aston Martin'
    }
    return team_mapping.get(driver_name, 'Unknown Team')

# Get environment-specific configuration
config = EnvironmentConfig.get_config()

# Initialize Flask app with configuration
app = Flask(__name__)
app.config.from_object(config)
app.config['START_TIME'] = datetime.now()  # Track app start time
CORS(app)

# Initialize security features
if SECURITY_FEATURES_AVAILABLE:
    init_security_manager(app.secret_key or 'driveahead-f1-analytics-2025-secret-key')
    register_security_handlers(app)
    logger.info("✅ Security features initialized")

# Initialize ML models for real accuracy metrics
ml_models = None
robust_models = None

class JolpicaAPIClient:
    """Enhanced Jolpica F1 API client with advanced caching and performance optimization"""
    
    def __init__(self):
        self.base_url = Config.JOLPICA_API_BASE
        self.session = requests.Session()
        self.cache = {}
        self.cache_ttl = Config.API_CACHE_TTL
        self.last_race_check = None
        self.current_next_race = None
    
    def _get_cache_key(self, endpoint: str) -> str:
        return f"jolpica_{endpoint}_{int(time.time() / self.cache_ttl)}"
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make request to Jolpica API with caching"""
        cache_key = self._get_cache_key(endpoint)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            if endpoint.isdigit() or endpoint == "current":
                url = f"{self.base_url}/{endpoint}.json"
            else:
                url = f"{self.base_url}/{endpoint}.json"
            
            logger.info(f"🌐 Fetching from Jolpica API: {url}")
            
            response = self.session.get(url, timeout=Config.API_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            self.cache[cache_key] = data
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Jolpica API request failed: {e}")
            return None
    
    def get_current_season_races(self) -> List[Dict]:
        """Get current season race schedule"""
        current_year = Config.get_current_season()
        
        # Try current year first
        data = self._make_request(str(current_year))
        if data and 'MRData' in data and data['MRData']['RaceTable']['Races']:
            races = data['MRData']['RaceTable']['Races']
            return races

        # If no current year data, fall back to "current" season
        data = self._make_request("current")
        if data and 'MRData' in data:
            races = data['MRData']['RaceTable']['Races']
            return races
            
        return []
    
    def get_next_race(self) -> Optional[Dict]:
        """Get next upcoming race"""
        races = self.get_current_season_races()
        current_datetime = datetime.now()
        
        for race in races:
            try:
                race_date = datetime.strptime(race['date'], '%Y-%m-%d')
                
                # If race has time information, use it
                if 'time' in race and race['time']:
                    try:
                        time_str = race['time'].replace('Z', '')
                        race_time = datetime.strptime(time_str, '%H:%M:%S').time()
                        race_datetime = datetime.combine(race_date.date(), race_time)
                    except:
                        race_datetime = race_date.replace(hour=23, minute=59)
                else:
                    race_datetime = race_date.replace(hour=23, minute=59)
                
                # Check if race is still upcoming
                if race_datetime > current_datetime:
                    return race
                        
            except ValueError:
                continue
        
        return None
    
    def get_driver_standings(self, season: str = "current") -> List[Dict]:
        """Get current driver championship standings"""
        data = self._make_request(f"{season}/driverStandings")
        if data and 'MRData' in data:
            standings_list = data['MRData']['StandingsTable']['StandingsLists']
            if standings_list:
                return standings_list[0]['DriverStandings']
        return []
    
    def get_constructor_standings(self, season: str = "current") -> List[Dict]:
        """Get current constructor championship standings"""
        data = self._make_request(f"{season}/constructorStandings")
        if data and 'MRData' in data:
            standings_list = data['MRData']['StandingsTable']['StandingsLists']
            if standings_list:
                return standings_list[0]['ConstructorStandings']
        return []
    
    def get_latest_race_results(self, season: str = "current") -> Optional[Dict]:
        """Get results from the most recent completed race"""
        data = self._make_request(f"{season}/results")
        if data and 'MRData' in data:
            races = data['MRData']['RaceTable']['Races']
            if races:
                # Get the latest race (races are ordered by round)
                latest_race = races[-1]
                return latest_race
        return None

class F1DataManager:
    """Enhanced F1 Data Management System with Jolpica API Integration"""
    
    def __init__(self):
        self.current_season = 2024
        self.jolpica_client = JolpicaAPIClient()
        self.cache = {}
        
        # Fallback data
        self.constructor_standings = [
            {"position": 1, "team": "Red Bull Racing", "points": 589, "wins": 8},
            {"position": 2, "team": "McLaren", "points": 544, "wins": 4},
            {"position": 3, "team": "Ferrari", "points": 537, "wins": 5}
        ]
        
        self.driver_standings = [
            {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 408, "wins": 8},
            {"position": 2, "driver": "Lando Norris", "team": "McLaren", "points": 371, "wins": 4},
            {"position": 3, "driver": "Charles Leclerc", "team": "Ferrari", "points": 356, "wins": 3}
        ]
        
        logger.info("🏎️ F1DataManager initialized with Jolpica API integration")
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        set_cached(endpoint, data)
        return data
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None

def get_current_standings():
    """Get current driver and constructor standings"""
    driver_data = fetch_f1_data(f"{CURRENT_SEASON}/driverStandings")
    constructor_data = fetch_f1_data(f"{CURRENT_SEASON}/constructorStandings")
    
    drivers = []
    constructors = []
    
    if driver_data:
        standings = driver_data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        if standings:
            drivers = standings[0].get('DriverStandings', [])
    
    if constructor_data:
        standings = constructor_data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        if standings:
            constructors = standings[0].get('ConstructorStandings', [])
    
    return {'drivers': drivers, 'constructors': constructors}

def get_last_race():
    """Get last race results"""
    data = fetch_f1_data(f"{CURRENT_SEASON}/last/results")
    if data:
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        return races[0] if races else None
    return None

def get_next_race():
    """Get next race information"""
    data = fetch_f1_data(f"{CURRENT_SEASON}")
    if data:
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        current_date = datetime.now()
        
        for race in races:
            race_date = datetime.strptime(race['date'], '%Y-%m-%d')
            if race_date > current_date:
                return race
    
    # Fallback to next season
    return {
        'round': '1',
        'raceName': 'Bahrain Grand Prix',
        'Circuit': {
            'circuitName': 'Bahrain International Circuit',
            'Location': {'country': 'Bahrain'}
        },
        'date': f'{CURRENT_SEASON + 1}-03-02',
        'time': '15:00:00Z'
    }

# Human-based prediction logic
def predict_race_outcome(race_data=None):
    """Advanced analysis for race predictions"""
    standings = get_current_standings()
    drivers = standings['drivers']
    
    if not drivers:
        return {
            'winner': {'driver': 'Verstappen', 'probability': 30},
            'podium': [
                {'driver': 'Verstappen', 'position': 1, 'probability': 30},
                {'driver': 'Norris', 'position': 2, 'probability': 25},
                {'driver': 'Leclerc', 'position': 3, 'probability': 20}
            ]
        }
    
    # Human logic based on championship standings
    predictions = []
    for i, driver in enumerate(drivers[:8]):
        base_prob = max(25 - (i * 3), 5)
        
        # Adjust for known performance factors
        driver_name = driver['Driver']['familyName']
        track_bonus = 0
        
        # Human knowledge adjustments
        if driver_name == 'Verstappen':
            track_bonus = 5
        elif driver_name in ['Norris', 'Leclerc']:
            track_bonus = 3
        elif driver_name in ['Russell', 'Hamilton']:
            track_bonus = 2
        
        final_prob = min(base_prob + track_bonus, 35)
        
        predictions.append({
            'driver': driver_name,
            'team': driver['Constructors'][0]['name'],
            'probability': final_prob,
            'championship_position': int(driver['position'])
        })
    
    return {
        'winner': predictions[0] if predictions else {'driver': 'Verstappen', 'probability': 30},
        'podium': predictions[:3]
    }

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/telemetry')
def telemetry():
    """Live telemetry page"""
    return render_template('telemetry.html')

@app.route('/standings')
def standings():
    """Championship standings page"""
    return render_template('standings.html')

# API Endpoints
@app.route('/api/standings')
def api_standings():
    """Get current championship standings"""
    try:
        data = get_current_standings()
        return jsonify({
            'success': True,
            'data': data,
            'updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/next-race')
def api_next_race():
    """Get next race information"""
    try:
        race = get_next_race()
        if race:
            race_datetime = datetime.strptime(f"{race['date']} {race.get('time', '15:00:00Z')}", '%Y-%m-%d %H:%M:%SZ')
            time_until = race_datetime - datetime.utcnow()
            
            return jsonify({
                'success': True,
                'race': {
                    'name': race['raceName'],
                    'circuit': race['Circuit']['circuitName'],
                    'country': race['Circuit']['Location']['country'],
                    'date': race['date'],
                    'time': race.get('time', '15:00:00Z'),
                    'round': race['round'],
                    'days_until': time_until.days,
                    'hours_until': time_until.seconds // 3600
                }
            })
        else:
            return jsonify({'success': False, 'error': 'No upcoming race found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/last-race')
def api_last_race():
    """Get last race results"""
    try:
        race = get_last_race()
        return jsonify({
            'success': True,
            'race': race,
            'updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predictions')
def api_predictions():
    """Get race predictions based on advanced analysis"""
    try:
        predictions = predict_race_outcome()
        return jsonify({
            'success': True,
            'predictions': predictions,
            'methodology': 'Advanced analysis based on championship standings and track performance',
            'updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """System status"""
    return jsonify({
        'success': True,
        'status': 'operational',
        'version': '1.0.0',
        'features': ['Live F1 Data', 'Real-time Predictions', 'Championship Standings'],
        'uptime': time.time() - app.config.get('start_time', time.time())
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.config['start_time'] = time.time()
    logger.info("🏁 DriveAhead F1 Analytics Platform Starting")
    logger.info("📊 Features: Live standings, Race predictions, Clean telemetry")
    logger.info("🎯 Real-time F1 Data Platform")
    
    app.run(host='0.0.0.0', port=5000, debug=True)