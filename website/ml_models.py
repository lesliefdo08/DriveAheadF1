"""
F1 Race Prediction ML Models
Professional machine learning models for race outcome predictions
Uses scikit-learn, XGBoost with comprehensive model evaluation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import os
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, classification_report
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

from feature_engineering import F1FeatureEngineering
from jolpica_api import JolpicaF1API
from enhanced_fastf1 import EnhancedFastF1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1PredictionModels:
    """
    Professional F1 ML prediction models with comprehensive training and evaluation
    Supports both regression (finishing position) and classification (podium/winner) tasks
    """
    
    def __init__(self):
        self.feature_engineer = F1FeatureEngineering()
        self.jolpica_api = JolpicaF1API()
        self.fastf1_api = EnhancedFastF1()
        
        # Model storage
        self.models = {}
        self.model_scores = {}
        self.feature_importance = {}
        
        # Model configurations
        self.model_configs = {
            'random_forest_position': {
                'model': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
                'task_type': 'regression',
                'target': 'race_position'
            },
            'xgboost_position': {
                'model': xgb.XGBRegressor(n_estimators=100, random_state=42, max_depth=6),
                'task_type': 'regression',
                'target': 'race_position'
            },
            'random_forest_podium': {
                'model': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8),
                'task_type': 'classification',
                'target': 'podium_finish'
            },
            'xgboost_winner': {
                'model': xgb.XGBClassifier(n_estimators=100, random_state=42, max_depth=6),
                'task_type': 'classification',
                'target': 'race_winner'
            }
        }
        
    def prepare_training_data(self, seasons: List[int], circuits: List[str]) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """Prepare training data from multiple seasons and circuits"""
        try:
            all_features = []
            all_targets = {'race_position': [], 'podium_finish': [], 'race_winner': []}
            
            for season in seasons:
                for circuit in circuits:
                    try:
                        # Get feature matrix and target for this race
                        X, y_position = self.feature_engineer.build_feature_matrix(season, circuit)
                        
                        if X.empty:
                            continue
                        
                        # Add season and circuit identifiers
                        X['season'] = season
                        X['circuit_name'] = circuit
                        
                        # Create classification targets
                        y_podium = (y_position <= 3).astype(int)  # Podium finish (1-3)
                        y_winner = (y_position == 1).astype(int)  # Race winner
                        
                        all_features.append(X)
                        all_targets['race_position'].extend(y_position.values)
                        all_targets['podium_finish'].extend(y_podium.values)
                        all_targets['race_winner'].extend(y_winner.values)
                        
                        logger.info(f"Added data for {season} {circuit}: {len(X)} samples")
                        
                    except Exception as e:
                        logger.warning(f"Could not process {season} {circuit}: {e}")
                        continue
            
            if not all_features:
                logger.error("No training data collected")
                return pd.DataFrame(), {}
            
            # Combine all features
            X_combined = pd.concat(all_features, ignore_index=True)
            
            # Convert targets to Series
            targets_combined = {}
            for target_name, target_values in all_targets.items():
                targets_combined[target_name] = pd.Series(target_values, name=target_name)
            
            logger.info(f"Total training samples: {len(X_combined)}")
            logger.info(f"Features available: {X_combined.columns.tolist()}")
            
            return X_combined, targets_combined
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame(), {}
    
    def train_model(self, model_name: str, X: pd.DataFrame, y: pd.Series, 
                   test_size: float = 0.2, optimize_hyperparameters: bool = False) -> Dict:
        """Train a specific ML model with evaluation"""
        try:
            if model_name not in self.model_configs:
                raise ValueError(f"Model {model_name} not configured")
            
            config = self.model_configs[model_name]
            model = config['model']
            task_type = config['task_type']
            
            logger.info(f"Training {model_name} ({task_type}) on {len(X)} samples...")
            
            # Preprocess features
            X_processed = self.feature_engineer.preprocess_features(X, fit_preprocessors=True)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=test_size, random_state=42
            )
            
            # Hyperparameter optimization
            if optimize_hyperparameters:
                model = self._optimize_hyperparameters(model, X_train, y_train, task_type)
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate model
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
            
            evaluation = self._evaluate_model(
                y_train, train_pred, y_test, test_pred, task_type
            )
            
            # Feature importance
            feature_importance = self._get_feature_importance(model, X_processed.columns)
            
            # Store model and results
            self.models[model_name] = model
            self.model_scores[model_name] = evaluation
            self.feature_importance[model_name] = feature_importance
            
            logger.info(f"Model {model_name} trained successfully")
            logger.info(f"Test Score: {evaluation['test_score']:.3f}")
            
            return {
                'model': model,
                'evaluation': evaluation,
                'feature_importance': feature_importance
            }
            
        except Exception as e:
            logger.error(f"Error training model {model_name}: {e}")
            return {}
    
    def train_all_models(self, seasons: List[int], circuits: List[str]) -> Dict:
        """Train all configured models"""
        try:
            logger.info("Preparing training data for all models...")
            X, targets = self.prepare_training_data(seasons, circuits)
            
            if X.empty:
                logger.error("No training data available")
                return {}
            
            results = {}
            
            # Train each model with appropriate target
            for model_name, config in self.model_configs.items():
                target_name = config['target']
                
                if target_name not in targets:
                    logger.warning(f"Target {target_name} not available for {model_name}")
                    continue
                
                y = targets[target_name]
                
                try:
                    result = self.train_model(model_name, X, y, optimize_hyperparameters=False)
                    results[model_name] = result
                    
                except Exception as e:
                    logger.error(f"Failed to train {model_name}: {e}")
                    continue
            
            # Save all models
            self.save_models()
            
            logger.info(f"Successfully trained {len(results)} models")
            return results
            
        except Exception as e:
            logger.error(f"Error in train_all_models: {e}")
            return {}
    
    def predict_race_outcome(self, season: int, circuit: str, model_types: List[str] = None) -> Dict:
        """Make race predictions using trained models"""
        try:
            if model_types is None:
                model_types = ['random_forest_position', 'xgboost_position', 'random_forest_podium']
            
            # Get feature data for prediction
            X, _ = self.feature_engineer.build_feature_matrix(season, circuit)
            
            if X.empty:
                logger.error("No feature data available for prediction")
                return {}
            
            # Preprocess features
            X_processed = self.feature_engineer.preprocess_features(X, fit_preprocessors=False)
            
            predictions = {}
            
            for model_name in model_types:
                if model_name not in self.models:
                    logger.warning(f"Model {model_name} not trained")
                    continue
                
                try:
                    model = self.models[model_name]
                    pred = model.predict(X_processed)
                    
                    # Get prediction probabilities for classification models
                    if hasattr(model, 'predict_proba'):
                        pred_proba = model.predict_proba(X_processed)
                        predictions[model_name] = {
                            'predictions': pred,
                            'probabilities': pred_proba
                        }
                    else:
                        predictions[model_name] = {
                            'predictions': pred
                        }
                    
                except Exception as e:
                    logger.error(f"Error predicting with {model_name}: {e}")
                    continue
            
            # Create comprehensive prediction summary
            prediction_summary = self._create_prediction_summary(X, predictions)
            
            return prediction_summary
            
        except Exception as e:
            logger.error(f"Error in predict_race_outcome: {e}")
            return {}
    
    def _optimize_hyperparameters(self, model, X_train, y_train, task_type: str):
        """Optimize model hyperparameters using GridSearch"""
        try:
            # Define parameter grids for different models
            param_grids = {
                'RandomForestRegressor': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10]
                },
                'RandomForestClassifier': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10]
                },
                'XGBRegressor': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 6, 9],
                    'learning_rate': [0.1, 0.2, 0.3]
                },
                'XGBClassifier': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 6, 9],
                    'learning_rate': [0.1, 0.2, 0.3]
                }
            }
            
            model_type = type(model).__name__
            param_grid = param_grids.get(model_type, {})
            
            if not param_grid:
                return model
            
            # Scoring metric
            scoring = 'neg_mean_absolute_error' if task_type == 'regression' else 'accuracy'
            
            grid_search = GridSearchCV(
                model, param_grid, cv=3, scoring=scoring, n_jobs=-1
            )
            
            grid_search.fit(X_train, y_train)
            
            logger.info(f"Best parameters for {model_type}: {grid_search.best_params_}")
            return grid_search.best_estimator_
            
        except Exception as e:
            logger.error(f"Hyperparameter optimization failed: {e}")
            return model
    
    def _evaluate_model(self, y_train, train_pred, y_test, test_pred, task_type: str) -> Dict:
        """Evaluate model performance"""
        try:
            if task_type == 'regression':
                evaluation = {
                    'train_mae': mean_absolute_error(y_train, train_pred),
                    'test_mae': mean_absolute_error(y_test, test_pred),
                    'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                    'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                    'test_score': -mean_absolute_error(y_test, test_pred)  # Negative MAE as score
                }
            else:  # classification
                evaluation = {
                    'train_accuracy': accuracy_score(y_train, train_pred),
                    'test_accuracy': accuracy_score(y_test, test_pred),
                    'test_score': accuracy_score(y_test, test_pred)
                }
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {'test_score': 0.0}
    
    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict:
        """Get feature importance from trained model"""
        try:
            if hasattr(model, 'feature_importances_'):
                importance_values = model.feature_importances_
                importance_dict = dict(zip(feature_names, importance_values))
                
                # Sort by importance
                sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                
                return {
                    'importance_scores': dict(sorted_importance),
                    'top_features': [item[0] for item in sorted_importance[:10]]
                }
            else:
                return {}
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
    
    def _create_prediction_summary(self, X: pd.DataFrame, predictions: Dict) -> Dict:
        """Create comprehensive prediction summary"""
        try:
            summary = {
                'drivers': [],
                'prediction_details': predictions,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
            # Get driver information from features
            for idx, row in X.iterrows():
                driver_data = {
                    'driver_name': row.get('driver_name', f'Driver_{idx}'),
                    'team': row.get('constructor', 'Unknown'),
                    'current_position': row.get('position', idx + 1),
                    'points': row.get('points', 0),
                    'recent_form': row.get('recent_form_score', 5.0)
                }
                
                # Add model predictions for this driver
                for model_name, pred_data in predictions.items():
                    if 'predictions' in pred_data:
                        driver_data[f'{model_name}_prediction'] = pred_data['predictions'][idx]
                    
                    if 'probabilities' in pred_data and len(pred_data['probabilities']) > idx:
                        # For binary classification, take probability of positive class
                        if pred_data['probabilities'][idx].shape[0] == 2:
                            driver_data[f'{model_name}_probability'] = pred_data['probabilities'][idx][1]
                        else:
                            driver_data[f'{model_name}_probability'] = pred_data['probabilities'][idx].max()
                
                summary['drivers'].append(driver_data)
            
            # Sort drivers by position prediction (if available)
            if 'random_forest_position_prediction' in summary['drivers'][0]:
                summary['drivers'].sort(key=lambda x: x.get('random_forest_position_prediction', 20))
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating prediction summary: {e}")
            return {'drivers': [], 'prediction_details': predictions}
    
    def save_models(self, filepath_base: str = None):
        """Save trained models to disk"""
        try:
            if filepath_base is None:
                models_dir = os.path.join(os.path.dirname(__file__), 'models')
                os.makedirs(models_dir, exist_ok=True)
                filepath_base = os.path.join(models_dir, 'f1_models')
            
            # Save models
            models_data = {
                'models': self.models,
                'model_scores': self.model_scores,
                'feature_importance': self.feature_importance,
                'timestamp': datetime.now().isoformat()
            }
            
            joblib.dump(models_data, f"{filepath_base}.joblib")
            
            # Save feature preprocessors
            self.feature_engineer.save_preprocessors(f"{filepath_base}_preprocessors.joblib")
            
            logger.info(f"Models saved to {filepath_base}.joblib")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, filepath_base: str = None):
        """Load trained models from disk"""
        try:
            if filepath_base is None:
                models_dir = os.path.join(os.path.dirname(__file__), 'models')
                filepath_base = os.path.join(models_dir, 'f1_models')
            
            model_file = f"{filepath_base}.joblib"
            preprocessor_file = f"{filepath_base}_preprocessors.joblib"
            
            if os.path.exists(model_file):
                models_data = joblib.load(model_file)
                self.models = models_data.get('models', {})
                self.model_scores = models_data.get('model_scores', {})
                self.feature_importance = models_data.get('feature_importance', {})
                
                logger.info(f"Models loaded from {model_file}")
                
            # Load feature preprocessors
            if os.path.exists(preprocessor_file):
                self.feature_engineer.load_preprocessors(preprocessor_file)
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def get_model_performance_summary(self) -> Dict:
        """Get summary of all model performances"""
        try:
            summary = {}
            
            for model_name, scores in self.model_scores.items():
                summary[model_name] = {
                    'test_score': scores.get('test_score', 0.0),
                    'model_type': self.model_configs[model_name]['task_type'],
                    'target': self.model_configs[model_name]['target']
                }
                
                if 'top_features' in self.feature_importance.get(model_name, {}):
                    summary[model_name]['top_features'] = self.feature_importance[model_name]['top_features'][:5]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating performance summary: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    ml_models = F1PredictionModels()
    
    print("🤖 Testing F1 ML Prediction Models...")
    
    try:
        # Test with limited data for demonstration
        seasons = [2024]
        circuits = ["Azerbaijan Grand Prix"]
        
        # Train models
        results = ml_models.train_all_models(seasons, circuits)
        print(f"Training results: {list(results.keys())}")
        
        # Make predictions
        predictions = ml_models.predict_race_outcome(2025, "Azerbaijan Grand Prix")
        print(f"Predictions available: {bool(predictions)}")
        
        # Performance summary
        performance = ml_models.get_model_performance_summary()
        print(f"Model performance: {performance}")
        
    except Exception as e:
        print(f"Test error: {e}")