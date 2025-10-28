'use client';

import { useEffect, useState } from 'react';
import apiService from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [standings, predictions] = await Promise.all([
          apiService.getStandings(),
          apiService.getPredictions(),
        ]);
        setStats({ standings, predictions });
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="animate-pulse text-white text-2xl">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl md:text-5xl font-f1 font-black text-center mb-4 f1-gradient-text">
          Analytics Dashboard
        </h1>
        <p className="text-center text-gray-400 mb-12">Comprehensive F1 Statistics & Insights</p>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="glass-panel rounded-xl p-6">
            <div className="text-f1-red text-3xl mb-2">
              <i className="fas fa-trophy"></i>
            </div>
            <div className="text-2xl font-f1 font-black text-white mb-1">
              {stats?.standings?.drivers?.[0]?.driver || 'N/A'}
            </div>
            <div className="text-gray-400 text-sm">Championship Leader</div>
          </div>

          <div className="glass-panel rounded-xl p-6">
            <div className="text-f1-blue text-3xl mb-2">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="text-2xl font-f1 font-black text-white mb-1">
              {stats?.standings?.drivers?.[0]?.points || '0'}
            </div>
            <div className="text-gray-400 text-sm">Leader Points</div>
          </div>

          <div className="glass-panel rounded-xl p-6">
            <div className="text-f1-red text-3xl mb-2">
              <i className="fas fa-flag-checkered"></i>
            </div>
            <div className="text-2xl font-f1 font-black text-white mb-1">
              {stats?.standings?.drivers?.[0]?.wins || '0'}
            </div>
            <div className="text-gray-400 text-sm">Race Wins</div>
          </div>

          <div className="glass-panel rounded-xl p-6">
            <div className="text-f1-blue text-3xl mb-2">
              <i className="fas fa-users"></i>
            </div>
            <div className="text-2xl font-f1 font-black text-white mb-1">
              {stats?.standings?.drivers?.length || '0'}
            </div>
            <div className="text-gray-400 text-sm">Drivers</div>
          </div>
        </div>

        {/* Top Drivers */}
        <div className="glass-panel rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-f1 font-bold text-white mb-6">
            <i className="fas fa-star text-f1-red mr-2"></i>
            Top 5 Drivers
          </h2>
          <div className="space-y-4">
            {stats?.standings?.drivers?.slice(0, 5).map((driver: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                <div className="flex items-center space-x-4">
                  <span className="text-2xl font-f1 font-black text-f1-red w-8">
                    {driver.position}
                  </span>
                  <div>
                    <div className="text-white font-bold">{driver.driver}</div>
                    <div className="text-gray-400 text-sm">{driver.team}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-white font-bold text-lg">{driver.points} pts</div>
                  <div className="text-gray-400 text-sm">{driver.wins} wins</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Next Race Prediction */}
        {stats?.predictions?.winner_prediction && (
          <div className="glass-panel rounded-xl p-8">
            <h2 className="text-2xl font-f1 font-bold text-white mb-6">
              <i className="fas fa-chart-line text-f1-red mr-2"></i>
              Next Race Prediction
            </h2>
            <div className="text-center">
              <div className="text-4xl font-f1 font-black text-f1-red mb-2">
                {stats.predictions.winner_prediction.driver}
              </div>
              <div className="text-xl text-gray-300 mb-4">
                Predicted Winner - {stats.predictions.winner_prediction.confidence}% Confidence
              </div>
              <div className="text-gray-400 text-sm max-w-2xl mx-auto">
                {stats.predictions.winner_prediction.reasoning}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
