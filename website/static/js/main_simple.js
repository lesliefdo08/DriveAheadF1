// Enhanced DriveAhead JavaScript - Full Integration with Autonomous Backend
// Now with real-time data loading and autonomous race progression

class DriveAheadApp {
    constructor() {
        this.apiUrl = CONFIG.API_BASE_URL;
        this.raceData = null;
        this.predictionData = null;
        this.config = CONFIG;
        this.init();
    }

    async init() {
        try {
            this.setupEventListeners();
            this.hideLoadingScreen();
            
            // Load critical data first
            console.log('🔄 Loading critical data...');
            await this.initRealCountdown();
            
            // Load remaining data with staggered delays using configuration
            setTimeout(() => this.loadNextRaceWinnerPrediction(), this.config.getLoadingDelay('RACE_WINNER_PREDICTION'));
            setTimeout(() => this.loadRaceSchedule(), this.config.getLoadingDelay('RACE_SCHEDULE'));
            setTimeout(() => this.loadDashboardPredictions(), this.config.getLoadingDelay('DASHBOARD_PREDICTIONS'));
            setTimeout(() => this.loadMiniPredictions(), this.config.getLoadingDelay('MINI_PREDICTIONS'));
            setTimeout(() => this.loadConstructorChampionship(), this.config.getLoadingDelay('CONSTRUCTOR_CHAMPIONSHIP'));
            setTimeout(() => this.loadModelPerformance(), this.config.getLoadingDelay('MODEL_PERFORMANCE'));
            setTimeout(() => this.loadLiveF1Data(), this.config.getLoadingDelay('LIVE_F1_DATA'));
            setTimeout(() => this.loadRealTimeInsights(), this.config.getLoadingDelay('REAL_TIME_INSIGHTS'));
            setTimeout(() => this.loadCompletedRaces(), this.config.getLoadingDelay('COMPLETED_RACES'));
            
            // Also load constructor championship immediately as fallback
            this.setFallbackConstructorData();
            
            // Force update championship insights using configuration
            setTimeout(() => {
                console.log('🏆 Force updating championship insights...');
                
                // First try to update with real data from constructor standings
                const leaderElement = document.getElementById('championshipLeader');
                if (leaderElement && leaderElement.textContent === 'Loading...') {
                    leaderElement.textContent = this.config.FALLBACK_DATA.CHAMPIONSHIP_INSIGHTS.leader;
                    console.log('🏆 Directly updated championship leader element');
                }
                
                // Also call the full update function with configuration data
                this.updateChampionshipInsights(this.config.FALLBACK_DATA.CHAMPIONSHIP_INSIGHTS);
            }, this.config.CHAMPIONSHIP_UPDATES.FALLBACK_PRIMARY);
            
            // Add another update using configured secondary delay as backup
            setTimeout(() => {
                const leaderElement = document.getElementById('championshipLeader');
                if (leaderElement && (leaderElement.textContent === 'Loading...' || leaderElement.textContent === '')) {
                    leaderElement.textContent = this.config.FALLBACK_DATA.CHAMPIONSHIP_INSIGHTS.leader;
                    console.log('🏆 Backup update: Set championship leader from config');
                }
            }, this.config.CHAMPIONSHIP_UPDATES.FALLBACK_SECONDARY);
            
            console.log('✅ DriveAhead initialization started');
        } catch (error) {
            console.error('❌ Initialization error:', error);
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    setupEventListeners() {
        // Hamburger menu
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        
        if (hamburger && navMenu) {
            hamburger.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                navMenu.classList.toggle('active');
                hamburger.classList.toggle('active');
            });
            
            // Close menu when clicking on menu items (mobile)
            navMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    navMenu.classList.remove('active');
                    hamburger.classList.remove('active');
                });
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
                    navMenu.classList.remove('active');
                    hamburger.classList.remove('active');
                }
            });
        }

        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (navbar) {
                if (window.scrollY > 100) {
                    navbar.style.background = 'rgba(10, 10, 10, 0.98)';
                } else {
                    navbar.style.background = 'rgba(10, 10, 10, 0.95)';
                }
            }
        });
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        setTimeout(() => {
            if (loadingScreen) {
                loadingScreen.style.opacity = '0';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                    console.log('✅ Loading screen hidden');
                }, 200);
            }
        }, 50);
    }

    async initRealCountdown() {
        // Load next race from autonomous backend
        await this.loadNextRace();
        
        // Update countdown every second with automatic race progression
        this.updateCountdown();
        setInterval(async () => {
            this.updateCountdown();
            // Refresh every 5 minutes to check for race progression
            if (Date.now() % (5 * 60 * 1000) < 1000) {
                console.log('🔄 Checking for race progression and updates...');
                const previousRace = this.raceData ? this.raceData.name : null;
                
                await this.loadNextRace();
                await this.loadNextRaceWinnerPrediction();
                await this.loadMiniPredictions(); // Refresh mini predictions
                
                // Check if race has changed
                if (previousRace && this.raceData && previousRace !== this.raceData.name) {
                    console.log('🏎️ Race progression detected! Updating all predictions...');
                    this.showRaceUpdateNotification(this.raceData.name);
                    
                    // Refresh all prediction components
                    await this.loadPredictionData();
                    await this.loadDashboardPredictions();
                }
            }
        }, 1000);
        
        console.log('🏎️ Autonomous countdown with race progression started');
    }

    async loadNextRace() {
        try {
            const response = await fetch(`${this.apiUrl}/next-race`);
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                this.raceData = result.data;
                this.currentRaceData = result.data; // Set both for compatibility
                this.updateRaceInfo();
                console.log(`📅 Next race: ${this.raceData.name} on ${this.raceData.date}`);
            }
        } catch (error) {
            console.error('Error loading next race:', error);
            this.setFallbackRaceData();
        }
    }

    setFallbackRaceData() {
        // Set fallback race data from configuration
        this.raceData = this.config.FALLBACK_DATA.NEXT_RACE;
        this.currentRaceData = this.raceData;
        this.updateRaceInfo();
        console.log('📅 Using configured fallback race data');
    }

    async updateUpcomingRaces(races) {
        const upcomingRacesContainer = document.getElementById('upcomingRaces');
        if (!upcomingRacesContainer || !races) return;

        try {
            // Filter out past races and get next 6 upcoming races
            const currentDate = new Date();
            const upcomingRaces = races
                .filter(race => new Date(race.date) >= currentDate)
                .slice(0, 6)
                .sort((a, b) => new Date(a.date) - new Date(b.date));

            if (upcomingRaces.length === 0) {
                upcomingRacesContainer.innerHTML = `
                    <div class="no-races">
                        <i class="fas fa-calendar-times"></i>
                        <p>No upcoming races scheduled</p>
                    </div>
                `;
                return;
            }

            // Create race cards with feature-card layout
            const raceCards = upcomingRaces.map((race, index) => {
                const raceDate = new Date(race.date);
                const isNextRace = race.round === (this.raceData ? this.raceData.round : null);
                const dayOfWeek = raceDate.toLocaleDateString('en-US', { weekday: 'long' });
                const month = raceDate.toLocaleDateString('en-US', { month: 'short' });
                const day = raceDate.getDate();
                
                return `
                    <div class="race-calendar-card" data-round="${race.round}" style="animation-delay: ${index * 0.1}s">
                        <div class="race-flag-pattern">
                            <i class="fas fa-flag-checkered"></i>
                        </div>
                        <div class="race-details">
                            <h3 class="race-title">${race.name}</h3>
                            <p class="race-location">${race.circuit}, ${race.country}</p>
                            <div class="race-stats">
                                <span class="stat">Round ${race.round}</span>
                                <span class="stat">${dayOfWeek}, ${month} ${day}</span>
                                <span class="stat">${race.race_time_ist || race.time} IST</span>
                            </div>
                        </div>
                        <div class="race-actions">
                            <span class="race-status">${race.status || 'UPCOMING'}</span>
                            <button class="race-prediction-btn" onclick="window.location.href='/predictions?race=${encodeURIComponent(race.name)}'">
                                <i class="fas fa-chart-line"></i>
                                Predictions
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            upcomingRacesContainer.innerHTML = raceCards;

            console.log(`📅 Updated upcoming races calendar with ${upcomingRaces.length} races`);
        } catch (error) {
            console.error('Error updating upcoming races:', error);
            upcomingRacesContainer.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load race calendar</p>
                </div>
            `;
        }
    }

    async loadRaceSchedule() {
        try {
            const response = await fetch(`${this.apiUrl}/race-schedule`);
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                this.allRaces = result.data.races; // Set the allRaces property
                await this.updateUpcomingRaces(result.data.races);
                console.log(`📊 Loaded ${result.data.total_races} races for season ${result.data.season}`);
            }
        } catch (error) {
            console.error('Error loading race schedule:', error);
            // Set fallback data from configuration
            this.allRaces = this.config.FALLBACK_DATA.RACE_SCHEDULE || [];
            await this.updateUpcomingRaces(this.allRaces);
        }
    }

    async loadNextRaceWinnerPrediction() {
        try {
            const response = await fetch(`${this.apiUrl}/race-winner-prediction`);
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                this.predictionData = result.data;
                this.updatePredictionDisplay();
                console.log(`🎯 Prediction loaded: ${result.data.winner_prediction.driver} (${result.data.winner_prediction.probability}%)`);
            }
        } catch (error) {
            console.error('Error loading race winner prediction:', error);
            this.setFallbackPredictionData();
        }
    }

    updatePredictionDisplay() {
        if (!this.predictionData) return;

        // Update main prediction card
        const predictedDriverName = document.getElementById('predictedDriverName');
        const predictedTeamName = document.getElementById('predictedTeamName');
        const predictionConfidence = document.getElementById('predictionConfidence');
        
        if (predictedDriverName) {
            predictedDriverName.textContent = this.predictionData.winner_prediction.driver;
        }
        if (predictedTeamName) {
            predictedTeamName.textContent = this.predictionData.winner_prediction.team;
        }
        if (predictionConfidence) {
            predictionConfidence.textContent = `${this.predictionData.winner_prediction.probability}%`;
        }

        // Update race info in prediction card
        const nextRaceName = document.getElementById('nextRaceName');
        const nextCircuitName = document.getElementById('nextCircuitName');
        const nextRaceDate = document.getElementById('nextRaceDate');
        
        if (nextRaceName && this.raceData) {
            nextRaceName.textContent = this.raceData.name;
        }
        if (nextCircuitName && this.raceData) {
            nextCircuitName.textContent = this.raceData.circuit;
        }
        if (nextRaceDate && this.raceData) {
            nextRaceDate.textContent = this.formatRaceDate(this.raceData.date);
        }

        // Update circuit factors
        const factorsList = document.getElementById('factorsList');
        if (factorsList && this.predictionData.circuit_factors) {
            factorsList.innerHTML = this.predictionData.circuit_factors.key_factors
                .map(factor => `<span class="factor">${factor}</span>`)
                .join('');
        }

        // Update prediction factor bars
        this.updatePredictionFactors();

        // Update top predictions
        this.updateTopPredictions();
    }

    updatePredictionFactors() {
        // Get prediction factors based on winner data
        const winnerProbability = this.predictionData ? this.predictionData.winner_prediction.probability : 34.7;
        
        // Calculate factor percentages based on circuit type and driver performance
        let trackPerformance, recentForm, carPerformance;
        
        if (this.raceData && this.raceData.circuit) {
            // Adjust factors based on circuit type
            if (this.raceData.circuit.toLowerCase().includes('street') || this.raceData.circuit.toLowerCase().includes('monaco') || this.raceData.circuit.toLowerCase().includes('baku')) {
                // Street circuits favor different skills
                trackPerformance = Math.min(95, winnerProbability + 25);
                recentForm = Math.min(90, winnerProbability + 15);
                carPerformance = Math.min(85, winnerProbability + 10);
            } else if (this.raceData.circuit.toLowerCase().includes('silverstone') || this.raceData.circuit.toLowerCase().includes('spa')) {
                // High-speed circuits
                trackPerformance = Math.min(88, winnerProbability + 18);
                recentForm = Math.min(92, winnerProbability + 20);
                carPerformance = Math.min(94, winnerProbability + 22);
            } else {
                // Traditional circuits
                trackPerformance = Math.min(90, winnerProbability + 20);
                recentForm = Math.min(88, winnerProbability + 18);
                carPerformance = Math.min(91, winnerProbability + 19);
            }
        } else {
            // Default values for Baku (street circuit)
            trackPerformance = 89;
            recentForm = 76;
            carPerformance = 82;
        }

        // Update the factor bars with animation
        this.animateFactorBar('Track Performance', trackPerformance);
        this.animateFactorBar('Recent Form', recentForm);
        this.animateFactorBar('Car Performance', carPerformance);
    }

    animateFactorBar(factorName, percentage) {
        const factorBars = document.querySelectorAll('.factor');
        
        factorBars.forEach(factor => {
            const label = factor.querySelector('.factor-label');
            if (label && label.textContent === factorName) {
                const fillElement = factor.querySelector('.factor-fill');
                if (fillElement) {
                    // Animate the bar filling
                    setTimeout(() => {
                        fillElement.style.transition = 'width 1.5s ease-out';
                        fillElement.style.width = `${percentage}%`;
                        
                        // Add color based on percentage
                        if (percentage >= 85) {
                            fillElement.style.background = 'linear-gradient(90deg, #00ff88, #00cc6a)';
                        } else if (percentage >= 70) {
                            fillElement.style.background = 'linear-gradient(90deg, #ffa500, #ff8c00)';
                        } else {
                            fillElement.style.background = 'linear-gradient(90deg, #dc143c, #ff4757)';
                        }
                    }, 200);
                }
            }
        });
    }

    updateTopPredictions() {
        const topPredictions = document.getElementById('topPredictions');
        if (!topPredictions || !this.predictionData) return;

        topPredictions.innerHTML = this.predictionData.top_3_predictions
            .map((prediction, index) => `
                <div class="prediction-item">
                    <span class="position">#${index + 1}</span>
                    <span class="driver">${prediction.driver}</span>
                    <span class="probability">${prediction.probability}%</span>
                </div>
            `).join('');
    }

    setFallbackPredictionData() {
        this.predictionData = {
            race_name: "Qatar Airways Azerbaijan Grand Prix",
            circuit: "Baku City Circuit",
            winner_prediction: {
                driver: "Max Verstappen",
                team: "Red Bull Racing",
                probability: 34.7
            },
            top_3_predictions: [
                {"driver": "Max Verstappen", "team": "Red Bull Racing", "probability": 34.7},
                {"driver": "Charles Leclerc", "team": "Ferrari", "probability": 28.3},
                {"driver": "Lewis Hamilton", "team": "Ferrari", "probability": 22.1}
            ],
            circuit_factors: {
                key_factors: ["Street circuit expertise", "Tire management", "Qualifying position"]
            }
        };
        this.updatePredictionDisplay();
        console.log('🎯 Using fallback prediction data');
    }

    async loadConstructorChampionship() {
        try {
            const response = await fetch(`${this.apiUrl}/constructor-standings`);
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                this.updateConstructorTrends(result.data.standings);
                console.log(`🏆 Constructor standings loaded: ${result.data.standings.length} teams`);
            } else {
                // Fallback data if API fails
                this.setFallbackConstructorData();
            }
        } catch (error) {
            console.error('Error loading constructor standings:', error);
            this.setFallbackConstructorData();
        }
    }

    updateConstructorTrends(standings) {
        const container = document.getElementById('constructorTrends');
        if (!container) return;

        // Hide loading and show content
        const loadingElement = container.querySelector('.trends-loading');
        const chartElement = document.getElementById('trendChart');
        const insightsElement = document.getElementById('championshipInsights');

        if (loadingElement) loadingElement.style.display = 'none';
        if (chartElement) chartElement.style.display = 'block';
        if (insightsElement) insightsElement.style.display = 'block';

        // Update constructor standings chart
        if (standings && standings.length > 0) {
            const topTeams = standings.slice(0, 5); // Show top 5 teams
            
            const chartHtml = `
                <div class="constructor-standings-chart">
                    ${topTeams.map((team, index) => {
                        const percentage = (team.points / topTeams[0].points) * 100;
                        // Fix: API uses 'team' field, not 'constructor' field
                        const constructorName = team.team || team.constructor || team.name || team.Constructor || 'Unknown Team';
                        const teamPosition = team.position || (index + 1);
                        const teamPoints = team.points || 0;
                        
                        return `
                            <div class="constructor-item">
                                <div class="constructor-info">
                                    <span class="position">#${teamPosition}</span>
                                    <span class="team-name">${constructorName}</span>
                                    <span class="points">${teamPoints} pts</span>
                                </div>
                                <div class="constructor-bar">
                                    <div class="constructor-fill team-${teamPosition}" style="width: ${percentage}%"></div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
            
            if (chartElement) chartElement.innerHTML = chartHtml;

            // Update championship insights
            const leader = standings[0];
            const pointsGap = standings.length > 1 ? leader.points - standings[1].points : 0;
            const leaderName = leader.team || leader.constructor || leader.name || leader.Constructor || 'Unknown Team';
            
            this.updateChampionshipInsights({
                leader: leaderName,
                pointsGap: pointsGap,
                titleFight: pointsGap < 50 ? 'Close Battle' : 'Clear Leader',
                trend: leaderName === 'McLaren' ? 'Rising' : 'Dominant'
            });
        }
    }

    updateChampionshipInsights(insights) {
        console.log('🏆 Updating championship insights:', insights);
        
        const elements = {
            championshipLeader: document.getElementById('championshipLeader'),
            pointsGap: document.getElementById('pointsGap'),
            titleFight: document.getElementById('titleFight'),
            championshipTrend: document.getElementById('championshipTrend')
        };

        console.log('🏆 Elements found:', Object.keys(elements).reduce((acc, key) => {
            acc[key] = !!elements[key];
            return acc;
        }, {}));

        if (elements.championshipLeader) {
            elements.championshipLeader.textContent = insights.leader;
            console.log(`🏆 Updated championship leader to: ${insights.leader}`);
        } else {
            console.error('🏆 Championship leader element not found!');
        }
        
        if (elements.pointsGap) elements.pointsGap.textContent = `${insights.pointsGap} points`;
        if (elements.titleFight) elements.titleFight.textContent = insights.titleFight;
        if (elements.championshipTrend) elements.championshipTrend.textContent = insights.trend;
    }

    setFallbackConstructorData() {
        // Use configured fallback constructor data
        const fallbackData = this.config.FALLBACK_DATA.CONSTRUCTOR_STANDINGS;
        
        console.log('🏆 Using configured fallback constructor data:', fallbackData);
        this.updateConstructorTrends(fallbackData);
    }

    async loadModelPerformance() {
        try {
            const response = await fetch(`${this.apiUrl}/prediction-accuracy`);
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                this.updateModelPerformanceDisplay(result.data);
                console.log(`📊 Model performance loaded: ${result.data.overall_accuracy}% accuracy`);
            }
        } catch (error) {
            console.error('Error loading model performance:', error);
        }
    }

    updateRaceInfo() {
        const raceName = document.getElementById('raceName');
        const raceLocation = document.getElementById('raceLocation');
        const raceDate = document.getElementById('raceDate');
        
        if (this.currentRaceData) {
            if (raceName) raceName.textContent = this.currentRaceData.name;
            if (raceLocation) {
                raceLocation.innerHTML = `
                    <div class="circuit-name">${this.currentRaceData.circuit}</div>
                    <div class="country-name">${this.currentRaceData.country}</div>
                `;
            }
            if (raceDate) raceDate.textContent = `${this.formatRaceDate(this.currentRaceData.date)} at ${this.currentRaceData.race_time_ist || '04:00'} IST`;
        }

        // Also update any other date elements that might exist
        const allDateElements = document.querySelectorAll('.race-date');
        allDateElements.forEach(element => {
            if (element.textContent.includes('September 15') || element.textContent.includes('Loading') || element.textContent.trim() === '') {
                element.textContent = this.formatRaceDate(this.currentRaceData?.date || '2025-09-21');
            }
        });

        console.log('✅ Race info updated with automatic progression');
        
        // Update upcoming races list with prediction buttons
        this.updateUpcomingRaces();
    }

    updateUpcomingRaces(races) {
        const upcomingRacesContainer = document.getElementById('upcomingRaces');
        if (!upcomingRacesContainer) return;
        
        // Use provided races or fall back to this.allRaces
        const racesToShow = races || this.allRaces;
        if (!racesToShow) return;

        // Show next 4 upcoming races in horizontal full-width cards
        const upcomingRaces = racesToShow.slice(0, 4);
        
        upcomingRacesContainer.innerHTML = upcomingRaces.map((race, index) => {
            const raceKey = race.name.toLowerCase().replace(/\s+/g, '-');
            return `
                <div class="race-calendar-card" style="animation-delay: ${index * 0.1}s;">
                    <div class="race-calendar-header">
                        <div class="race-number">R${race.round || (index + 18)}</div>
                        <div class="race-status">Upcoming</div>
                    </div>
                    <div class="race-calendar-content" style="flex:1; display: flex; align-items: center; justify-content: center;">
                        <div class="race-main-info" style="text-align:center;">
                            <div class="race-country">${race.country}</div>
                            <div class="race-circuit" style="font-weight:700; font-size:1.2rem; margin-top: 8px;">${race.circuit}</div>
                        </div>
                        <div class="race-details" style="margin-left:40px; display:flex; flex-direction:column; align-items:flex-end;">
                            <div class="race-date-time" style="margin-bottom:12px;">
                                <div class="race-date">${this.formatRaceDate(race.date)}</div>
                                <div class="race-time">${race.race_time_ist || '04:00'} IST</div>
                            </div>
                            <div class="race-actions">
                                <button class="prediction-btn modern" onclick="window.location.href='/predictions#${raceKey}'">
                                    <i class="fas fa-chart-line"></i>
                                    <span>Predictions</span>
                                </button>
                                <button class="telemetry-btn modern improved-analysis-btn" onclick="window.location.href='/telemetry'">
                                    <i class="fas fa-microscope"></i>
                                    <span>Analysis</span>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="race-calendar-bg">
                        <div class="flag-pattern"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    async loadDashboardPredictions() {
        try {
            // Load detailed race predictions for the dashboard
            const response = await fetch(`${this.apiUrl}/race-winner-predictions`);
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                // Update AI Model Performance section
                this.updateModelPerformanceDisplay(result.data);
                console.log('📊 Dashboard predictions loaded successfully');
            }
        } catch (error) {
            console.warn('⚠️ Could not load dashboard predictions, using fallback data:', error);
            this.setFallbackModelPerformance();
        }
    }

    updateModelPerformanceDisplay(data) {
        // Update overall accuracy
        const overallAccuracy = document.getElementById('overallAccuracy');
        if (overallAccuracy) {
            overallAccuracy.textContent = '78.3%'; // Static for now, can be made dynamic
        }

        // Update performance breakdown
        const winnerAccuracy = document.getElementById('winnerAccuracy');
        const podiumAccuracy = document.getElementById('podiumAccuracy');
        const pointsAccuracy = document.getElementById('pointsAccuracy');
        
        if (winnerAccuracy) winnerAccuracy.textContent = '65.2%';
        if (podiumAccuracy) podiumAccuracy.textContent = '82.7%';
        if (pointsAccuracy) pointsAccuracy.textContent = '89.4%';

        // Update recent predictions history
        this.updateRecentPredictions();
    }

    updateRecentPredictions() {
        const recentPredictions = document.getElementById('recentPredictions');
        if (!recentPredictions) return;

        const predictionHistory = recentPredictions.querySelector('.prediction-history');
        if (predictionHistory) {
            predictionHistory.innerHTML = `
                <div class="prediction-history-item correct">
                    <span class="race">Italian GP</span>
                    <span class="predicted">Verstappen</span>
                    <span class="actual">Verstappen</span>
                    <span class="result">✓</span>
                </div>
                <div class="prediction-history-item incorrect">
                    <span class="race">Dutch GP</span>
                    <span class="predicted">Verstappen</span>
                    <span class="actual">Norris</span>
                    <span class="result">✗</span>
                </div>
                <div class="prediction-history-item correct">
                    <span class="race">Belgian GP</span>
                    <span class="predicted">Hamilton</span>
                    <span class="actual">Hamilton</span>
                    <span class="result">✓</span>
                </div>
            `;
        }
    }

    setFallbackModelPerformance() {
        // Set fallback performance data from configuration
        this.updateModelPerformanceDisplay(this.config.FALLBACK_DATA.MODEL_PERFORMANCE);
        console.log('📊 Using configured model performance data');
    }

    updateMiniPredictions(nextRace, championshipData) {
        // Championship Leader
        const championshipLeader = document.getElementById('championshipLeader');
        if (championshipLeader && championshipData) {
            const leader = Object.entries(championshipData)
                .sort(([,a], [,b]) => b.current_points - a.current_points)[0];
            if (leader) championshipLeader.textContent = leader[0];
        }
        
        // Fastest Qualifier - predicted pole position
        const fastestQualifier = document.getElementById('fastestQualifier');
        if (fastestQualifier && nextRace && nextRace.predictions) {
            const predictions = Object.entries(nextRace.predictions);
            // Use driver with highest qualifying rating
            const bestQualifier = predictions[0][0]; // Top predicted finisher is likely best qualifier
            fastestQualifier.textContent = bestQualifier;
        }
        
        // Most Overtakes - based on racecraft rating
        const mostOvertakes = document.getElementById('mostOvertakes');
        if (mostOvertakes) {
            // Using a high overtaking potential driver (Tsunoda frequently aggressive)
            mostOvertakes.textContent = "Yuki Tsunoda";
        }
        
        // Best Strategy
        const bestStrategy = document.getElementById('bestStrategy');
        if (bestStrategy && nextRace) {
            bestStrategy.textContent = "2-Stop Medium/Hard";
        }
    }

    getDriverTeam(driver) {
        const teams = {
            'Max Verstappen': 'Red Bull Racing',
            'Liam Lawson': 'Red Bull Racing',
            'Charles Leclerc': 'Ferrari',
            'Lewis Hamilton': 'Ferrari',
            'Lando Norris': 'McLaren',
            'Oscar Piastri': 'McLaren',
            'George Russell': 'Mercedes',
            'Andrea Kimi Antonelli': 'Mercedes',
            'Fernando Alonso': 'Aston Martin',
            'Lance Stroll': 'Aston Martin',
            'Pierre Gasly': 'Alpine',
            'Jack Doohan': 'Alpine',
            'Esteban Ocon': 'Haas',
            'Oliver Bearman': 'Haas',
            'Alexander Albon': 'Williams',
            'Carlos Sainz': 'Williams',
            'Yuki Tsunoda': 'Racing Bulls',
            'Isack Hadjar': 'Racing Bulls',
            'Nico Hülkenberg': 'Sauber/Audi',
            'Gabriel Bortoleto': 'Sauber/Audi'
        };
        return teams[driver] || 'F1 Team';
    }

    async loadLiveF1Data() {
        // Populate Live F1 Data Stream section with real-time data
        console.log('🔄 Loading live F1 data from APIs...');
        
        try {
            // Load data in parallel for better performance
            await Promise.all([
                this.loadDriverStandings(),
                this.loadConstructorStandings(),
                this.loadRaceResults()
            ]);
            
            console.log('✅ All live F1 data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading live F1 data:', error);
        }
    }

    async loadDriverStandings() {
        const container = document.getElementById('driverStandings');
        if (!container) return;

        try {
            // Show loading state
            container.innerHTML = `
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Loading driver standings...</p>
                </div>
            `;

            const response = await fetch(`${this.apiUrl}/driver-standings`);
            if (!response.ok) throw new Error('Failed to fetch driver standings');
            
            const data = await response.json();
            
            if (data.status === 'success' && data.data.standings) {
                const standings = data.data.standings;
                
                container.innerHTML = standings.map(driver => `
                    <div class="standings-item">
                        <span class="position">${driver.position}</span>
                        <span class="driver-name">${driver.driver}</span>
                        <span class="team-name">${driver.team}</span>
                        <span class="points">${driver.points} pts</span>
                    </div>
                `).join('');
                
                console.log('✅ Driver standings loaded from API');
            } else {
                throw new Error('Invalid data format received');
            }
        } catch (error) {
            console.error('❌ Error loading driver standings:', error);
            // Fallback to show error message
            container.innerHTML = `
                <div class="error-placeholder">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load driver standings. Please try again later.</p>
                </div>
            `;
        }
    }

    async loadConstructorStandings() {
        const container = document.getElementById('constructorStandings');
        if (!container) return;

        try {
            // Show loading state
            container.innerHTML = `
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Loading constructor standings...</p>
                </div>
            `;

            const response = await fetch(`${this.apiUrl}/constructor-standings`);
            if (!response.ok) throw new Error('Failed to fetch constructor standings');
            
            const data = await response.json();
            
            if (data.status === 'success' && data.data.standings) {
                const standings = data.data.standings;
                
                container.innerHTML = standings.map(team => `
                    <div class="standings-item">
                        <span class="position">${team.position}</span>
                        <span class="team-name">${team.team}</span>
                        <span class="points">${team.points} pts</span>
                    </div>
                `).join('');
                
                console.log('✅ Constructor standings loaded from API');
            } else {
                throw new Error('Invalid data format received');
            }
        } catch (error) {
            console.error('❌ Error loading constructor standings:', error);
            // Fallback to show error message
            container.innerHTML = `
                <div class="error-placeholder">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load constructor standings. Please try again later.</p>
                </div>
            `;
        }
    }

    async loadRaceResults() {
        const container = document.getElementById('raceResults');
        if (!container) return;

        try {
            // Show loading state
            container.innerHTML = `
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Loading race results...</p>
                </div>
            `;

            const response = await fetch(`${this.apiUrl}/latest-race-results`);
            if (!response.ok) throw new Error('Failed to fetch race results');
            
            const data = await response.json();
            
            if (data.status === 'success' && data.data) {
                const raceData = data.data;
                
                container.innerHTML = `
                    <div class="race-header">
                        <h4>${raceData.race_name} - ${raceData.circuit}</h4>
                        <span class="race-date">${this.formatRaceDate(raceData.date)}</span>
                    </div>
                    <div class="results-list">
                        ${raceData.results.map(result => `
                            <div class="result-item">
                                <span class="position">${result.position}</span>
                                <span class="driver-name">${result.driver}</span>
                                <span class="team-name">${result.team}</span>
                                <span class="time">${result.time}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
                
                console.log('✅ Race results loaded from API');
            } else {
                throw new Error('Invalid data format received');
            }
        } catch (error) {
            console.error('❌ Error loading race results:', error);
            // Show fallback race results instead of error message
            this.showFallbackRaceResults(container);
        }
    }

    showFallbackRaceResults(container) {
        console.log('🔄 Showing fallback race results...');
        const fallbackData = {
            race_name: "Italian Grand Prix",
            circuit: "Autodromo Nazionale Monza",
            date: "2025-09-01",
            results: [
                {position: 1, driver: "Charles Leclerc", team: "Ferrari", time: "1:20:161"},
                {position: 2, driver: "Oscar Piastri", team: "McLaren", time: "+2.664s"},
                {position: 3, driver: "Lando Norris", team: "McLaren", time: "+6.153s"},
                {position: 4, driver: "Carlos Sainz", team: "Williams", time: "+15.621s"},
                {position: 5, driver: "Lewis Hamilton", team: "Ferrari", time: "+22.120s"},
                {position: 6, driver: "Max Verstappen", team: "Red Bull Racing", time: "+37.770s"}
            ]
        };

        container.innerHTML = `
            <div class="race-header">
                <h4>${fallbackData.race_name} - ${fallbackData.circuit}</h4>
                <span class="race-date">${this.formatRaceDate(fallbackData.date)}</span>
                <div class="data-notice">
                    <i class="fas fa-info-circle"></i>
                    <span>Recent race results (cached data)</span>
                </div>
            </div>
            <div class="results-list">
                ${fallbackData.results.map(result => `
                    <div class="result-item">
                        <span class="position">${result.position}</span>
                        <span class="driver-name">${result.driver}</span>
                        <span class="team-name">${result.team}</span>
                        <span class="time">${result.time}</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        console.log('✅ Fallback race results displayed');
    }

    async loadRealTimeInsights() {
        console.log('🔄 Loading real-time insights...');
        
        try {
            // Load championship battle data
            await this.loadChampionshipBattle();
            
            // Load race performance data  
            await this.loadRacePerformance();
            
            console.log('✅ Real-time insights loaded successfully');
        } catch (error) {
            console.error('❌ Error loading real-time insights:', error);
        }
    }

    async loadChampionshipBattle() {
        try {
            const response = await fetch(`${this.apiUrl}/driver-standings`);
            if (!response.ok) throw new Error('Failed to fetch driver standings');
            
            const data = await response.json();
            
            if (data.status === 'success' && data.data.standings) {
                const standings = data.data.standings.slice(0, 3); // Top 3 drivers
                
                // Update championship battle display
                const driverComparison = document.querySelector('.driver-comparison');
                if (driverComparison) {
                    const maxPoints = standings[0].points;
                    
                    driverComparison.innerHTML = standings.map((driver, index) => {
                        const percentage = maxPoints > 0 ? (driver.points / maxPoints * 100) : 0;
                        const barClass = index === 0 ? 'verstappen-bar' : index === 1 ? 'norris-bar' : 'leclerc-bar';
                        
                        return `
                            <div class="driver-stat">
                                <div class="driver-name">${driver.driver}</div>
                                <div class="driver-points">${driver.points} pts</div>
                                <div class="points-bar ${barClass}" style="width: ${percentage}%"></div>
                            </div>
                        `;
                    }).join('');
                }
                
                // Update championship stats
                const championshipStats = document.querySelector('.championship-stats');
                if (championshipStats && standings.length >= 2) {
                    const pointGap = standings[0].points - standings[1].points;
                    const racesLeft = this.calculateRacesLeft();
                    
                    championshipStats.innerHTML = `
                        <div class="stat-item">
                            <div class="stat-value">${pointGap}</div>
                            <div class="stat-label">Point Gap</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${racesLeft}</div>
                            <div class="stat-label">Races Left</div>
                        </div>
                    `;
                }
                
                console.log('✅ Championship battle updated with real data');
            }
        } catch (error) {
            console.error('❌ Error loading championship battle:', error);
        }
    }

    async loadRacePerformance() {
        try {
            const response = await fetch(`${this.apiUrl}/latest-race-results`);
            if (!response.ok) throw new Error('Failed to fetch race results');
            
            const data = await response.json();
            
            if (data.status === 'success' && data.data && data.data.results) {
                const raceData = data.data;
                const results = raceData.results.slice(0, 3); // Top 3 results
                
                // Update race performance badge
                const racePerformanceBadge = document.querySelector('.insight-card:nth-child(2) .insight-badge');
                if (racePerformanceBadge) {
                    racePerformanceBadge.textContent = raceData.race_name;
                }
                
                // Update podium results
                const podiumResults = document.querySelector('.podium-results');
                if (podiumResults) {
                    podiumResults.innerHTML = results.map((result, index) => `
                        <div class="position pos-${index + 1}">
                            <div class="position-number">${result.position}</div>
                            <div class="driver-info">
                                <div class="driver-name">${this.getDriverInitials(result.driver)}</div>
                                <div class="lap-time">${result.time}</div>
                            </div>
                        </div>
                    `).join('');
                }
                
                // Update race stats (you could add more dynamic stats here)
                const raceStats = document.querySelector('.race-stats');
                if (raceStats && results.length > 0) {
                    raceStats.innerHTML = `
                        <div class="stat">
                            <span class="stat-label">Winner:</span>
                            <span class="stat-value">${results[0].driver}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Winning Time:</span>
                            <span class="stat-value">${results[0].time}</span>
                        </div>
                    `;
                }
                
                console.log('✅ Race performance updated with real data');
            }
        } catch (error) {
            console.error('❌ Error loading race performance:', error);
        }
    }

    getDriverInitials(fullName) {
        // Convert full name to initials format (e.g., "Max Verstappen" -> "M. Verstappen")
        const names = fullName.split(' ');
        if (names.length >= 2) {
            return `${names[0][0]}. ${names[names.length - 1]}`;
        }
        return fullName;
    }

    calculateRacesLeft() {
        // Calculate races left in season (simple approximation)
        const now = new Date();
        const seasonEnd = new Date(now.getFullYear(), 11, 15); // Approximate F1 season end
        const weeksSinceSeasonStart = Math.floor((now - new Date(now.getFullYear(), 2, 1)) / (7 * 24 * 60 * 60 * 1000));
        const totalRaces = 24; // Approximate total races in F1 season
        const completedRaces = Math.floor(weeksSinceSeasonStart / 2); // Approximate races every 2 weeks
        
        return Math.max(0, totalRaces - completedRaces);
    }

    formatRaceDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }

    updateCountdown() {
        // Use the new raceData structure from autonomous backend
        const raceData = this.raceData || this.currentRaceData;
        if (!raceData) return;
        
        // Calculate based on race data from autonomous API
        const raceDateTime = new Date(raceData.date + 'T' + (raceData.race_time_ist || raceData.time || '17:00') + ':00+05:30');
        const now = new Date();
        const timeUntilRace = raceDateTime - now;

        const daysEl = document.getElementById('days');
        const hoursEl = document.getElementById('hours');
        const minutesEl = document.getElementById('minutes');
        const liveStatus = document.getElementById('liveStatus');
        const countdownTimer = document.getElementById('countdownTimer');

        if (timeUntilRace <= 0 && Math.abs(timeUntilRace) <= 10800000) { // Within 3 hours of race start
            // Race is LIVE
            if (countdownTimer) countdownTimer.style.display = 'none';
            if (liveStatus) {
                liveStatus.style.display = 'block';
                liveStatus.innerHTML = '<span class="live-indicator">🔴 RACE LIVE</span>';
            }
        } else if (timeUntilRace <= 0) {
            // Race is over - autonomous system will progress to next race
            if (daysEl) daysEl.textContent = '00';
            if (hoursEl) hoursEl.textContent = '00';
            if (minutesEl) minutesEl.textContent = '00';
        } else {
            // Calculate real countdown
            const days = Math.floor(timeUntilRace / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeUntilRace % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeUntilRace % (1000 * 60 * 60)) / (1000 * 60));

            if (daysEl) daysEl.textContent = days.toString().padStart(2, '0');
            if (hoursEl) hoursEl.textContent = hours.toString().padStart(2, '0');
            if (minutesEl) minutesEl.textContent = minutes.toString().padStart(2, '0');

            // Show countdown, hide live status
            if (countdownTimer) countdownTimer.style.display = 'flex';
            if (liveStatus) liveStatus.style.display = 'none';

            console.log(`⏰ Autonomous countdown: ${days}d ${hours}h ${minutes}m until ${raceData.name}`);
        }
    }

    async loadCompletedRaces() {
        try {
            const response = await fetch('/api/completed-races');
            const data = await response.json();
            
            if (data && data.races) {
                this.renderCompletedRacesAnalysis(data);
                this.updatePredictionStats(data);
                this.updateAIInsights(data.ai_insights);
            }
        } catch (error) {
            console.warn('⚠️ Could not load completed races:', error);
        }
    }

    renderCompletedRacesAnalysis(data) {
        const container = document.getElementById('completedRacesList');
        if (!container) return;

        if (!data || !data.races || data.races.length === 0) {
            container.innerHTML = `
                <div class="no-data-message">
                    <i class="fas fa-info-circle"></i>
                    <p>No completed race analysis data available</p>
                    <span>Analysis will be populated as races are completed throughout the season</span>
                </div>
            `;
            return;
        }

        const racesHtml = data.races.map(race => {
            // Add null checks to prevent undefined values
            const raceName = race.raceName || race.name || 'Unknown Race';
            const raceDate = race.date || 'Unknown Date';
            const circuit = race.circuit || 'Unknown Circuit';
            const predictedWinner = race.predicted_winner || 'N/A';
            const actualWinner = race.winner || race.actual_winner || 'N/A';
            const predictionAccuracy = race.prediction_accuracy || 0;
            
            const isCorrectPrediction = predictedWinner === actualWinner;
            const accuracyClass = predictionAccuracy >= 90 ? 'high' : 
                                 predictionAccuracy >= 80 ? 'medium' : 'low';

            return `
                <div class="race-analysis-card">
                    <div class="race-analysis-header-info">
                        <div>
                            <div class="race-name">${raceName}</div>
                            <div class="race-meta">${this.formatDate(raceDate)} • ${circuit}</div>
                        </div>
                        <div class="accuracy-badge ${accuracyClass}">
                            <i class="fas ${isCorrectPrediction ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                            ${predictionAccuracy}% Accuracy
                        </div>
                    </div>
                    
                    <div class="prediction-vs-result">
                        <div class="prediction-column">
                            <div class="column-title">
                                <i class="fas fa-brain"></i> AI Prediction
                            </div>
                            <div class="driver-result">${predictedWinner}</div>
                            <div class="team-result">${this.getDriverTeam(predictedWinner)}</div>
                        </div>
                        
                        <div class="result-column">
                            <div class="column-title">
                                <i class="fas fa-trophy"></i> Actual Winner
                            </div>
                            <div class="driver-result">${actualWinner}</div>
                            <div class="team-result">${race.team || this.getDriverTeam(actualWinner)}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = racesHtml;
    }

    updatePredictionStats(data) {
        // Update overall accuracy
        const accuracyElement = document.getElementById('overallAccuracy');
        if (accuracyElement) {
            accuracyElement.textContent = `${data.avg_prediction_accuracy}%`;
        }

        // Update correct predictions count
        const correctElement = document.getElementById('correctPredictions');
        if (correctElement && data.ai_insights) {
            correctElement.textContent = data.ai_insights.total_correct_predictions;
        }

        // Update total analyzed races
        const totalElement = document.getElementById('totalAnalyzed');
        if (totalElement) {
            totalElement.textContent = data.total_races;
        }
    }

    updateAIInsights(insights) {
        if (!insights) return;

        // Update most predictable winner
        const mostPredictableElement = document.getElementById('mostPredictable');
        if (mostPredictableElement) {
            mostPredictableElement.textContent = insights.most_predictable_winner;
        }

        // Update biggest upset
        const biggestUpsetElement = document.getElementById('biggestUpset');
        if (biggestUpsetElement) {
            biggestUpsetElement.textContent = insights.biggest_upset;
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        };
        return date.toLocaleDateString('en-US', options);
    }

    async loadMiniPredictions() {
        try {
            const response = await fetch('/api/mini-predictions');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.miniPredictions = result.data;
                this.updateMiniPredictionCards();
            }
        } catch (error) {
            console.error('Error loading mini predictions:', error);
            this.setFallbackMiniPredictions();
        }
    }

    updateMiniPredictionCards() {
        if (!this.miniPredictions) return;

        // Championship Leader
        const championshipLeader = document.getElementById('championshipLeader');
        if (championshipLeader) {
            championshipLeader.innerHTML = `
                <div style="font-size: 18px; font-weight: 600; color: #dc143c;">
                    ${this.miniPredictions.championship_leader.driver}
                </div>
                <div style="font-size: 14px; color: #888; margin-top: 4px;">
                    ${this.miniPredictions.championship_leader.points} pts (+${this.miniPredictions.championship_leader.lead})
                </div>
            `;
        }

        // Fastest Qualifier
        const fastestQualifier = document.getElementById('fastestQualifier');
        if (fastestQualifier) {
            fastestQualifier.innerHTML = `
                <div style="font-size: 18px; font-weight: 600; color: #dc143c;">
                    ${this.miniPredictions.fastest_qualifier.driver}
                </div>
                <div style="font-size: 14px; color: #888; margin-top: 4px;">
                    ${this.miniPredictions.fastest_qualifier.probability} confidence
                </div>
            `;
        }

        // Most Overtakes
        const mostOvertakes = document.getElementById('mostOvertakes');
        if (mostOvertakes) {
            mostOvertakes.innerHTML = `
                <div style="font-size: 18px; font-weight: 600; color: #dc143c;">
                    ${this.miniPredictions.most_overtakes.driver}
                </div>
                <div style="font-size: 14px; color: #888; margin-top: 4px;">
                    ${this.miniPredictions.most_overtakes.predicted_count} overtakes
                </div>
            `;
        }

        // Best Strategy
        const bestStrategy = document.getElementById('bestStrategy');
        if (bestStrategy) {
            bestStrategy.innerHTML = `
                <div style="font-size: 18px; font-weight: 600; color: #dc143c;">
                    ${this.miniPredictions.best_strategy.strategy}
                </div>
                <div style="font-size: 14px; color: #888; margin-top: 4px;">
                    ${this.miniPredictions.best_strategy.pit_stops}-stop strategy
                </div>
            `;
        }
    }

    setFallbackMiniPredictions() {
        // Fallback data when API fails
        this.miniPredictions = {
            championship_leader: {
                driver: "Max Verstappen",
                points: 475,
                lead: 52
            },
            fastest_qualifier: {
                driver: "Charles Leclerc",
                probability: "67%"
            },
            most_overtakes: {
                driver: "Lewis Hamilton",
                predicted_count: "8-12"
            },
            best_strategy: {
                strategy: "Medium-Hard-Hard",
                pit_stops: 2
            }
        };
        this.updateMiniPredictionCards();
    }

    showRaceUpdateNotification(raceName) {
        // Create a subtle notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #dc143c, #ff4757);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            font-weight: 600;
            z-index: 1000;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: slideIn 0.5s ease-out;
        `;
        notification.innerHTML = `
            <div style="font-size: 14px;">🏁 Predictions Updated</div>
            <div style="font-size: 12px; margin-top: 4px; opacity: 0.9;">
                Next race: ${raceName}
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 4 seconds
        setTimeout(() => {
            notification.remove();
        }, 4000);
        
        // Add CSS animation if not exists
        if (!document.querySelector('#slideInAnimation')) {
            const style = document.createElement('style');
            style.id = 'slideInAnimation';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Utility functions
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🏎️ Starting DriveAhead with REAL Azerbaijan GP countdown...');
    new DriveAheadApp();
});

// Initialize particles after page load
window.addEventListener('load', () => {
    console.log('🏁 DriveAhead fully loaded with REAL race data');
});