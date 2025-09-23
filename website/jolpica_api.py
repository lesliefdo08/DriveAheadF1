"""
Jolpica API Integration for F1 Historical Data
Replacement for deprecated Ergast API
"""
import requests
import pandas as pd
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JolpicaF1API:
    """
    Professional F1 Data API using Jolpica (Ergast replacement)
    Provides: race results, driver stats, constructor data, circuit info, standings
    """
    
    def __init__(self):
        # Use official Ergast API as fallback to Jolpica
        self.base_url = "http://ergast.com/api/f1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DriveAhead F1 Analytics/1.0',
            'Accept': 'application/json'
        })
        
        # Cache for repeated requests
        self.cache = {}
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling and caching"""
        cache_key = f"{endpoint}_{str(params)}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            url = f"{self.base_url}/{endpoint}.json"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.cache[cache_key] = data
            
            # Add small delay to be respectful to API
            time.sleep(0.1)
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return {}
    
    def get_season_races(self, season: int = 2024) -> Dict:
        """Get all races for a season"""
        try:
            data = self._make_request(f"{season}")
            return data
        except Exception as e:
            logger.error(f"Error fetching season races: {e}")
            return {}
    
    def get_current_season_standings(self, season: int = 2024) -> pd.DataFrame:
        """Get current driver championship standings"""
        try:
            data = self._make_request(f"{season}/driverStandings")
            
            if 'MRData' not in data:
                return pd.DataFrame()
                
            standings_list = data['MRData'].get('StandingsTable', {}).get('StandingsLists', [])
            
            if not standings_list:
                return pd.DataFrame()
            
            drivers_standings = []
            for standing in standings_list[0].get('DriverStandings', []):
                driver_data = {
                    'position': int(standing['position']),
                    'points': float(standing['points']),
                    'wins': int(standing['wins']),
                    'driver_id': standing['Driver']['driverId'],
                    'driver_name': f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}",
                    'constructor': standing['Constructors'][0]['name'],
                    'constructor_id': standing['Constructors'][0]['constructorId'],
                    'nationality': standing['Driver']['nationality']
                }
                drivers_standings.append(driver_data)
            
            return pd.DataFrame(drivers_standings)
            
        except Exception as e:
            logger.error(f"Error fetching driver standings: {e}")
            return pd.DataFrame()
    
    def get_constructor_standings(self, season: int = 2024) -> pd.DataFrame:
        """Get constructor championship standings"""
        try:
            data = self._make_request(f"{season}/constructorStandings")
            
            if 'MRData' not in data:
                return pd.DataFrame()
                
            standings_list = data['MRData'].get('StandingsTable', {}).get('StandingsLists', [])
            
            if not standings_list:
                return pd.DataFrame()
            
            constructor_standings = []
            for standing in standings_list[0].get('ConstructorStandings', []):
                constructor_data = {
                    'position': int(standing['position']),
                    'points': float(standing['points']),
                    'wins': int(standing['wins']),
                    'constructor_id': standing['Constructor']['constructorId'],
                    'constructor_name': standing['Constructor']['name'],
                    'nationality': standing['Constructor']['nationality']
                }
                constructor_standings.append(constructor_data)
            
            return pd.DataFrame(constructor_standings)
            
        except Exception as e:
            logger.error(f"Error fetching constructor standings: {e}")
            return pd.DataFrame()
    
    def get_race_schedule(self, season: int = 2024) -> pd.DataFrame:
        """Get race schedule for the season"""
        try:
            data = self._make_request(f"{season}/races")
            
            if 'MRData' not in data:
                return pd.DataFrame()
                
            races = data['MRData'].get('RaceTable', {}).get('Races', [])
            
            if not races:
                return pd.DataFrame()
            
            race_schedule = []
            for race in races:
                race_data = {
                    'round': int(race['round']),
                    'race_name': race['raceName'],
                    'circuit_id': race['Circuit']['circuitId'],
                    'circuit_name': race['Circuit']['circuitName'],
                    'locality': race['Circuit']['Location']['locality'],
                    'country': race['Circuit']['Location']['country'],
                    'date': race['date'],
                    'time': race.get('time', ''),
                    'season': int(race['season']),
                    'url': race.get('url', '')
                }
                race_schedule.append(race_data)
            
            return pd.DataFrame(race_schedule)
            
        except Exception as e:
            logger.error(f"Error fetching race schedule: {e}")
            return pd.DataFrame()
    
    def get_next_race(self, season: int = 2024) -> Dict:
        """Get information about the next upcoming race"""
        try:
            schedule = self.get_race_schedule(season)
            
            if schedule.empty:
                return {}
            
            # Convert date strings to datetime for comparison
            current_date = datetime.now()
            schedule['date_obj'] = pd.to_datetime(schedule['date'])
            
            # Find next race (first race after current date)
            upcoming_races = schedule[schedule['date_obj'] >= current_date]
            
            if upcoming_races.empty:
                # If no upcoming races, get the last race of the season
                next_race = schedule.iloc[-1]
            else:
                next_race = upcoming_races.iloc[0]
            
            return {
                'round': next_race['round'],
                'race_name': next_race['race_name'],
                'circuit_id': next_race['circuit_id'],
                'circuit_name': next_race['circuit_name'],
                'locality': next_race['locality'],
                'country': next_race['country'],
                'date': next_race['date'],
                'time': next_race.get('time', ''),
                'season': next_race['season']
            }
            
        except Exception as e:
            logger.error(f"Error finding next race: {e}")
            return {}

    def get_race_results(self, season: int, round_number: int = None) -> pd.DataFrame:
        """Get race results for specific season/round"""
        try:
            endpoint = f"{season}/results" if round_number is None else f"{season}/{round_number}/results"
            data = self._make_request(endpoint)
            
            if 'MRData' not in data:
                return pd.DataFrame()
            
            races = data['MRData'].get('RaceTable', {}).get('Races', [])
            all_results = []
            
            for race in races:
                race_info = {
                    'season': season,
                    'round': int(race['round']),
                    'race_name': race['raceName'],
                    'circuit_id': race['Circuit']['circuitId'],
                    'circuit_name': race['Circuit']['circuitName'],
                    'date': race['date'],
                    'country': race['Circuit']['Location']['country']
                }
                
                for result in race.get('Results', []):
                    result_data = {
                        **race_info,
                        'position': result.get('position'),
                        'points': float(result.get('points', 0)),
                        'driver_id': result['Driver']['driverId'],
                        'driver_name': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                        'constructor_id': result['Constructor']['constructorId'],
                        'constructor_name': result['Constructor']['name'],
                        'grid': result.get('grid'),
                        'laps': result.get('laps'),
                        'status': result['status'],
                        'fastest_lap_rank': result.get('FastestLap', {}).get('rank'),
                        'fastest_lap_time': result.get('FastestLap', {}).get('Time', {}).get('time'),
                    }
                    all_results.append(result_data)
            
            return pd.DataFrame(all_results)
            
        except Exception as e:
            logger.error(f"Error fetching race results: {e}")
            return pd.DataFrame()
    
    def get_circuits_info(self, season: int = 2024) -> pd.DataFrame:
        """Get circuit information for season"""
        try:
            data = self._make_request(f"{season}/circuits")
            
            if 'MRData' not in data:
                return pd.DataFrame()
            
            circuits = data['MRData'].get('CircuitTable', {}).get('Circuits', [])
            circuit_data = []
            
            for circuit in circuits:
                circuit_info = {
                    'circuit_id': circuit['circuitId'],
                    'circuit_name': circuit['circuitName'],
                    'country': circuit['Location']['country'],
                    'locality': circuit['Location']['locality'],
                    'latitude': float(circuit['Location']['lat']),
                    'longitude': float(circuit['Location']['long']),
                    'url': circuit['url']
                }
                circuit_data.append(circuit_info)
            
            return pd.DataFrame(circuit_data)
            
        except Exception as e:
            logger.error(f"Error fetching circuits info: {e}")
            return pd.DataFrame()
    
    def get_season_schedule(self, season: int = 2025) -> pd.DataFrame:
        """Get race schedule for season"""
        try:
            data = self._make_request(f"{season}")
            
            if 'MRData' not in data:
                return pd.DataFrame()
            
            races = data['MRData'].get('RaceTable', {}).get('Races', [])
            schedule_data = []
            
            for race in races:
                race_info = {
                    'season': season,
                    'round': int(race['round']),
                    'race_name': race['raceName'],
                    'circuit_id': race['Circuit']['circuitId'],
                    'circuit_name': race['Circuit']['circuitName'],
                    'country': race['Circuit']['Location']['country'],
                    'locality': race['Circuit']['Location']['locality'],
                    'date': race['date'],
                    'time': race.get('time'),
                    'url': race['url']
                }
                schedule_data.append(race_info)
            
            return pd.DataFrame(schedule_data)
            
        except Exception as e:
            logger.error(f"Error fetching season schedule: {e}")
            return pd.DataFrame()
    
    def get_driver_career_stats(self, driver_id: str) -> Dict:
        """Get comprehensive driver career statistics"""
        try:
            # Get driver info
            data = self._make_request(f"drivers/{driver_id}")
            
            if 'MRData' not in data:
                return {}
            
            drivers = data['MRData'].get('DriverTable', {}).get('Drivers', [])
            if not drivers:
                return {}
            
            driver = drivers[0]
            driver_info = {
                'driver_id': driver['driverId'],
                'name': f"{driver['givenName']} {driver['familyName']}",
                'nationality': driver['nationality'],
                'date_of_birth': driver['dateOfBirth'],
                'permanent_number': driver.get('permanentNumber'),
                'code': driver.get('code'),
                'url': driver['url']
            }
            
            # Get race results for this driver
            results_data = self._make_request(f"drivers/{driver_id}/results")
            wins = 0
            podiums = 0
            points_total = 0
            races_count = 0
            
            if 'MRData' in results_data:
                races = results_data['MRData'].get('RaceTable', {}).get('Races', [])
                for race in races:
                    for result in race.get('Results', []):
                        races_count += 1
                        position = result.get('position')
                        if position:
                            pos = int(position)
                            if pos == 1:
                                wins += 1
                            if pos <= 3:
                                podiums += 1
                        
                        points_total += float(result.get('points', 0))
            
            driver_info.update({
                'career_wins': wins,
                'career_podiums': podiums,
                'career_points': points_total,
                'career_races': races_count,
                'win_percentage': (wins / races_count * 100) if races_count > 0 else 0,
                'podium_percentage': (podiums / races_count * 100) if races_count > 0 else 0
            })
            
            return driver_info
            
        except Exception as e:
            logger.error(f"Error fetching driver career stats: {e}")
            return {}
    
    def get_recent_form(self, driver_id: str, races_count: int = 5) -> Dict:
        """Get driver's recent form over last N races"""
        try:
            data = self._make_request(f"drivers/{driver_id}/results")
            
            if 'MRData' not in data:
                return {'recent_form_score': 5.0}
            
            races = data['MRData'].get('RaceTable', {}).get('Races', [])
            
            # Get most recent races
            recent_results = []
            for race in races[-races_count:]:
                for result in race.get('Results', []):
                    position = result.get('position')
                    if position and position.isdigit():
                        recent_results.append({
                            'position': int(position),
                            'points': float(result.get('points', 0)),
                            'race': race['raceName'],
                            'date': race['date']
                        })
            
            if not recent_results:
                return {'recent_form_score': 5.0}
            
            # Calculate form score (1-10 scale)
            total_score = 0
            for result in recent_results:
                # Position scoring: P1=10, P2=9, P3=8, P4=7, P5=6, P6-P10=4, P11-P20=2, DNF=0
                pos = result['position']
                if pos == 1:
                    score = 10
                elif pos == 2:
                    score = 9
                elif pos == 3:
                    score = 8
                elif pos <= 5:
                    score = 7 - (pos - 4)
                elif pos <= 10:
                    score = 4
                elif pos <= 20:
                    score = 2
                else:
                    score = 0
                
                total_score += score
            
            form_score = total_score / len(recent_results)
            
            return {
                'recent_form_score': round(form_score, 1),
                'recent_results': recent_results,
                'races_analyzed': len(recent_results)
            }
            
        except Exception as e:
            logger.error(f"Error calculating recent form for {driver_id}: {e}")
            return {'recent_form_score': 5.0}

# Example usage and testing
if __name__ == "__main__":
    api = JolpicaF1API()
    
    print("🏁 Testing Jolpica F1 API Integration...")
    
    # Test driver standings
    standings = api.get_current_season_standings(2024)
    print(f"Driver standings shape: {standings.shape}")
    if not standings.empty:
        print(standings.head())
    
    # Test recent form
    form = api.get_recent_form('leclerc')
    print(f"Leclerc recent form: {form}")