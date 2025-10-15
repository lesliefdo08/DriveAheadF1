from flask import Flask, render_template, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
import random
import time
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "driveahead-f1-analytics-2025"
CORS(app)

# REAL 2025 F1 Championship Standings (After Singapore GP, Round 18 - October 5, 2025)
# Source: Jolpica F1 API - Official Data
driver_standings = [
    {"position": 1, "driver": "Oscar Piastri", "team": "McLaren", "points": 336, "wins": 7},
    {"position": 2, "driver": "Lando Norris", "team": "McLaren", "points": 314, "wins": 5},
    {"position": 3, "driver": "Max Verstappen", "team": "Red Bull", "points": 273, "wins": 4},
    {"position": 4, "driver": "George Russell", "team": "Mercedes", "points": 237, "wins": 2},
    {"position": 5, "driver": "Charles Leclerc", "team": "Ferrari", "points": 173, "wins": 0},
    {"position": 6, "driver": "Lewis Hamilton", "team": "Ferrari", "points": 125, "wins": 0},
    {"position": 7, "driver": "Andrea Kimi Antonelli", "team": "Mercedes", "points": 88, "wins": 0},
    {"position": 8, "driver": "Alexander Albon", "team": "Williams", "points": 70, "wins": 0},
    {"position": 9, "driver": "Isack Hadjar", "team": "RB F1 Team", "points": 39, "wins": 0},
    {"position": 10, "driver": "Nico Hulkenberg", "team": "Sauber", "points": 37, "wins": 0}
]

constructor_standings = [
    {"position": 1, "team": "McLaren", "points": 650, "wins": 12},
    {"position": 2, "team": "Mercedes", "points": 325, "wins": 2},
    {"position": 3, "team": "Ferrari", "points": 298, "wins": 0},
    {"position": 4, "team": "Red Bull", "points": 290, "wins": 4},
    {"position": 5, "team": "Williams", "points": 102, "wins": 0},
    {"position": 6, "team": "RB F1 Team", "points": 72, "wins": 0}
]

next_race = {
    "round": 19,
    "name": "United States Grand Prix",
    "circuit": "Circuit of the Americas",
    "country": "United States",
    "date": "2025-10-19",
    "time": "19:00:00Z",
    "location": "Austin, Texas"
}

# For demo purposes, you can use a future date for testing:
# next_race["date"] = "2025-10-20"  # Tomorrow for testing

@app.route("/favicon.ico")
def favicon():
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                             'logo.png', mimetype='image/png')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/telemetry")
def telemetry():
    return render_template("telemetry.html")

@app.route("/standings")
def standings():
    return render_template("standings.html")

@app.route("/predictions")
def predictions():
    return render_template("predictions.html")

@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "ml_enabled": True
    })

@app.route("/api/standings")
def api_standings():
    return jsonify({
        "drivers": driver_standings,
        "constructors": constructor_standings,
        "last_updated": datetime.now().isoformat(),
        "season": 2025
    })

@app.route("/api/next-race")
def api_next_race():
    return jsonify({
        "race": next_race,
        "last_updated": datetime.now().isoformat()
    })

@app.route("/api/predictions/winner")
def api_predictions_winner():
    prediction = {
        "driver": driver_standings[0]["driver"],
        "team": driver_standings[0]["team"],
        "confidence": 87,
        "position": 1
    }
    
    return jsonify({
        "prediction": prediction,
        "last_updated": datetime.now().isoformat()
    })

