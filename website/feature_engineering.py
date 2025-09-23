"""
ML Feature Engineering for F1 Race Predictions
Combines Jolpica historical data + FastF1 telemetry into feature vectors
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import joblib
import os

from jolpica_api import JolpicaF1API
from enhanced_fastf1 import EnhancedFastF1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1FeatureEngineering:
    """
    Professional F1 feature engineering combining multiple data sources
    Creates ML-ready feature vectors for race outcome predictions
    """
    
    def __init__(self):
        self.jolpica_api = JolpicaF1API()
        self.fastf1_api = EnhancedFastF1()
        
        # Feature preprocessing components
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        
        # Feature definitions
        self.driver_features = []
        self.circuit_features = []
        self.weather_features = []
        self.form_features = []
        
    def create_driver_features(self, drivers_df: pd.DataFrame, season: int) -> pd.DataFrame:
        """Create driver-specific features from historical data"""
        try:
            driver_features = drivers_df.copy()
            
            # Add driver career statistics
            career_stats = []
            for _, driver in drivers_df.iterrows():
                driver_id = driver.get('driver_id')
                if driver_id:
                    stats = self.jolpica_api.get_driver_career_stats(driver_id)
                    career_stats.append({
                        'driver_id': driver_id,
                        'career_wins': stats.get('career_wins', 0),
                        'career_podiums': stats.get('career_podiums', 0),
                        'career_points': stats.get('career_points', 0),
                        'career_races': stats.get('career_races', 1),
                        'win_percentage': stats.get('win_percentage', 0),
                        'podium_percentage': stats.get('podium_percentage', 0),
                        'experience_years': season - 2000  # Approximate F1 debut year
                    })
                else:
                    career_stats.append({
                        'driver_id': driver_id,
                        'career_wins': 0, 'career_podiums': 0, 'career_points': 0,
                        'career_races': 1, 'win_percentage': 0, 'podium_percentage': 0,
                        'experience_years': 1
                    })
            
            career_df = pd.DataFrame(career_stats)
            driver_features = driver_features.merge(career_df, on='driver_id', how='left')
            
            # Calculate recent form scores
            form_scores = []
            for _, driver in driver_features.iterrows():
                driver_id = driver.get('driver_id')
                if driver_id:
                    form_data = self.jolpica_api.get_recent_form(driver_id, races_count=5)
                    form_scores.append({
                        'driver_id': driver_id,
                        'recent_form_score': form_data.get('recent_form_score', 5.0),
                        'form_races_count': form_data.get('races_analyzed', 0)
                    })
                else:
                    form_scores.append({
                        'driver_id': driver_id,
                        'recent_form_score': 5.0,
                        'form_races_count': 0
                    })
            
            form_df = pd.DataFrame(form_scores)
            driver_features = driver_features.merge(form_df, on='driver_id', how='left')
            
            # Add championship standing features
            driver_features['championship_position_norm'] = driver_features['position'] / driver_features['position'].max()
            driver_features['points_leader_gap'] = driver_features['points'].max() - driver_features['points']
            driver_features['points_per_race'] = driver_features['points'] / (driver_features.get('races_completed', 1) + 1)
            
            # Constructor strength features
            constructor_strength = driver_features.groupby('constructor_id')['points'].sum().reset_index()
            constructor_strength.columns = ['constructor_id', 'constructor_points']
            driver_features = driver_features.merge(constructor_strength, on='constructor_id', how='left')
            
            logger.info(f"Created driver features: {driver_features.shape}")
            return driver_features
            
        except Exception as e:
            logger.error(f"Error creating driver features: {e}")
            return drivers_df
    
    def create_circuit_features(self, circuit_name: str, year: int) -> Dict:
        """Create circuit-specific features"""
        try:
            # Get circuit characteristics from FastF1
            circuit_data = self.fastf1_api.get_circuit_characteristics(year, circuit_name)
            
            # Define circuit type characteristics
            circuit_types = {
                'Street': {'overtaking_difficulty': 0.8, 'qualifying_importance': 0.9, 'tire_degradation': 0.6},
                'Permanent': {'overtaking_difficulty': 0.4, 'qualifying_importance': 0.6, 'tire_degradation': 0.8}
            }
            
            circuit_type = circuit_data.get('circuit_type', 'Permanent')
            type_characteristics = circuit_types.get(circuit_type, circuit_types['Permanent'])
            
            features = {
                'circuit_name': circuit_name,
                'circuit_type': circuit_type,
                'is_street_circuit': 1 if circuit_type == 'Street' else 0,
                'overtaking_difficulty': type_characteristics['overtaking_difficulty'],
                'qualifying_importance': type_characteristics['qualifying_importance'],
                'tire_degradation_factor': type_characteristics['tire_degradation'],
                'typical_race_laps': circuit_data.get('typical_race_laps', 60),
                'lap_record_seconds': circuit_data.get('lap_record', 90.0),
                'drs_zones': circuit_data.get('drs_zones', 1)
            }
            
            # Add historical circuit performance if available
            historical_winners = self._get_circuit_historical_winners(circuit_name, year)
            features.update(historical_winners)
            
            logger.info(f"Created circuit features for {circuit_name}")
            return features
            
        except Exception as e:
            logger.error(f"Error creating circuit features: {e}")
            return {'circuit_name': circuit_name, 'is_street_circuit': 0, 'overtaking_difficulty': 0.5}
    
    def create_weather_features(self, circuit_name: str, year: int) -> Dict:
        """Create weather-based features"""
        try:
            # Get historical weather data from FastF1
            weather_data = self.fastf1_api.get_weather_data(year, circuit_name, 'Race')
            
            # Default weather features if no data available
            default_weather = {
                'air_temperature': 25.0,
                'track_temperature': 35.0,
                'humidity': 60.0,
                'wind_speed': 10.0,
                'rainfall_probability': 0.1
            }
            
            weather_features = {
                'air_temperature': weather_data.get('air_temperature', default_weather['air_temperature']),
                'track_temperature': weather_data.get('track_temperature', default_weather['track_temperature']),
                'humidity': weather_data.get('humidity', default_weather['humidity']),
                'wind_speed': weather_data.get('wind_speed', default_weather['wind_speed']),
                'is_wet_conditions': 1 if weather_data.get('rainfall', False) else 0,
                'temperature_difference': abs(
                    weather_data.get('air_temperature', 25) - 
                    weather_data.get('track_temperature', 35)
                ) if weather_data else 10.0
            }
            
            logger.info(f"Created weather features for {circuit_name}")
            return weather_features
            
        except Exception as e:
            logger.error(f"Error creating weather features: {e}")
            return {'air_temperature': 25.0, 'track_temperature': 35.0, 'is_wet_conditions': 0}
    
    def create_qualifying_features(self, circuit_name: str, year: int) -> pd.DataFrame:
        """Create qualifying performance features"""
        try:
            qualifying_data = self.fastf1_api.get_qualifying_performance(year, circuit_name)
            
            if qualifying_data.empty:
                return pd.DataFrame()
            
            # Calculate qualifying features
            qualifying_features = qualifying_data.copy()
            
            # Grid position impact (pole position advantage, etc.)
            qualifying_features['pole_position'] = (qualifying_features['grid_position'] == 1).astype(int)
            qualifying_features['front_row'] = (qualifying_features['grid_position'] <= 2).astype(int)
            qualifying_features['top_5_grid'] = (qualifying_features['grid_position'] <= 5).astype(int)
            qualifying_features['q3_participant'] = qualifying_features['q3_time'].notna().astype(int)
            
            # Qualifying time gaps
            if qualifying_features['best_qualifying_time'].notna().sum() > 0:
                pole_time = qualifying_features['best_qualifying_time'].min()
                qualifying_features['quali_gap_to_pole'] = qualifying_features['best_qualifying_time'] - pole_time
                qualifying_features['quali_gap_normalized'] = qualifying_features['quali_gap_to_pole'] / pole_time
            else:
                qualifying_features['quali_gap_to_pole'] = 0
                qualifying_features['quali_gap_normalized'] = 0
            
            logger.info(f"Created qualifying features: {qualifying_features.shape}")
            return qualifying_features
            
        except Exception as e:
            logger.error(f"Error creating qualifying features: {e}")
            return pd.DataFrame()
    
    def build_feature_matrix(self, season: int, circuit_name: str, target_race_round: int = None) -> Tuple[pd.DataFrame, pd.Series]:
        """Build complete feature matrix for ML model training"""
        try:
            logger.info(f"Building feature matrix for {circuit_name} season {season}")
            
            # Get base driver standings
            drivers_df = self.jolpica_api.get_current_season_standings(season)
            if drivers_df.empty:
                logger.error("No driver standings data available")
                return pd.DataFrame(), pd.Series(dtype=float)
            
            # Create driver features
            driver_features = self.create_driver_features(drivers_df, season)
            
            # Create circuit features
            circuit_features = self.create_circuit_features(circuit_name, season)
            
            # Create weather features  
            weather_features = self.create_weather_features(circuit_name, season)
            
            # Get qualifying features
            qualifying_features = self.create_qualifying_features(circuit_name, season)
            
            # Combine all features
            feature_matrix = driver_features.copy()
            
            # Add circuit features to each driver
            for key, value in circuit_features.items():
                feature_matrix[f'circuit_{key}'] = value
            
            # Add weather features to each driver
            for key, value in weather_features.items():
                feature_matrix[f'weather_{key}'] = value
            
            # Merge qualifying features if available
            if not qualifying_features.empty:
                feature_matrix = feature_matrix.merge(
                    qualifying_features[['driver', 'grid_position', 'pole_position', 'front_row', 'top_5_grid', 'quali_gap_normalized']],
                    left_on='driver_name', right_on='driver_name', how='left'
                )
            
            # Create target variable (race finishing position)
            # This would be populated from actual race results for training
            target = pd.Series(range(1, len(feature_matrix) + 1), name='race_position')
            
            # Select final features for ML model
            ml_features = [
                'points', 'wins', 'career_wins', 'career_podiums', 'win_percentage', 'podium_percentage',
                'recent_form_score', 'championship_position_norm', 'points_leader_gap', 'constructor_points',
                'circuit_is_street_circuit', 'circuit_overtaking_difficulty', 'circuit_qualifying_importance',
                'weather_air_temperature', 'weather_track_temperature', 'weather_is_wet_conditions',
                'grid_position', 'pole_position', 'front_row', 'quali_gap_normalized'
            ]
            
            # Filter features that exist
            available_features = [f for f in ml_features if f in feature_matrix.columns]
            feature_matrix_final = feature_matrix[available_features].fillna(0)
            
            logger.info(f"Final feature matrix shape: {feature_matrix_final.shape}")
            logger.info(f"Features used: {available_features}")
            
            return feature_matrix_final, target
            
        except Exception as e:
            logger.error(f"Error building feature matrix: {e}")
            return pd.DataFrame(), pd.Series(dtype=float)
    
    def _get_circuit_historical_winners(self, circuit_name: str, year: int) -> Dict:
        """Get historical performance statistics for circuit"""
        try:
            # This would typically analyze last 3-5 years of data
            historical_features = {
                'ferrari_wins_last_5': 1,  # Placeholder - would calculate from historical data
                'mercedes_wins_last_5': 1,
                'redbull_wins_last_5': 2,
                'mclaren_wins_last_5': 0,
                'pole_to_win_percentage': 0.6  # Historical pole-to-win conversion rate
            }
            
            return historical_features
            
        except Exception as e:
            logger.error(f"Error getting historical circuit data: {e}")
            return {}
    
    def preprocess_features(self, X: pd.DataFrame, fit_preprocessors: bool = False) -> pd.DataFrame:
        """Preprocess features for ML model"""
        try:
            X_processed = X.copy()
            
            # Handle missing values
            if 'imputer' not in self.imputers:
                self.imputers['imputer'] = SimpleImputer(strategy='median')
            
            if fit_preprocessors:
                X_processed = pd.DataFrame(
                    self.imputers['imputer'].fit_transform(X_processed),
                    columns=X_processed.columns,
                    index=X_processed.index
                )
            else:
                X_processed = pd.DataFrame(
                    self.imputers['imputer'].transform(X_processed),
                    columns=X_processed.columns,
                    index=X_processed.index
                )
            
            # Scale numerical features
            if 'scaler' not in self.scalers:
                self.scalers['scaler'] = StandardScaler()
            
            if fit_preprocessors:
                X_scaled = self.scalers['scaler'].fit_transform(X_processed)
            else:
                X_scaled = self.scalers['scaler'].transform(X_processed)
            
            X_final = pd.DataFrame(X_scaled, columns=X_processed.columns, index=X_processed.index)
            
            return X_final
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            return X
    
    def save_preprocessors(self, filepath: str):
        """Save feature preprocessors"""
        try:
            preprocessors = {
                'scalers': self.scalers,
                'encoders': self.encoders,
                'imputers': self.imputers
            }
            joblib.dump(preprocessors, filepath)
            logger.info(f"Preprocessors saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving preprocessors: {e}")
    
    def load_preprocessors(self, filepath: str):
        """Load feature preprocessors"""
        try:
            if os.path.exists(filepath):
                preprocessors = joblib.load(filepath)
                self.scalers = preprocessors.get('scalers', {})
                self.encoders = preprocessors.get('encoders', {})
                self.imputers = preprocessors.get('imputers', {})
                logger.info(f"Preprocessors loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading preprocessors: {e}")

# Example usage
if __name__ == "__main__":
    feature_engineer = F1FeatureEngineering()
    
    print("🔧 Testing F1 Feature Engineering...")
    
    try:
        # Test feature matrix creation
        X, y = feature_engineer.build_feature_matrix(2024, "Azerbaijan Grand Prix")
        print(f"Feature matrix shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        if not X.empty:
            print("Features created:")
            print(X.columns.tolist())
            print("\nFirst few rows:")
            print(X.head())
        
    except Exception as e:
        print(f"Test error: {e}")