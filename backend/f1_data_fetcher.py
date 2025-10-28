"""
Real-time F1 Data Fetcher
Fetches live data from Jolpica F1 API (Ergast)
"""

import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class F1DataFetcher:
    """Fetches real-time F1 data from Jolpica API"""
    
    def __init__(self):
        self.base_url = "http://api.jolpi.ca/ergast/f1"
        self.current_season = 2025
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    def _get_cached_or_fetch(self, key: str, fetch_func, cache_duration: int = None):
        """Get data from cache or fetch if expired"""
        duration = cache_duration or self.cache_duration
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < duration:
                logger.info(f"Cache hit for {key}")
                return data
        
        logger.info(f"Fetching fresh data for {key}")
        data = fetch_func()
        self.cache[key] = (data, time.time())
        return data
    
    def get_current_standings(self) -> Dict:
        """Fetch current driver standings from Jolpica API"""
        def fetch():
            try:
                url = f"{self.base_url}/{self.current_season}/driverStandings.json"
                logger.info(f"Fetching driver standings from: {url}")
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                standings_list = data['MRData']['StandingsTable']['StandingsLists']
                
                if not standings_list:
                    logger.warning("No standings data available")
                    return self._get_fallback_standings()
                
                # Get the latest standings
                latest_standings = standings_list[0]
                round_num = latest_standings.get('round', 'Unknown')
                driver_standings = latest_standings['DriverStandings']
                
                # Format the data
                formatted_standings = []
                for standing in driver_standings:
                    formatted_standings.append({
                        'position': int(standing['position']),
                        'driver': f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}",
                        'driver_code': standing['Driver']['code'],
                        'team': standing['Constructors'][0]['name'],
                        'points': int(standing['points']),
                        'wins': int(standing['wins'])
                    })
                
                logger.info(f"Successfully fetched standings for round {round_num}")
                return {
                    'season': self.current_season,
                    'round': round_num,
                    'standings': formatted_standings,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'jolpica_api'
                }
                
            except Exception as e:
                logger.error(f"Error fetching driver standings: {e}")
                return self._get_fallback_standings()
        
        return self._get_cached_or_fetch('driver_standings', fetch)
    
    def get_constructor_standings(self) -> Dict:
        """Fetch current constructor standings"""
        def fetch():
            try:
                url = f"{self.base_url}/{self.current_season}/constructorStandings.json"
                logger.info(f"Fetching constructor standings from: {url}")
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                standings_list = data['MRData']['StandingsTable']['StandingsLists']
                
                if not standings_list:
                    return self._get_fallback_constructor_standings()
                
                latest_standings = standings_list[0]
                constructor_standings = latest_standings['ConstructorStandings']
                
                formatted_standings = []
                for standing in constructor_standings:
                    formatted_standings.append({
                        'position': int(standing['position']),
                        'team': standing['Constructor']['name'],
                        'points': int(standing['points']),
                        'wins': int(standing['wins'])
                    })
                
                return {
                    'season': self.current_season,
                    'standings': formatted_standings,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'jolpica_api'
                }
                
            except Exception as e:
                logger.error(f"Error fetching constructor standings: {e}")
                return self._get_fallback_constructor_standings()
        
        return self._get_cached_or_fetch('constructor_standings', fetch)
    
    def get_race_schedule(self) -> Dict:
        """Fetch complete race schedule for the season"""
        def fetch():
            try:
                url = f"{self.base_url}/{self.current_season}.json"
                logger.info(f"Fetching race schedule from: {url}")
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                races = data['MRData']['RaceTable']['Races']
                
                formatted_races = []
                for race in races:
                    formatted_races.append({
                        'round': int(race['round']),
                        'name': race['raceName'],
                        'circuit': race['Circuit']['circuitName'],
                        'location': race['Circuit']['Location']['locality'],
                        'country': race['Circuit']['Location']['country'],
                        'date': race['date'],
                        'time': race.get('time', '14:00:00Z')
                    })
                
                logger.info(f"Successfully fetched {len(formatted_races)} races")
                return {
                    'season': self.current_season,
                    'total_races': len(formatted_races),
                    'races': formatted_races,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'jolpica_api'
                }
                
            except Exception as e:
                logger.error(f"Error fetching race schedule: {e}")
                return self._get_fallback_race_schedule()
        
        return self._get_cached_or_fetch('race_schedule', fetch, cache_duration=3600)  # Cache for 1 hour
    
    def get_next_race(self) -> Dict:
        """Determine the next upcoming race"""
        try:
            schedule = self.get_race_schedule()
            races = schedule['races']
            
            now = datetime.now()
            
            for race in races:
                race_date = datetime.strptime(race['date'], '%Y-%m-%d')
                race_time = race.get('time', '14:00:00Z')
                
                # Combine date and time
                race_datetime_str = f"{race['date']}T{race_time}"
                race_datetime = datetime.strptime(race_datetime_str.replace('Z', '+00:00'), '%Y-%m-%dT%H:%M:%S%z')
                race_datetime = race_datetime.replace(tzinfo=None)  # Remove timezone for comparison
                
                if race_datetime > now:
                    logger.info(f"Next race: {race['name']} on {race['date']}")
                    return {
                        'race': race,
                        'last_updated': datetime.now().isoformat(),
                        'source': 'jolpica_api'
                    }
            
            # If no future races, return the last race
            logger.warning("No upcoming races found, returning last race")
            return {
                'race': races[-1] if races else self._get_fallback_next_race()['race'],
                'last_updated': datetime.now().isoformat(),
                'source': 'fallback'
            }
            
        except Exception as e:
            logger.error(f"Error determining next race: {e}")
            return self._get_fallback_next_race()
    
    def get_last_race_results(self) -> Dict:
        """Fetch results from the most recent completed race"""
        def fetch():
            try:
                url = f"{self.base_url}/{self.current_season}/last/results.json"
                logger.info(f"Fetching last race results from: {url}")
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                races = data['MRData']['RaceTable']['Races']
                
                if not races:
                    return self._get_fallback_last_race()
                
                race_data = races[0]
                results = race_data['Results']
                
                formatted_results = []
                for result in results[:10]:  # Top 10
                    formatted_results.append({
                        'position': int(result['position']),
                        'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                        'team': result['Constructor']['name'],
                        'time': result.get('Time', {}).get('time', 'N/A') if int(result['position']) == 1 else result.get('Time', {}).get('time', 'N/A'),
                        'points': float(result['points'])
                    })
                
                return {
                    'round': int(race_data['round']),
                    'race_name': race_data['raceName'],
                    'circuit': race_data['Circuit']['circuitName'],
                    'date': race_data['date'],
                    'results': formatted_results,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'jolpica_api'
                }
                
            except Exception as e:
                logger.error(f"Error fetching last race results: {e}")
                return self._get_fallback_last_race()
        
        return self._get_cached_or_fetch('last_race_results', fetch)
    
    def _get_fallback_standings(self) -> Dict:
        """Fallback driver standings (Singapore GP - Round 18)"""
        return {
            'season': 2025,
            'round': '18',
            'standings': [
                {'position': 1, 'driver': 'Oscar Piastri', 'driver_code': 'PIA', 'team': 'McLaren', 'points': 336, 'wins': 7},
                {'position': 2, 'driver': 'Lando Norris', 'driver_code': 'NOR', 'team': 'McLaren', 'points': 314, 'wins': 5},
                {'position': 3, 'driver': 'Max Verstappen', 'driver_code': 'VER', 'team': 'Red Bull', 'points': 273, 'wins': 4},
                {'position': 4, 'driver': 'George Russell', 'driver_code': 'RUS', 'team': 'Mercedes', 'points': 237, 'wins': 2},
                {'position': 5, 'driver': 'Charles Leclerc', 'driver_code': 'LEC', 'team': 'Ferrari', 'points': 173, 'wins': 0},
                {'position': 6, 'driver': 'Lewis Hamilton', 'driver_code': 'HAM', 'team': 'Ferrari', 'points': 125, 'wins': 0},
                {'position': 7, 'driver': 'Andrea Kimi Antonelli', 'driver_code': 'ANT', 'team': 'Mercedes', 'points': 88, 'wins': 0},
                {'position': 8, 'driver': 'Alexander Albon', 'driver_code': 'ALB', 'team': 'Williams', 'points': 70, 'wins': 0},
                {'position': 9, 'driver': 'Isack Hadjar', 'driver_code': 'HAD', 'team': 'RB F1 Team', 'points': 39, 'wins': 0},
                {'position': 10, 'driver': 'Nico Hulkenberg', 'driver_code': 'HUL', 'team': 'Sauber', 'points': 37, 'wins': 0}
            ],
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _get_fallback_constructor_standings(self) -> Dict:
        """Fallback constructor standings"""
        return {
            'season': 2025,
            'standings': [
                {'position': 1, 'team': 'McLaren', 'points': 650, 'wins': 12},
                {'position': 2, 'team': 'Mercedes', 'points': 325, 'wins': 2},
                {'position': 3, 'team': 'Ferrari', 'points': 298, 'wins': 0},
                {'position': 4, 'team': 'Red Bull', 'points': 290, 'wins': 4},
                {'position': 5, 'team': 'Williams', 'points': 102, 'wins': 0},
                {'position': 6, 'team': 'RB F1 Team', 'points': 72, 'wins': 0}
            ],
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _get_fallback_race_schedule(self) -> Dict:
        """Fallback race schedule"""
        return {
            'season': 2025,
            'total_races': 24,
            'races': [
                {'round': 19, 'name': 'United States Grand Prix', 'circuit': 'Circuit of the Americas', 'location': 'Austin', 'country': 'United States', 'date': '2025-10-19', 'time': '19:00:00Z'},
                {'round': 20, 'name': 'Mexico City Grand Prix', 'circuit': 'Autódromo Hermanos Rodríguez', 'location': 'Mexico City', 'country': 'Mexico', 'date': '2025-10-26', 'time': '20:00:00Z'},
                {'round': 21, 'name': 'Brazilian Grand Prix', 'circuit': 'Autódromo José Carlos Pace', 'location': 'São Paulo', 'country': 'Brazil', 'date': '2025-11-02', 'time': '17:00:00Z'},
                {'round': 22, 'name': 'Las Vegas Grand Prix', 'circuit': 'Las Vegas Street Circuit', 'location': 'Las Vegas', 'country': 'United States', 'date': '2025-11-22', 'time': '06:00:00Z'},
                {'round': 23, 'name': 'Qatar Grand Prix', 'circuit': 'Losail International Circuit', 'location': 'Lusail', 'country': 'Qatar', 'date': '2025-11-30', 'time': '17:00:00Z'},
                {'round': 24, 'name': 'Abu Dhabi Grand Prix', 'circuit': 'Yas Marina Circuit', 'location': 'Abu Dhabi', 'country': 'United Arab Emirates', 'date': '2025-12-07', 'time': '13:00:00Z'}
            ],
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _get_fallback_next_race(self) -> Dict:
        """Fallback next race"""
        return {
            'race': {
                'round': 19,
                'name': 'United States Grand Prix',
                'circuit': 'Circuit of the Americas',
                'location': 'Austin',
                'country': 'United States',
                'date': '2025-10-19',
                'time': '19:00:00Z'
            },
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _get_fallback_last_race(self) -> Dict:
        """Fallback last race results (Singapore GP)"""
        return {
            'round': 18,
            'race_name': 'Singapore Grand Prix',
            'circuit': 'Marina Bay Street Circuit',
            'date': '2025-10-05',
            'results': [
                {'position': 1, 'driver': 'George Russell', 'team': 'Mercedes', 'time': '1:40:22.367', 'points': 25.0},
                {'position': 2, 'driver': 'Max Verstappen', 'team': 'Red Bull', 'time': '+5.430s', 'points': 18.0},
                {'position': 3, 'driver': 'Lando Norris', 'team': 'McLaren', 'time': '+6.066s', 'points': 15.0},
                {'position': 4, 'driver': 'Oscar Piastri', 'team': 'McLaren', 'time': '+8.146s', 'points': 12.0},
                {'position': 5, 'driver': 'Andrea Kimi Antonelli', 'team': 'Mercedes', 'time': '+12.345s', 'points': 10.0}
            ],
            'last_updated': datetime.now().isoformat(),
            'source': 'fallback'
        }


# Create a global instance
f1_fetcher = F1DataFetcher()
