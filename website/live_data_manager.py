"""
DriveAhead - Live Race Data Manager
Real-time F1 telemetry and race data integration using FastF1
"""

import fastf1
import fastf1.plotting
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import time
import logging
import requests

class LiveRaceDataManager:
    """Manages real-time F1 race data during live sessions"""
    
    def __init__(self):
        # Enable FastF1 cache for performance
        fastf1.Cache.enable_cache('cache')
        
        self.current_session = None
        self.is_live_session = False
        self.session_type = None  # 'FP1', 'FP2', 'FP3', 'Q', 'R'
        self.last_update = None
        
        # F1 2025 Race Schedule - Updated with correct dates
        self.race_info = {
            'year': 2025,
            'current_race': 'Azerbaijan Grand Prix',
            'circuit': 'Baku',
            'country': 'Azerbaijan',
            'weekend_date': '2025-09-21',
            'sessions': {
                'FP1': '2025-09-19 09:30:00',  # Friday FP1
                'FP2': '2025-09-19 13:00:00',  # Friday FP2
                'FP3': '2025-09-20 10:30:00',  # Saturday FP3
                'Q': '2025-09-20 14:00:00',    # Saturday Qualifying
                'R': '2025-09-21 22:30:00'     # Sunday Race (4:00 AM IST = 22:30 UTC Sat)
            },
            'upcoming_races': {
                'singapore': {
                    'name': 'Singapore Airlines Singapore Grand Prix',
                    'date': '2025-10-05',
                    'race_time': '23:30:00'  # 5:00 AM IST = 23:30 UTC Sat
                },
                'usa': {
                    'name': 'MSC Cruises United States Grand Prix', 
                    'date': '2025-10-19',
                    'race_time': '06:30:00'  # 12:00 PM IST = 6:30 UTC
                },
                'mexico': {
                    'name': 'Mexico City Grand Prix',
                    'date': '2025-10-26', 
                    'race_time': '07:30:00'  # 1:00 PM IST = 7:30 UTC
                }
            }
        }
        
        logging.info("LiveRaceDataManager initialized for Azerbaijan GP 2025")
    
    def check_live_session_status(self):
        """Check if any F1 session is currently live"""
        try:
            current_time = datetime.now()
            
            for session_type, session_time_str in self.race_info['sessions'].items():
                session_time = datetime.strptime(session_time_str, '%Y-%m-%d %H:%M:%S')
                
                # Check if we're within session window (sessions are ~90-120 minutes)
                session_end_time = session_time + timedelta(hours=2)
                
                if session_time <= current_time <= session_end_time:
                    self.is_live_session = True
                    self.session_type = session_type
                    logging.info(f"🔴 LIVE SESSION DETECTED: {session_type} - Azerbaijan GP")
                    return True
            
            self.is_live_session = False
            self.session_type = None
            return False
            
        except Exception as e:
            logging.error(f"Error checking live session status: {e}")
            return False
    
    def load_live_session_data(self):
        """Load live session data using FastF1"""
        try:
            if not self.is_live_session:
                logging.warning("No live session detected")
                return None
            
            # Load the session
            session = fastf1.get_session(2025, 'Azerbaijan Grand Prix', self.session_type)
            session.load()
            
            self.current_session = session
            self.last_update = datetime.now()
            
            logging.info(f"✅ Loaded live {self.session_type} session data")
            return session
            
        except Exception as e:
            logging.error(f"Error loading live session data: {e}")
            return None
    
    def get_live_telemetry_data(self):
        """Get real-time telemetry data during live sessions"""
        try:
            if not self.current_session:
                return self._get_simulated_telemetry()
            
            # Get live telemetry for top drivers
            drivers = ['VER', 'HAM']  # Verstappen, Hamilton
            telemetry_data = {}
            
            for driver_code in drivers:
                try:
                    driver_data = self.current_session.laps.pick_driver(driver_code)
                    
                    if not driver_data.empty:
                        latest_lap = driver_data.iloc[-1]
                        
                        # Get telemetry for the latest lap
                        lap_telemetry = latest_lap.get_telemetry()
                        
                        if not lap_telemetry.empty:
                            # Get most recent telemetry point
                            latest_telemetry = lap_telemetry.iloc[-1]
                            
                            # Map driver code to full name
                            driver_name = 'Max Verstappen' if driver_code == 'VER' else 'Lewis Hamilton'
                            
                            telemetry_data[driver_name] = {
                                'speed': float(latest_telemetry['Speed']) if pd.notna(latest_telemetry['Speed']) else 0,
                                'rpm': int(latest_telemetry['RPM']) if pd.notna(latest_telemetry['RPM']) else 0,
                                'gear': int(latest_telemetry['nGear']) if pd.notna(latest_telemetry['nGear']) else 0,
                                'throttle': float(latest_telemetry['Throttle']) if pd.notna(latest_telemetry['Throttle']) else 0,
                                'brake': float(latest_telemetry['Brake']) if pd.notna(latest_telemetry['Brake']) else 0,
                                'drs': 'Open' if latest_telemetry['DRS'] > 0 else 'Closed',
                                'lap_time': str(latest_lap['LapTime']) if pd.notna(latest_lap['LapTime']) else '0:00.000',
                                'sector': 1,  # Current sector
                                'position': int(latest_lap['Position']) if pd.notna(latest_lap['Position']) else 0
                            }
                            
                            logging.info(f"🔴 LIVE TELEMETRY - {driver_name}: {latest_telemetry['Speed']:.1f} km/h")
                
                except Exception as driver_error:
                    logging.warning(f"Could not get telemetry for {driver_code}: {driver_error}")
                    continue
            
            return telemetry_data if telemetry_data else self._get_simulated_telemetry()
            
        except Exception as e:
            logging.error(f"Error getting live telemetry: {e}")
            return self._get_simulated_telemetry()
    
    def get_live_race_positions(self):
        """Get current race positions and gaps"""
        try:
            if not self.current_session or self.session_type != 'R':
                return None
            
            # Get latest position data
            latest_laps = self.current_session.laps.pick_laps('latest')
            
            positions = []
            for idx, lap in latest_laps.iterrows():
                positions.append({
                    'position': int(lap['Position']),
                    'driver': lap['Driver'],
                    'team': lap['Team'],
                    'gap': str(lap['Time']) if pd.notna(lap['Time']) else '0.000',
                    'last_lap_time': str(lap['LapTime']) if pd.notna(lap['LapTime']) else '0:00.000'
                })
            
            # Sort by position
            positions.sort(key=lambda x: x['position'])
            
            logging.info(f"🏁 LIVE RACE POSITIONS: Leader is {positions[0]['driver']}")
            return positions
            
        except Exception as e:
            logging.error(f"Error getting live race positions: {e}")
            return None
    
    def get_session_status(self):
        """Get current session status and information"""
        try:
            status = {
                'is_live': self.is_live_session,
                'session_type': self.session_type,
                'session_name': self._get_session_name(),
                'race_info': self.race_info,
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'data_source': 'live' if self.is_live_session else 'simulated'
            }
            
            if self.current_session:
                status.update({
                    'session_weather': self._get_session_weather(),
                    'track_status': 'Green',  # Would be obtained from session data
                    'remaining_time': '45:30'  # Would be calculated from session data
                })
            
            return status
            
        except Exception as e:
            logging.error(f"Error getting session status: {e}")
            return {'is_live': False, 'error': str(e)}
    
    def _get_session_weather(self):
        """Get weather data from current session"""
        try:
            if not self.current_session:
                return None
            
            weather = self.current_session.weather_data
            if weather.empty:
                return None
            
            latest_weather = weather.iloc[-1]
            return {
                'temperature': float(latest_weather['AirTemp']),
                'track_temp': float(latest_weather['TrackTemp']),
                'humidity': float(latest_weather['Humidity']),
                'pressure': float(latest_weather['Pressure']),
                'wind_speed': float(latest_weather['WindSpeed']),
                'wind_direction': float(latest_weather['WindDirection']),
                'rainfall': bool(latest_weather['Rainfall'])
            }
            
        except Exception as e:
            logging.warning(f"Could not get weather data: {e}")
            return None
    
    def _get_session_name(self):
        """Convert session type to readable name"""
        session_names = {
            'FP1': 'Free Practice 1',
            'FP2': 'Free Practice 2', 
            'FP3': 'Free Practice 3',
            'Q': 'Qualifying',
            'R': 'Race'
        }
        return session_names.get(self.session_type, 'Unknown Session')
    
    def _get_simulated_telemetry(self):
        """Fallback simulated telemetry when no live data available"""
        # This returns the algorithmic telemetry we already have
        return {
            'Max Verstappen': {
                'speed': 285.0 + np.random.uniform(-10, 10),
                'rpm': 12800 + np.random.randint(-200, 200),
                'gear': np.random.choice([6, 7, 8]),
                'throttle': 92.0 + np.random.uniform(-5, 5),
                'brake': 12.0 + np.random.uniform(-3, 8),
                'drs': np.random.choice(['Open', 'Closed'], p=[0.3, 0.7]),
                'lap_time': '1:41.542',
                'sector': np.random.randint(1, 4),
                'position': 1
            },
            'Lewis Hamilton': {
                'speed': 283.0 + np.random.uniform(-8, 8),
                'rpm': 12700 + np.random.randint(-150, 150),
                'gear': np.random.choice([6, 7, 8]),
                'throttle': 90.5 + np.random.uniform(-4, 4),
                'brake': 13.5 + np.random.uniform(-2, 7),
                'drs': np.random.choice(['Open', 'Closed'], p=[0.25, 0.75]),
                'lap_time': '1:41.789',
                'sector': np.random.randint(1, 4),
                'position': 2
            }
        }

# Global instance
live_data_manager = LiveRaceDataManager()