"""
DriveAhead F1 - Machine Learning Model Training System
Implements Random Forest, XGBoost, and Logistic Regression for F1 Predictions
Based on presentation: The Powerhouse Machine Learning Algorithms
"""

import pandas as pd
import numpy as np
import pickle
import json
import requests
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
        """Save trained models and metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n💾 Saving trained models (timestamp: {timestamp})...")
        
        # Save models
        model_files = {}
        for algorithm in self.models:
            for task in self.models[algorithm]:
                filename = f"models/{algorithm}_{task}_{timestamp}.pkl"
                with open(filename, 'wb') as f:
                    pickle.dump(self.models[algorithm][task], f)
                model_files[f"{algorithm}_{task}"] = filename
                print(f"   Saved: {filename}")
        
        # Save scalers and encoders
        scaler_file = f"models/scaler_{timestamp}.pkl"
        with open(scaler_file, 'wb') as f:
            pickle.dump(self.scalers, f)
        
        encoder_file = f"models/encoders_{timestamp}.pkl"
        with open(encoder_file, 'wb') as f:
            pickle.dump(self.encoders, f)
        
        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'algorithms': ['random_forest', 'xgboost', 'logistic_regression'],
            'tasks': ['position', 'winner', 'podium'],
            'feature_columns': self.feature_columns,
            'model_performance': self.model_performance,
            'model_files': model_files,
            'scaler_file': scaler_file,
            'encoder_file': encoder_file,
            'training_date': datetime.now().isoformat()
        }
        
        metadata_file = f"models/ml_metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   Saved metadata: {metadata_file}")
        print("✅ All models saved successfully!")
        
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
        
        # Generate 2000+ race results for robust training
        data = []
        np.random.seed(42)  # For reproducible results
        
        for race_id in range(500):  # 500 races
            circuit = np.random.choice(circuits)
            weather = np.random.choice(['Dry', 'Wet', 'Mixed'])
            
            # Circuit characteristics affect performance
            circuit_features = self.get_circuit_characteristics(circuit)
            
            for position in range(1, 21):  # Top 20 positions
                driver = np.random.choice(drivers)
                team = self.get_driver_team(driver)
                
                # Realistic performance factors
                driver_skill = self.get_driver_skill_rating(driver)
                team_performance = self.get_team_performance_rating(team)
                
                # Generate realistic telemetry and performance data
                qualifying_position = max(1, min(20, position + np.random.randint(-5, 6)))
                grid_position = qualifying_position
                
                # Performance factors
                lap_time_avg = 90 + np.random.normal(0, 5)  # Average lap time in seconds
                top_speed = 320 + np.random.normal(0, 15)   # Top speed in km/h
                tire_strategy = np.random.choice(['Soft-Medium-Hard', 'Medium-Hard', 'Soft-Hard'])
                pit_stops = np.random.choice([1, 2, 3], p=[0.2, 0.6, 0.2])
                
                # Points system (realistic F1 points)
                points_mapping = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
                points = points_mapping.get(position, 0)
                
                # Binary classifications for different prediction tasks
                is_winner = 1 if position == 1 else 0
                is_podium = 1 if position <= 3 else 0
                is_points = 1 if position <= 10 else 0
                
                data.append({
                    'race_id': race_id,
                    'driver': driver,
                    'team': team,
                    'circuit': circuit,
                    'weather': weather,
                    'grid_position': grid_position,
                    'qualifying_position': qualifying_position,
                    'driver_skill_rating': driver_skill,
                    'team_performance_rating': team_performance,
                    'lap_time_avg': lap_time_avg,
                    'top_speed': top_speed,
                    'tire_strategy': tire_strategy,
                    'pit_stops': pit_stops,
                    'circuit_length': circuit_features['length'],
                    'circuit_corners': circuit_features['corners'],
                    'circuit_difficulty': circuit_features['difficulty'],
                    'position': position,
                    'points': points,
                    'is_winner': is_winner,
                    'is_podium': is_podium,
                    'is_points': is_points
                })
        
        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df)} training samples across {len(df['race_id'].unique())} races")
        return df
    
    def get_circuit_characteristics(self, circuit):
        """Get realistic circuit characteristics"""
        circuit_data = {
            'Monaco': {'length': 3.337, 'corners': 19, 'difficulty': 9},
            'Silverstone': {'length': 5.891, 'corners': 18, 'difficulty': 7},
            'Spa-Francorchamps': {'length': 7.004, 'corners': 19, 'difficulty': 8},
            'Monza': {'length': 5.793, 'corners': 11, 'difficulty': 5},
            'Suzuka': {'length': 5.807, 'corners': 18, 'difficulty': 8}
        }
        return circuit_data.get(circuit, {'length': 5.0, 'corners': 15, 'difficulty': 6})
    
    def get_driver_skill_rating(self, driver):
        """Realistic driver skill ratings (1-10)"""
        ratings = {
            'Max Verstappen': 9.8, 'Lewis Hamilton': 9.5, 'Charles Leclerc': 9.2,
            'Lando Norris': 8.8, 'Fernando Alonso': 9.3, 'George Russell': 8.5,
            'Carlos Sainz': 8.2, 'Sergio Perez': 8.0, 'Oscar Piastri': 8.3
        }
        return ratings.get(driver, 7.5 + np.random.normal(0, 0.5))
    
    def get_team_performance_rating(self, team):
        """Realistic team performance ratings (1-10)"""
        ratings = {
            'Red Bull Racing': 9.5, 'Mercedes': 8.5, 'Ferrari': 8.8,
            'McLaren': 8.3, 'Aston Martin': 7.5, 'Alpine': 7.0
        }
        return ratings.get(team, 6.5 + np.random.normal(0, 0.8))
    
    def get_driver_team(self, driver):
        """Map drivers to their teams"""
        driver_team_map = {
            'Max Verstappen': 'Red Bull Racing', 'Sergio Perez': 'Red Bull Racing',
            'Lewis Hamilton': 'Mercedes', 'George Russell': 'Mercedes',
            'Charles Leclerc': 'Ferrari', 'Carlos Sainz': 'Ferrari',
            'Lando Norris': 'McLaren', 'Oscar Piastri': 'McLaren',
            'Fernando Alonso': 'Aston Martin', 'Lance Stroll': 'Aston Martin'
        }
        return driver_team_map.get(driver, 'McLaren')
    
    def prepare_features(self, df):
        """Prepare features for machine learning"""
        print("\n🔧 Preparing features for ML training...")
        
        # Create feature encoders
        self.encoders['driver'] = LabelEncoder()
        self.encoders['team'] = LabelEncoder()
        self.encoders['circuit'] = LabelEncoder()
        self.encoders['weather'] = LabelEncoder()
        self.encoders['tire_strategy'] = LabelEncoder()
        
        # Encode categorical features
        df_encoded = df.copy()
        df_encoded['driver_encoded'] = self.encoders['driver'].fit_transform(df['driver'])
        df_encoded['team_encoded'] = self.encoders['team'].fit_transform(df['team'])
        df_encoded['circuit_encoded'] = self.encoders['circuit'].fit_transform(df['circuit'])
        df_encoded['weather_encoded'] = self.encoders['weather'].fit_transform(df['weather'])
        df_encoded['tire_strategy_encoded'] = self.encoders['tire_strategy'].fit_transform(df['tire_strategy'])
        
        # Select feature columns
        self.feature_columns = [
            'driver_encoded', 'team_encoded', 'circuit_encoded', 'weather_encoded',
            'grid_position', 'qualifying_position', 'driver_skill_rating',
            'team_performance_rating', 'lap_time_avg', 'top_speed',
            'tire_strategy_encoded', 'pit_stops', 'circuit_length',
            'circuit_corners', 'circuit_difficulty'
        ]
        
        X = df_encoded[self.feature_columns]
        
        # Scale numerical features
        self.scalers['features'] = StandardScaler()
        X_scaled = self.scalers['features'].fit_transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns=self.feature_columns)
        
        print(f"✅ Prepared {len(self.feature_columns)} features for training")
        return X_scaled_df, df_encoded
    
    def train_random_forest_models(self, X, y_dict):
        """Train Random Forest models for different prediction tasks"""
        print("\n🌳 Training Random Forest Models...")
        
        rf_models = {}
        
        # Winner Prediction (Classification)
        print("  📊 Training Winner Prediction Model...")
        rf_winner = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        rf_winner.fit(X, y_dict['is_winner'])
        rf_models['winner'] = rf_winner
        
        # Podium Prediction (Classification)
        print("  🏆 Training Podium Prediction Model...")
        rf_podium = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        rf_podium.fit(X, y_dict['is_podium'])
        rf_models['podium'] = rf_podium
        
        # Position Prediction (Regression)
        print("  🏁 Training Position Prediction Model...")
        rf_position = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        rf_position.fit(X, y_dict['position'])
        rf_models['position'] = rf_position
        
        return rf_models
    
    def train_xgboost_models(self, X, y_dict):
        """Train XGBoost models for different prediction tasks"""
        print("\n🚀 Training XGBoost Models...")
        
        xgb_models = {}
        
        # Winner Prediction (Classification)
        print("  📊 Training XGBoost Winner Prediction...")
        xgb_winner = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        xgb_winner.fit(X, y_dict['is_winner'])
        xgb_models['winner'] = xgb_winner
        
        # Podium Prediction (Classification)
        print("  🏆 Training XGBoost Podium Prediction...")
        xgb_podium = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        xgb_podium.fit(X, y_dict['is_podium'])
        xgb_models['podium'] = xgb_podium
        
        # Position Prediction (Regression)
        print("  🏁 Training XGBoost Position Prediction...")
        xgb_position = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='mae'
        )
        xgb_position.fit(X, y_dict['position'])
        xgb_models['position'] = xgb_position
        
        return xgb_models
    
    def train_logistic_regression_models(self, X, y_dict):
        """Train Logistic Regression models for classification tasks"""
        print("\n📈 Training Logistic Regression Models...")
        
        lr_models = {}
        
        # Winner Prediction
        print("  📊 Training Logistic Regression Winner Prediction...")
        lr_winner = LogisticRegression(
            random_state=42,
            class_weight='balanced',
            max_iter=1000
        )
        lr_winner.fit(X, y_dict['is_winner'])
        lr_models['winner'] = lr_winner
        
        # Podium Prediction
        print("  🏆 Training Logistic Regression Podium Prediction...")
        lr_podium = LogisticRegression(
            random_state=42,
            class_weight='balanced',
            max_iter=1000
        )
        lr_podium.fit(X, y_dict['is_podium'])
        lr_models['podium'] = lr_podium
        
        return lr_models
    
    def evaluate_models(self, models_dict, X_test, y_test_dict):
        """Rigorous Model Evaluation using industry-standard metrics"""
        print("\n📊 Rigorous Model Evaluation:")
        print("=" * 60)
        
        evaluation_results = {}
        
        for algorithm_name, models in models_dict.items():
            print(f"\n🤖 {algorithm_name.upper()} PERFORMANCE:")
            evaluation_results[algorithm_name] = {}
            
            # Winner Prediction Evaluation
            if 'winner' in models:
                y_pred_winner = models['winner'].predict(X_test)
                winner_accuracy = accuracy_score(y_test_dict['is_winner'], y_pred_winner)
                evaluation_results[algorithm_name]['winner_accuracy'] = winner_accuracy
                print(f"  🏆 Winner Prediction Accuracy: {winner_accuracy:.3f}")
            
            # Podium Prediction Evaluation
            if 'podium' in models:
                y_pred_podium = models['podium'].predict(X_test)
                podium_accuracy = accuracy_score(y_test_dict['is_podium'], y_pred_podium)
                evaluation_results[algorithm_name]['podium_accuracy'] = podium_accuracy
                print(f"  🥇 Podium Prediction Accuracy: {podium_accuracy:.3f}")
            
            # Position Prediction Evaluation (MAE)
            if 'position' in models:
                y_pred_position = models['position'].predict(X_test)
                position_mae = mean_absolute_error(y_test_dict['position'], y_pred_position)
                evaluation_results[algorithm_name]['position_mae'] = position_mae
                print(f"  📍 Position MAE (lower is better): {position_mae:.3f}")
        
        return evaluation_results
    
    def save_models(self, best_models, evaluation_results):
        """Save the best performing models"""
        print("\n💾 Saving trained models...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save models
        model_files = {}
        for task, model in best_models.items():
            filename = f"models/{task}_predictor_{timestamp}.pkl"
            with open(filename, 'wb') as f:
                pickle.dump(model, f)
            model_files[task] = filename
            print(f"  ✅ Saved {task} model: {filename}")
        
        # Save encoders and scalers
        with open(f"models/encoders_{timestamp}.pkl", 'wb') as f:
            pickle.dump(self.encoders, f)
        
        with open(f"models/scalers_{timestamp}.pkl", 'wb') as f:
            pickle.dump(self.scalers, f)
        
        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'models': list(best_models.keys()),
            'feature_columns': self.feature_columns,
            'evaluation_results': evaluation_results,
            'training_date': datetime.now().isoformat(),
            'model_files': model_files,
            'algorithms_used': ['Random Forest', 'XGBoost', 'Logistic Regression']
        }
        
        with open(f"models/model_metadata_{timestamp}.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✅ Saved metadata: models/model_metadata_{timestamp}.json")
        return metadata
    
    def run_complete_training(self):
        """Run the complete ML training pipeline"""
        print("🏁 DRIVEAHEAD F1 - MACHINE LEARNING TRAINING PIPELINE")
        print("=" * 70)
        
        # Step 1: Fetch/Generate training data
        df = self.fetch_training_data()
        
        # Step 2: Prepare features
        X, df_encoded = self.prepare_features(df)
        
        # Prepare target variables
        y_dict = {
            'is_winner': df_encoded['is_winner'],
            'is_podium': df_encoded['is_podium'],
            'position': df_encoded['position']
        }
        
        # Step 3: Split data
        X_train, X_test, y_train_winner, y_test_winner = train_test_split(
            X, y_dict['is_winner'], test_size=0.2, random_state=42, stratify=y_dict['is_winner']
        )
        
        y_train_dict = {
            'is_winner': y_train_winner,
            'is_podium': df_encoded['is_podium'][X_train.index],
            'position': df_encoded['position'][X_train.index]
        }
        
        y_test_dict = {
            'is_winner': y_test_winner,
            'is_podium': df_encoded['is_podium'][X_test.index],
            'position': df_encoded['position'][X_test.index]
        }
        
        # Step 4: Train all algorithms
        rf_models = self.train_random_forest_models(X_train, y_train_dict)
        xgb_models = self.train_xgboost_models(X_train, y_train_dict)
        lr_models = self.train_logistic_regression_models(X_train, y_train_dict)
        
        all_models = {
            'Random Forest': rf_models,
            'XGBoost': xgb_models,
            'Logistic Regression': lr_models
        }
        
        # Step 5: Evaluate all models
        evaluation_results = self.evaluate_models(all_models, X_test, y_test_dict)
        
        # Step 6: Select best models for each task
        best_models = self.select_best_models(all_models, evaluation_results)
        
        # Step 7: Save models
        metadata = self.save_models(best_models, evaluation_results)
        
        print("\n🎉 MODEL TRAINING COMPLETE!")
        print("=" * 50)
        print("📊 Summary of Best Models:")
        for task, model in best_models.items():
            algorithm = model.__class__.__name__
            print(f"  🏆 {task.title()}: {algorithm}")
        
        return metadata
    
    def select_best_models(self, all_models, evaluation_results):
        """Select the best performing model for each task"""
        best_models = {}
        
        # Best Winner Prediction Model
        best_winner_acc = 0
        best_winner_algo = None
        for algo, results in evaluation_results.items():
            if 'winner_accuracy' in results and results['winner_accuracy'] > best_winner_acc:
                best_winner_acc = results['winner_accuracy']
                best_winner_algo = algo
        
        if best_winner_algo:
            best_models['winner'] = all_models[best_winner_algo]['winner']
        
        # Best Podium Prediction Model
        best_podium_acc = 0
        best_podium_algo = None
        for algo, results in evaluation_results.items():
            if 'podium_accuracy' in results and results['podium_accuracy'] > best_podium_acc:
                best_podium_acc = results['podium_accuracy']
                best_podium_algo = algo
        
        if best_podium_algo:
            best_models['podium'] = all_models[best_podium_algo]['podium']
        
        # Best Position Prediction Model (lowest MAE)
        best_position_mae = float('inf')
        best_position_algo = None
        for algo, results in evaluation_results.items():
            if 'position_mae' in results and results['position_mae'] < best_position_mae:
                best_position_mae = results['position_mae']
                best_position_algo = algo
        
        if best_position_algo:
            best_models['position'] = all_models[best_position_algo]['position']
        
        return best_models

if __name__ == "__main__":
    # Run the complete training pipeline
    trainer = F1MLTrainingSystem()
    metadata = trainer.run_complete_training()
    
    print(f"\n🚀 Training completed! Check models/ directory for saved models.")
    print(f"📁 Metadata saved as: {metadata['timestamp']}")