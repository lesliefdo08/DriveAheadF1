"""
Generate comprehensive F1 2025 race dataset from actual race results
"""
import requests
import json
import csv
from datetime import datetime
import time

class F1DatasetGenerator:
    def __init__(self):
        self.api_base = "http://api.jolpi.ca/ergast/f1/2025"
        self.session = requests.Session()
        self.races_data = []
        
    def fetch_race_results(self):
        """Fetch all 2025 race results"""
        print("Fetching 2025 F1 race results from Jolpica API...")
        
        try:
            # Get race schedule first to know which races have happened
            schedule_url = f"{self.api_base}.json"
            response = self.session.get(schedule_url, timeout=10)
            schedule_data = response.json()
            
            races = schedule_data['MRData']['RaceTable']['Races']
            total_races = len(races)
            print(f"Total races in 2025 calendar: {total_races}")
            
            # Fetch results for each race
            for race in races:
                round_num = race['round']
                race_name = race['raceName']
                circuit = race['Circuit']['circuitName']
                date = race['date']
                
                # Check if race has happened (compare with current date)
                race_date = datetime.strptime(date, '%Y-%m-%d')
                current_date = datetime.now()
                
                if race_date > current_date:
                    print(f"Round {round_num}: {race_name} - Not yet held")
                    continue
                
                # Fetch race results
                print(f"Fetching Round {round_num}: {race_name}...")
                results_url = f"{self.api_base}/{round_num}/results.json"
                
                try:
                    results_response = self.session.get(results_url, timeout=10)
                    results_data = results_response.json()
                    
                    if 'Races' in results_data['MRData']['RaceTable'] and len(results_data['MRData']['RaceTable']['Races']) > 0:
                        race_results = results_data['MRData']['RaceTable']['Races'][0]
                        
                        # Process each driver's result
                        for result in race_results['Results']:
                            driver_data = {
                                'race_round': round_num,
                                'race_name': race_name,
                                'race_date': date,
                                'circuit_name': circuit,
                                'circuit_location': race['Circuit']['Location']['locality'],
                                'circuit_country': race['Circuit']['Location']['country'],
                                'position': result['position'],
                                'driver_number': result['number'],
                                'driver_code': result['Driver']['code'],
                                'driver_firstname': result['Driver']['givenName'],
                                'driver_lastname': result['Driver']['familyName'],
                                'driver_nationality': result['Driver']['nationality'],
                                'constructor_name': result['Constructor']['name'],
                                'constructor_nationality': result['Constructor']['nationality'],
                                'grid_position': result['grid'],
                                'laps_completed': result['laps'],
                                'status': result['status'],
                                'points': result['points'],
                                'fastest_lap_rank': result.get('FastestLap', {}).get('rank', 'N/A'),
                                'fastest_lap_time': result.get('FastestLap', {}).get('Time', {}).get('time', 'N/A'),
                                'fastest_lap_speed': result.get('FastestLap', {}).get('AverageSpeed', {}).get('speed', 'N/A'),
                                'time_or_retired': result.get('Time', {}).get('time', result['status'])
                            }
                            self.races_data.append(driver_data)
                        
                        print(f"Round {round_num}: {race_name} - {len(race_results['Results'])} drivers")
                    else:
                        print(f"Round {round_num}: {race_name} - No results available yet")
                        
                except Exception as e:
                    print(f"Error fetching Round {round_num}: {e}")
                
                # Be nice to the API
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error fetching schedule: {e}")
            
        return self.races_data
    
    def save_to_csv(self, filename='f1_2025_race_results_dataset.csv'):
        """Save data to CSV file"""
        if not self.races_data:
            print("No data to save!")
            return
        
        print(f"\nSaving dataset to {filename}...")
        
        # Define CSV columns
        fieldnames = [
            'race_round', 'race_name', 'race_date', 'circuit_name', 
            'circuit_location', 'circuit_country', 'position', 'driver_number',
            'driver_code', 'driver_firstname', 'driver_lastname', 'driver_nationality',
            'constructor_name', 'constructor_nationality', 'grid_position',
            'laps_completed', 'status', 'points', 'fastest_lap_rank',
            'fastest_lap_time', 'fastest_lap_speed', 'time_or_retired'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.races_data)
        
        print(f"Dataset saved successfully!")
        print(f"Total records: {len(self.races_data)}")
        print(f"File: {filename}")
        
    def save_to_json(self, filename='f1_2025_race_results_dataset.json'):
        """Save data to JSON file"""
        if not self.races_data:
            print("No data to save!")
            return
        
        print(f"\nSaving dataset to {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.races_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"JSON dataset saved successfully!")
        print(f"Total records: {len(self.races_data)}")
        print(f"File: {filename}")
    
    def print_summary(self):
        """Print dataset summary"""
        if not self.races_data:
            return
        
        print("\n" + "="*60)
        print("DATASET SUMMARY")
        print("="*60)
        
        # Count races
        races = set(row['race_name'] for row in self.races_data)
        print(f"Total Races: {len(races)}")
        
        # Count drivers
        drivers = set(row['driver_code'] for row in self.races_data)
        print(f"Total Drivers: {len(drivers)}")
        
        # Count teams
        teams = set(row['constructor_name'] for row in self.races_data)
        print(f"Total Teams: {len(teams)}")
        
        # Total entries
        print(f"Total Data Entries: {len(self.races_data)}")
        
        print("\nRace Winners:")
        winners = {}
        for row in self.races_data:
            if row['position'] == '1':
                race_key = f"R{row['race_round']} - {row['race_name']}"
                winners[race_key] = f"{row['driver_code']} ({row['constructor_name']})"
        
        for race, winner in sorted(winners.items()):
            print(f"  {race}: {winner}")
        
        print("="*60 + "\n")

if __name__ == "__main__":
    print("F1 2025 DATASET GENERATOR")
    print("="*60)
    
    generator = F1DatasetGenerator()
    
    # Fetch data
    data = generator.fetch_race_results()
    
    if data:
        # Print summary
        generator.print_summary()
        
        # Save to CSV
        generator.save_to_csv('f1_2025_race_results_dataset.csv')
        
        # Save to JSON
        generator.save_to_json('f1_2025_race_results_dataset.json')
        
        print("\nDataset generation complete!")
        print("Check your project root for the generated files.")
    else:
        print("\nNo race data available to generate dataset.")
