from advanced_predictor import advanced_predictor

predictions = advanced_predictor.predict_all_upcoming_races()

print(f"Generated predictions for {len(predictions)} upcoming races:\n")

for p in predictions[:3]:
    print(f"Round {p['round']}: {p['race_name']}")
    print(f"  Predicted Winner: {p['predicted_winner']} ({p['team']})")
    print(f"  Confidence: {p['confidence']:.1f}%")
    print(f"  Top 3: {[pred['driver'] for pred in p['top_3_predictions']]}")
    print(f"  Reasoning: {p['reasoning'][0]}")
    print()
