"""
OpenF1 API Data Manager
Handles all interactions with the OpenF1 API for live and historical F1 telemetry data.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import threading
import sqlite3
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CarTelemetry:
    """Data class for car telemetry information"""
    driver_number: int
    date: str
    speed: float
    throttle: int
    brake: int
    gear: int
    rpm: int
    drs: int
    
@dataclass
class DriverInfo:
    """Data class for driver information"""
    driver_number: int
    name_acronym: str
    full_name: str
    team_name: str
    team_colour: str
    broadcast_name: str

@dataclass
class SessionInfo:
    """Data class for session information"""
    session_key: int
    meeting_key: int
    session_name: str
    date_start: str
    date_end: str
    circuit_short_name: str
    country_name: str
    location: str

class OpenF1Manager:
    """
    Manager class for interacting with the OpenF1 API.
    Provides methods for fetching live and historical F1 data.
    """
    
    def __init__(self, cache_duration_minutes=5, use_cache=True):
        self.base_url = "https://api.openf1.org/v1"
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.use_cache = use_cache
        self.cache = {}
        self.cache_db_path = os.path.join('cache', 'openf1_cache.db')
        self._init_cache_db()
        
    def _init_cache_db(self):
        """Initialize SQLite cache database"""
        os.makedirs('cache', exist_ok=True)
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_cache (
                    endpoint TEXT PRIMARY KEY,
                    data TEXT,
                    timestamp REAL
                )
            ''')
            conn.commit()
    
    def _get_cached_data(self, endpoint: str) -> Optional[Dict]:
        """Retrieve cached data if still valid"""
        if not self.use_cache:
            return None
            
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute(
                    'SELECT data, timestamp FROM api_cache WHERE endpoint = ?',
                    (endpoint,)
                )
                result = cursor.fetchone()
                
                if result:
                    data_str, timestamp = result
                    cached_time = datetime.fromtimestamp(timestamp)
                    
                    if datetime.now() - cached_time < self.cache_duration:
                        return json.loads(data_str)
                        
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            
        return None
    
    def _cache_data(self, endpoint: str, data: Dict):
        """Cache API response data"""
        if not self.use_cache:
            return
            
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO api_cache (endpoint, data, timestamp) VALUES (?, ?, ?)',
                    (endpoint, json.dumps(data), time.time())
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make HTTP request to OpenF1 API with caching"""
        cache_key = f"{endpoint}_{params}" if params else endpoint
        
        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            logger.info(f"Using cached data for {endpoint}")
            return cached_data
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self._cache_data(cache_key, data)
            
            logger.info(f"Successfully fetched {len(data) if isinstance(data, list) else 1} records from {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            # Try to return stale cached data as fallback
            return self._get_stale_cache(cache_key)
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {e}")
            return []
    
    def _get_stale_cache(self, cache_key: str) -> Dict:
        """Get stale cached data as fallback"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute(
                    'SELECT data FROM api_cache WHERE endpoint = ?',
                    (cache_key,)
                )
                result = cursor.fetchone()
                
                if result:
                    logger.warning(f"Using stale cached data for {cache_key}")
                    return json.loads(result[0])
        except Exception as e:
            logger.error(f"Failed to retrieve stale cache: {e}")
        
        return []
    
    def get_latest_session(self) -> Optional[SessionInfo]:
        """Get the most recent F1 session"""
        try:
            data = self._make_request("sessions", {"session_key": "latest"})
            if data:
                session = data[0]
                return SessionInfo(
                    session_key=session['session_key'],
                    meeting_key=session['meeting_key'],
                    session_name=session['session_name'],
                    date_start=session['date_start'],
                    date_end=session['date_end'],
                    circuit_short_name=session['circuit_short_name'],
                    country_name=session['country_name'],
                    location=session['location']
                )
        except Exception as e:
            logger.error(f"Failed to get latest session: {e}")
        
        return None
    
    def get_session_by_date(self, year: int = 2023, country_name: str = None) -> Optional[SessionInfo]:
        """Get a specific session by year and optionally country"""
        try:
            params = {"year": year, "session_name": "Race"}
            if country_name:
                params["country_name"] = country_name
                
            data = self._make_request("sessions", params)
            if data:
                session = data[0]  # Get first race session
                return SessionInfo(
                    session_key=session['session_key'],
                    meeting_key=session['meeting_key'],
                    session_name=session['session_name'],
                    date_start=session['date_start'],
                    date_end=session['date_end'],
                    circuit_short_name=session['circuit_short_name'],
                    country_name=session['country_name'],
                    location=session['location']
                )
        except Exception as e:
            logger.error(f"Failed to get session for {year} {country_name}: {e}")
        
        return None
    
    def get_drivers(self, session_key: int) -> List[DriverInfo]:
        """Get all drivers for a session"""
        try:
            data = self._make_request("drivers", {"session_key": session_key})
            drivers = []
            
            for driver in data:
                drivers.append(DriverInfo(
                    driver_number=driver['driver_number'],
                    name_acronym=driver['name_acronym'],
                    full_name=driver['full_name'],
                    team_name=driver['team_name'],
                    team_colour=driver['team_colour'],
                    broadcast_name=driver['broadcast_name']
                ))
            
            return drivers
        except Exception as e:
            logger.error(f"Failed to get drivers for session {session_key}: {e}")
            return []
    
    def get_car_data(self, session_key: int, driver_number: int = None, 
                     limit: int = 100) -> List[CarTelemetry]:
        """Get car telemetry data for a session and optionally specific driver"""
        try:
            params = {"session_key": session_key}
            if driver_number:
                params["driver_number"] = driver_number
            
            # Add limit to prevent massive responses
            data = self._make_request("car_data", params)
            
            # Limit the results to prevent overwhelming the system
            if isinstance(data, list) and len(data) > limit:
                # Take evenly distributed samples
                step = len(data) // limit
                data = data[::step][:limit]
            
            telemetry_data = []
            for car_data in data:
                telemetry_data.append(CarTelemetry(
                    driver_number=car_data['driver_number'],
                    date=car_data['date'],
                    speed=car_data.get('speed', 0),
                    throttle=car_data.get('throttle', 0),
                    brake=car_data.get('brake', 0),
                    gear=car_data.get('n_gear', 0),
                    rpm=car_data.get('rpm', 0),
                    drs=car_data.get('drs', 0)
                ))
            
            return telemetry_data
        except Exception as e:
            logger.error(f"Failed to get car data for session {session_key}: {e}")
            return []
    
    def get_weather(self, session_key: int) -> Dict:
        """Get weather data for a session"""
        try:
            data = self._make_request("weather", {"session_key": session_key})
            if data:
                weather = data[-1]  # Get latest weather data
                return {
                    'air_temperature': weather.get('air_temperature', 25),
                    'track_temperature': weather.get('track_temperature', 45),
                    'humidity': weather.get('humidity', 60),
                    'wind_speed': weather.get('wind_speed', 5),
                    'wind_direction': weather.get('wind_direction', 0),
                    'rainfall': weather.get('rainfall', 0)
                }
        except Exception as e:
            logger.error(f"Failed to get weather for session {session_key}: {e}")
        
        # Return default values if API fails
        return {
            'air_temperature': 25,
            'track_temperature': 45,
            'humidity': 60,
            'wind_speed': 5,
            'wind_direction': 0,
            'rainfall': 0
        }
    
    def get_driver_positions(self, session_key: int) -> Dict[int, int]:
        """Get current positions for all drivers"""
        try:
            data = self._make_request("position", {"session_key": session_key})
            positions = {}
            
            # Get the latest position for each driver
            for position_data in data:
                driver_num = position_data['driver_number']
                position = position_data['position']
                positions[driver_num] = position
            
            return positions
        except Exception as e:
            logger.error(f"Failed to get positions for session {session_key}: {e}")
            return {}
    
    def get_lap_times(self, session_key: int, driver_number: int = None) -> List[Dict]:
        """Get lap times for a session"""
        try:
            params = {"session_key": session_key}
            if driver_number:
                params["driver_number"] = driver_number
            
            data = self._make_request("laps", params)
            lap_times = []
            
            for lap in data:
                lap_times.append({
                    'driver_number': lap['driver_number'],
                    'lap_number': lap['lap_number'],
                    'lap_duration': lap.get('lap_duration'),
                    'sector_1': lap.get('duration_sector_1'),
                    'sector_2': lap.get('duration_sector_2'),
                    'sector_3': lap.get('duration_sector_3'),
                    'i1_speed': lap.get('i1_speed'),
                    'i2_speed': lap.get('i2_speed'),
                    'st_speed': lap.get('st_speed')
                })
            
            return lap_times
        except Exception as e:
            logger.error(f"Failed to get lap times for session {session_key}: {e}")
            return []
    
    def get_intervals(self, session_key: int) -> List[Dict]:
        """Get real-time intervals between drivers"""
        try:
            data = self._make_request("intervals", {"session_key": session_key})
            intervals = []
            
            for interval in data:
                intervals.append({
                    'driver_number': interval['driver_number'],
                    'gap_to_leader': interval.get('gap_to_leader'),
                    'interval': interval.get('interval'),
                    'date': interval['date']
                })
            
            return intervals
        except Exception as e:
            logger.error(f"Failed to get intervals for session {session_key}: {e}")
            return []
    
    def get_comprehensive_telemetry(self, session_key: int, 
                                   driver_numbers: List[int] = None) -> Dict:
        """Get comprehensive telemetry data for telemetry dashboard"""
        try:
            # Get session info
            session_info = None
            sessions = self._make_request("sessions", {"session_key": session_key})
            if sessions:
                session_info = sessions[0]
            
            # Get drivers
            drivers = self.get_drivers(session_key)
            
            # Filter drivers if specific numbers requested
            if driver_numbers:
                drivers = [d for d in drivers if d.driver_number in driver_numbers]
            
            # Get telemetry data for each driver
            comprehensive_data = {
                'session_info': session_info,
                'drivers': {d.driver_number: d.__dict__ for d in drivers},
                'telemetry': {},
                'weather': self.get_weather(session_key),
                'positions': self.get_driver_positions(session_key),
                'intervals': self.get_intervals(session_key)
            }
            
            # Get car data for each driver (limited to prevent overload)
            for driver in drivers:
                car_data = self.get_car_data(session_key, driver.driver_number, limit=50)
                comprehensive_data['telemetry'][driver.driver_number] = [
                    data.__dict__ for data in car_data
                ]
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive telemetry: {e}")
            return {}
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute('DELETE FROM api_cache')
                conn.commit()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

# Global instance for easy access
openf1_manager = OpenF1Manager()

def get_demo_session_data():
    """Get demo data for telemetry dashboard using historical F1 data"""
    try:
        # Get 2023 Singapore GP data (known to have good data)
        session = openf1_manager.get_session_by_date(2023, "Singapore")
        
        if not session:
            logger.warning("Failed to get Singapore GP session, trying latest session")
            session = openf1_manager.get_latest_session()
        
        if not session:
            logger.error("No session data available")
            return None
        
        logger.info(f"Using session: {session.session_name} at {session.circuit_short_name}")
        
        # Get comprehensive data for Verstappen (1) and Hamilton (44) if available
        drivers = openf1_manager.get_drivers(session.session_key)
        target_drivers = [1, 44]  # Verstappen and Hamilton
        
        # If target drivers not available, use first two drivers
        if not any(d.driver_number in target_drivers for d in drivers):
            target_drivers = [d.driver_number for d in drivers[:2]]
        
        comprehensive_data = openf1_manager.get_comprehensive_telemetry(
            session.session_key, 
            target_drivers
        )
        
        return comprehensive_data
        
    except Exception as e:
        logger.error(f"Failed to get demo session data: {e}")
        return None

if __name__ == "__main__":
    # Test the OpenF1 manager
    print("Testing OpenF1 Manager...")
    
    # Test getting latest session
    session = openf1_manager.get_latest_session()
    if session:
        print(f"Latest session: {session.session_name} at {session.circuit_short_name}")
        
        # Test getting drivers
        drivers = openf1_manager.get_drivers(session.session_key)
        print(f"Found {len(drivers)} drivers")
        
        if drivers:
            # Test getting car data for first driver
            car_data = openf1_manager.get_car_data(session.session_key, drivers[0].driver_number, limit=5)
            print(f"Got {len(car_data)} telemetry records for {drivers[0].name_acronym}")
            
            if car_data:
                sample = car_data[0]
                print(f"Sample telemetry: Speed={sample.speed}km/h, Throttle={sample.throttle}%, Brake={sample.brake}")
    
    # Test demo data function
    print("\nTesting demo data function...")
    demo_data = get_demo_session_data()
    if demo_data:
        print(f"Demo data loaded successfully with {len(demo_data['drivers'])} drivers")
    else:
        print("Failed to load demo data")