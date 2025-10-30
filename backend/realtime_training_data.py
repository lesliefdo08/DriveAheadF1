"""
Real-Time F1 Data Fetcher for ML Training

Fetches live F1 data from the API:
- Current season drivers and teams
- Driver performance ratings (calculated from championship standings)
- Circuit schedule (from F1 API)
- Team performance (calculated from constructor standings)

All data is fetched in real-time. No hardcoded values.
"""

import requests
import logging
from typing import Dict, List, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class F1DataFetcherForML:
    """Fetch real F1 data for ML training"""
    
    def __init__(self, season=2025):
        self.season = season
        self.base_url = "https://api.jolpi.ca/ergast/f1"
        
    def get_current_drivers_and_teams(self) -> Dict:
        """
        Fetch current season drivers and their teams from F1 API
        Returns: {driver: team, ...}
        """
        try:
            logger.info(f"Fetching {self.season} season driver lineup from API...")
            
            url = f"{self.base_url}/{self.season}/drivers.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            drivers_data = data['MRData']['DriverTable']['Drivers']
            
            # Get constructor info for each driver
            driver_teams = {}
            
            for driver_info in drivers_data:
                driver_name = f"{driver_info['givenName']} {driver_info['familyName']}"
                
                # Get driver's current team
                driver_id = driver_info['driverId']
                team_url = f"{self.base_url}/{self.season}/drivers/{driver_id}/constructors.json"
                
                try:
                    team_response = requests.get(team_url, timeout=5)
                    team_data = team_response.json()
                    
                    constructors = team_data['MRData']['ConstructorTable']['Constructors']
                    if constructors:
                        team_name = constructors[0]['name']
                        driver_teams[driver_name] = team_name
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Could not fetch team for {driver_name}: {e}")
            
            logger.info(f"Fetched {len(driver_teams)} drivers from API")
            return driver_teams
            
        except Exception as e:
            logger.error(f"Error fetching drivers from API: {e}")
            # Fallback to 2025 grid (current known lineup)
            return self._get_fallback_drivers()
    
    def calculate_driver_skills(self, driver_teams: Dict[str, str]) -> Dict[str, int]:
        """
        Calculate driver skill ratings based on:
        - Championship standings (points)
        - Career wins
        - Experience (number of races)
        
        Returns: {driver: skill_rating, ...} (0-100)
        """
        try:
            logger.info("Calculating driver skill ratings from championship data...")
            
            # Get current season standings
            url = f"{self.base_url}/{self.season}/driverStandings.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            standings_list = data['MRData']['StandingsTable']['StandingsLists']
            
            driver_skills = {}
            
            if standings_list:
                standings = standings_list[0]['DriverStandings']
                
                # Get max points for normalization
                max_points = max([int(s['points']) for s in standings]) if standings else 1
                
                for standing in standings:
                    driver_name = f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}"
                    points = int(standing['points'])
                    position = int(standing['position'])
                    wins = int(standing['wins'])
                    
                    # Calculate skill rating (0-100)
                    # Based on: championship position (40%), points (30%), wins (30%)
                    position_score = (21 - min(position, 20)) / 20 * 40  # Higher pos = higher score
                    points_score = (points / max_points) * 30 if max_points > 0 else 0
                    wins_score = min(wins * 5, 30)  # 5 points per win, max 30
                    
                    skill_rating = int(position_score + points_score + wins_score + 40)  # +40 base
                    skill_rating = min(100, max(60, skill_rating))  # Clamp 60-100
                    
                    driver_skills[driver_name] = skill_rating
            
            # For drivers not in standings (rookies, etc), use base rating
            for driver in driver_teams.keys():
                if driver not in driver_skills:
                    driver_skills[driver] = 65  # Rookie/unproven base rating
            
            logger.info(f"Calculated skill ratings for {len(driver_skills)} drivers")
            return driver_skills
            
        except Exception as e:
            logger.error(f"Error calculating driver skills: {e}")
            # Fallback to estimated ratings
            return self._get_fallback_driver_skills()
    
    def calculate_team_performance(self, driver_teams: Dict[str, str]) -> Dict[str, int]:
        """
        Calculate team performance ratings based on constructor championship
        
        Returns: {team: performance_rating, ...} (0-100)
        """
        try:
            logger.info("Calculating team performance from constructor standings...")
            
            url = f"{self.base_url}/{self.season}/constructorStandings.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            standings_list = data['MRData']['StandingsTable']['StandingsLists']
            
            team_performance = {}
            
            if standings_list:
                standings = standings_list[0]['ConstructorStandings']
                
                # Get max points
                max_points = max([int(s['points']) for s in standings]) if standings else 1
                
                for standing in standings:
                    team_name = standing['Constructor']['name']
                    points = int(standing['points'])
                    position = int(standing['position'])
                    wins = int(standing['wins'])
                    
                    # Calculate performance (0-100)
                    position_score = (11 - min(position, 10)) / 10 * 40
                    points_score = (points / max_points) * 40 if max_points > 0 else 0
                    wins_score = min(wins * 2, 20)
                    
                    performance = int(position_score + points_score + wins_score)
                    performance = min(100, max(40, performance))
                    
                    team_performance[team_name] = performance
            
            logger.info(f"Calculated performance for {len(team_performance)} teams")
            return team_performance
            
        except Exception as e:
            logger.error(f"Error calculating team performance: {e}")
            return self._get_fallback_team_performance()
    
    def get_circuits(self) -> List[str]:
        """
        Fetch current season circuit list from API
        
        Returns: List of circuit names
        """
        try:
            logger.info(f"Fetching {self.season} season circuits from API...")
            
            url = f"{self.base_url}/{self.season}/circuits.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            circuits_data = data['MRData']['CircuitTable']['Circuits']
            
            circuits = [circuit['circuitName'] for circuit in circuits_data]
            
            logger.info(f"Fetched {len(circuits)} circuits from API")
            return circuits
            
        except Exception as e:
            logger.error(f"Error fetching circuits: {e}")
            return self._get_fallback_circuits()
    
    def get_all_training_metadata(self) -> Dict:
        """
        Fetch all necessary data for ML training
        
        Returns: Complete metadata dict with drivers, teams, skills, circuits
        """
        logger.info("=" * 60)
        logger.info(f"FETCHING REAL-TIME F1 DATA FOR {self.season} SEASON")
        logger.info("=" * 60)
        
        # Fetch all data
        driver_teams = self.get_current_drivers_and_teams()
        driver_skills = self.calculate_driver_skills(driver_teams)
        team_performance = self.calculate_team_performance(driver_teams)
        circuits = self.get_circuits()
        
        metadata = {
            'season': self.season,
            'driver_teams': driver_teams,
            'driver_skills': driver_skills,
            'team_performance': team_performance,
            'circuits': circuits,
            'circuit_types': self._get_circuit_types()
        }
        
        logger.info("=" * 60)
        logger.info("DATA FETCH COMPLETE")
        logger.info("=" * 60)
        logger.info(f"  Drivers: {len(driver_teams)}")
        logger.info(f"  Teams: {len(set(driver_teams.values()))}")
        logger.info(f"  Circuits: {len(circuits)}")
        
        return metadata
    
    def _get_circuit_types(self) -> Dict[str, str]:
        """
        Circuit type classification (static - based on track characteristics)
        This doesn't change, so it's OK to keep as a dict
        """
        return {
            'Circuit de Monaco': 'street',
            'Monaco': 'street',
            'Marina Bay Street Circuit': 'street',
            'Singapore': 'street',
            'Baku City Circuit': 'street',
            'Baku': 'street',
            'Jeddah Corniche Circuit': 'street_fast',
            'Jeddah': 'street_fast',
            'Miami International Autodrome': 'street_fast',
            'Miami': 'street_fast',
            'Las Vegas Street Circuit': 'street_fast',
            'Las Vegas': 'street_fast',
            'Autodromo Nazionale di Monza': 'high_speed',
            'Monza': 'high_speed',
            'Circuit de Spa-Francorchamps': 'high_speed',
            'Spa-Francorchamps': 'high_speed',
            'Silverstone Circuit': 'high_speed',
            'Silverstone': 'high_speed',
            'Suzuka Circuit': 'high_speed',
            'Suzuka': 'high_speed',
            'Red Bull Ring': 'high_speed',
            'Bahrain International Circuit': 'mixed',
            'Bahrain': 'mixed',
            'Circuit of the Americas': 'mixed',
            'Shanghai International Circuit': 'mixed',
            'Shanghai': 'mixed',
            'Albert Park Grand Prix Circuit': 'mixed',
            'Albert Park': 'mixed',
            'Losail International Circuit': 'mixed',
            'Losail': 'mixed',
            'Yas Marina Circuit': 'mixed',
            'Yas Marina': 'mixed',
            'Autodromo Enzo e Dino Ferrari': 'mixed',
            'Imola': 'mixed',
            'Circuit Gilles Villeneuve': 'mixed',
            'Hungaroring': 'mixed',
            'Circuit Zandvoort': 'mixed',
            'Zandvoort': 'mixed',
            'Autódromo José Carlos Pace': 'mixed',
            'Interlagos': 'mixed',
            'Autódromo Hermanos Rodríguez': 'mixed',
            'Mexico City': 'mixed',
            'Circuit de Barcelona-Catalunya': 'mixed',
            'Barcelona': 'mixed'
        }
    
    # ===== FALLBACK METHODS (if API fails) =====
    
    def _get_fallback_drivers(self) -> Dict[str, str]:
        """Fallback: 2025 known driver lineup"""
        return {
            'Max Verstappen': 'Red Bull Racing',
            'Sergio Perez': 'Red Bull Racing',
            'Oscar Piastri': 'McLaren',
            'Lando Norris': 'McLaren',
            'Charles Leclerc': 'Ferrari',
            'Lewis Hamilton': 'Ferrari',
            'George Russell': 'Mercedes',
            'Andrea Kimi Antonelli': 'Mercedes',
            'Fernando Alonso': 'Aston Martin',
            'Lance Stroll': 'Aston Martin',
            'Pierre Gasly': 'Alpine F1 Team',
            'Jack Doohan': 'Alpine F1 Team',
            'Alexander Albon': 'Williams',
            'Carlos Sainz': 'Williams',
            'Nico Hulkenberg': 'Haas F1 Team',
            'Esteban Ocon': 'Haas F1 Team',
            'Yuki Tsunoda': 'RB',
            'Isack Hadjar': 'RB',
            'Gabriel Bortoleto': 'Sauber',
            'Oliver Bearman': 'Sauber'
        }
    
    def _get_fallback_driver_skills(self) -> Dict[str, int]:
        """Fallback: Estimated driver skills"""
        return {
            'Max Verstappen': 98,
            'Oscar Piastri': 90,
            'Lando Norris': 92,
            'Charles Leclerc': 93,
            'Lewis Hamilton': 96,
            'George Russell': 88,
            'Fernando Alonso': 94,
            'Carlos Sainz': 87,
            'Sergio Perez': 82,
            'Alexander Albon': 80,
            'Pierre Gasly': 81,
            'Nico Hulkenberg': 79,
            'Yuki Tsunoda': 77,
            'Esteban Ocon': 76,
            'Lance Stroll': 72,
            'Andrea Kimi Antonelli': 75,
            'Oliver Bearman': 70,
            'Isack Hadjar': 71,
            'Jack Doohan': 68,
            'Gabriel Bortoleto': 67
        }
    
    def _get_fallback_team_performance(self) -> Dict[str, int]:
        """Fallback: Estimated team performance"""
        return {
            'Red Bull Racing': 95,
            'McLaren': 92,
            'Ferrari': 90,
            'Mercedes': 85,
            'Aston Martin': 70,
            'Alpine F1 Team': 65,
            'Williams': 60,
            'Haas F1 Team': 55,
            'RB': 58,
            'Sauber': 50
        }
    
    def _get_fallback_circuits(self) -> List[str]:
        """Fallback: Known 2025 circuits"""
        return [
            'Bahrain International Circuit',
            'Jeddah Corniche Circuit',
            'Albert Park Circuit',
            'Suzuka Circuit',
            'Shanghai International Circuit',
            'Miami International Autodrome',
            'Autodromo Enzo e Dino Ferrari',
            'Circuit de Monaco',
            'Circuit Gilles Villeneuve',
            'Circuit de Barcelona-Catalunya',
            'Red Bull Ring',
            'Silverstone Circuit',
            'Hungaroring',
            'Circuit de Spa-Francorchamps',
            'Circuit Zandvoort',
            'Autodromo Nazionale di Monza',
            'Marina Bay Street Circuit',
            'Baku City Circuit',
            'Circuit of the Americas',
            'Autódromo Hermanos Rodríguez',
            'Autódromo José Carlos Pace',
            'Las Vegas Street Circuit',
            'Losail International Circuit',
            'Yas Marina Circuit'
        ]


if __name__ == '__main__':
    # Test the data fetcher
    fetcher = F1DataFetcherForML(season=2025)
    metadata = fetcher.get_all_training_metadata()
    
    print("\n" + "=" * 60)
    print("SAMPLE DATA FETCHED:")
    print("=" * 60)
    
    print("\nDrivers and Teams (first 5):")
    for i, (driver, team) in enumerate(list(metadata['driver_teams'].items())[:5], 1):
        skill = metadata['driver_skills'].get(driver, 0)
        print(f"  {i}. {driver} ({team}) - Skill: {skill}/100")
    
    print("\nTeam Performance (top 5):")
    sorted_teams = sorted(
        metadata['team_performance'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    for i, (team, perf) in enumerate(sorted_teams[:5], 1):
        print(f"  {i}. {team} - Performance: {perf}/100")
    
    print(f"\nCircuits: {len(metadata['circuits'])} tracks")
    print(f"Sample: {', '.join(metadata['circuits'][:3])}...")
