"""
F1 Model Training Pipeline
Comprehensive training system for race prediction models
No hardcoded data - all dynamic from API sources
"""
import os
import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import joblib
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_models import F1PredictionModels
from jolpica_api import JolpicaF1API
from feature_engineering import F1FeatureEngineering

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainingPipeline:
    """Complete pipeline for training and evaluating F1 prediction models"""
    
    def __init__(self):
        self.models = F1PredictionModels()
        self.jolpica_api = JolpicaF1API()
        self.feature_engineer = F1FeatureEngineering()
        self.model_dir = Path('models')
        self.model_dir.mkdir(exist_ok=True)
        
    def get_available_seasons_and_circuits(self) -> tuple:
        """Get available seasons and circuits from API"""
        try:
            # Get recent seasons (last 5 years)
            current_year = datetime.now().year
            seasons = list(range(current_year - 4, current_year + 1))
            
            # Get all circuits from current season
            races = self.jolpica_api.get_season_races(current_year)
            circuits = []
            
            if races and 'MRData' in races:
                race_table = races['MRData']['RaceTable']['Races']
                circuits = [race['Circuit']['circuitId'] for race in race_table]
            
            logger.info(f"Available seasons: {seasons}")
            logger.info(f"Available circuits: {len(circuits)} circuits")
            
            return seasons, circuits
            
        except Exception as e:
            logger.error(f"Error getting available data: {e}")
            # Fallback to known circuits if API fails
            return [2023, 2024], ['monaco', 'silverstone', 'monza', 'spa', 'suzuka']
    
    def train_all_models(self, force_retrain=False):
        """Train all prediction models with current data"""
        logger.info("🏎️ Starting F1 Model Training Pipeline...")
        
        # Get available data
        seasons, circuits = self.get_available_seasons_and_circuits()
        
        if not seasons or not circuits:
            logger.error("No training data available")
            return False
        
        # Check if models exist and are recent
        if not force_retrain and self._models_are_recent():
            logger.info("Models are recent, skipping training. Use force_retrain=True to override.")
            return True
        
        try:
            # Prepare training data
            logger.info("📊 Preparing training data...")
            X, y_dict = self.models.prepare_training_data(seasons[:3], circuits[:10])  # Limit for efficiency
            
            if X.empty:
                logger.error("No training data could be prepared")
                return False
            
            logger.info(f"Training data prepared: {len(X)} samples with {len(X.columns)} features")
            
            # Train all models
            trained_models = {}
            model_scores = {}
            
            for model_name, config in self.models.model_configs.items():
                try:
                    logger.info(f"🤖 Training {model_name}...")
                    
                    if config['target'] not in y_dict:
                        logger.warning(f"Target {config['target']} not available, skipping {model_name}")
                        continue
                    
                    y = np.array(y_dict[config['target']])
                    
                    if len(y) == 0:
                        logger.warning(f"No target data for {model_name}")
                        continue
                    
                    # Train model
                    trained_model, score = self._train_single_model(
                        X, y, config['model'], config['task_type']
                    )
                    
                    if trained_model:
                        trained_models[model_name] = trained_model
                        model_scores[model_name] = score
                        logger.info(f"✅ {model_name} trained successfully - Score: {score:.3f}")
                    
                except Exception as e:
                    logger.error(f"❌ Error training {model_name}: {e}")
                    continue
            
            # Save trained models
            if trained_models:
                self._save_models(trained_models, model_scores)
                logger.info(f"🎯 Training complete! {len(trained_models)} models saved.")
                return True
            else:
                logger.error("❌ No models were successfully trained")
                return False
                
        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            return False
    
    def _train_single_model(self, X, y, model, task_type):
        """Train a single model with proper validation"""
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, mean_absolute_error
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y if task_type == 'classification' else None
            )
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            
            if task_type == 'classification':
                score = accuracy_score(y_test, y_pred)
            else:
                score = 1.0 / (1.0 + mean_absolute_error(y_test, y_pred))  # Inverse MAE as score
            
            return model, score
            
        except Exception as e:
            logger.error(f"Error in single model training: {e}")
            return None, 0.0
    
    def _save_models(self, models, scores):
        """Save trained models to disk"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for model_name, model in models.items():
                model_path = self.model_dir / f"{model_name}_{timestamp}.pkl"
                joblib.dump(model, model_path)
                
            # Save metadata
            metadata = {
                'timestamp': timestamp,
                'models': list(models.keys()),
                'scores': scores,
                'training_date': datetime.now().isoformat()
            }
            
            metadata_path = self.model_dir / f"training_metadata_{timestamp}.json"
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Models saved to {self.model_dir}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def _models_are_recent(self, max_age_days=7):
        """Check if models are recent enough"""
        try:
            model_files = list(self.model_dir.glob("*.pkl"))
            if not model_files:
                return False
            
            # Check most recent model
            newest_model = max(model_files, key=os.path.getctime)
            model_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(newest_model))
            
            return model_age.days < max_age_days
            
        except Exception:
            return False
    
    def load_latest_models(self):
        """Load the most recent trained models"""
        try:
            model_files = list(self.model_dir.glob("*.pkl"))
            if not model_files:
                logger.warning("No trained models found")
                return {}
            
            # Group by model type and get latest
            latest_models = {}
            
            for model_file in model_files:
                model_name = model_file.stem.rsplit('_', 1)[0]  # Remove timestamp
                if model_name not in latest_models:
                    latest_models[model_name] = model_file
                else:
                    # Keep the newer one
                    current_time = os.path.getctime(latest_models[model_name])
                    new_time = os.path.getctime(model_file)
                    if new_time > current_time:
                        latest_models[model_name] = model_file
            
            # Load the models
            loaded_models = {}
            for model_name, model_path in latest_models.items():
                try:
                    loaded_models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded model: {model_name}")
                except Exception as e:
                    logger.error(f"Error loading {model_name}: {e}")
            
            return loaded_models
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return {}

def main():
    """Main training function"""
    pipeline = ModelTrainingPipeline()
    
    # Train models
    success = pipeline.train_all_models(force_retrain=True)
    
    if success:
        print("🏁 Training completed successfully!")
        
        # Load and test models
        models = pipeline.load_latest_models()
        print(f"📊 Loaded {len(models)} trained models")
        
    else:
        print("❌ Training failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()