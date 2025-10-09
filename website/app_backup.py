"""
DriveAhead - Advanced F1 Analytics Platform
Real-time F1 data integration with machine learning predictions
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
import requests
import time
import random
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'driveahead-f1-analytics-2025'
CORS(app)
app.config['START_TIME'] = datetime.now()

class MLPredictionSystem:
    """
    Machine Learning Prediction System for F1 Race Outcomes
    Uses trained Random Forest, XGBoost, and Logistic Regression models
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.model_loaded = False
        
        # Load the latest trained models
        self.load_models()
    
    def load_models(self):
        """Load the trained ML models and preprocessing objects"""
        try:
            # Find the latest model files
            model_dir = '../models'
            if not os.path.exists(model_dir):
                logger.error("Models directory not found")
                return
                
            # Load metadata to get the latest timestamp
            metadata_files = [f for f in os.listdir(model_dir) if f.startswith('ml_metadata_')]
            if not metadata_files:
                logger.error("No model metadata found")
                return
                
            latest_metadata = sorted(metadata_files)[-1]
            
            with open(os.path.join(model_dir, latest_metadata), 'r') as f:
                metadata = json.load(f)
            
            timestamp = metadata['timestamp']
            
            # Load models
            model_files = {
                'random_forest_winner': f'random_forest_winner_{timestamp}.pkl',
                'random_forest_podium': f'random_forest_podium_{timestamp}.pkl',
                'random_forest_position': f'random_forest_position_{timestamp}.pkl',
                'xgboost_winner': f'xgboost_winner_{timestamp}.pkl',
                'xgboost_podium': f'xgboost_podium_{timestamp}.pkl',
                'logistic_regression_winner': f'logistic_regression_winner_{timestamp}.pkl'
            }
            
            for model_name, filename in model_files.items():
                filepath = os.path.join(model_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
            
            # Load scalers and encoders
            scaler_file = os.path.join(model_dir, f'scaler_{timestamp}.pkl')
            encoder_file = os.path.join(model_dir, f'encoders_{timestamp}.pkl')
            
            if os.path.exists(scaler_file):
                with open(scaler_file, 'rb') as f:
                    self.scalers = pickle.load(f)
                    
            if os.path.exists(encoder_file):
                with open(encoder_file, 'rb') as f:
                    self.encoders = pickle.load(f)
            
            self.feature_columns = metadata['feature_columns']
            self.model_loaded = True
            logger.info(f"ML models loaded successfully from timestamp: {timestamp}")
            
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")
            self.model_loaded = False
    
    def prepare_driver_features(self, driver_name, team_name, circuit_name):
        """Prepare features for a specific driver prediction"""
        if not self.model_loaded:
            return None
            
        try:
            # Driver performance mapping based on 2024 season
            driver_skills = {
                'Max Verstappen': 0.95, 'Charles Leclerc': 0.88, 'Lando Norris': 0.85,
                'Oscar Piastri': 0.82, 'George Russell': 0.80, 'Lewis Hamilton': 0.78,
                'Carlos Sainz': 0.76, 'Fernando Alonso': 0.75, 'Sergio Perez': 0.72,
                'Pierre Gasly': 0.68, 'Alexander Albon': 0.65, 'Nico Hulkenberg': 0.62,
                'Esteban Ocon': 0.60, 'Daniel Ricciardo': 0.58, 'Yuki Tsunoda': 0.55,
                'Kevin Magnussen': 0.52, 'Lance Stroll': 0.50, 'Valtteri Bottas': 0.48,
                'Logan Sargeant': 0.45, 'Zhou Guanyu': 0.42
            }
            
            team_performance = {
                'Red Bull Racing': 0.92, 'McLaren': 0.88, 'Ferrari': 0.85,
                'Mercedes': 0.75, 'Aston Martin': 0.65, 'RB': 0.55,
                'Alpine': 0.52, 'Williams': 0.48, 'Haas': 0.45, 'Sauber': 0.40
            }
            
            # Encode categorical variables
            try:
                driver_encoded = self.encoders['driver'].transform([driver_name])[0] if driver_name in self.encoders['driver'].classes_ else 0
                team_encoded = self.encoders['team'].transform([team_name])[0] if team_name in self.encoders['team'].classes_ else 0
                circuit_encoded = self.encoders['circuit'].transform([circuit_name])[0] if circuit_name in self.encoders['circuit'].classes_ else 0
            except:
                driver_encoded = 0
                team_encoded = 0
                circuit_encoded = 0
            
            # Create feature vector
            features = [
                5.0,  # qualifying_position (average)
                1,    # weather_clear
                35.0, # track_temperature
                2,    # tire_strategy (medium)
                220.0, # avg_speed
                2.5,  # pit_stop_time
                driver_skills.get(driver_name, 0.5),
                team_performance.get(team_name, 0.5),
                1.0,  # circuit_factor
                driver_encoded,
                team_encoded,
                circuit_encoded
            ]
            
            # Scale features
            features_array = np.array(features).reshape(1, -1)
            scaled_features = self.scalers['main'].transform(features_array)
            
            return scaled_features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None
    
    def predict_race_outcomes(self, drivers_data):
        """Predict race outcomes for multiple drivers"""
        if not self.model_loaded:
            return self.fallback_predictions(drivers_data)
            
        predictions = []
        
        for driver_data in drivers_data:
            driver_name = driver_data['driver']
            team_name = driver_data['team']
            circuit_name = driver_data.get('circuit', 'Monaco')
            
            features = self.prepare_driver_features(driver_name, team_name, circuit_name)
            
            if features is not None:
                try:
                    # Use Random Forest models (best performers)
                    winner_prob = self.models['random_forest_winner'].predict_proba(features)[0][1] * 100
                    podium_prob = self.models['random_forest_podium'].predict_proba(features)[0][1] * 100
                    position_pred = self.models['random_forest_position'].predict(features)[0]
                    
                    predictions.append({
                        'driver': driver_name,
                        'team': team_name,
                        'probability': round(winner_prob, 1),
                        'podium_probability': round(podium_prob, 1),
                        'predicted_position': max(1, min(20, round(position_pred))),
                        'confidence': 'High' if winner_prob > 25 else 'Medium' if winner_prob > 15 else 'Low',
                        'odds': f"{round(100/max(winner_prob, 1), 1)}:1"
                    })
                    
                except Exception as e:
                    logger.error(f"Error predicting for {driver_name}: {e}")
                    
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        return predictions
    
    def fallback_predictions(self, drivers_data):
        """Simple fallback predictions when ML models aren't available"""
        # Championship standings based approximation
        standings_points = {
            'Max Verstappen': 429, 'Lando Norris': 349, 'Charles Leclerc': 341,
            'Oscar Piastri': 291, 'Carlos Sainz': 272, 'George Russell': 235,
            'Lewis Hamilton': 220, 'Sergio Perez': 152, 'Fernando Alonso': 62,
            'Nico Hulkenberg': 31, 'Yuki Tsunoda': 30, 'Pierre Gasly': 26
        }
        
        predictions = []
        for driver_data in drivers_data:
            driver = driver_data['driver']
            points = standings_points.get(driver, 0)
            probability = min(45, max(5, (points / 429) * 45))
            
            predictions.append({
                'driver': driver,
                'team': driver_data['team'],
                'probability': round(probability, 1),
                'predicted_position': len(predictions) + 1,
                'confidence': 'High' if probability > 25 else 'Medium',
                'odds': f"{round(100/max(probability, 1), 1)}:1"
            })
        
        return sorted(predictions, key=lambda x: x['probability'], reverse=True)

# Initialize ML Prediction System
ml_system = MLPredictionSystem()

# Configuration
class Config:
    JOLPICA_API_BASE = "http://api.jolpi.ca/ergast/f1"
    API_CACHE_TTL = 300
    API_TIMEOUT = 10

class JolpicaAPIClient:
    """Jolpica F1 API client for real-time data fetching"""
    
    def __init__(self):
        self.base_url = Config.JOLPICA_API_BASE
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DriveAhead-F1-Analytics/2.0'})
        self.cache_ttl = Config.API_CACHE_TTL
        self.cache = {}

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make request to Jolpica API with caching"""
        cache_key = endpoint
        current_time = time.time()
        
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if current_time - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['data']
        
        try:
            logger.info(f"Fetching from Jolpica API: {self.base_url}/{endpoint}")
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, timeout=Config.API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            self.cache[cache_key] = {'data': data, 'timestamp': current_time}
            return data
            
        except Exception as e:
            logger.error(f"Jolpica API request failed: {e}")
            return None

    def get_next_race(self) -> Optional[Dict]:
        """Get next upcoming race"""
        data = self._make_request("2025.json")
        if not data or 'MRData' not in data:
            return None
            
        races = data['MRData']['RaceTable']['Races']
        current_date = datetime.now()
        
        for race in races:
            try:
                race_date = datetime.strptime(race['date'], '%Y-%m-%d')
                
                if 'time' in race:
                    try:
                        time_str = race['time'].replace('Z', '')
                        race_time = datetime.strptime(time_str, '%H:%M:%S').time()
                        race_datetime = datetime.combine(race_date.date(), race_time)
                    except:
                        race_datetime = race_date.replace(hour=23, minute=59)
                else:
                    race_datetime = race_date.replace(hour=23, minute=59)
                
                if race_datetime > current_date:
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

class F1DataManager:
    """F1 Data Management System with ML Integration"""
    
    def __init__(self):
        self.current_season = 2025
        self.jolpica_client = JolpicaAPIClient()
        self.cache = {}
        
        # Fallback data
        self.constructor_standings = [
            {"position": 1, "team": "McLaren", "points": 666, "wins": 6},
            {"position": 2, "team": "Ferrari", "points": 652, "wins": 5},
            {"position": 3, "team": "Red Bull Racing", "points": 589, "wins": 8}
        ]
        
        self.driver_standings = [
            {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 429, "wins": 8},
            {"position": 2, "driver": "Lando Norris", "team": "McLaren", "points": 349, "wins": 4},
            {"position": 3, "driver": "Charles Leclerc", "team": "Ferrari", "points": 341, "wins": 3}
        ]
        
        logger.info("F1DataManager initialized with ML integration")
    
    def get_next_race(self):
        """Get the next upcoming race"""
        try:
            next_race = self.jolpica_client.get_next_race()
            if next_race:
                formatted_race = {
                    "round": int(next_race.get('round', 0)),
                    "name": next_race.get('raceName', ''),
                    "circuit": next_race.get('Circuit', {}).get('circuitName', ''),
                    "country": next_race.get('Circuit', {}).get('Location', {}).get('country', ''),
                    "date": next_race.get('date', ''),
                    "time": next_race.get('time', '12:00:00Z'),
                    "location": f"{next_race.get('Circuit', {}).get('Location', {}).get('locality', '')}, {next_race.get('Circuit', {}).get('Location', {}).get('country', '')}"
                }
                return formatted_race
            else:
                return {
                    "round": 19,
                    "name": "United States Grand Prix",
                    "circuit": "Circuit of the Americas",
                    "country": "United States",
                    "date": "2025-10-19",
                    "time": "19:00:00Z",
                    "location": "Austin, Texas"
                }
                
        except Exception as e:
            logger.error(f"Error fetching next race: {e}")
            return {
                "round": 19,
                "name": "United States Grand Prix",
                "circuit": "Circuit of the Americas",
                "country": "United States",
                "date": "2025-10-19",
                "time": "19:00:00Z",
                "location": "Austin, Texas"
            }
    
    def get_driver_standings(self):
        """Get current driver championship standings"""
        try:
            standings = self.jolpica_client.get_driver_standings()
            if standings:
                formatted_standings = []
                for standing in standings:
                    driver_info = standing.get('Driver', {})
                    constructor_info = standing.get('Constructors', [{}])[0]
                    
                    formatted_standings.append({
                        'position': int(standing.get('position', 0)),
                        'driver': f"{driver_info.get('givenName', '')} {driver_info.get('familyName', '')}".strip(),
                        'team': constructor_info.get('name', ''),
                        'points': int(standing.get('points', 0)),
                        'wins': int(standing.get('wins', 0))
                    })
                return formatted_standings
            else:
                return self.driver_standings
                
        except Exception as e:
            logger.error(f"Error fetching driver standings: {e}")
            return self.driver_standings
    
    def get_constructor_standings(self):
        """Get current constructor championship standings"""
        try:
            standings = self.jolpica_client.get_constructor_standings()
            if standings:
                formatted_standings = []
                for standing in standings:
                    constructor_info = standing.get('Constructor', {})
                    
                    formatted_standings.append({
                        'position': int(standing.get('position', 0)),
                        'team': constructor_info.get('name', ''),
                        'points': int(standing.get('points', 0)),
                        'wins': int(standing.get('wins', 0))
                    })
                return formatted_standings
            else:
                return self.constructor_standings
                
        except Exception as e:
            logger.error(f"Error fetching constructor standings: {e}")
            return self.constructor_standings
    
    def get_race_schedule(self):
        """Get upcoming race schedule"""
        try:
            data = self.jolpica_client._make_request("2025.json")
            if data and 'MRData' in data:
                races = data['MRData']['RaceTable']['Races']
                current_date = datetime.now()
                upcoming_races = []
                
                for race in races:
                    try:
                        race_date = datetime.strptime(race['date'], '%Y-%m-%d')
                        if race_date >= current_date:
                            race_info = {
                                "round": int(race.get('round', 0)),
                                "name": race.get('raceName', ''),
                                "date": race.get('date', ''),
                                "time": race.get('time', '12:00:00Z'),
                                "location": f"{race.get('Circuit', {}).get('Location', {}).get('locality', '')}, {race.get('Circuit', {}).get('Location', {}).get('country', '')}"
                            }
                            upcoming_races.append(race_info)
                    except:
                        continue
                
                return upcoming_races[:5]  # Return next 5 races
                
        except Exception as e:
            logger.error(f"Error fetching race schedule: {e}")
        
        # Fallback schedule
        return [
            {"round": 19, "name": "United States Grand Prix", "date": "2025-10-19", "time": "19:00:00Z", "location": "Austin, Texas"},
            {"round": 20, "name": "Mexico City Grand Prix", "date": "2025-10-27", "time": "20:00:00Z", "location": "Mexico City, Mexico"},
            {"round": 21, "name": "Brazilian Grand Prix", "date": "2025-11-03", "time": "17:00:00Z", "location": "São Paulo, Brazil"},
            {"round": 22, "name": "Las Vegas Grand Prix", "date": "2025-11-21", "time": "06:00:00Z", "location": "Las Vegas, Nevada"},
            {"round": 23, "name": "Abu Dhabi Grand Prix", "date": "2025-12-08", "time": "13:00:00Z", "location": "Abu Dhabi, UAE"}
        ]

# Initialize F1 Data Manager
f1_data_manager = F1DataManager()

# Routes
@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/telemetry')
def telemetry():
    """Render telemetry page"""
    return render_template('telemetry.html')

@app.route('/standings')
def standings():
    """Render standings page"""
    return render_template('standings.html')

@app.route('/predictions')
def predictions():
    """Render live predictions page"""
    return render_template('predictions.html')

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'ml_enabled': ml_system.model_loaded
    })

@app.route('/api/standings')
def api_standings():
    """Get F1 standings data"""
    try:
        driver_standings = f1_data_manager.get_driver_standings()
        constructor_standings = f1_data_manager.get_constructor_standings()
        
        return jsonify({
            'drivers': driver_standings,
            'constructors': constructor_standings,
            'last_updated': datetime.now().isoformat(),
            'season': 2025
        })
    except Exception as e:
        logger.error(f"Error in api_standings: {e}")
        return jsonify({'error': 'Failed to fetch standings'}), 500

@app.route('/api/next-race')
def api_next_race():
    """Get next race information"""
    try:
        next_race = f1_data_manager.get_next_race()
        return jsonify({
            'race': next_race,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in api_next_race: {e}")
        return jsonify({'error': 'Failed to fetch next race'}), 500

@app.route('/api/race-schedule')
def api_race_schedule():
    """Get upcoming race schedule"""
    try:
        races = f1_data_manager.get_race_schedule()
        return jsonify({
            'races': races,
            'last_updated': datetime.now().isoformat(),
            'season': 2025
        })
    except Exception as e:
        logger.error(f"Error in api_race_schedule: {e}")
        return jsonify({'error': 'Failed to fetch race schedule'}), 500

@app.route('/api/predictions')
def api_predictions():
    """Get ML-powered race predictions"""
    try:
        # Get current driver standings for predictions
        driver_standings = f1_data_manager.get_driver_standings()
        
        # Prepare driver data for ML predictions
        drivers_data = []
        for standing in driver_standings[:10]:  # Top 10 drivers
            drivers_data.append({
                'driver': standing['driver'],
                'team': standing['team'],
                'points': standing['points'],
                'wins': standing['wins'],
                'circuit': 'United States'  # Current next race
            })
        
        # Get ML predictions
        predictions = ml_system.predict_race_outcomes(drivers_data)
        
        return jsonify({
            'predictions': predictions,
            'last_updated': datetime.now().isoformat(),
            'model_type': 'ML' if ml_system.model_loaded else 'Fallback',
            'next_race': f1_data_manager.get_next_race()
        })
        
    except Exception as e:
        logger.error(f"Error in api_predictions: {e}")
        return jsonify({'error': 'Failed to generate predictions'}), 500

@app.route('/api/predictions/winner')
def api_predictions_winner():
    """Get winner prediction for live predictions page"""
    try:
        # Get driver standings for prediction base
        driver_standings = f1_data_manager.get_driver_standings()
        
        if driver_standings and len(driver_standings) > 0:
            # Use ML predictions for the top driver
            drivers_data = [{
                'driver': driver_standings[0]['driver'],
                'team': driver_standings[0]['team'],
                'circuit': 'United States'
            }]
            
            ml_predictions = ml_system.predict_race_outcomes(drivers_data)
            
            if ml_predictions:
                prediction = {
                    'driver': ml_predictions[0]['driver'],
                    'team': ml_predictions[0]['team'],
                    'confidence': int(ml_predictions[0]['probability']),
                    'position': 1
                }
            else:
                prediction = {
                    'driver': driver_standings[0]['driver'],
                    'team': driver_standings[0]['team'],
                    'confidence': 87,
                    'position': 1
                }
        else:
            prediction = {
                'driver': 'Max Verstappen',
                'team': 'Red Bull Racing',
                'confidence': 87,
                'position': 1
            }
        
        return jsonify({
            'prediction': prediction,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in api_predictions_winner: {e}")
        return jsonify({'error': 'Failed to get winner prediction'}), 500

@app.route('/api/telemetry')
def api_telemetry():
    """Get realistic live telemetry data"""
    try:
        import math
        
        current_time = datetime.now()
        drivers = [
            {'name': 'Max Verstappen', 'team': 'Red Bull Racing', 'color': '#1E41FF'},
            {'name': 'Lando Norris', 'team': 'McLaren', 'color': '#FF8000'},
            {'name': 'Charles Leclerc', 'team': 'Ferrari', 'color': '#DC143C'},
            {'name': 'Oscar Piastri', 'team': 'McLaren', 'color': '#FF8000'},
            {'name': 'George Russell', 'team': 'Mercedes', 'color': '#00D2BE'}
        ]
        
        telemetry_data = {}
        base_time = time.time()
        
        for i, driver in enumerate(drivers):
            position = i + 1
            lap_variation = math.sin(base_time * 0.1 + i) * 2
            speed_variation = math.cos(base_time * 0.05 + i) * 15
            
            telemetry_data[str(position)] = {
                'position': position,
                'driver': driver['name'],
                'team': driver['team'],
                'gap': '+0.000' if position == 1 else f'+{(position-1)*0.5 + lap_variation:.3f}',
                'last_lap': f'1:{22 + lap_variation:.3f}',
                'best_lap': f'1:{20 + i*0.2:.3f}',
                'sector_1': f'25.{random.randint(100, 999)}',
                'sector_2': f'42.{random.randint(100, 999)}',
                'sector_3': f'28.{random.randint(100, 999)}',
                'speed': int(310 + speed_variation),
                'tire': random.choice(['SOFT', 'MEDIUM', 'HARD']),
                'stint': random.randint(5, 25)
            }
        
        return jsonify({
            'session': 'Race',
            'lap': random.randint(15, 45),
            'weather': 'Clear',
            'track_temp': '32°C',
            'air_temp': '26°C',
            'humidity': '45%',
            'drivers': telemetry_data,
            'timestamp': current_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in api_telemetry: {e}")
        return jsonify({'error': 'Failed to fetch telemetry'}), 500

if __name__ == '__main__':
    logger.info("Starting DriveAhead F1 Analytics Platform...")
    logger.info("Real-time F1 data integration active")
    logger.info(f"ML Models Status: {'Loaded' if ml_system.model_loaded else 'Fallback Mode'}")
    logger.info("Application will be available at: http://localhost:5000")
    print("=" * 60)
    print("DRIVEAHEAD F1 ANALYTICS PLATFORM")
    print("ENHANCED WITH MACHINE LEARNING PREDICTIONS")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)