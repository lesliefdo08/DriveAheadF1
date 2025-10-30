"""
Real ML-Based F1 Race Predictor
================================
Uses trained RandomForest/XGBoost models to predict race outcomes.

This is the REAL machine learning predictor that loads and uses 
trained models (not just hardcoded scoring).
"""

import numpy as np
import joblib
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION - SET THESE TO USE YOUR TRAINED MODELS
# ============================================================================
ML_PREDICTOR_ENABLED = False  # Set to True after training models
MODEL_TIMESTAMP = None  # Set to your model timestamp (e.g., '20251030_120000')

# If no timestamp set, try to auto-detect latest model
if MODEL_TIMESTAMP is None:
    try:
        models_dir = 'backend/models'
        metadata_files = [f for f in os.listdir(models_dir) if f.startswith('ml_metadata_') and f.endswith('.json')]
        if metadata_files:
            # Get the latest metadata file
            latest_metadata = sorted(metadata_files)[-1]
            MODEL_TIMESTAMP = latest_metadata.replace('ml_metadata_', '').replace('.json', '')
            logger.info(f"Auto-detected model timestamp: {MODEL_TIMESTAMP}")
    except Exception as e:
        logger.warning(f"Could not auto-detect model timestamp: {e}")


class MLF1Predictor:
    """
    Real ML-based F1 predictor using trained models
    
    If ML_PREDICTOR_ENABLED=False, falls back to algorithmic prediction
    """
    
    def __init__(self, model_timestamp: Optional[str] = None):
        self.model_timestamp = model_timestamp or MODEL_TIMESTAMP
        self.models_loaded = False
        self.models_dir = 'backend/models'
        
        # Model objects (loaded on first use)
        self.winner_model = None
        self.podium_model = None
        self.position_model = None
        self.scaler = None
        self.encoders = None
        self.feature_columns = None
        self.metadata = None
        
        # Driver/team/circuit mappings (2025 F1 season)
        self.driver_teams = {
            'Max Verstappen': 'Red Bull', 'Sergio Perez': 'Red Bull',
            'Oscar Piastri': 'McLaren', 'Lando Norris': 'McLaren',
            'Charles Leclerc': 'Ferrari', 'Lewis Hamilton': 'Ferrari',
            'George Russell': 'Mercedes', 'Andrea Kimi Antonelli': 'Mercedes',
            'Fernando Alonso': 'Aston Martin', 'Lance Stroll': 'Aston Martin',
            'Pierre Gasly': 'Alpine F1 Team', 'Jack Doohan': 'Alpine F1 Team',
            'Alexander Albon': 'Williams', 'Carlos Sainz': 'Williams',
            'Nico Hulkenberg': 'Haas F1 Team', 'Esteban Ocon': 'Haas F1 Team',
            'Yuki Tsunoda': 'RB F1 Team', 'Isack Hadjar': 'RB F1 Team',
            'Gabriel Bortoleto': 'Sauber', 'Oliver Bearman': 'Sauber'
        }
        
        self.team_performance = {
            'Red Bull': 95, 'McLaren': 92, 'Ferrari': 90, 'Mercedes': 85,
            'Aston Martin': 70, 'Alpine F1 Team': 65, 'Williams': 60,
            'Haas F1 Team': 55, 'RB F1 Team': 58, 'Sauber': 50
        }
        
        self.driver_skill = {
            'Max Verstappen': 98, 'Oscar Piastri': 90, 'Lando Norris': 92,
            'Charles Leclerc': 93, 'Lewis Hamilton': 96, 'George Russell': 88,
            'Fernando Alonso': 94, 'Carlos Sainz': 87, 'Sergio Perez': 82,
            'Alexander Albon': 80, 'Pierre Gasly': 81, 'Nico Hulkenberg': 79,
            'Yuki Tsunoda': 77, 'Esteban Ocon': 76, 'Lance Stroll': 72,
            'Andrea Kimi Antonelli': 75, 'Oliver Bearman': 70, 'Isack Hadjar': 71,
            'Jack Doohan': 68, 'Gabriel Bortoleto': 67
        }
        
        # Try to load models on initialization
        if ML_PREDICTOR_ENABLED and self.model_timestamp:
            self.load_models()
    
    def load_models(self) -> bool:
        """Load trained ML models"""
        try:
            if not self.model_timestamp:
                logger.error("No model timestamp provided. Cannot load models.")
                return False
            
            logger.info(f"Loading ML models with timestamp: {self.model_timestamp}")
            
            # Load models
            winner_path = f'{self.models_dir}/winner_model_{self.model_timestamp}.pkl'
            podium_path = f'{self.models_dir}/podium_model_{self.model_timestamp}.pkl'
            position_path = f'{self.models_dir}/position_model_{self.model_timestamp}.pkl'
            scaler_path = f'{self.models_dir}/scaler_{self.model_timestamp}.pkl'
            encoders_path = f'{self.models_dir}/encoders_{self.model_timestamp}.pkl'
            
            # Check if files exist
            required_files = [winner_path, podium_path, position_path, scaler_path, encoders_path]
            missing_files = [f for f in required_files if not os.path.exists(f)]
            
            if missing_files:
                logger.error(f"Missing model files: {missing_files}")
                logger.error("Run 'python backend/train_ml_models.py' to train models first!")
                return False
            
            # Load all components
            self.winner_model = joblib.load(winner_path)
            self.podium_model = joblib.load(podium_path)
            self.position_model = joblib.load(position_path)
            self.scaler = joblib.load(scaler_path)
            self.encoders = joblib.load(encoders_path)
            
            # Load metadata
            metadata_path = f'{self.models_dir}/ml_metadata_{self.model_timestamp}.json'
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                    self.feature_columns = self.metadata.get('feature_columns', [])
            
            self.models_loaded = True
            logger.info("✓ ML models loaded successfully!")
            logger.info(f"  Winner model: {self.metadata.get('best_models', {}).get('winner', {}).get('algorithm', 'unknown')}")
            logger.info(f"  Podium model: {self.metadata.get('best_models', {}).get('podium', {}).get('algorithm', 'unknown')}")
            logger.info(f"  Position model: {self.metadata.get('best_models', {}).get('position', {}).get('algorithm', 'unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
            self.models_loaded = False
            return False
    
    def predict_race_winner(self, drivers: List[str], circuit: str, 
                          qualifying_positions: Optional[Dict[str, int]] = None) -> Dict:
        """
        Predict race winner using ML models or fallback to algorithm
        
        Args:
            drivers: List of driver names competing
            circuit: Circuit name
            qualifying_positions: Optional dict of {driver: quali_position}
        
        Returns:
            Prediction dict with winner, confidence, top 3, etc.
        """
        
        # If ML disabled or models not loaded, use algorithmic fallback
        if not ML_PREDICTOR_ENABLED or not self.models_loaded:
            logger.info("Using algorithmic prediction (ML models not loaded)")
            return self._algorithmic_prediction(drivers, circuit, qualifying_positions)
        
        try:
            logger.info(f"Predicting winner for {circuit} using ML models")
            
            # Prepare features for each driver
            predictions = []
            
            for driver in drivers:
                if driver not in self.driver_teams:
                    continue
                
                team = self.driver_teams[driver]
                
                # Get qualifying position (or estimate)
                if qualifying_positions and driver in qualifying_positions:
                    quali_pos = qualifying_positions[driver]
                else:
                    # Estimate based on skill and team
                    skill = self.driver_skill.get(driver, 70)
                    team_perf = self.team_performance.get(team, 50)
                    quali_pos = int(20 - ((skill + team_perf) / 200 * 19))
                
                # Create feature vector
                features = self._create_feature_vector(
                    driver=driver,
                    team=team,
                    circuit=circuit,
                    qualifying_position=quali_pos
                )
                
                if features is None:
                    continue
                
                # Scale features
                features_scaled = self.scaler.transform([features])
                
                # Get predictions
                winner_prob = self.winner_model.predict_proba(features_scaled)[0][1]
                podium_prob = self.podium_model.predict_proba(features_scaled)[0][1]
                predicted_position = self.position_model.predict(features_scaled)[0]
                
                predictions.append({
                    'driver': driver,
                    'team': team,
                    'winner_probability': winner_prob * 100,
                    'podium_probability': podium_prob * 100,
                    'predicted_position': round(predicted_position, 1),
                    'qualifying_position': quali_pos
                })
            
            # Sort by winner probability
            predictions.sort(key=lambda x: x['winner_probability'], reverse=True)
            
            if not predictions:
                logger.warning("No valid predictions generated, using fallback")
                return self._algorithmic_prediction(drivers, circuit, qualifying_positions)
            
            # Top 3 predictions
            winner = predictions[0]
            second = predictions[1] if len(predictions) > 1 else predictions[0]
            third = predictions[2] if len(predictions) > 2 else predictions[0]
            
            # Build reasoning
            reasoning = self._build_ml_reasoning(winner, circuit)
            
            return {
                'predicted_winner': winner['driver'],
                'team': winner['team'],
                'confidence': round(winner['winner_probability'], 1),
                'probability': round(winner['winner_probability'], 1),
                'reasoning': reasoning,
                'top_3_predictions': [
                    {
                        'driver': p['driver'],
                        'team': p['team'],
                        'score': round(p['winner_probability'], 2),
                        'probability': round(p['winner_probability'], 1),
                        'predicted_position': p['predicted_position']
                    }
                    for p in predictions[:3]
                ],
                'all_predictions': predictions[:10],  # Top 10
                'circuit': circuit,
                'prediction_method': 'ML Models (Trained)',
                'model_info': {
                    'winner_model': self.metadata.get('best_models', {}).get('winner', {}).get('algorithm', 'unknown'),
                    'timestamp': self.model_timestamp,
                    'accuracy': self.metadata.get('best_models', {}).get('winner', {}).get('accuracy', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return self._algorithmic_prediction(drivers, circuit, qualifying_positions)
    
    def _create_feature_vector(self, driver: str, team: str, circuit: str, 
                               qualifying_position: int) -> Optional[List[float]]:
        """Create feature vector for prediction"""
        try:
            # Feature values
            features = {
                'qualifying_position': qualifying_position,
                'weather_clear': 1,  # Assume clear weather (can be updated)
                'track_temperature': 35.0,  # Default temp
                'tire_strategy': 2,  # Medium tires
                'avg_speed': 200.0,  # Default average speed
                'pit_stop_time': 21.0,  # Default pit time
                'driver_skill': self.driver_skill.get(driver, 70),
                'team_performance': self.team_performance.get(team, 50),
                'circuit_factor': 1.0,
                'recent_form': qualifying_position,  # Use quali as proxy for form
            }
            
            # Encode categorical variables
            try:
                driver_encoded = self.encoders['driver'].transform([driver])[0]
                team_encoded = self.encoders['team'].transform([team])[0]
                circuit_encoded = self.encoders['circuit'].transform([circuit])[0]
            except Exception:
                # If driver/team/circuit not in encoder, use default
                return None
            
            features['driver_encoded'] = driver_encoded
            features['team_encoded'] = team_encoded
            features['circuit_encoded'] = circuit_encoded
            
            # Return in correct order (matching feature_columns)
            feature_vector = [features[col] for col in self.feature_columns]
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error creating feature vector for {driver}: {e}")
            return None
    
    def _build_ml_reasoning(self, prediction: Dict, circuit: str) -> List[str]:
        """Build reasoning based on ML prediction"""
        reasoning = []
        
        prob = prediction['winner_probability']
        driver = prediction['driver']
        
        if prob > 60:
            reasoning.append(f"ML model gives {driver} a {prob:.1f}% win probability - very high confidence")
        elif prob > 40:
            reasoning.append(f"ML model predicts {prob:.1f}% win probability - strong contender")
        else:
            reasoning.append(f"ML model gives {prob:.1f}% win probability based on current form")
        
        if prediction['predicted_position'] < 3:
            reasoning.append(f"Model predicts P{int(prediction['predicted_position'])} finish")
        
        if prediction['qualifying_position'] <= 3:
            reasoning.append(f"Starting from P{prediction['qualifying_position']} - front row advantage")
        
        skill = self.driver_skill.get(driver, 70)
        if skill >= 90:
            reasoning.append(f"{driver} is a top-tier driver (skill rating: {skill}/100)")
        
        return reasoning if reasoning else ["Model prediction based on historical performance patterns"]
    
    def _algorithmic_prediction(self, drivers: List[str], circuit: str,
                               qualifying_positions: Optional[Dict[str, int]] = None) -> Dict:
        """
        Fallback algorithmic prediction (used when ML models not available)
        This is the BACKUP - not the primary prediction method
        """
        logger.info("Using algorithmic fallback prediction")
        
        scores = []
        
        for driver in drivers:
            if driver not in self.driver_teams:
                continue
            
            team = self.driver_teams[driver]
            skill = self.driver_skill.get(driver, 70)
            team_perf = self.team_performance.get(team, 50)
            
            # Simple scoring
            score = (skill * 0.6) + (team_perf * 0.4)
            
            # Qualifying bonus
            if qualifying_positions and driver in qualifying_positions:
                quali_pos = qualifying_positions[driver]
                score += (20 - quali_pos) * 2
            
            scores.append({
                'driver': driver,
                'team': team,
                'score': score,
                'skill': skill,
                'team_perf': team_perf
            })
        
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        if not scores:
            return {
                'predicted_winner': 'Max Verstappen',
                'team': 'Red Bull',
                'confidence': 70.0,
                'probability': 70.0,
                'reasoning': ['Default prediction - no data available'],
                'prediction_method': 'Fallback (No Data)'
            }
        
        winner = scores[0]
        confidence = min(95, 50 + (winner['score'] - scores[1]['score']))
        
        return {
            'predicted_winner': winner['driver'],
            'team': winner['team'],
            'confidence': round(confidence, 1),
            'probability': round(confidence, 1),
            'reasoning': [
                f"High skill rating ({winner['skill']}/100)",
                f"Strong team performance ({winner['team_perf']}/100)",
                "Based on algorithmic scoring (ML models not loaded)"
            ],
            'top_3_predictions': [
                {
                    'driver': s['driver'],
                    'team': s['team'],
                    'score': round(s['score'], 2),
                    'probability': round(50 + (s['score'] / 2), 1)
                }
                for s in scores[:3]
            ],
            'circuit': circuit,
            'prediction_method': 'Algorithmic Fallback (ML Not Available)'
        }


# Global instance
ml_predictor = MLF1Predictor()

# Try to load models on import
if ML_PREDICTOR_ENABLED:
    if ml_predictor.load_models():
        logger.info("✓ ML Predictor ready with trained models!")
    else:
        logger.warning("⚠ ML Predictor using fallback mode (models not loaded)")
else:
    logger.info("ℹ ML Predictor in fallback mode (ML_PREDICTOR_ENABLED=False)")
