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

driver_standings = [
    {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 429, "wins": 8},
    {"position": 2, "driver": "Lando Norris", "team": "McLaren", "points": 349, "wins": 4},
    {"position": 3, "driver": "Charles Leclerc", "team": "Ferrari", "points": 341, "wins": 3},
    {"position": 4, "driver": "Oscar Piastri", "team": "McLaren", "points": 291, "wins": 2},
    {"position": 5, "driver": "Carlos Sainz", "team": "Ferrari", "points": 272, "wins": 1}
]

constructor_standings = [
    {"position": 1, "team": "McLaren", "points": 666, "wins": 6},
    {"position": 2, "team": "Ferrari", "points": 652, "wins": 5},
    {"position": 3, "team": "Red Bull Racing", "points": 589, "wins": 8}
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
    drivers = [
        {"name": "Max Verstappen", "team": "Red Bull Racing"},
        {"name": "Lando Norris", "team": "McLaren"},
        {"name": "Charles Leclerc", "team": "Ferrari"},
        {"name": "Oscar Piastri", "team": "McLaren"},
        {"name": "George Russell", "team": "Mercedes"}
    ]
    
    telemetry_data = {}
    base_time = time.time()
    
    for i, driver in enumerate(drivers):
        position = i + 1
        lap_variation = math.sin(base_time * 0.1 + i) * 2
        speed_variation = math.cos(base_time * 0.05 + i) * 15
        
        telemetry_data[str(position)] = {
            "position": position,
            "driver": driver["name"],
            "team": driver["team"],
            "gap": "+0.000" if position == 1 else f"+{(position-1)*0.5 + lap_variation:.3f}",
            "last_lap": f"1:{22 + lap_variation:.3f}",
            "best_lap": f"1:{20 + i*0.2:.3f}",
            "sector_1": f"25.{random.randint(100, 999)}",
            "sector_2": f"42.{random.randint(100, 999)}",
            "sector_3": f"28.{random.randint(100, 999)}",
            "speed": int(310 + speed_variation),
            "tire": random.choice(["SOFT", "MEDIUM", "HARD"]),
            "stint": random.randint(5, 25)
        }
    
    return jsonify({
        "session": "Race",
        "lap": random.randint(15, 45),
        "weather": "Clear",
        "track_temp": "32°C",
        "air_temp": "26°C",
        "humidity": "45%",
        "drivers": telemetry_data,
        "timestamp": current_time.isoformat()
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
    last_race = {
        "round": 18,
        "name": "Azerbaijan Grand Prix",
        "circuit": "Baku City Circuit",
        "country": "Azerbaijan", 
        "date": "2025-09-15",
        "time": "12:00:00Z",
        "location": "Baku, Azerbaijan"
    }
    return jsonify({
        "race": last_race,
        "last_updated": datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
