"""
Advanced F1 Race Day Prediction Engine
Real-time predictions during live races using telemetry and race data
"""

import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

class F1PredictionEngine:
    """Advanced F1 prediction system for race day"""
    
    def __init__(self):
        self.driver_ratings = {
            "Max Verstappen": {"skill": 98, "consistency": 96, "racecraft": 97},
            "Lando Norris": {"skill": 94, "consistency": 92, "racecraft": 91},
            "Charles Leclerc": {"skill": 96, "consistency": 88, "racecraft": 93},
            "Oscar Piastri": {"skill": 90, "consistency": 91, "racecraft": 89},
            "Carlos Sainz": {"skill": 92, "consistency": 89, "racecraft": 91},
            "Lewis Hamilton": {"skill": 97, "consistency": 94, "racecraft": 98},
            "George Russell": {"skill": 89, "consistency": 93, "racecraft": 87},
            "Sergio Perez": {"skill": 88, "consistency": 85, "racecraft": 90}
        }
        
        self.team_performance = {
            "Red Bull Racing": {"car_pace": 95, "strategy": 94, "reliability": 92},
            "McLaren": {"car_pace": 93, "strategy": 89, "reliability": 91},
            "Ferrari": {"car_pace": 91, "strategy": 85, "reliability": 88},
            "Mercedes": {"car_pace": 87, "strategy": 92, "reliability": 94}
        }
        
        self.track_characteristics = {
            "Baku City Circuit": {
                "overtaking": 85,
                "strategy_impact": 75,
                "tire_degradation": 60,
                "weather_sensitivity": 40
            }
        }
    
    def calculate_race_winner_probability(self, telemetry_data: Dict) -> Dict[str, float]:
        """Calculate live race winner probabilities based on current race state"""
        probabilities = {}
        
        for driver_name, data in telemetry_data.items():
            if driver_name == "_meta" or "session" in driver_name:
                continue
                
            # Base probability from driver skill and current position
            base_prob = self.driver_ratings.get(driver_name, {}).get("skill", 80) / 100
            position_factor = max(0.1, (9 - data.get("position", 8)) / 8)
            
            # Current race factors
            gap_factor = 1.0
            if "gap" in data and data["gap"] != "Leader":
                gap_seconds = self._parse_gap(data["gap"])
                gap_factor = max(0.1, 1 - (gap_seconds / 60))  # Reduce probability for larger gaps
            
            # Car health and strategy factors
            car_health = data.get("car_health", {})
            health_factor = sum(car_health.values()) / (len(car_health) * 100) if car_health else 0.9
            
            # Tire strategy impact
            tire_age = data.get("tyre_age", 20)
            tire_factor = max(0.5, 1 - (tire_age / 50))
            
            # Combine all factors
            final_prob = base_prob * position_factor * gap_factor * health_factor * tire_factor
            probabilities[driver_name] = min(0.95, max(0.01, final_prob))
        
        # Normalize probabilities
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            probabilities = {k: v/total_prob for k, v in probabilities.items()}
        
        return dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True))
    
    def predict_podium_finishers(self, telemetry_data: Dict) -> List[Dict]:
        """Predict podium finishers with confidence levels"""
        winner_probs = self.calculate_race_winner_probability(telemetry_data)
        
        podium_predictions = []
        for i, (driver, prob) in enumerate(list(winner_probs.items())[:3]):
            confidence = prob * 100
            podium_predictions.append({
                "position": i + 1,
                "driver": driver,
                "probability": round(prob, 3),
                "confidence": f"{confidence:.1f}%",
                "reasoning": self._generate_reasoning(driver, telemetry_data.get(driver, {}))
            })
        
        return podium_predictions
    
    def predict_fastest_lap(self, telemetry_data: Dict) -> Dict:
        """Predict who will get fastest lap"""
        candidates = {}
        
        for driver_name, data in telemetry_data.items():
            if driver_name == "_meta" or "session" in driver_name:
                continue
            
            # Factors: current pace, car performance, track position
            current_speed = data.get("speed", 250)
            best_lap_time = self._parse_lap_time(data.get("best_lap", "1:42.000"))
            position = data.get("position", 8)
            
            # Calculate fastest lap probability
            pace_factor = current_speed / 300
            lap_time_factor = max(0.1, 1 - ((best_lap_time - 98.0) / 10))  # Normalize around 1:38
            position_factor = max(0.3, (9 - position) / 8)
            
            probability = pace_factor * lap_time_factor * position_factor
            candidates[driver_name] = probability
        
        if candidates:
            best_candidate = max(candidates.keys(), key=lambda x: candidates[x])
            return {
                "driver": best_candidate,
                "probability": round(candidates[best_candidate], 3),
                "confidence": f"{candidates[best_candidate] * 100:.1f}%"
            }
        
        return {"driver": "Max Verstappen", "probability": 0.75, "confidence": "75.0%"}
    
    def predict_race_strategy(self, telemetry_data: Dict) -> Dict:
        """Predict optimal race strategies"""
        strategies = {}
        
        for driver_name, data in telemetry_data.items():
            if driver_name == "_meta" or "session" in driver_name:
                continue
            
            tire_age = data.get("tyre_age", 20)
            position = data.get("position", 8)
            fuel_load = data.get("fuel_load", 50)
            
            # Determine strategy based on current state
            if tire_age > 25:
                strategy = "Pit Soon"
                confidence = "High"
            elif position <= 3 and fuel_load > 60:
                strategy = "One-Stop"
                confidence = "Medium"
            elif position > 5:
                strategy = "Aggressive"
                confidence = "Medium"
            else:
                strategy = "Conservative"
                confidence = "Low"
            
            strategies[driver_name] = {
                "recommended": strategy,
                "confidence": confidence,
                "reasoning": f"Based on P{position}, {tire_age}-lap tires, {fuel_load}kg fuel"
            }
        
        return strategies
    
    def generate_live_insights(self, telemetry_data: Dict, session_data: Dict) -> List[str]:
        """Generate live race insights and predictions"""
        insights = []
        
        # Track status insights
        track_status = session_data.get("track_status", "Green")
        if track_status != "Green":
            insights.append(f"🚨 {track_status} flag conditions affecting race strategy")
        
        # Weather insights
        weather = session_data.get("weather", {})
        temp = weather.get("temperature", 25)
        if temp > 35:
            insights.append("🌡️ High track temperatures favoring hard compound tires")
        elif temp < 15:
            insights.append("❄️ Cool conditions may benefit tire warm-up strategies")
        
        # Leader gap analysis
        leader_data = None
        for driver, data in telemetry_data.items():
            if data.get("gap") == "Leader":
                leader_data = data
                break
        
        if leader_data:
            speed = leader_data.get("speed", 0)
            if speed > 320:
                insights.append("💨 Leader hitting peak speeds on main straight")
            elif speed < 200:
                insights.append("🏎️ Technical sector with lower speeds favoring handling")
        
        # DRS insights
        drs_count = sum(1 for d in telemetry_data.values() 
                       if isinstance(d, dict) and d.get("drs") == "Open")
        if drs_count > 3:
            insights.append("📡 Multiple cars using DRS - overtaking opportunities ahead")
        
        # Pit window analysis
        old_tires = sum(1 for d in telemetry_data.values() 
                       if isinstance(d, dict) and d.get("tyre_age", 0) > 25)
        if old_tires > 2:
            insights.append("🔧 Pit window opening - expect strategic battles")
        
        return insights[:4]  # Return top 4 insights
    
    def _parse_gap(self, gap_str: str) -> float:
        """Parse gap string to seconds"""
        if gap_str == "Leader" or not gap_str:
            return 0.0
        try:
            return float(gap_str.replace("+", "").replace("s", ""))
        except:
            return 5.0
    
    def _parse_lap_time(self, lap_time_str: str) -> float:
        """Parse lap time to seconds"""
        try:
            if ":" in lap_time_str:
                parts = lap_time_str.split(":")
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            return float(lap_time_str)
        except:
            return 100.0
    
    def _generate_reasoning(self, driver: str, data: Dict) -> str:
        """Generate reasoning for predictions"""
        position = data.get("position", 8)
        gap = data.get("gap", "+5.0")
        
        if position == 1:
            return f"Leading the race with strong pace"
        elif position <= 3:
            return f"In podium position, {gap} gap to leader"
        else:
            return f"Fighting from P{position}, needs strategic advantage"


# Global prediction engine instance
prediction_engine = F1PredictionEngine()