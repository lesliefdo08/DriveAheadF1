"""
Verify prediction accuracy for recent races
"""
from f1_data_fetcher import f1_fetcher
import requests

print("=== VERIFYING PREDICTION ACCURACY ===\n")

# Races shown in screenshot
races_to_check = [
    ('Singapore GP', 18),
    ('Azerbaijan GP', 17),
    ('Italian GP', 16)
]

for race_name, round_num in races_to_check:
    try:
        url = f'http://api.jolpi.ca/ergast/f1/2025/{round_num}/results.json'
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        race_data = data['MRData']['RaceTable']['Races']
        if race_data:
            winner = race_data[0]['Results'][0]
            winner_name = f"{winner['Driver']['givenName']} {winner['Driver']['familyName']}"
            
            print(f"{race_name} (Round {round_num}):")
            print(f"  Actual Winner: {winner_name}")
            print()
    except Exception as e:
        print(f"Error fetching {race_name}: {e}")
        print()