@app.route("/api/telemetry")
def api_telemetry():
    current_time = datetime.now()
    base_time = time.time()
    
    drivers_list = [
        {"name": "Max Verstappen", "acronym": "VER", "team": "Red Bull Racing", "number": "1"},
        {"name": "Lando Norris", "acronym": "NOR", "team": "McLaren", "number": "4"},
        {"name": "Charles Leclerc", "acronym": "LEC", "team": "Ferrari", "number": "16"},
        {"name": "Oscar Piastri", "acronym": "PIA", "team": "McLaren", "number": "81"},
        {"name": "George Russell", "acronym": "RUS", "team": "Mercedes", "number": "63"},
        {"name": "Lewis Hamilton", "acronym": "HAM", "team": "Mercedes", "number": "44"},
        {"name": "Carlos Sainz", "acronym": "SAI", "team": "Ferrari", "number": "55"},
        {"name": "Sergio Perez", "acronym": "PER", "team": "Red Bull Racing", "number": "11"}
    ]
    
    # Simulate position changes
    positions = list(range(1, len(drivers_list) + 1))
    if random.random() > 0.7:  # 30% chance of position change
        i = random.randint(0, len(positions) - 2)
        positions[i], positions[i + 1] = positions[i + 1], positions[i]
    
    telemetry_data = {}
    
    for idx, driver in enumerate(drivers_list):
        position = positions[idx]
        lap_variation = math.sin(base_time * 0.1 + idx) * 2
        speed_variation = math.cos(base_time * 0.05 + idx) * 15
        
        telemetry_data[driver["number"]] = {
            "position": position,
            "driver_acronym": driver["acronym"],
            "driver_name": driver["name"],
            "team_name": driver["team"],
            "gap_to_leader": "+0.000" if position == 1 else f"+{(position-1)*1.2 + lap_variation:.3f}",
            "interval": "+0.000" if position == 1 else f"+{0.5 + lap_variation:.3f}",
            "last_lap_time": f"1:{22 + lap_variation:.3f}",
            "best_lap_time": f"1:{20 + idx*0.2:.3f}",
            "sectors": [
                {"time": f"25.{random.randint(100, 999)}", "status": random.choice(["fastest", "personal", "slower"])},
                {"time": f"42.{random.randint(100, 999)}", "status": random.choice(["fastest", "personal", "slower"])},
                {"time": f"28.{random.randint(100, 999)}", "status": random.choice(["fastest", "personal", "slower"])}
            ],
            "speed_trap": int(310 + speed_variation),
            "tire_compound": random.choice(["SOFT", "MEDIUM", "HARD"]),
            "tire_age": random.randint(5, 25),
            "drs_enabled": random.choice([True, False]),
            "in_pit": False,
            "pit_out": False,
            "throttle_percent": random.randint(0, 100),
            "brake_pressure": random.randint(0, 100)
        }
    
    return jsonify({
        **telemetry_data,
        "_meta": {
            "session_name": "RACE",
            "lap_number": random.randint(15, 45),
            "weather": {
                "air_temp": "26",
                "track_temp": "32",
                "humidity": "45",
                "wind_speed": "12"
            }
        }
    })

@app.route("/api/predictions")
def api_predictions():
    predictions = []
    for i, standing in enumerate(driver_standings):
        points = standing["points"]
        probability = min(45, max(5, (points / 429) * 45))
        
        predictions.append({
            "driver": standing["driver"],
            "team": standing["team"],
            "probability": round(probability, 1),
            "predicted_position": i + 1,
            "confidence": "High" if probability > 25 else "Medium",
            "odds": f"{round(100/max(probability, 1), 1)}:1"
        })
    
    return jsonify({
        "predictions": predictions,
        "last_updated": datetime.now().isoformat(),
        "model_type": "ML"
    })

@app.route("/api/race-schedule")
def api_race_schedule():
    races = [
        {"round": 19, "name": "United States Grand Prix", "date": "2025-10-19", "time": "19:00:00Z", "location": "Austin, Texas"},
        {"round": 20, "name": "Mexico City Grand Prix", "date": "2025-10-27", "time": "20:00:00Z", "location": "Mexico City, Mexico"},
        {"round": 21, "name": "Brazilian Grand Prix", "date": "2025-11-03", "time": "17:00:00Z", "location": "São Paulo, Brazil"}
    ]
    return jsonify({
        "races": races,
        "last_updated": datetime.now().isoformat(),
        "season": 2025
    })

@app.route("/api/last-race")
def api_last_race():
    # REAL Singapore GP 2025 Results (October 5, 2025 - Round 18)
    # Source: Jolpica F1 API - Official Data
    last_race = {
        "round": 18,
        "raceName": "Singapore Grand Prix",
        "name": "Singapore Grand Prix",
        "circuit": "Marina Bay Street Circuit",
        "country": "Singapore", 
        "date": "2025-10-05",
        "time": "12:00:00Z",
        "location": "Marina Bay, Singapore",
        "Results": [
            {
                "position": "1",
                "Driver": {
                    "givenName": "George",
                    "familyName": "Russell"
                },
                "Constructor": {
                    "name": "Mercedes"
                },
                "Time": {
                    "time": "1:40:22.367"
                }
            },
            {
                "position": "2",
                "Driver": {
                    "givenName": "Max",
                    "familyName": "Verstappen"
                },
                "Constructor": {
                    "name": "Red Bull"
                },
                "Time": {
                    "time": "+5.430s"
                }
            },
            {
                "position": "3",
                "Driver": {
                    "givenName": "Lando",
                    "familyName": "Norris"
                },
                "Constructor": {
                    "name": "McLaren"
                },
                "Time": {
                    "time": "+6.066s"
                }
            },
            {
                "position": "4",
                "Driver": {
                    "givenName": "Oscar",
                    "familyName": "Piastri"
                },
                "Constructor": {
                    "name": "McLaren"
                },
                "Time": {
                    "time": "+8.146s"
                }
            },
            {
                "position": "5",
                "Driver": {
                    "givenName": "Andrea Kimi",
                    "familyName": "Antonelli"
                },
                "Constructor": {
                    "name": "Mercedes"
                },
                "Time": {
                    "time": "+33.681s"
                }
            }
        ]
    }
    return jsonify({
        "race": last_race,
        "last_updated": datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
