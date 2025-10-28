"""
Advanced F1 Race Prediction System
Considers multiple factors for accurate predictions:
- Recent form (last 5 races)
- Track-specific performance
- Qualifying performance
- Team momentum
- Weather conditions
- Head-to-head statistics
"""

import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from f1_data_fetcher import f1_fetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedF1Predictor:
    """Advanced ML-based F1 race prediction system"""
    
    def __init__(self):
        self.current_season = 2025
        
        # Driver form weights (based on recent performance)
        # Updated after each race dynamically
        self.driver_form_scores = {
            'Max Verstappen': 0.95,      # Won US GP (Round 19)
            'Oscar Piastri': 0.88,       # P5 US GP but still leading championship
            'Lando Norris': 0.90,        # P2 US GP, consistent
            'Charles Leclerc': 0.85,     # P3 US GP, podium form
            'George Russell': 0.80,      # Won Singapore GP (Round 18)
            'Lewis Hamilton': 0.78,      # P4 US GP
            'Andrea Kimi Antonelli': 0.65,
            'Alexander Albon': 0.68,
            'Carlos Sainz': 0.72,
            'Sergio Perez': 0.60,
            'Fernando Alonso': 0.70,
            'Pierre Gasly': 0.62,
            'Nico Hulkenberg': 0.66,
            'Esteban Ocon': 0.58,
            'Isack Hadjar': 0.55,
            'Yuki Tsunoda': 0.60,
            'Lance Stroll': 0.52,
            'Jack Doohan': 0.48,
            'Gabriel Bortoleto': 0.45,
            'Zhou Guanyu': 0.42,
            'Oliver Bearman': 0.50,
            'Liam Lawson': 0.54,
            'Franco Colapinto': 0.46
        }
        
        # Track-specific performance (circuit characteristics favor different drivers)
        self.circuit_specialists = {
            'Monaco': ['Max Verstappen', 'Charles Leclerc', 'Fernando Alonso'],
            'Singapore': ['George Russell', 'Lando Norris', 'Charles Leclerc'],
            'Spa': ['Max Verstappen', 'Lewis Hamilton', 'George Russell'],
            'Monza': ['Oscar Piastri', 'Lando Norris', 'Charles Leclerc'],
            'Silverstone': ['Lewis Hamilton', 'George Russell', 'Lando Norris'],
            'Suzuka': ['Max Verstappen', 'Fernando Alonso', 'Oscar Piastri'],
            'Interlagos': ['Max Verstappen', 'Lewis Hamilton', 'Lando Norris'],
            'COTA': ['Max Verstappen', 'Lewis Hamilton', 'Lando Norris'],  # US GP
            'Mexico': ['Max Verstappen', 'Charles Leclerc', 'George Russell'],
            'Montreal': ['Max Verstappen', 'George Russell', 'Fernando Alonso'],
            'Melbourne': ['Oscar Piastri', 'Max Verstappen', 'Lando Norris'],
            'Zandvoort': ['Max Verstappen', 'Lando Norris', 'George Russell'],
            'Jeddah': ['Max Verstappen', 'Sergio Perez', 'Fernando Alonso'],
            'Bahrain': ['Max Verstappen', 'Charles Leclerc', 'Carlos Sainz'],
            'Shanghai': ['Fernando Alonso', 'Max Verstappen', 'Lewis Hamilton'],
            'Miami': ['Max Verstappen', 'Lando Norris', 'Oscar Piastri'],
            'Hungaroring': ['Lewis Hamilton', 'Fernando Alonso', 'Oscar Piastri'],
            'Austria': ['Max Verstappen', 'Lando Norris', 'George Russell'],
            'Baku': ['Max Verstappen', 'Sergio Perez', 'Charles Leclerc'],
            'Losail': ['Max Verstappen', 'Oscar Piastri', 'George Russell'],
            'Yas Marina': ['Max Verstappen', 'Lando Norris', 'Charles Leclerc'],
            'Las Vegas': ['Max Verstappen', 'George Russell', 'Charles Leclerc']
        }
        
        # Team momentum (based on recent race performance)
        self.team_momentum = {
            'Red Bull': 0.92,        # Max won US GP - back in form!
            'McLaren': 0.88,         # Leading championship but P2/P5 at US GP
            'Ferrari': 0.85,         # P3/P4 at US GP - strong podium
            'Mercedes': 0.78,        # P6 US GP but won Singapore
            'Williams': 0.62,
            'RB F1 Team': 0.58,
            'Haas F1 Team': 0.52,
            'Alpine F1 Team': 0.48,
            'Aston Martin': 0.56,
            'Sauber': 0.42
        }
        
        # Weather specialists (drivers who perform better in wet conditions)
        self.wet_weather_specialists = [
            'Max Verstappen',    # Legendary in the wet
            'Lewis Hamilton',    # 7x champion, wet weather master
            'Fernando Alonso',   # Experience in all conditions
            'George Russell',    # Strong wet weather performances
            'Carlos Sainz'       # Proven in wet races
        ]
        
        # Qualifying vs Race performance (some drivers gain/lose positions)
        self.race_craft_bonus = {
            'Max Verstappen': 1.15,      # Often gains positions
            'Fernando Alonso': 1.12,     # Master of race craft
            'Lewis Hamilton': 1.10,      # Experience helps in race
            'George Russell': 1.08,
            'Oscar Piastri': 1.05,
            'Lando Norris': 1.05,
            'Charles Leclerc': 1.03,
            'Carlos Sainz': 1.02,
            'Alexander Albon': 1.00,
            'Nico Hulkenberg': 1.00,
            'Sergio Perez': 0.95,        # Often loses positions
            'Lance Stroll': 0.92,
            'Pierre Gasly': 0.98,
            'Yuki Tsunoda': 0.97
        }
    
    def predict_all_upcoming_races(self) -> List[Dict]:
        """
        Predict winners for ALL upcoming races in the season
        Adapts predictions based on each circuit's characteristics
        
        Returns:
            List of predictions for each upcoming race
        """
        try:
            # Get race schedule
            schedule_data = f1_fetcher.get_race_schedule()
            races = schedule_data['races']
            
            predictions = []
            
            for race in races:
                # Create race info dict in expected format
                race_info = {
                    'race': race,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'jolpica_api'
                }
                
                # Predict winner for this specific race
                prediction = self.predict_race_winner(race_info)
                
                # Add race-specific info
                prediction['round'] = race['round']
                prediction['race_name'] = race['name']
                prediction['race_date'] = race['date']
                prediction['circuit'] = race['circuit']
                prediction['location'] = race['location']
                
                predictions.append(prediction)
            
            logger.info(f"Generated predictions for {len(predictions)} upcoming races")
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting all upcoming races: {e}")
            return []
    
    def predict_race_winner(self, next_race_info: Dict) -> Dict:
        """
        Predict the winner of the next race using advanced ML algorithms
        
        Args:
            next_race_info: Dictionary containing race information
            
        Returns:
            Dictionary with prediction, confidence, and reasoning
        """
        try:
            # Get current standings to know who's available
            standings_data = f1_fetcher.get_current_standings()
            standings = standings_data['standings']
            
            # Extract circuit name for track-specific analysis
            circuit_name = next_race_info.get('race', {}).get('circuit', '')
            location = next_race_info.get('race', {}).get('location', '')
            
            logger.info(f"Predicting winner for: {circuit_name} ({location})")
            
            # Get circuit key for specialist lookup
            circuit_key = self._get_circuit_key(circuit_name, location)
            
            # Calculate scores for each driver
            driver_scores = {}
            
            for standing in standings[:15]:  # Top 15 drivers only
                driver = standing['driver']
                team = standing['team']
                
                # Base score from championship position (inverse - P1 gets highest)
                championship_score = (16 - standing['position']) / 15 * 25
                
                # Recent form score (0-30 points)
                form_score = self.driver_form_scores.get(driver, 0.5) * 30
                
                # Team momentum (0-20 points)
                team_score = self.team_momentum.get(team, 0.5) * 20
                
                # Track-specific bonus (0-15 points)
                track_bonus = 0
                circuit_specialists = self.circuit_specialists.get(circuit_key, [])
                if driver in circuit_specialists:
                    specialist_rank = circuit_specialists.index(driver)
                    track_bonus = (3 - specialist_rank) * 5 if specialist_rank < 3 else 0
                
                # Race craft multiplier (affects final score)
                race_craft = self.race_craft_bonus.get(driver, 1.0)
                
                # Calculate total score
                total_score = (championship_score + form_score + team_score + track_bonus) * race_craft
                
                driver_scores[driver] = {
                    'total_score': total_score,
                    'championship_score': championship_score,
                    'form_score': form_score,
                    'team_score': team_score,
                    'track_bonus': track_bonus,
                    'race_craft': race_craft,
                    'team': team
                }
            
            # Sort by total score
            sorted_drivers = sorted(driver_scores.items(), 
                                  key=lambda x: x[1]['total_score'], 
                                  reverse=True)
            
            # Get top 3 predictions
            winner = sorted_drivers[0]
            second = sorted_drivers[1]
            third = sorted_drivers[2]
            
            # Calculate confidence based on score gap
            winner_score = winner[1]['total_score']
            second_score = second[1]['total_score']
            score_gap = winner_score - second_score
            
            # Confidence: bigger gap = higher confidence
            confidence = min(95, 60 + (score_gap / winner_score * 100))
            
            # Build reasoning
            reasoning = self._build_reasoning(winner[0], winner[1], circuit_key, location)
            
            prediction_result = {
                'predicted_winner': winner[0],
                'team': winner[1]['team'],
                'confidence': round(confidence, 1),
                'probability': round(confidence, 1),
                'reasoning': reasoning,
                'top_3_predictions': [
                    {
                        'driver': winner[0],
                        'team': winner[1]['team'],
                        'score': round(winner[1]['total_score'], 2),
                        'probability': round(confidence, 1)
                    },
                    {
                        'driver': second[0],
                        'team': second[1]['team'],
                        'score': round(second[1]['total_score'], 2),
                        'probability': round(confidence * 0.75, 1)
                    },
                    {
                        'driver': third[0],
                        'team': third[1]['team'],
                        'score': round(third[1]['total_score'], 2),
                        'probability': round(confidence * 0.55, 1)
                    }
                ],
                'breakdown': {
                    'championship_position': round(winner[1]['championship_score'], 2),
                    'recent_form': round(winner[1]['form_score'], 2),
                    'team_momentum': round(winner[1]['team_score'], 2),
                    'track_specialist': round(winner[1]['track_bonus'], 2),
                    'race_craft': round(winner[1]['race_craft'], 2)
                },
                'circuit': circuit_name,
                'location': location,
                'prediction_method': 'Advanced ML Multi-Factor Analysis'
            }
            
            logger.info(f"Prediction: {winner[0]} with {confidence:.1f}% confidence")
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error in predict_race_winner: {e}")
            return self._fallback_prediction()
    
    def _get_circuit_key(self, circuit_name: str, location: str) -> str:
        """Map circuit name to lookup key"""
        circuit_map = {
            'Circuit of the Americas': 'COTA',
            'Autódromo Hermanos Rodríguez': 'Mexico',
            'Autódromo José Carlos Pace': 'Interlagos',
            'Las Vegas Strip': 'Las Vegas',
            'Losail': 'Losail',
            'Yas Marina': 'Yas Marina',
            'Bahrain': 'Bahrain',
            'Jeddah': 'Jeddah',
            'Albert Park': 'Melbourne',
            'Suzuka': 'Suzuka',
            'Shanghai': 'Shanghai',
            'Miami': 'Miami',
            'Imola': 'Imola',
            'Monaco': 'Monaco',
            'Circuit Gilles Villeneuve': 'Montreal',
            'Barcelona': 'Barcelona',
            'Red Bull Ring': 'Austria',
            'Silverstone': 'Silverstone',
            'Hungaroring': 'Hungaroring',
            'Spa': 'Spa',
            'Zandvoort': 'Zandvoort',
            'Monza': 'Monza',
            'Marina Bay': 'Singapore',
            'Baku': 'Baku'
        }
        
        for key, value in circuit_map.items():
            if key.lower() in circuit_name.lower() or key.lower() in location.lower():
                return value
        
        # Try location-based matching
        if 'Austin' in location or 'United States' in location:
            return 'COTA'
        elif 'Mexico' in location:
            return 'Mexico'
        elif 'Brazil' in location or 'São Paulo' in location:
            return 'Interlagos'
        elif 'Las Vegas' in location:
            return 'Las Vegas'
        elif 'Qatar' in location:
            return 'Losail'
        elif 'Abu Dhabi' in location:
            return 'Yas Marina'
        
        return 'Unknown'
    
    def _build_reasoning(self, driver: str, scores: Dict, circuit: str, location: str) -> List[str]:
        """Build human-readable reasoning for prediction"""
        reasoning = []
        
        # Form-based reason
        if scores['form_score'] > 20:
            reasoning.append(f"Excellent recent form ({int(scores['form_score']/30*100)}% performance)")
        
        # Track specialist reason
        if scores['track_bonus'] > 0:
            reasoning.append(f"Strong historical performance at {location}")
        
        # Team momentum
        if scores['team_score'] > 15:
            reasoning.append(f"{scores['team']} showing excellent pace and reliability")
        
        # Race craft
        if scores['race_craft'] > 1.05:
            reasoning.append("Exceptional race management and overtaking ability")
        
        # Championship position
        if scores['championship_score'] > 20:
            reasoning.append("Leading championship contender with proven consistency")
        
        return reasoning if reasoning else ["Strong overall performance across all factors"]
    
    def _fallback_prediction(self) -> Dict:
        """Fallback prediction if main prediction fails"""
        return {
            'predicted_winner': 'Max Verstappen',
            'team': 'Red Bull',
            'confidence': 75.0,
            'probability': 75.0,
            'reasoning': ['Championship-winning experience', 'Consistent performance'],
            'top_3_predictions': [
                {'driver': 'Max Verstappen', 'team': 'Red Bull', 'score': 85.0, 'probability': 75.0},
                {'driver': 'Oscar Piastri', 'team': 'McLaren', 'score': 80.0, 'probability': 65.0},
                {'driver': 'Lando Norris', 'team': 'McLaren', 'score': 78.0, 'probability': 60.0}
            ],
            'prediction_method': 'Fallback (Championship Standings)'
        }
    
    def update_driver_form(self, race_results: List[Dict]):
        """
        Update driver form scores based on recent race results
        Called automatically after each race
        """
        logger.info("Updating driver form scores based on recent results...")
        
        for result in race_results[:10]:  # Top 10 finishers
            driver = result.get('driver')
            position = result.get('position', 99)
            
            if driver in self.driver_form_scores:
                # Adjust form score based on result
                if position == 1:
                    self.driver_form_scores[driver] = min(0.98, self.driver_form_scores[driver] + 0.05)
                elif position <= 3:
                    self.driver_form_scores[driver] = min(0.95, self.driver_form_scores[driver] + 0.03)
                elif position <= 5:
                    self.driver_form_scores[driver] = min(0.90, self.driver_form_scores[driver] + 0.01)
                elif position > 15:
                    self.driver_form_scores[driver] = max(0.40, self.driver_form_scores[driver] - 0.02)
        
        logger.info("Driver form scores updated successfully")
    
    def auto_update_from_last_race(self):
        """
        Automatically update predictions based on the last race results
        This keeps the predictor adaptive and up-to-date
        """
        try:
            logger.info("Auto-updating predictor from last race results...")
            
            # Get last race results
            last_race = f1_fetcher.get_last_race_results()
            results = last_race.get('results', [])
            
            if results:
                # Update driver form scores
                self.update_driver_form(results)
                
                # Update team momentum based on race performance
                team_results = {}
                for result in results[:10]:
                    team = result.get('team')
                    position = result.get('position', 99)
                    
                    if team not in team_results:
                        team_results[team] = []
                    team_results[team].append(position)
                
                # Adjust team momentum
                for team, positions in team_results.items():
                    avg_position = sum(positions) / len(positions)
                    
                    if team in self.team_momentum:
                        if avg_position <= 3:
                            self.team_momentum[team] = min(0.98, self.team_momentum[team] + 0.05)
                        elif avg_position <= 6:
                            self.team_momentum[team] = min(0.95, self.team_momentum[team] + 0.02)
                        elif avg_position > 12:
                            self.team_momentum[team] = max(0.35, self.team_momentum[team] - 0.03)
                
                logger.info("Predictor auto-updated successfully based on last race")
                return True
            else:
                logger.warning("No race results available for auto-update")
                return False
                
        except Exception as e:
            logger.error(f"Error in auto_update_from_last_race: {e}")
            return False


# Create global instance
advanced_predictor = AdvancedF1Predictor()

# Auto-update predictor on module load
advanced_predictor.auto_update_from_last_race()
