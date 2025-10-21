from flask import Flask, render_template, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
import random
import time
import math

# Import the real-time F1 data fetcher
from f1_data_fetcher import f1_fetcher

# Import the advanced ML predictor
from advanced_predictor import advanced_predictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "driveahead-f1-analytics-2025"
CORS(app)

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

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

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
    """REAL-TIME: Fetch live standings from Jolpica F1 API"""
    try:
        driver_data = f1_fetcher.get_current_standings()
        constructor_data = f1_fetcher.get_constructor_standings()
        
        return jsonify({
            "drivers": driver_data['standings'],
            "constructors": constructor_data['standings'],
            "last_updated": driver_data['last_updated'],
            "season": driver_data['season'],
            "round": driver_data['round'],
            "source": driver_data['source']
        })
    except Exception as e:
        logger.error(f"Error in api_standings: {e}")
        return jsonify({
            "error": "Failed to fetch standings",
            "message": str(e)
        }), 500

@app.route("/api/next-race")
def api_next_race():
    """REAL-TIME: Dynamically detect next upcoming race"""
    try:
        next_race_data = f1_fetcher.get_next_race()
        return jsonify(next_race_data)
    except Exception as e:
        logger.error(f"Error in api_next_race: {e}")
        return jsonify({
            "error": "Failed to fetch next race",
            "message": str(e)
        }), 500

@app.route("/api/predictions/winner")
def api_predictions_winner():
    """REAL-TIME: Advanced ML prediction for next race winner"""
    try:
        # Get next race information
        next_race_data = f1_fetcher.get_next_race()
        
        # Use advanced predictor to predict winner
        prediction = advanced_predictor.predict_race_winner(next_race_data)
        
        return jsonify({
            "prediction": {
                "driver": prediction['predicted_winner'],
                "team": prediction['team'],
                "confidence": prediction['confidence'],
                "position": 1,
                "reasoning": prediction['reasoning'],
                "breakdown": prediction.get('breakdown', {}),
                "top_3": prediction.get('top_3_predictions', [])
            },
            "race": next_race_data.get('race', {}),
            "last_updated": datetime.now().isoformat(),
            "prediction_method": prediction.get('prediction_method', 'Advanced ML Multi-Factor Analysis')
        })
    except Exception as e:
        logger.error(f"Error in api_predictions_winner: {e}")
        # Fallback to simple prediction
        driver_data = f1_fetcher.get_current_standings()
        leader = driver_data['standings'][0] if driver_data['standings'] else {}
        return jsonify({
            "prediction": {
                "driver": leader.get("driver", "Oscar Piastri"),
                "team": leader.get("team", "McLaren"),
                "confidence": 75,
                "position": 1
            },
            "last_updated": datetime.now().isoformat(),
            "prediction_method": "Fallback (Championship Leader)"
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
    """REAL-TIME: Advanced ML predictions for all drivers"""
    try:
        # Get current standings and next race
        driver_data = f1_fetcher.get_current_standings()
        next_race_data = f1_fetcher.get_next_race()
        
        # Get advanced prediction for winner
        winner_prediction = advanced_predictor.predict_race_winner(next_race_data)
        
        # Get top 3 predictions from advanced predictor
        top_3_predictions = winner_prediction.get('top_3_predictions', [])
        
        # Build full prediction list
        predictions = []
        
        # Add top 3 from advanced predictor
        for idx, pred in enumerate(top_3_predictions):
            predictions.append({
                "driver": pred['driver'],
                "team": pred['team'],
                "probability": pred['probability'],
                "predicted_position": idx + 1,
                "confidence": "High" if pred['probability'] > 70 else "Medium",
                "odds": f"{round(100/max(pred['probability'], 1), 1)}:1",
                "score": pred.get('score', 0)
            })
        
        # Add remaining drivers from standings
        standings = driver_data['standings']
        added_drivers = {pred['driver'] for pred in top_3_predictions}
        
        for i, standing in enumerate(standings):
            if standing['driver'] not in added_drivers and len(predictions) < 10:
                # Calculate probability based on championship position
                points = standing["points"]
                max_points = standings[0]["points"] if standings else 400
                probability = min(50, max(5, (points / max_points) * 50))
                
                predictions.append({
                    "driver": standing["driver"],
                    "team": standing["team"],
                    "probability": round(probability, 1),
                    "predicted_position": len(predictions) + 1,
                    "confidence": "Medium" if probability > 20 else "Low",
                    "odds": f"{round(100/max(probability, 1), 1)}:1",
                    "current_points": standing["points"],
                    "wins": standing["wins"]
                })
        
        return jsonify({
            "predictions": predictions,
            "winner_prediction": {
                "driver": winner_prediction['predicted_winner'],
                "confidence": winner_prediction['confidence'],
                "reasoning": winner_prediction['reasoning'],
                "breakdown": winner_prediction.get('breakdown', {})
            },
            "next_race": next_race_data.get('race', {}),
            "last_updated": driver_data['last_updated'],
            "model_type": "Advanced ML Multi-Factor",
            "source": driver_data['source'],
            "season": driver_data['season'],
            "round": driver_data['round']
        })
    except Exception as e:
        logger.error(f"Error in api_predictions: {e}")
        return jsonify({
            "error": "Failed to generate predictions",
            "message": str(e)
        }), 500

@app.route("/api/predictions/all-races")
def api_predictions_all_races():
    """REAL-TIME: Predictions for ALL upcoming races (adapts to each circuit)"""
    try:
        all_predictions = advanced_predictor.predict_all_upcoming_races()
        
        return jsonify({
            "predictions": all_predictions,
            "total_races": len(all_predictions),
            "last_updated": datetime.now().isoformat(),
            "model_type": "Advanced ML Multi-Factor (Circuit-Adaptive)",
            "note": "Predictions adapt to each circuit's unique characteristics"
        })
    except Exception as e:
        logger.error(f"Error in api_predictions_all_races: {e}")
        return jsonify({
            "error": "Failed to generate all race predictions",
            "message": str(e)
        }), 500
        }), 500

@app.route("/api/race-schedule")
def api_race_schedule():
    """REAL-TIME: Fetch full season race schedule"""
    try:
        schedule_data = f1_fetcher.get_race_schedule()
        
        # Filter to show only upcoming races
        now = datetime.now()
        upcoming_races = []
        for race in schedule_data['races']:
            race_date = datetime.strptime(race['date'], '%Y-%m-%d')
            if race_date >= now.replace(hour=0, minute=0, second=0, microsecond=0):
                upcoming_races.append(race)
        
        return jsonify({
            "races": upcoming_races if upcoming_races else schedule_data['races'][-3:],  # Show last 3 if season ended
            "total_races": schedule_data['total_races'],
            "last_updated": schedule_data['last_updated'],
            "season": schedule_data['season'],
            "source": schedule_data['source']
        })
    except Exception as e:
        logger.error(f"Error in api_race_schedule: {e}")
        return jsonify({
            "error": "Failed to fetch race schedule",
            "message": str(e)
        }), 500

@app.route("/api/last-race")
def api_last_race():
    """REAL-TIME: Fetch results from the most recent race"""
    try:
        last_race_data = f1_fetcher.get_last_race_results()
        return jsonify({
            "race": last_race_data,
            "last_updated": datetime.now().isoformat(),
            "source": last_race_data.get('source', 'jolpica_api')
        })
    except Exception as e:
        logger.error(f"Error in api_last_race: {e}")
        return jsonify({
            "error": "Failed to fetch last race results",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
