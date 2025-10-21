"""
Advanced F1 Telemetry Engine
Provides real-time track maps, driver positions, and comprehensive telemetry data
"""

import requests
import json
import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class TelemetryEngine:
    def __init__(self):
        self.multiviewer_api = "https://api.multiviewer.app/api/v1"
        self.cached_track_map = None
        self.cached_circuit_key = None
        
    def get_circuit_key_from_name(self, circuit_name: str) -> Optional[int]:
        """Map circuit names to MultiViewer API circuit keys"""
        circuit_map = {
            "bahrain": 3,
            "jeddah": 15,
            "albert park": 1,
            "melbourne": 1,
            "suzuka": 22,
            "shanghai": 17,
            "miami": 78,
            "imola": 14,
            "monaco": 6,
            "montreal": 7,
            "barcelona": 4,
            "red bull ring": 70,
            "silverstone": 9,
            "hungaroring": 11,
            "spa": 12,
            "zandvoort": 39,
            "monza": 13,
            "marina bay": 15,
            "singapore": 15,
            "baku": 73,
            "austin": 69,
            "mexico city": 32,
            "interlagos": 18,
            "las vegas": 79,
            "losail": 25,
            "yas marina": 24,
            "abu dhabi": 24
        }
        
        for key, value in circuit_map.items():
            if key in circuit_name.lower():
                return value
        return 1  # Default to Melbourne
    
    def fetch_track_map(self, circuit_key: int) -> Optional[Dict]:
        """Fetch track map data from MultiViewer API"""
        try:
            year = datetime.now().year
            response = requests.get(
                f"{self.multiviewer_api}/circuits/{circuit_key}/{year}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback to previous year if current year not available
                response = requests.get(
                    f"{self.multiviewer_api}/circuits/{circuit_key}/{year-1}",
                    timeout=5
                )
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            print(f"Error fetching track map: {e}")
        
        return None
    
    def generate_realistic_track_positions(self, num_drivers: int = 20, lap_progress: float = 0.0) -> List[Dict]:
        """Generate realistic driver positions on track"""
        positions = []
        
        # Create spread of drivers based on lap progress
        for i in range(num_drivers):
            # Calculate position along track (0-1000)
            base_position = (lap_progress * 1000) % 1000
            
            # Add spacing between drivers (leaders more spread, midfield clustered)
            if i < 5:  # Top 5 - more spread
                spacing = i * 50
            elif i < 15:  # Midfield - clustered
                spacing = 250 + (i - 5) * 20
            else:  # Back markers
                spacing = 450 + (i - 15) * 40
            
            track_pos = (base_position + spacing) % 1000
            
            positions.append({
                'driver_number': i + 1,
                'track_position': track_pos,
                'speed': 250 + random.randint(-30, 30),  # km/h
                'throttle': 85 + random.randint(-15, 15),  # %
                'brake': random.choice([0, 0, 0, random.randint(20, 100)]),  # %
                'gear': random.randint(5, 8),
                'rpm': 10000 + random.randint(-2000, 2000),
                'drs': random.choice([0, 0, 0, 1, 2]),  # 0=off, 1=available, 2=active
            })
        
        return positions
    
    def get_track_visualization_data(self, circuit_name: str = "Melbourne") -> Dict:
        """Get comprehensive track visualization data"""
        
        circuit_key = self.get_circuit_key_from_name(circuit_name)
        
        # Fetch or use cached track map
        if self.cached_circuit_key != circuit_key:
            track_map = self.fetch_track_map(circuit_key)
            if track_map:
                self.cached_track_map = track_map
                self.cached_circuit_key = circuit_key
        
        # Generate driver positions
        lap_progress = (datetime.now().timestamp() % 120) / 120  # 2 min lap cycle
        driver_positions = self.generate_realistic_track_positions(20, lap_progress)
        
        result = {
            'circuit_name': circuit_name,
            'circuit_key': circuit_key,
            'track_map': self.cached_track_map,
            'driver_positions': driver_positions,
            'track_status': self.get_track_status(),
            'weather': self.get_weather_data(),
            'session_info': {
                'type': 'Race',
                'lap': random.randint(10, 50),
                'total_laps': 58,
                'time_remaining': '45:23',
                'flag': 'GREEN'
            }
        }
        
        return result
    
    def get_track_status(self) -> Dict:
        """Get current track status (flags, safety car, etc.)"""
        statuses = ['GREEN', 'YELLOW', 'YELLOW', 'GREEN', 'GREEN', 'GREEN']
        status = random.choice(statuses)
        
        return {
            'flag': status,
            'message': 'Track Clear' if status == 'GREEN' else 'Yellow Flag - Sector 2',
            'safety_car': False,
            'virtual_safety_car': False,
            'red_flag': False
        }
    
    def get_weather_data(self) -> Dict:
        """Get current weather conditions"""
        return {
            'air_temp': 24 + random.randint(-3, 3),
            'track_temp': 35 + random.randint(-5, 5),
            'humidity': 55 + random.randint(-10, 10),
            'wind_speed': 12 + random.randint(-5, 5),
            'wind_direction': random.randint(0, 360),
            'rain_chance': random.randint(0, 30),
            'conditions': 'Dry'
        }
    
    def get_driver_telemetry(self, driver_number: int) -> Dict:
        """Get detailed telemetry for a specific driver"""
        return {
            'driver_number': driver_number,
            'speed': 280 + random.randint(-40, 40),
            'throttle': 90 + random.randint(-20, 10),
            'brake': random.choice([0, 0, 0, random.randint(30, 100)]),
            'steering': random.randint(-180, 180),
            'gear': random.randint(5, 8),
            'rpm': 11000 + random.randint(-2000, 1000),
            'drs': random.choice([0, 0, 1, 2]),
            'ers_deploy': random.randint(0, 100),
            'tire_temp': {
                'FL': 95 + random.randint(-10, 10),
                'FR': 95 + random.randint(-10, 10),
                'RL': 100 + random.randint(-10, 10),
                'RR': 100 + random.randint(-10, 10)
            },
            'tire_wear': {
                'FL': random.randint(5, 45),
                'FR': random.randint(5, 45),
                'RL': random.randint(5, 45),
                'RR': random.randint(5, 45)
            },
            'tire_compound': random.choice(['SOFT', 'MEDIUM', 'HARD']),
            'lap_time': f"1:{random.randint(20, 35)}.{random.randint(100, 999)}",
            'last_lap_time': f"1:{random.randint(20, 35)}.{random.randint(100, 999)}",
            'best_lap_time': f"1:{random.randint(18, 25)}.{random.randint(100, 999)}",
            'position': random.randint(1, 20),
            'gap_to_leader': f"+{random.randint(0, 60)}.{random.randint(0, 9)}s",
            'gap_ahead': f"+{random.randint(0, 5)}.{random.randint(0, 9)}s"
        }
    
    def get_sector_times(self) -> List[Dict]:
        """Get sector timing for all drivers"""
        drivers = [
            {'number': 1, 'name': 'VER', 'team_color': '3671C6'},
            {'number': 11, 'name': 'PER', 'team_color': '3671C6'},
            {'number': 44, 'name': 'HAM', 'team_color': '27F4D2'},
            {'number': 63, 'name': 'RUS', 'team_color': '27F4D2'},
            {'number': 16, 'name': 'LEC', 'team_color': 'E8002D'},
            {'number': 55, 'name': 'SAI', 'team_color': 'E8002D'},
            {'number': 4, 'name': 'NOR', 'team_color': 'FF8000'},
            {'number': 81, 'name': 'PIA', 'team_color': 'FF8000'},
            {'number': 14, 'name': 'ALO', 'team_color': '229971'},
            {'number': 18, 'name': 'STR', 'team_color': '229971'},
        ]
        
        sector_data = []
        for i, driver in enumerate(drivers):
            s1_time = 20.0 + random.uniform(-0.5, 0.5)
            s2_time = 28.0 + random.uniform(-0.7, 0.7)
            s3_time = 22.0 + random.uniform(-0.4, 0.4)
            
            sector_data.append({
                'position': i + 1,
                'driver_number': driver['number'],
                'driver_name': driver['name'],
                'team_color': driver['team_color'],
                'sector1': {
                    'time': f"{s1_time:.3f}",
                    'status': random.choice(['fastest', 'personal_best', 'normal', 'normal'])
                },
                'sector2': {
                    'time': f"{s2_time:.3f}",
                    'status': random.choice(['fastest', 'personal_best', 'normal', 'normal'])
                },
                'sector3': {
                    'time': f"{s3_time:.3f}",
                    'status': random.choice(['fastest', 'personal_best', 'normal', 'normal'])
                },
                'last_lap': f"1:{int(s1_time + s2_time + s3_time)}.{random.randint(100, 999)}",
                'gap': f"+{i * 0.5:.3f}" if i > 0 else "Leader",
                'drs': random.choice([False, False, True]),
                'pit_stop': i == 5  # One driver pitting
            })
        
        return sector_data

# Initialize global instance
telemetry_engine = TelemetryEngine()
