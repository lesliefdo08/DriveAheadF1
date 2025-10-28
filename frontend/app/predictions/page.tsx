'use client';

import { useEffect, useState } from 'react';
import apiService, { PredictionsResponse } from '@/lib/api';

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<PredictionsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPredictions() {
      try {
        const data = await apiService.getPredictions();
        setPredictions(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching predictions:', error);
        setLoading(false);
      }
    }
    fetchPredictions();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="animate-pulse text-white text-2xl">Loading predictions...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl md:text-5xl font-f1 font-black text-center mb-4 f1-gradient-text">
          Race Predictions
        </h1>
        <p className="text-center text-gray-400 mb-12">ML-Powered Next Race Winner Predictions</p>

        {/* Winner Prediction */}
        {predictions?.winner_prediction && (
          <div className="glass-panel rounded-2xl p-8 mb-8 max-w-3xl mx-auto">
            <h2 className="text-2xl font-f1 font-bold text-white mb-4 text-center">
              🏆 Predicted Winner
            </h2>
            <div className="text-center">
              <div className="text-5xl font-f1 font-black text-f1-red mb-2">
                {predictions.winner_prediction.driver}
              </div>
              <div className="text-xl text-gray-300 mb-4">
                Confidence: {predictions.winner_prediction.confidence}%
              </div>
              <div className="text-gray-400 text-sm max-w-xl mx-auto">
                {predictions.winner_prediction.reasoning}
              </div>
            </div>
          </div>
        )}

        {/* All Predictions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {predictions?.predictions.map((pred, index) => (
            <div
              key={index}
              className="glass-panel rounded-xl p-6 hover:bg-white/5 transition-all duration-300"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="text-3xl font-f1 font-black text-f1-red">
                  #{pred.predicted_position}
                </div>
                <div className="text-sm font-semibold px-3 py-1 rounded-full bg-f1-red/20 text-f1-red">
                  {pred.confidence}
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-1">{pred.driver}</h3>
              <div className="text-gray-400 text-sm mb-3">{pred.team}</div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 text-sm">Probability</span>
                <span className="text-white font-bold">{pred.probability}%</span>
              </div>
              <div className="flex justify-between items-center mt-2">
                <span className="text-gray-500 text-sm">Odds</span>
                <span className="text-white font-bold">{pred.odds}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Metadata */}
        {predictions && (
          <div className="mt-12 text-center text-gray-500 text-sm">
            <p>Model: {predictions.model_type}</p>
            <p>Last Updated: {new Date(predictions.last_updated).toLocaleString()}</p>
          </div>
        )}
      </div>
    </div>
  );
}
