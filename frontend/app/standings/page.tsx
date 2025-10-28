'use client';

import { useEffect, useState } from 'react';
import apiService, { StandingsResponse } from '@/lib/api';

export default function StandingsPage() {
  const [standings, setStandings] = useState<StandingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'drivers' | 'constructors'>('drivers');

  useEffect(() => {
    async function fetchStandings() {
      try {
        const data = await apiService.getStandings();
        setStandings(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching standings:', error);
        setLoading(false);
      }
    }
    fetchStandings();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="animate-pulse text-white text-2xl">Loading standings...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl md:text-5xl font-f1 font-black text-center mb-4 f1-gradient-text">
          Championship Standings
        </h1>
        <p className="text-center text-gray-400 mb-12">2025 Formula 1 World Championship</p>

        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className="glass-panel rounded-lg p-1 inline-flex">
            <button
              onClick={() => setActiveTab('drivers')}
              className={`px-8 py-3 rounded-lg font-bold transition-all duration-300 ${
                activeTab === 'drivers'
                  ? 'bg-gradient-f1 text-white shadow-glow'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <i className="fas fa-user mr-2"></i>
              Drivers
            </button>
            <button
              onClick={() => setActiveTab('constructors')}
              className={`px-8 py-3 rounded-lg font-bold transition-all duration-300 ${
                activeTab === 'constructors'
                  ? 'bg-gradient-f1 text-white shadow-glow'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <i className="fas fa-flag mr-2"></i>
              Constructors
            </button>
          </div>
        </div>

        {/* Drivers Standings */}
        {activeTab === 'drivers' && standings?.drivers && (
          <div className="glass-panel rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-white/5">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Position
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Driver
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Team
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Points
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Wins
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10">
                  {standings.drivers.map((driver, index) => (
                    <tr
                      key={index}
                      className="hover:bg-white/5 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-2xl font-f1 font-black text-f1-red">
                          {driver.position}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-white font-bold">{driver.driver}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-gray-400">{driver.team}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-white font-bold text-lg">{driver.points}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-gray-400">{driver.wins}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Constructors Standings */}
        {activeTab === 'constructors' && standings?.constructors && (
          <div className="glass-panel rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-white/5">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Position
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Team
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Points
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-f1 text-gray-400 uppercase tracking-wider">
                      Wins
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10">
                  {standings.constructors.map((team, index) => (
                    <tr
                      key={index}
                      className="hover:bg-white/5 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-2xl font-f1 font-black text-f1-red">
                          {team.position}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-white font-bold text-lg">{team.team}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-white font-bold text-lg">{team.points}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-gray-400">{team.wins}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Metadata */}
        {standings && (
          <div className="mt-8 text-center text-gray-500 text-sm">
            <p>Season {standings.season} - Round {standings.round}</p>
            <p>Last Updated: {new Date(standings.last_updated).toLocaleString()}</p>
          </div>
        )}
      </div>
    </div>
  );
}
