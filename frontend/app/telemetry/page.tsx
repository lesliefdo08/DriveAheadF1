'use client';

import { useEffect, useState } from 'react';
import apiService, { TelemetryData } from '@/lib/api';

export default function TelemetryPage() {
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState<'live' | 'track' | 'analytics'>('live');
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    async function fetchTelemetry() {
      try {
        const data = await apiService.getTelemetry();
        setTelemetry(data);
        setLastUpdate(new Date());
        setLoading(false);
      } catch (error) {
        console.error('Error fetching telemetry:', error);
        setLoading(false);
      }
    }

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 1500); // Update every 1.5 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-red-500"></div>
            <div className="text-white text-2xl font-['Orbitron']">Initializing Telemetry Systems...</div>
            <div className="text-gray-400">Connecting to live data feed</div>
          </div>
        </div>
      </div>
    );
  }

  // Extract drivers from telemetry
  const drivers = telemetry ? Object.entries(telemetry)
    .filter(([key]) => key !== '_meta')
    .map(([number, data]: [string, any]) => ({
      number,
      ...data,
    }))
    .sort((a, b) => a.position - b.position) : [];

  const meta = telemetry?._meta as any;

  // Calculate gaps and intervals
  const driversWithGaps = drivers.map((driver, index) => {
    if (index === 0) {
      return { ...driver, gap: 'LEADER', interval: '-' };
    }
    const leader = drivers[0];
    const ahead = drivers[index - 1];
    
    // Simple gap calculation (in a real app, this would come from actual timing data)
    const gapToLeader = `+${(index * 2.5).toFixed(1)}s`;
    const interval = `+${(0.5 + Math.random() * 2).toFixed(3)}s`;
    
    return { ...driver, gap: gapToLeader, interval };
  });

  // Mock weather data (in production, this would come from API)
  const weather = {
    airTemp: 28,
    trackTemp: 42,
    humidity: 65,
    windSpeed: 12,
    windDirection: 'NE',
    rainfall: 0,
    condition: 'Dry'
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black py-20 px-4">
      <div className="container mx-auto max-w-7xl">
        {/* Header with Live Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <h1 className="font-['Orbitron'] text-4xl font-bold text-white">
                Live Telemetry
              </h1>
              <div className="flex items-center gap-2 bg-red-600/20 border border-red-500 rounded-full px-4 py-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-red-500 font-bold text-sm">LIVE</span>
              </div>
            </div>
            <div className="text-gray-400 text-sm">
              Updated: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>

          {/* Session Info Bar */}
          {meta && (
            <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-4">
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 text-center">
                <div>
                  <div className="text-gray-400 text-xs uppercase mb-1">Session</div>
                  <div className="text-white font-bold">{meta.session_type || 'Race'}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs uppercase mb-1">Status</div>
                  <div className="text-green-500 font-bold">{meta.session_status || 'Active'}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs uppercase mb-1">Lap</div>
                  <div className="text-white font-bold">{meta.current_lap || '15'} / {meta.total_laps || '57'}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs uppercase mb-1">Track Temp</div>
                  <div className="text-orange-500 font-bold">{weather.trackTemp}°C</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs uppercase mb-1">Air Temp</div>
                  <div className="text-blue-400 font-bold">{weather.airTemp}°C</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs uppercase mb-1">Conditions</div>
                  <div className="text-white font-bold flex items-center justify-center gap-1">
                    <i className="fas fa-sun text-yellow-400"></i>
                    {weather.condition}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* View Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveView('live')}
            className={`px-6 py-3 rounded-lg font-bold transition-all duration-300 ${
              activeView === 'live'
                ? 'bg-gradient-to-r from-red-600 to-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.5)]'
                : 'bg-black/50 border border-white/10 text-gray-400 hover:text-white hover:border-red-500/50'
            }`}
          >
            <i className="fas fa-tachometer-alt mr-2"></i>
            Live Timing
          </button>
          <button
            onClick={() => setActiveView('track')}
            className={`px-6 py-3 rounded-lg font-bold transition-all duration-300 ${
              activeView === 'track'
                ? 'bg-gradient-to-r from-red-600 to-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.5)]'
                : 'bg-black/50 border border-white/10 text-gray-400 hover:text-white hover:border-red-500/50'
            }`}
          >
            <i className="fas fa-map-marked-alt mr-2"></i>
            Track Map
          </button>
          <button
            onClick={() => setActiveView('analytics')}
            className={`px-6 py-3 rounded-lg font-bold transition-all duration-300 ${
              activeView === 'analytics'
                ? 'bg-gradient-to-r from-red-600 to-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.5)]'
                : 'bg-black/50 border border-white/10 text-gray-400 hover:text-white hover:border-red-500/50'
            }`}
          >
            <i className="fas fa-chart-line mr-2"></i>
            Analytics
          </button>
        </div>

        {/* Live Timing View */}
        {activeView === 'live' && (
          <div className="space-y-6">
            {/* Timing Tower */}
            <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden">
              <div className="bg-gradient-to-r from-red-600 to-red-500 p-4">
                <h2 className="font-['Orbitron'] text-xl font-bold text-white">
                  <i className="fas fa-list-ol mr-2"></i>
                  Timing Tower
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-black/50">
                    <tr className="text-gray-400 text-xs uppercase">
                      <th className="p-3 text-left">Pos</th>
                      <th className="p-3 text-left">Driver</th>
                      <th className="p-3 text-left">Team</th>
                      <th className="p-3 text-center">Last Lap</th>
                      <th className="p-3 text-center">Gap</th>
                      <th className="p-3 text-center">Interval</th>
                      <th className="p-3 text-center">Tire</th>
                      <th className="p-3 text-center">Laps</th>
                      <th className="p-3 text-center">DRS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {driversWithGaps.map((driver, index) => (
                      <tr 
                        key={driver.number}
                        className={`border-t border-white/10 hover:bg-white/5 transition-colors ${
                          index < 3 ? 'bg-green-500/5' : ''
                        }`}
                      >
                        <td className="p-3">
                          <span className={`font-bold ${
                            index === 0 ? 'text-yellow-400' :
                            index === 1 ? 'text-gray-300' :
                            index === 2 ? 'text-orange-400' :
                            'text-white'
                          }`}>
                            {driver.position}
                          </span>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <div className="w-1 h-8 bg-red-500 rounded"></div>
                            <div>
                              <div className="font-bold text-white">{driver.driver}</div>
                              <div className="text-xs text-gray-500">#{driver.number}</div>
                            </div>
                          </div>
                        </td>
                        <td className="p-3 text-gray-300">{driver.team}</td>
                        <td className="p-3 text-center">
                          <span className="font-mono text-white">{driver.last_lap_time || '1:24.567'}</span>
                        </td>
                        <td className="p-3 text-center">
                          <span className={`font-mono ${
                            driver.gap === 'LEADER' ? 'text-green-400 font-bold' : 'text-gray-300'
                          }`}>
                            {driver.gap}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <span className="font-mono text-gray-400">{driver.interval}</span>
                        </td>
                        <td className="p-3 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            driver.tire_compound === 'SOFT' ? 'bg-red-600 text-white' :
                            driver.tire_compound === 'MEDIUM' ? 'bg-yellow-500 text-black' :
                            driver.tire_compound === 'HARD' ? 'bg-gray-300 text-black' :
                            'bg-green-600 text-white'
                          }`}>
                            {driver.tire_compound || 'SOFT'}
                          </span>
                        </td>
                        <td className="p-3 text-center text-white">
                          {driver.tire_laps || Math.floor(Math.random() * 15)}
                        </td>
                        <td className="p-3 text-center">
                          {driver.drs_enabled ? (
                            <span className="text-green-400">
                              <i className="fas fa-check-circle"></i>
                            </span>
                          ) : (
                            <span className="text-gray-600">
                              <i className="fas fa-times-circle"></i>
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Speed Trap & Sector Times */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Sector Times */}
              <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-6">
                <h3 className="font-['Orbitron'] text-lg font-bold text-white mb-4">
                  <i className="fas fa-clock mr-2 text-blue-400"></i>
                  Latest Sector Times
                </h3>
                <div className="space-y-3">
                  {drivers.slice(0, 5).map((driver) => (
                    <div key={driver.number} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center text-white font-bold text-sm">
                          {driver.position}
                        </div>
                        <span className="text-white font-bold">{driver.driver}</span>
                      </div>
                      <div className="flex gap-2">
                        <span className="font-mono text-green-400 text-sm">S1: 23.5</span>
                        <span className="font-mono text-yellow-400 text-sm">S2: 38.2</span>
                        <span className="font-mono text-purple-400 text-sm">S3: 22.8</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Speed Trap */}
              <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-6">
                <h3 className="font-['Orbitron'] text-lg font-bold text-white mb-4">
                  <i className="fas fa-tachometer-alt mr-2 text-red-400"></i>
                  Speed Trap Leaders
                </h3>
                <div className="space-y-3">
                  {drivers.slice(0, 5).map((driver, idx) => {
                    const speed = 340 - (idx * 3);
                    return (
                      <div key={driver.number} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                            idx === 0 ? 'bg-purple-600' : 'bg-gray-600'
                          }`}>
                            {idx + 1}
                          </div>
                          <span className="text-white font-bold">{driver.driver}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-red-400">{speed}</div>
                          <div className="text-xs text-gray-400">km/h</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Track Map View */}
        {activeView === 'track' && (
          <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-8">
            <h2 className="font-['Orbitron'] text-2xl font-bold text-white mb-6">
              <i className="fas fa-map-marked-alt mr-2"></i>
              Circuit Map - Live Positions
            </h2>
            
            {/* SVG Track Map Placeholder */}
            <div className="bg-gradient-to-br from-gray-900 to-black rounded-xl p-8 border border-white/10">
              <div className="relative w-full aspect-video flex items-center justify-center">
                <svg viewBox="0 0 800 400" className="w-full h-full">
                  {/* Track outline */}
                  <path
                    d="M 100 200 Q 100 100, 200 100 L 600 100 Q 700 100, 700 200 Q 700 300, 600 300 L 200 300 Q 100 300, 100 200 Z"
                    fill="none"
                    stroke="#374151"
                    strokeWidth="40"
                  />
                  <path
                    d="M 100 200 Q 100 100, 200 100 L 600 100 Q 700 100, 700 200 Q 700 300, 600 300 L 200 300 Q 100 300, 100 200 Z"
                    fill="none"
                    stroke="#1f2937"
                    strokeWidth="30"
                  />
                  
                  {/* DRS Zone */}
                  <path
                    d="M 200 100 L 400 100"
                    stroke="#10b981"
                    strokeWidth="8"
                    opacity="0.5"
                  />
                  
                  {/* Start/Finish Line */}
                  <rect x="95" y="180" width="10" height="40" fill="#ef4444" />
                  <text x="80" y="170" fill="#ef4444" fontSize="12" fontWeight="bold">START</text>
                  
                  {/* Car positions (animated dots) */}
                  {drivers.slice(0, 8).map((driver, idx) => {
                    const angle = (idx / 8) * Math.PI * 2;
                    const radius = 150;
                    const cx = 400 + Math.cos(angle) * radius;
                    const cy = 200 + Math.sin(angle) * radius;
                    
                    return (
                      <g key={driver.number}>
                        <circle
                          cx={cx}
                          cy={cy}
                          r="8"
                          fill="#ef4444"
                          className="animate-pulse"
                        />
                        <text
                          x={cx}
                          y={cy - 15}
                          fill="white"
                          fontSize="10"
                          fontWeight="bold"
                          textAnchor="middle"
                        >
                          {driver.position}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </div>
              <div className="mt-4 text-center text-gray-400">
                <i className="fas fa-info-circle mr-2"></i>
                Real-time car positions on track (simulated data)
              </div>
            </div>

            {/* Track Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/5 rounded-lg p-4 text-center">
                <div className="text-gray-400 text-xs uppercase mb-1">Circuit Length</div>
                <div className="text-white font-bold text-xl">5.412 km</div>
              </div>
              <div className="bg-white/5 rounded-lg p-4 text-center">
                <div className="text-gray-400 text-xs uppercase mb-1">Total Corners</div>
                <div className="text-white font-bold text-xl">16</div>
              </div>
              <div className="bg-white/5 rounded-lg p-4 text-center">
                <div className="text-gray-400 text-xs uppercase mb-1">DRS Zones</div>
                <div className="text-green-400 font-bold text-xl">2</div>
              </div>
              <div className="bg-white/5 rounded-lg p-4 text-center">
                <div className="text-gray-400 text-xs uppercase mb-1">Lap Record</div>
                <div className="text-purple-400 font-bold text-xl">1:18.887</div>
              </div>
            </div>
          </div>
        )}

        {/* Analytics View */}
        {activeView === 'analytics' && (
          <div className="space-y-6">
            {/* Tire Strategy */}
            <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-6">
              <h2 className="font-['Orbitron'] text-xl font-bold text-white mb-6">
                <i className="fas fa-circle-notch mr-2 text-yellow-400"></i>
                Tire Strategy Analysis
              </h2>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-red-600/20 to-red-500/10 border border-red-500/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-bold">SOFT</span>
                    <div className="w-8 h-8 rounded-full bg-red-600"></div>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {drivers.filter(d => d.tire_compound === 'SOFT').length}
                  </div>
                  <div className="text-sm text-gray-400">drivers currently on softs</div>
                  <div className="mt-3 text-xs text-gray-400">
                    Avg Laps: 8-12 | Grip: High | Degradation: Fast
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-400/10 border border-yellow-500/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-bold">MEDIUM</span>
                    <div className="w-8 h-8 rounded-full bg-yellow-500"></div>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {drivers.filter(d => d.tire_compound === 'MEDIUM').length}
                  </div>
                  <div className="text-sm text-gray-400">drivers currently on mediums</div>
                  <div className="mt-3 text-xs text-gray-400">
                    Avg Laps: 15-20 | Grip: Medium | Degradation: Medium
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-gray-400/20 to-gray-300/10 border border-gray-400/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-bold">HARD</span>
                    <div className="w-8 h-8 rounded-full bg-gray-300"></div>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {drivers.filter(d => d.tire_compound === 'HARD').length}
                  </div>
                  <div className="text-sm text-gray-400">drivers currently on hards</div>
                  <div className="mt-3 text-xs text-gray-400">
                    Avg Laps: 25-30 | Grip: Low | Degradation: Slow
                  </div>
                </div>
              </div>
            </div>

            {/* Weather Dashboard */}
            <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-6">
              <h2 className="font-['Orbitron'] text-xl font-bold text-white mb-6">
                <i className="fas fa-cloud-sun mr-2 text-blue-400"></i>
                Weather Conditions
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                <div className="bg-orange-500/10 border border-orange-500/50 rounded-lg p-4 text-center">
                  <i className="fas fa-temperature-high text-3xl text-orange-400 mb-2"></i>
                  <div className="text-2xl font-bold text-white">{weather.trackTemp}°C</div>
                  <div className="text-xs text-gray-400">Track Temp</div>
                </div>
                
                <div className="bg-blue-500/10 border border-blue-500/50 rounded-lg p-4 text-center">
                  <i className="fas fa-thermometer-half text-3xl text-blue-400 mb-2"></i>
                  <div className="text-2xl font-bold text-white">{weather.airTemp}°C</div>
                  <div className="text-xs text-gray-400">Air Temp</div>
                </div>
                
                <div className="bg-cyan-500/10 border border-cyan-500/50 rounded-lg p-4 text-center">
                  <i className="fas fa-tint text-3xl text-cyan-400 mb-2"></i>
                  <div className="text-2xl font-bold text-white">{weather.humidity}%</div>
                  <div className="text-xs text-gray-400">Humidity</div>
                </div>
                
                <div className="bg-green-500/10 border border-green-500/50 rounded-lg p-4 text-center">
                  <i className="fas fa-wind text-3xl text-green-400 mb-2"></i>
                  <div className="text-2xl font-bold text-white">{weather.windSpeed}</div>
                  <div className="text-xs text-gray-400">Wind km/h</div>
                </div>
                
                <div className="bg-purple-500/10 border border-purple-500/50 rounded-lg p-4 text-center">
                  <i className="fas fa-compass text-3xl text-purple-400 mb-2"></i>
                  <div className="text-2xl font-bold text-white">{weather.windDirection}</div>
                  <div className="text-xs text-gray-400">Direction</div>
                </div>
                
                <div className="bg-blue-600/10 border border-blue-600/50 rounded-lg p-4 text-center">
                  <i className="fas fa-cloud-rain text-3xl text-blue-500 mb-2"></i>
                  <div className="text-2xl font-bold text-white">{weather.rainfall}%</div>
                  <div className="text-xs text-gray-400">Rain Chance</div>
                </div>
                
                <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-4 text-center">
                  <i className="fas fa-sun text-3xl text-yellow-400 mb-2"></i>
                  <div className="text-2xl font-bold text-white">{weather.condition}</div>
                  <div className="text-xs text-gray-400">Condition</div>
                </div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-6">
                <h3 className="font-['Orbitron'] text-lg font-bold text-white mb-4">
                  <i className="fas fa-bolt mr-2 text-yellow-400"></i>
                  Top Speed Analysis
                </h3>
                <div className="space-y-3">
                  {drivers.slice(0, 5).map((driver, idx) => {
                    const speed = 342 - (idx * 2);
                    const percentage = (speed / 350) * 100;
                    return (
                      <div key={driver.number}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-white font-bold">{driver.driver}</span>
                          <span className="text-red-400 font-mono">{speed} km/h</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-red-600 to-orange-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-6">
                <h3 className="font-['Orbitron'] text-lg font-bold text-white mb-4">
                  <i className="fas fa-stopwatch mr-2 text-green-400"></i>
                  Best Lap Times
                </h3>
                <div className="space-y-3">
                  {drivers.slice(0, 5).map((driver, idx) => {
                    const baseTime = 84.567;
                    const lapTime = baseTime + (idx * 0.234);
                    const minutes = Math.floor(lapTime / 60);
                    const seconds = (lapTime % 60).toFixed(3);
                    
                    return (
                      <div key={driver.number} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                            idx === 0 ? 'bg-purple-600' : 'bg-gray-600'
                          }`}>
                            {idx + 1}
                          </div>
                          <span className="text-white font-bold">{driver.driver}</span>
                        </div>
                        <span className="font-mono text-purple-400 font-bold">
                          {minutes}:{seconds.padStart(6, '0')}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Pit Stop Strategy */}
            <div className="bg-black/70 backdrop-blur-md border border-white/10 rounded-xl p-6">
              <h3 className="font-['Orbitron'] text-lg font-bold text-white mb-4">
                <i className="fas fa-tools mr-2 text-orange-400"></i>
                Pit Stop Predictions
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-green-600/20 to-green-500/10 border border-green-500/50 rounded-lg p-4">
                  <div className="text-green-400 font-bold mb-2">
                    <i className="fas fa-check-circle mr-2"></i>
                    Completed Stops
                  </div>
                  <div className="text-4xl font-bold text-white mb-2">
                    {Math.floor(drivers.length * 0.6)}
                  </div>
                  <div className="text-sm text-gray-400">
                    Average: 2.4s
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-400/10 border border-yellow-500/50 rounded-lg p-4">
                  <div className="text-yellow-400 font-bold mb-2">
                    <i className="fas fa-clock mr-2"></i>
                    Predicted Next
                  </div>
                  <div className="text-4xl font-bold text-white mb-2">
                    {Math.floor(drivers.length * 0.3)}
                  </div>
                  <div className="text-sm text-gray-400">
                    Within 3 laps
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-blue-600/20 to-blue-500/10 border border-blue-500/50 rounded-lg p-4">
                  <div className="text-blue-400 font-bold mb-2">
                    <i className="fas fa-trophy mr-2"></i>
                    Fastest Stop
                  </div>
                  <div className="text-4xl font-bold text-white mb-2">
                    1.9s
                  </div>
                  <div className="text-sm text-gray-400">
                    Red Bull Racing
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
