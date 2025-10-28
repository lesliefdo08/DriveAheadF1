'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiService, NextRaceResponse } from '@/lib/api';

interface TimeLeft {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
}

export default function HomePage() {
  const [nextRace, setNextRace] = useState<NextRaceResponse | null>(null);
  const [timeLeft, setTimeLeft] = useState<TimeLeft | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNextRace = async () => {
      try {
        const data = await apiService.getNextRace();
        if (data) {
          setNextRace(data);
        }
      } catch (error) {
        console.error('Error fetching next race:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNextRace();
  }, []);

  useEffect(() => {
    if (!nextRace) return;

    const calculateTimeLeft = () => {
      const raceDate = new Date(nextRace.date + 'T' + nextRace.time);
      const now = new Date();
      const difference = raceDate.getTime() - now.getTime();

      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
          minutes: Math.floor((difference / 1000 / 60) % 60),
          seconds: Math.floor((difference / 1000) % 60)
        });
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, [nextRace]);

  return (
    <div className="min-h-screen overflow-x-hidden">
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-32 h-32 border border-red-500/30 rounded-full animate-pulse-slow"></div>
          <div className="absolute bottom-1/4 right-1/4 w-24 h-24 border border-blue-500/30 rounded-full animate-pulse-slow" style={{animationDelay: '1s'}}></div>
          <div className="absolute top-1/2 left-1/2 w-16 h-16 border border-yellow-500/30 rounded-full animate-pulse-slow" style={{animationDelay: '2s'}}></div>
          <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-transparent to-blue-500/5"></div>
        </div>
        
        <div className="container mx-auto px-6 text-center z-10">
          <div className="animate-slide-up">
            <h1 className="font-['Orbitron'] text-7xl md:text-9xl font-black mb-6 bg-gradient-to-r from-red-500 via-white to-blue-500 bg-clip-text text-transparent bg-[length:200%_200%] animate-gradient-shift">
              DriveAhead
            </h1>
            <p className="text-2xl md:text-4xl font-light mb-4 text-gray-300">
              F1 Analytics & Probability Engine
            </p>
            <p className="text-lg text-gray-400 mb-12 max-w-3xl mx-auto">
              Explore how machine learning interprets F1 data to calculate win probabilities. Track live standings, compare statistical favorites to race results, and dive into the beautiful chaos of Formula 1.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
              <Link href="/predictions" className="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105 shadow-[0_0_20px_rgba(255,30,30,0.3)]">
                <i className="fas fa-brain mr-2"></i>View Probabilities
              </Link>
              <Link href="/standings" className="border-2 border-gray-600 hover:border-red-500 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105">
                <i className="fas fa-trophy mr-2"></i>Live Standings
              </Link>
            </div>
            
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="font-['Orbitron'] text-3xl font-bold text-red-500">97.0%</div>
                <div className="text-sm text-gray-400">MODEL ACCURACY</div>
              </div>
              <div className="text-center">
                <div className="font-['Orbitron'] text-3xl font-bold text-blue-500">3 AI</div>
                <div className="text-sm text-gray-400">ALGORITHMS</div>
              </div>
              <div className="text-center">
                <div className="font-['Orbitron'] text-3xl font-bold text-green-500">2025</div>
                <div className="text-sm text-gray-400">LIVE SEASON</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gradient-to-b from-black to-gray-900">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <h2 className="font-['Orbitron'] text-4xl font-bold text-center mb-12 text-white">Next Race</h2>
            
            <div className="grid lg:grid-cols-2 gap-8">
              <div className="bg-black/70 backdrop-blur-[15px] border border-white/10 rounded-2xl p-8">
                <div className="space-y-4">
                  {loading ? (
                    <div className="animate-pulse">
                      <div className="h-6 bg-gray-700 rounded w-3/4 mb-3"></div>
                      <div className="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
                      <div className="h-4 bg-gray-700 rounded w-2/3"></div>
                    </div>
                  ) : nextRace ? (
                    <>
                      <h3 className="font-['Orbitron'] text-2xl font-bold text-white">{nextRace.name}</h3>
                      <div className="flex items-center text-gray-300">
                        <i className="fas fa-map-marker-alt mr-2 text-red-500"></i>
                        <span>{nextRace.location}</span>
                      </div>
                      <div className="flex items-center text-gray-300">
                        <i className="fas fa-road mr-2 text-red-500"></i>
                        <span>{nextRace.circuit}</span>
                      </div>
                      <div className="flex items-center text-gray-300">
                        <i className="fas fa-calendar mr-2 text-red-500"></i>
                        <span>{new Date(nextRace.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                      </div>
                      <div className="flex items-center text-gray-300">
                        <i className="fas fa-clock mr-2 text-red-500"></i>
                        <span>{nextRace.time} (Local Time)</span>
                      </div>
                    </>
                  ) : (
                    <div className="text-gray-400">No upcoming race data available</div>
                  )}
                </div>
              </div>
              
              <div className="bg-black/70 backdrop-blur-[15px] border border-white/10 rounded-2xl p-8">
                <div className="text-center">
                  <div className="text-sm text-gray-400 mb-6">
                    {nextRace ? nextRace.name : 'Loading...'}
                  </div>
                  <div className="text-white text-lg font-semibold mb-4">NEXT RACE COUNTDOWN</div>
                  <div className="flex justify-center items-center gap-4 flex-wrap">
                    <div className="text-center bg-gradient-to-br from-red-600/15 to-red-500/10 border-2 border-red-600/40 rounded-2xl p-6 min-w-[100px] relative overflow-hidden transition-all duration-300 hover:border-red-600/60 hover:-translate-y-0.5 hover:shadow-[0_8px_25px_rgba(220,38,38,0.2)]">
                      <span className="font-['Orbitron'] text-4xl font-black text-red-500 block leading-none" style={{textShadow: '0 0 10px rgba(239,68,68,0.5)'}}>
                        {timeLeft ? String(timeLeft.days).padStart(2, '0') : '--'}
                      </span>
                      <div className="text-xs text-gray-400 font-semibold uppercase tracking-wider mt-2">DAYS</div>
                    </div>
                    <div className="text-center bg-gradient-to-br from-red-600/15 to-red-500/10 border-2 border-red-600/40 rounded-2xl p-6 min-w-[100px] relative overflow-hidden transition-all duration-300 hover:border-red-600/60 hover:-translate-y-0.5 hover:shadow-[0_8px_25px_rgba(220,38,38,0.2)]">
                      <span className="font-['Orbitron'] text-4xl font-black text-red-500 block leading-none" style={{textShadow: '0 0 10px rgba(239,68,68,0.5)'}}>
                        {timeLeft ? String(timeLeft.hours).padStart(2, '0') : '--'}
                      </span>
                      <div className="text-xs text-gray-400 font-semibold uppercase tracking-wider mt-2">HOURS</div>
                    </div>
                    <div className="text-center bg-gradient-to-br from-red-600/15 to-red-500/10 border-2 border-red-600/40 rounded-2xl p-6 min-w-[100px] relative overflow-hidden transition-all duration-300 hover:border-red-600/60 hover:-translate-y-0.5 hover:shadow-[0_8px_25px_rgba(220,38,38,0.2)]">
                      <span className="font-['Orbitron'] text-4xl font-black text-red-500 block leading-none" style={{textShadow: '0 0 10px rgba(239,68,68,0.5)'}}>
                        {timeLeft ? String(timeLeft.minutes).padStart(2, '0') : '--'}
                      </span>
                      <div className="text-xs text-gray-400 font-semibold uppercase tracking-wider mt-2">MINUTES</div>
                    </div>
                    <div className="text-center bg-gradient-to-br from-red-600/15 to-red-500/10 border-2 border-red-600/40 rounded-2xl p-6 min-w-[100px] relative overflow-hidden transition-all duration-300 hover:border-red-600/60 hover:-translate-y-0.5 hover:shadow-[0_8px_25px_rgba(220,38,38,0.2)]">
                      <span className="font-['Orbitron'] text-4xl font-black text-red-500 block leading-none" style={{textShadow: '0 0 10px rgba(239,68,68,0.5)'}}>
                        {timeLeft ? String(timeLeft.seconds).padStart(2, '0') : '--'}
                      </span>
                      <div className="text-xs text-gray-400 font-semibold uppercase tracking-wider mt-2">SECONDS</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-['Orbitron'] text-4xl font-bold mb-4 text-white">Why DriveAhead?</h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              For fans who want live F1 data. For students learning ML. For developers building portfolios. For anyone who loves racing analytics.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-black/70 backdrop-blur-[15px] border border-white/10 rounded-xl p-6 hover:transform hover:scale-105 transition-all duration-300">
              <div className="text-center">
                <i className="fas fa-flag-checkered text-4xl text-red-500 mb-4"></i>
                <h3 className="font-['Orbitron'] text-xl font-bold mb-3 text-white">For F1 Fans</h3>
                <p className="text-gray-400 mb-6 text-sm">
                  Live 2025 season data with race countdowns, up-to-date standings, and probability insights. See which drivers ML favors and compare favorites to actual race chaos.
                </p>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-red-500">LIVE</div>
                    <div className="text-xs text-gray-400">2025 DATA</div>
                  </div>
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-red-500">24/7</div>
                    <div className="text-xs text-gray-400">UPDATES</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-black/70 backdrop-blur-[15px] border border-white/10 rounded-xl p-6 hover:transform hover:scale-105 transition-all duration-300">
              <div className="text-center">
                <i className="fas fa-graduation-cap text-4xl text-blue-500 mb-4"></i>
                <h3 className="font-['Orbitron'] text-xl font-bold mb-3 text-white">For Students</h3>
                <p className="text-gray-400 mb-6 text-sm">
                  Learn how ML interprets sports statistics. See Random Forest, XGBoost, and Logistic Regression in action. Understand probability vs certainty in unpredictable domains.
                </p>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-blue-500">3 AI</div>
                    <div className="text-xs text-gray-400">ALGORITHMS</div>
                  </div>
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-blue-500">97%</div>
                    <div className="text-xs text-gray-400">ACCURACY</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-black/70 backdrop-blur-[15px] border border-white/10 rounded-xl p-6 hover:transform hover:scale-105 transition-all duration-300">
              <div className="text-center">
                <i className="fas fa-code text-4xl text-green-500 mb-4"></i>
                <h3 className="font-['Orbitron'] text-xl font-bold mb-3 text-white">For Developers</h3>
                <p className="text-gray-400 mb-6 text-sm">
                  Full-stack ML deployment: Flask backend, real-time API integration, model training pipeline, professional F1 broadcast UI, and production deployment on Render.
                </p>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-green-500">FULL</div>
                    <div className="text-xs text-gray-400">STACK ML</div>
                  </div>
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-green-500">PROD</div>
                    <div className="text-xs text-gray-400">DEPLOYED</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-black/70 backdrop-blur-[15px] border border-white/10 rounded-xl p-6 hover:transform hover:scale-105 transition-all duration-300">
              <div className="text-center">
                <i className="fas fa-chart-line text-4xl text-yellow-500 mb-4"></i>
                <h3 className="font-['Orbitron'] text-xl font-bold mb-3 text-white">Probability Analytics</h3>
                <p className="text-gray-400 mb-6 text-sm">
                  This isn't fortune telling—it's statistical analysis. Track championship leader probabilities vs unpredictable race outcomes. When favorites lose, racing gets exciting!
                </p>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-yellow-500">STATS</div>
                    <div className="text-xs text-gray-400">NOT MAGIC</div>
                  </div>
                  <div>
                    <div className="font-['Orbitron'] text-lg font-bold text-yellow-500">CHAOS</div>
                    <div className="text-xs text-gray-400">IS EXCITING</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
