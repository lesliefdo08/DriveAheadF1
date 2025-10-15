"""
DriveAhead F1 - Machine Learning Model Training System
Implements Random Forest, XGBoost, and Logistic Regression for F1 Predictions
Based on presentation: The Powerhouse Machine Learning Algorithms
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_absolute_error, classification_report
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class F1MLTrainingSystem:
    """
    The Powerhouse: Machine Learning Algorithms for F1 Predictions
    Random Forest + XGBoost + Logistic Regression
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.model_performance = {}
        
        print("🏁 DriveAhead F1 ML Training System - ACTIVE")
        print("🤖 The Powerhouse: Random Forest | XGBoost | Logistic Regression")
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
    def generate_f1_training_data(self, n_samples=2000):
        """Generate realistic F1 training data"""
        print(f"🏎️ Generating {n_samples} F1 training samples...")
        
        # F1 2024-2025 drivers and teams
        drivers = [
            'Max Verstappen', 'Sergio Perez',  # Red Bull
            'Charles Leclerc', 'Carlos Sainz',  # Ferrari  
            'Lando Norris', 'Oscar Piastri',   # McLaren
            'George Russell', 'Lewis Hamilton', # Mercedes
            'Fernando Alonso', 'Lance Stroll',  # Aston Martin
            'Pierre Gasly', 'Esteban Ocon',    # Alpine
            'Alexander Albon', 'Logan Sargeant', # Williams
            'Nico Hulkenberg', 'Kevin Magnussen', # Haas
            'Daniel Ricciardo', 'Yuki Tsunoda', # RB
            'Valtteri Bottas', 'Zhou Guanyu'   # Sauber
        ]
        
        teams = {
            'Max Verstappen': 'Red Bull Racing', 'Sergio Perez': 'Red Bull Racing',
            'Charles Leclerc': 'Ferrari', 'Carlos Sainz': 'Ferrari',
            'Lando Norris': 'McLaren', 'Oscar Piastri': 'McLaren',
            'George Russell': 'Mercedes', 'Lewis Hamilton': 'Mercedes',
            'Fernando Alonso': 'Aston Martin', 'Lance Stroll': 'Aston Martin',
            'Pierre Gasly': 'Alpine', 'Esteban Ocon': 'Alpine',
            'Alexander Albon': 'Williams', 'Logan Sargeant': 'Williams',
            'Nico Hulkenberg': 'Haas', 'Kevin Magnussen': 'Haas',
            'Daniel Ricciardo': 'RB', 'Yuki Tsunoda': 'RB',
            'Valtteri Bottas': 'Sauber', 'Zhou Guanyu': 'Sauber'
        }
        
        circuits = [
            'Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China', 'Miami',
            'Emilia Romagna', 'Monaco', 'Canada', 'Spain', 'Austria', 'Britain',
            'Hungary', 'Belgium', 'Netherlands', 'Italy', 'Azerbaijan', 'Singapore',
            'United States', 'Mexico', 'Brazil', 'Qatar', 'Abu Dhabi'
        ]
        
        # Generate training data
        data = []
        np.random.seed(42)
        
        for i in range(n_samples):
            driver = np.random.choice(drivers)
            team = teams[driver]
            circuit = np.random.choice(circuits)
            
            # Driver performance factors (based on real 2024 performance)
            driver_skill = {
                'Max Verstappen': 0.95, 'Charles Leclerc': 0.88, 'Lando Norris': 0.85,
                'Oscar Piastri': 0.82, 'George Russell': 0.80, 'Lewis Hamilton': 0.78,
                'Carlos Sainz': 0.76, 'Fernando Alonso': 0.75, 'Sergio Perez': 0.72,
                'Pierre Gasly': 0.68, 'Alexander Albon': 0.65, 'Nico Hulkenberg': 0.62,
                'Esteban Ocon': 0.60, 'Daniel Ricciardo': 0.58, 'Yuki Tsunoda': 0.55,
                'Kevin Magnussen': 0.52, 'Lance Stroll': 0.50, 'Valtteri Bottas': 0.48,
                'Logan Sargeant': 0.45, 'Zhou Guanyu': 0.42
            }.get(driver, 0.5)
            
            # Team performance factors
            team_performance = {
                'Red Bull Racing': 0.92, 'McLaren': 0.88, 'Ferrari': 0.85,
                'Mercedes': 0.75, 'Aston Martin': 0.65, 'RB': 0.55,
                'Alpine': 0.52, 'Williams': 0.48, 'Haas': 0.45, 'Sauber': 0.40
            }.get(team, 0.5)
            
            # Generate features
            qualifying_position = max(1, min(20, np.random.normal(
                (1 - driver_skill) * 20 + (1 - team_performance) * 5, 3)))
            
            # Weather and track conditions
            weather_clear = np.random.choice([0, 1], p=[0.3, 0.7])
            track_temperature = np.random.normal(35, 8)
            tire_strategy = np.random.choice([1, 2, 3])  # 1=soft, 2=medium, 3=hard
            
            # Performance metrics
            avg_speed = np.random.normal(200 + team_performance * 50, 15)
            pit_stop_time = np.random.normal(2.5, 0.5)
            
            # Circuit-specific adjustments
            circuit_factor = np.random.uniform(0.8, 1.2)
            
            # Calculate race position (target variable)
            base_position = (qualifying_position + 
                           (1 - driver_skill) * 10 + 
                           (1 - team_performance) * 8 +
                           np.random.normal(0, 2) * circuit_factor)
            
            race_position = max(1, min(20, int(base_position)))
            
            # Binary targets
            race_winner = 1 if race_position == 1 else 0
            podium_finish = 1 if race_position <= 3 else 0
            points_finish = 1 if race_position <= 10 else 0
            
            data.append({
                'driver': driver,
                'team': team,
                'circuit': circuit,
                'qualifying_position': int(qualifying_position),
                'weather_clear': weather_clear,
                'track_temperature': track_temperature,
                'tire_strategy': tire_strategy,
                'avg_speed': avg_speed,
                'pit_stop_time': pit_stop_time,
                'driver_skill': driver_skill,
                'team_performance': team_performance,
                'circuit_factor': circuit_factor,
                'race_position': race_position,
                'race_winner': race_winner,
                'podium_finish': podium_finish,
                'points_finish': points_finish
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df)} training samples with {len(df.columns)} features")
        return df
    
    def prepare_features(self, df):
        """Prepare features for ML training"""
        print("🔧 Preparing features for machine learning...")
        
        # Encode categorical variables
        le_driver = LabelEncoder()
        le_team = LabelEncoder()
        le_circuit = LabelEncoder()
        
        df['driver_encoded'] = le_driver.fit_transform(df['driver'])
        df['team_encoded'] = le_team.fit_transform(df['team'])
        df['circuit_encoded'] = le_circuit.fit_transform(df['circuit'])
        
        # Store encoders
        self.encoders = {
            'driver': le_driver,
            'team': le_team,
            'circuit': le_circuit
        }
        
        # Select features for training
        feature_cols = [
            'qualifying_position', 'weather_clear', 'track_temperature',
            'tire_strategy', 'avg_speed', 'pit_stop_time',
            'driver_skill', 'team_performance', 'circuit_factor',
            'driver_encoded', 'team_encoded', 'circuit_encoded'
        ]
        
        self.feature_columns = feature_cols
        X = df[feature_cols]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['main'] = scaler
        
        return X_scaled, df
    
    def train_models(self, X, y_position, y_winner, y_podium):
        """Train all three ML algorithms"""
        print("\n🤖 Training The Powerhouse ML Algorithms...")
        
        # Split data
        X_train, X_test, y_pos_train, y_pos_test = train_test_split(
            X, y_position, test_size=0.2, random_state=42)
        
        _, _, y_win_train, y_win_test = train_test_split(
            X, y_winner, test_size=0.2, random_state=42)
        
        _, _, y_pod_train, y_pod_test = train_test_split(
            X, y_podium, test_size=0.2, random_state=42)
        
        # 1. RANDOM FOREST
        print("\n🌲 Training Random Forest Models...")
        
        # Position prediction (regression)
        rf_position = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42)
        rf_position.fit(X_train, y_pos_train)
        
        # Winner prediction (classification)
        rf_winner = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42)
        rf_winner.fit(X_train, y_win_train)
        
        # Podium prediction (classification)
        rf_podium = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42)
        rf_podium.fit(X_train, y_pod_train)
        
        # 2. XGBOOST
        print("🚀 Training XGBoost Models...")
        
        # Position prediction
        xgb_position = xgb.XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
        xgb_position.fit(X_train, y_pos_train)
        
        # Winner prediction
        xgb_winner = xgb.XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
        xgb_winner.fit(X_train, y_win_train)
        
        # Podium prediction
        xgb_podium = xgb.XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
        xgb_podium.fit(X_train, y_pod_train)
        
        # 3. LOGISTIC REGRESSION
        print("📊 Training Logistic Regression Models...")
        
        # Winner prediction
        lr_winner = LogisticRegression(random_state=42, max_iter=1000)
        lr_winner.fit(X_train, y_win_train)
        
        # Podium prediction
        lr_podium = LogisticRegression(random_state=42, max_iter=1000)
        lr_podium.fit(X_train, y_pod_train)
        
        # Store models
        self.models = {
            'random_forest': {
                'position': rf_position,
                'winner': rf_winner,
                'podium': rf_podium
            },
            'xgboost': {
                'position': xgb_position,
                'winner': xgb_winner,
                'podium': xgb_podium
            },
            'logistic_regression': {
                'winner': lr_winner,
                'podium': lr_podium
            }
        }
        
        # Evaluate models
        self.evaluate_models(X_test, y_pos_test, y_win_test, y_pod_test)
        
    def evaluate_models(self, X_test, y_pos_test, y_win_test, y_pod_test):
        """Rigorous Model Evaluation with MAE and Accuracy"""
        print("\n📈 Rigorous Model Evaluation:")
        print("=" * 60)
        
        performance = {}
        
        # Random Forest Evaluation
        print("🌲 RANDOM FOREST:")
        
        # Position prediction (MAE)
        rf_pos_pred = self.models['random_forest']['position'].predict(X_test)
        rf_pos_mae = mean_absolute_error(y_pos_test, rf_pos_pred)
        print(f"   Position MAE: {rf_pos_mae:.3f}")
        
        # Winner prediction (Accuracy)
        rf_win_pred = self.models['random_forest']['winner'].predict(X_test)
        rf_win_acc = accuracy_score(y_win_test, rf_win_pred)
        print(f"   Winner Accuracy: {rf_win_acc:.3f}")
        
        # Podium prediction (Accuracy)
        rf_pod_pred = self.models['random_forest']['podium'].predict(X_test)
        rf_pod_acc = accuracy_score(y_pod_test, rf_pod_pred)
        print(f"   Podium Accuracy: {rf_pod_acc:.3f}")
        
        performance['random_forest'] = {
            'position_mae': rf_pos_mae,
            'winner_accuracy': rf_win_acc,
            'podium_accuracy': rf_pod_acc
        }
        
        # XGBoost Evaluation
        print("\n🚀 XGBOOST:")
        
        # Position prediction (MAE)
        xgb_pos_pred = self.models['xgboost']['position'].predict(X_test)
        xgb_pos_mae = mean_absolute_error(y_pos_test, xgb_pos_pred)
        print(f"   Position MAE: {xgb_pos_mae:.3f}")
        
        # Winner prediction (Accuracy)
        xgb_win_pred = self.models['xgboost']['winner'].predict(X_test)
        xgb_win_acc = accuracy_score(y_win_test, xgb_win_pred)
        print(f"   Winner Accuracy: {xgb_win_acc:.3f}")
        
        # Podium prediction (Accuracy)
        xgb_pod_pred = self.models['xgboost']['podium'].predict(X_test)
        xgb_pod_acc = accuracy_score(y_pod_test, xgb_pod_pred)
        print(f"   Podium Accuracy: {xgb_pod_acc:.3f}")
        
        performance['xgboost'] = {
            'position_mae': xgb_pos_mae,
            'winner_accuracy': xgb_win_acc,
            'podium_accuracy': xgb_pod_acc
        }
        
        # Logistic Regression Evaluation
        print("\n📊 LOGISTIC REGRESSION:")
        
        # Winner prediction (Accuracy)
        lr_win_pred = self.models['logistic_regression']['winner'].predict(X_test)
        lr_win_acc = accuracy_score(y_win_test, lr_win_pred)
        print(f"   Winner Accuracy: {lr_win_acc:.3f}")
        
        # Podium prediction (Accuracy)
        lr_pod_pred = self.models['logistic_regression']['podium'].predict(X_test)
        lr_pod_acc = accuracy_score(y_pod_test, lr_pod_pred)
        print(f"   Podium Accuracy: {lr_pod_acc:.3f}")
        
        performance['logistic_regression'] = {
            'winner_accuracy': lr_win_acc,
            'podium_accuracy': lr_pod_acc
        }
        
        self.model_performance = performance
        
        # Find best models
        print("\n🏆 BEST PERFORMING MODELS:")
        print("=" * 40)
        
        # Best position predictor
        best_position = min([
            ('Random Forest', rf_pos_mae),
            ('XGBoost', xgb_pos_mae)
        ], key=lambda x: x[1])
        print(f"Position Prediction: {best_position[0]} (MAE: {best_position[1]:.3f})")
        
        # Best winner predictor
        best_winner = max([
            ('Random Forest', rf_win_acc),
            ('XGBoost', xgb_win_acc),
            ('Logistic Regression', lr_win_acc)
        ], key=lambda x: x[1])
        print(f"Winner Prediction: {best_winner[0]} (Accuracy: {best_winner[1]:.3f})")
        
        # Best podium predictor
        best_podium = max([
            ('Random Forest', rf_pod_acc),
            ('XGBoost', xgb_pod_acc),
            ('Logistic Regression', lr_pod_acc)
        ], key=lambda x: x[1])
        print(f"Podium Prediction: {best_podium[0]} (Accuracy: {best_podium[1]:.3f})")
        
    def save_models(self):
        """Save ONLY the 3 best performing models + scaler + encoders (OPTIMIZED)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n💾 Saving ONLY the 3 BEST models (timestamp: {timestamp})...")
        print("🎯 OPTIMIZATION: Saving only Position, Winner, and Podium best models")
        print("=" * 70)
        
        # Determine the best algorithm for each task based on performance
        best_algorithms = {}
        
        # 1. Best Position Model (lowest MAE)
        position_scores = [
            ('random_forest', self.model_performance['random_forest']['position_mae']),
            ('xgboost', self.model_performance['xgboost']['position_mae'])
        ]
        best_position_algo = min(position_scores, key=lambda x: x[1])
        best_algorithms['position'] = {
            'algorithm': best_position_algo[0],
            'score': best_position_algo[1],
            'metric': 'MAE'
        }
        print(f"✓ Best POSITION model: {best_position_algo[0]} (MAE: {best_position_algo[1]:.3f})")
        
        # 2. Best Winner Model (highest accuracy)
        winner_scores = [
            ('random_forest', self.model_performance['random_forest']['winner_accuracy']),
            ('xgboost', self.model_performance['xgboost']['winner_accuracy']),
            ('logistic_regression', self.model_performance['logistic_regression']['winner_accuracy'])
        ]
        best_winner_algo = max(winner_scores, key=lambda x: x[1])
        best_algorithms['winner'] = {
            'algorithm': best_winner_algo[0],
            'score': best_winner_algo[1],
            'metric': 'Accuracy'
        }
        print(f"✓ Best WINNER model: {best_winner_algo[0]} (Accuracy: {best_winner_algo[1]:.3f})")
        
        # 3. Best Podium Model (highest accuracy)
        podium_scores = [
            ('random_forest', self.model_performance['random_forest']['podium_accuracy']),
            ('xgboost', self.model_performance['xgboost']['podium_accuracy']),
            ('logistic_regression', self.model_performance['logistic_regression']['podium_accuracy'])
        ]
        best_podium_algo = max(podium_scores, key=lambda x: x[1])
        best_algorithms['podium'] = {
            'algorithm': best_podium_algo[0],
            'score': best_podium_algo[1],
            'metric': 'Accuracy'
        }
        print(f"✓ Best PODIUM model: {best_podium_algo[0]} (Accuracy: {best_podium_algo[1]:.3f})")
        
        print("=" * 70)
        
        # Create best_models dictionary containing ONLY the 3 best models
        best_models = {
            'position': self.models[best_position_algo[0]]['position'],
            'winner': self.models[best_winner_algo[0]]['winner'],
            'podium': self.models[best_podium_algo[0]]['podium']
        }
        
        # Save ONLY the 3 best models
        model_files = {}
        
        # Save Position model
        position_filename = f"models/position_model_{timestamp}.pkl"
        with open(position_filename, 'wb') as f:
            pickle.dump(best_models['position'], f)
        model_files['position'] = position_filename
        print(f"💾 Saved: {position_filename}")
        
        # Save Winner model
        winner_filename = f"models/winner_model_{timestamp}.pkl"
        with open(winner_filename, 'wb') as f:
            pickle.dump(best_models['winner'], f)
        model_files['winner'] = winner_filename
        print(f"💾 Saved: {winner_filename}")
        
        # Save Podium model
        podium_filename = f"models/podium_model_{timestamp}.pkl"
        with open(podium_filename, 'wb') as f:
            pickle.dump(best_models['podium'], f)
        model_files['podium'] = podium_filename
        print(f"💾 Saved: {podium_filename}")
        
        # Save scalers and encoders
        scaler_file = f"models/scaler_{timestamp}.pkl"
        with open(scaler_file, 'wb') as f:
            pickle.dump(self.scalers, f)
        print(f"💾 Saved: {scaler_file}")
        
        encoder_file = f"models/encoders_{timestamp}.pkl"
        with open(encoder_file, 'wb') as f:
            pickle.dump(self.encoders, f)
        print(f"💾 Saved: {encoder_file}")
        
        # Save optimized metadata with ONLY the 3 best models
        metadata = {
            'timestamp': timestamp,
            'optimization': 'ENABLED - Only 3 best models saved',
            'best_models': {
                'position': {
                    'algorithm': best_algorithms['position']['algorithm'],
                    'file': position_filename,
                    'mae': best_algorithms['position']['score']
                },
                'winner': {
                    'algorithm': best_algorithms['winner']['algorithm'],
                    'file': winner_filename,
                    'accuracy': best_algorithms['winner']['score']
                },
                'podium': {
                    'algorithm': best_algorithms['podium']['algorithm'],
                    'file': podium_filename,
                    'accuracy': best_algorithms['podium']['score']
                }
            },
            'feature_columns': self.feature_columns,
            'model_performance': self.model_performance,
            'scaler_file': scaler_file,
            'encoder_file': encoder_file,
            'training_date': datetime.now().isoformat(),
            'total_models_saved': 3,
            'files_saved': [position_filename, winner_filename, podium_filename, scaler_file, encoder_file]
        }
        
        metadata_file = f"models/ml_metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Saved: {metadata_file}")
        print("=" * 70)
        print("✅ OPTIMIZATION COMPLETE!")
        print(f"📊 Total files saved: 5 (3 models + scaler + encoders)")
        print(f"💡 Computation reduced by saving only best-performing models")
        print("=" * 70)
        
        return timestamp
    
    def run_complete_training(self):
        """Run the complete ML training pipeline"""
        print("🏁 Starting Complete F1 ML Training Pipeline...")
        print("🎯 The Powerhouse: Random Forest + XGBoost + Logistic Regression")
        print("=" * 70)
        
        # 1. Generate training data
        df = self.generate_f1_training_data(n_samples=3000)
        
        # 2. Prepare features
        X, df = self.prepare_features(df)
        
        # 3. Prepare targets
        y_position = df['race_position'].values
        y_winner = df['race_winner'].values
        y_podium = df['podium_finish'].values
        
        # 4. Train models
        self.train_models(X, y_position, y_winner, y_podium)
        
        # 5. Save models
        timestamp = self.save_models()
        
        print("\n" + "=" * 70)
        print("🏆 F1 ML Training Complete!")
        print(f"📅 Models trained: {timestamp}")
        print("🚀 Ready for integration with DriveAhead F1 predictions!")
        print("=" * 70)
        
        return timestamp

if __name__ == "__main__":
    # Initialize and run training
    trainer = F1MLTrainingSystem()
    timestamp = trainer.run_complete_training()