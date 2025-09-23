"""
Enhanced FastF1 Integration for F1 Telemetry and Session Data
Provides lap-by-lap data, timing, tire usage, and advanced analytics
"""
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime
import warnings

# Suppress FastF1 warnings for cleaner output
warnings.filterwarnings('ignore')
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFastF1:
    """
    Professional FastF1 integration for detailed F1 session analytics
    Provides: lap times, telemetry, tire strategies, sector analysis
    """
    
    def __init__(self):
        # Setup caching for faster data access
        cache_dir = os.path.join(os.path.dirname(__file__), 'cache', 'fastf1_cache')
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)
        
        # Cache for session data
        self.session_cache = {}
        
    def get_session(self, year: int, gp_name: str, session_type: str = 'Race') -> Optional[fastf1.core.Session]:
        """Get FastF1 session with caching"""
        cache_key = f"{year}_{gp_name}_{session_type}"
        
        if cache_key in self.session_cache:
            return self.session_cache[cache_key]
        
        try:
            session = fastf1.get_session(year, gp_name, session_type)
            session.load()
            
            self.session_cache[cache_key] = session
            return session
            
        except Exception as e:
            logger.error(f"Error loading session {year} {gp_name} {session_type}: {e}")
            return None
    
    def get_lap_times_analysis(self, year: int, gp_name: str, session_type: str = 'Race') -> pd.DataFrame:
        """Get comprehensive lap time analysis"""
        try:
            session = self.get_session(year, gp_name, session_type)
            if session is None:
                return pd.DataFrame()
            
            laps = session.laps
            
            # Calculate advanced metrics
            lap_analysis = []
            
            for driver in session.drivers:
                driver_laps = laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Filter out in/out laps and invalid times
                valid_laps = driver_laps[
                    (driver_laps['IsPersonalBest'] == True) | 
                    (driver_laps['LapTime'].notna())
                ].copy()
                
                if valid_laps.empty:
                    continue
                
                # Calculate metrics
                best_lap_time = valid_laps['LapTime'].min()
                avg_lap_time = valid_laps['LapTime'].mean()
                lap_consistency = valid_laps['LapTime'].std()
                
                driver_info = session.get_driver(driver)
                
                analysis = {
                    'driver': driver,
                    'driver_name': f"{driver_info['FirstName']} {driver_info['LastName']}" if driver_info else driver,
                    'team': driver_info.get('TeamName', 'Unknown') if driver_info else 'Unknown',
                    'best_lap_time': best_lap_time.total_seconds() if pd.notna(best_lap_time) else None,
                    'average_lap_time': avg_lap_time.total_seconds() if pd.notna(avg_lap_time) else None,
                    'lap_consistency': lap_consistency.total_seconds() if pd.notna(lap_consistency) else None,
                    'total_laps': len(valid_laps),
                    'fastest_sector_1': valid_laps['Sector1Time'].min().total_seconds() if not valid_laps['Sector1Time'].isna().all() else None,
                    'fastest_sector_2': valid_laps['Sector2Time'].min().total_seconds() if not valid_laps['Sector2Time'].isna().all() else None,
                    'fastest_sector_3': valid_laps['Sector3Time'].min().total_seconds() if not valid_laps['Sector3Time'].isna().all() else None
                }
                
                lap_analysis.append(analysis)
            
            return pd.DataFrame(lap_analysis)
            
        except Exception as e:
            logger.error(f"Error in lap times analysis: {e}")
            return pd.DataFrame()
    
    def get_tire_strategy_analysis(self, year: int, gp_name: str) -> pd.DataFrame:
        """Analyze tire strategies and compound performance"""
        try:
            session = self.get_session(year, gp_name, 'Race')
            if session is None:
                return pd.DataFrame()
            
            laps = session.laps
            tire_strategies = []
            
            for driver in session.drivers:
                driver_laps = laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Group by tire compound
                compound_stats = driver_laps.groupby('Compound').agg({
                    'LapTime': ['count', 'mean', 'min'],
                    'LapNumber': ['min', 'max']
                }).round(3)
                
                driver_info = session.get_driver(driver)
                team = driver_info.get('TeamName', 'Unknown') if driver_info else 'Unknown'
                
                for compound in compound_stats.index:
                    if pd.isna(compound) or compound == '':
                        continue
                    
                    strategy = {
                        'driver': driver,
                        'team': team,
                        'compound': compound,
                        'laps_on_compound': int(compound_stats.loc[compound, ('LapTime', 'count')]),
                        'avg_lap_time': compound_stats.loc[compound, ('LapTime', 'mean')],
                        'best_lap_time': compound_stats.loc[compound, ('LapTime', 'min')],
                        'first_lap': int(compound_stats.loc[compound, ('LapNumber', 'min')]),
                        'last_lap': int(compound_stats.loc[compound, ('LapNumber', 'max')])
                    }
                    tire_strategies.append(strategy)
            
            return pd.DataFrame(tire_strategies)
            
        except Exception as e:
            logger.error(f"Error in tire strategy analysis: {e}")
            return pd.DataFrame()
    
    def get_qualifying_performance(self, year: int, gp_name: str) -> pd.DataFrame:
        """Get qualifying session analysis"""
        try:
            session = self.get_session(year, gp_name, 'Qualifying')
            if session is None:
                return pd.DataFrame()
            
            # Get qualifying results
            results = session.results
            
            if results.empty:
                return pd.DataFrame()
            
            qualifying_data = []
            
            for _, result in results.iterrows():
                driver_data = {
                    'driver': result['Abbreviation'],
                    'driver_name': f"{result['FirstName']} {result['LastName']}",
                    'team': result['TeamName'],
                    'grid_position': result['Position'],
                    'q1_time': result['Q1'].total_seconds() if pd.notna(result['Q1']) else None,
                    'q2_time': result['Q2'].total_seconds() if pd.notna(result['Q2']) else None,
                    'q3_time': result['Q3'].total_seconds() if pd.notna(result['Q3']) else None,
                    'best_qualifying_time': min(
                        [t for t in [result['Q1'], result['Q2'], result['Q3']] if pd.notna(t)]
                    ).total_seconds() if any(pd.notna(t) for t in [result['Q1'], result['Q2'], result['Q3']]) else None
                }
                qualifying_data.append(driver_data)
            
            return pd.DataFrame(qualifying_data)
            
        except Exception as e:
            logger.error(f"Error in qualifying analysis: {e}")
            return pd.DataFrame()
    
    def get_weather_data(self, year: int, gp_name: str, session_type: str = 'Race') -> Dict:
        """Extract weather information from session"""
        try:
            session = self.get_session(year, gp_name, session_type)
            if session is None:
                return {}
            
            # Get weather data from laps
            laps = session.laps
            if laps.empty:
                return {}
            
            # Calculate average weather conditions
            weather_data = {
                'air_temperature': laps['AirTemp'].mean() if 'AirTemp' in laps.columns else None,
                'track_temperature': laps['TrackTemp'].mean() if 'TrackTemp' in laps.columns else None,
                'humidity': laps['Humidity'].mean() if 'Humidity' in laps.columns else None,
                'pressure': laps['Pressure'].mean() if 'Pressure' in laps.columns else None,
                'wind_speed': laps['WindSpeed'].mean() if 'WindSpeed' in laps.columns else None,
                'rainfall': laps['Rainfall'].any() if 'Rainfall' in laps.columns else False
            }
            
            return {k: v for k, v in weather_data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error extracting weather data: {e}")
            return {}
    
    def get_driver_performance_metrics(self, year: int, gp_name: str, driver_code: str) -> Dict:
        """Get comprehensive driver performance metrics"""
        try:
            session = self.get_session(year, gp_name, 'Race')
            if session is None:
                return {}
            
            driver_laps = session.laps.pick_driver(driver_code)
            if driver_laps.empty:
                return {}
            
            # Calculate performance metrics
            metrics = {
                'total_laps': len(driver_laps),
                'best_lap_time': driver_laps['LapTime'].min().total_seconds() if not driver_laps['LapTime'].isna().all() else None,
                'average_lap_time': driver_laps['LapTime'].mean().total_seconds() if not driver_laps['LapTime'].isna().all() else None,
                'consistency_score': 1 / (driver_laps['LapTime'].std().total_seconds() + 1) if not driver_laps['LapTime'].isna().all() else 0,
                'tire_compounds_used': list(driver_laps['Compound'].dropna().unique()),
                'total_pit_stops': len(driver_laps[driver_laps['PitOutTime'].notna()]),
                'sectors_won': {
                    'sector_1': (driver_laps['Sector1Time'] == driver_laps['Sector1Time'].min()).sum(),
                    'sector_2': (driver_laps['Sector2Time'] == driver_laps['Sector2Time'].min()).sum(),
                    'sector_3': (driver_laps['Sector3Time'] == driver_laps['Sector3Time'].min()).sum()
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating driver performance metrics: {e}")
            return {}
    
    def get_circuit_characteristics(self, year: int, gp_name: str) -> Dict:
        """Extract circuit characteristics from session data"""
        try:
            session = self.get_session(year, gp_name, 'Race')
            if session is None:
                return {}
            
            # Get circuit info
            circuit_info = {
                'circuit_name': session.event['EventName'],
                'location': session.event['Location'],
                'country': session.event['Country'],
                'circuit_type': 'Street' if 'street' in session.event['EventName'].lower() or 'monaco' in session.event['EventName'].lower() or 'singapore' in session.event['EventName'].lower() else 'Permanent',
                'session_date': session.date.isoformat() if hasattr(session, 'date') else None
            }
            
            # Analyze lap characteristics from fastest laps
            laps = session.laps
            if not laps.empty:
                fastest_lap = laps.pick_fastest()
                if fastest_lap is not None and not fastest_lap.empty:
                    if len(fastest_lap) > 0:
                        fastest_lap = fastest_lap.iloc[0]
                        
                        circuit_info.update({
                            'lap_record': fastest_lap['LapTime'].total_seconds() if pd.notna(fastest_lap['LapTime']) else None,
                            'typical_race_laps': laps['LapNumber'].max() if not laps['LapNumber'].isna().all() else None,
                            'drs_zones': len(laps.columns[laps.columns.str.contains('DRS', na=False)]) if any('DRS' in str(col) for col in laps.columns) else 0
                        })
            
            return circuit_info
            
        except Exception as e:
            logger.error(f"Error extracting circuit characteristics: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    fastf1_api = EnhancedFastF1()
    
    print("🏎️ Testing Enhanced FastF1 Integration...")
    
    try:
        # Test with recent race data
        lap_analysis = fastf1_api.get_lap_times_analysis(2024, 'Italian Grand Prix')
        print(f"Lap analysis shape: {lap_analysis.shape}")
        if not lap_analysis.empty:
            print(lap_analysis[['driver_name', 'team', 'best_lap_time', 'lap_consistency']].head())
        
        # Test circuit characteristics
        circuit_info = fastf1_api.get_circuit_characteristics(2024, 'Italian Grand Prix')
        print(f"Circuit info: {circuit_info}")
        
    except Exception as e:
        print(f"Test error: {e}")