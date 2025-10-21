from prediction_history import prediction_tracker

stats = prediction_tracker.get_accuracy_stats()

print("=== PREDICTION ACCURACY STATS ===\n")
print(f"Total Predictions: {stats['total_predictions']}")
print(f"Correct: {stats['correct']}")
print(f"Incorrect: {stats['incorrect']}")
print(f"Accuracy: {stats['accuracy_percentage']}%")

print("\n=== Recent History ===")
for race in stats['recent_history']:
    status_icon = '✓' if race['is_correct'] else '✗'
    print(f"{status_icon} {race['race_name']}: Predicted {race['predicted_winner']}, Actual {race['actual_winner']}")
