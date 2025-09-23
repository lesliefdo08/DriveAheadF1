// DriveAhead - Live F1 Race Predictions JavaScript
class PredictionsApp {
    constructor() {
        this.apiUrl = '/api';
        this.refreshInterval = null;
        this.lastRaceUpdate = null;
        this.init();
    }

    async init() {
        console.log('🏎️ Initializing DriveAhead Predictions Platform...');
        
        try {
            await this.loadStatsData();
            await this.loadRaceHeader();
            await this.loadPerformanceMetrics();
            await this.loadNextRace();
            await this.loadNextRacePredictions();
            await this.loadAllRacePredictions();
            await this.loadTeamsAndDrivers();
            await this.loadChampionshipData();
            await this.loadPredictionData();
            await this.loadKeyFactors();
            await this.loadFastestLapCandidates();
            await this.loadLivePredictions();
            
            // Set up auto-refresh for race transitions
            this.setupAutoRefresh();
            
            console.log('✅ All prediction data loaded successfully');
        } catch (error) {
            console.error('❌ Failed to initialize predictions:', error);
        }
    }
    
    setupAutoRefresh() {
        // Refresh every 30 minutes to catch race transitions
        this.refreshInterval = setInterval(async () => {
            console.log('🔄 Checking for race updates...');
            await this.checkForRaceUpdates();
        }, 30 * 60 * 1000); // 30 minutes
        
        // More frequent checks on weekends (every 10 minutes)
        const now = new Date();
        if (now.getDay() >= 5) { // Friday, Saturday, Sunday
            clearInterval(this.refreshInterval);
            this.refreshInterval = setInterval(async () => {
                console.log('🏁 Weekend race update check...');
                await this.checkForRaceUpdates();
            }, 10 * 60 * 1000); // 10 minutes
        }
    }
    
    async checkForRaceUpdates() {
        try {
            const response = await fetch(`${this.apiUrl}/live-predictions`);
            const data = await response.json();
            
            if (data.race_info) {
                const currentRace = `${data.race_info.name}_${data.race_info.date}`;
                
                // Check if race has changed
                if (this.lastRaceUpdate && this.lastRaceUpdate !== currentRace) {
                    console.log('🏎️ Race transition detected! Refreshing all data...');
                    await this.refreshAllData();
                }
                
                this.lastRaceUpdate = currentRace;
            }
        } catch (error) {
            console.error('Error checking for race updates:', error);
        }
    }
    
    async refreshAllData() {
        try {
            // Force refresh race data on server
            await fetch(`${this.apiUrl}/refresh-race-data`);
            
            // Reload all components
            await this.loadRaceHeader();
            await this.loadNextRace();
            await this.loadNextRacePredictions();
            await this.loadLivePredictions();
            
            console.log('✅ All data refreshed after race transition');
            
            // Show user notification
            this.showNotification('🏁 Race data updated! New predictions available.');
        } catch (error) {
            console.error('Error refreshing data:', error);
        }
    }
    
    showNotification(message) {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = 'race-update-notification';
        notification.innerHTML = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #dc143c, #ff4757);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 10000;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 5000);
    }

    async loadStatsData() {
        try {
            const response = await fetch(`${this.apiUrl}/prediction-stats`);
            const apiData = await response.json();
            
            if (apiData.status === 'success' && apiData.data) {
                const data = apiData.data;
                
                // Update remaining races
                const remainingRacesElement = document.getElementById('remainingRaces');
                if (remainingRacesElement) {
                    this.animateNumber(remainingRacesElement, data.remainingRaces);
                }
                
                // Update model accuracy
                const modelAccuracyElement = document.getElementById('modelAccuracy');
                if (modelAccuracyElement) {
                    this.animateNumber(modelAccuracyElement, data.modelAccuracy, '%');
                }
                
                // Update teams count
                const totalTeamsElement = document.getElementById('totalTeams');
                if (totalTeamsElement) {
                    this.animateNumber(totalTeamsElement, data.totalTeams);
                }
                
                // Update drivers count
                const totalDriversElement = document.getElementById('totalDrivers');
                if (totalDriversElement) {
                    this.animateNumber(totalDriversElement, data.totalDrivers);
                }
                
                console.log('📊 Stats data loaded successfully:', data);
            } else if (apiData.status === 'error' && apiData.data) {
                // Handle fallback data
                console.warn('⚠️ Using fallback stats data');
                this.loadFallbackStats(apiData.data);
            }
            
        } catch (error) {
            console.error('Error loading stats data:', error);
            // Load default values with animation anyway
            this.loadDefaultStats();
        }
    }

    loadFallbackStats(data) {
        const remainingRacesElement = document.getElementById('remainingRaces');
        const modelAccuracyElement = document.getElementById('modelAccuracy');
        const totalTeamsElement = document.getElementById('totalTeams');
        const totalDriversElement = document.getElementById('totalDrivers');
        
        if (remainingRacesElement) this.animateNumber(remainingRacesElement, data.remainingRaces);
        if (modelAccuracyElement) this.animateNumber(modelAccuracyElement, data.modelAccuracy, '%');
        if (totalTeamsElement) this.animateNumber(totalTeamsElement, data.totalTeams);
        if (totalDriversElement) this.animateNumber(totalDriversElement, data.totalDrivers);
    }

    loadDefaultStats() {
        const remainingRacesElement = document.getElementById('remainingRaces');
        const modelAccuracyElement = document.getElementById('modelAccuracy');
        const totalTeamsElement = document.getElementById('totalTeams');
        const totalDriversElement = document.getElementById('totalDrivers');
        
        if (remainingRacesElement) this.animateNumber(remainingRacesElement, 4);
        if (modelAccuracyElement) this.animateNumber(modelAccuracyElement, 93.2, '%');
        if (totalTeamsElement) this.animateNumber(totalTeamsElement, 10);
        if (totalDriversElement) this.animateNumber(totalDriversElement, 20);
    }

    animateNumber(element, targetValue, suffix = '') {
        const startValue = 0;
        const duration = 2000; // 2 seconds
        const increment = targetValue / (duration / 16); // 60fps
        let currentValue = startValue;
        
        const animate = () => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                element.textContent = Math.round(currentValue) + suffix;
                return;
            }
            
            element.textContent = Math.round(currentValue) + suffix;
            requestAnimationFrame(animate);
        };
        
        animate();
    }

    async loadNextRace() {
        try {
            const response = await fetch(`${this.apiUrl}/next-race`);
            const data = await response.json();
            
            console.log('Next Race API Response:', data); // Debug log
            
            if (data.status === 'success' && data.data) {
                const race = data.data;
                console.log('Race data:', race); // Debug log
                
                const titleElement = document.getElementById('nextRaceTitle');
                if (titleElement) {
                    // Try multiple possible property names for the race name
                    const raceName = race.name || race.raceName || race.race_name || race.title || 'Unknown Race';
                    titleElement.textContent = `${raceName}`;
                    console.log('Set race name to:', raceName); // Debug log
                }
                
                // Start countdown timer if race date is available
                if (race.date) {
                    this.startCountdown(race.date, race.time || '12:00:00');
                }
            } else {
                console.log('API failed, using fallback'); // Debug log
                this.setFallbackNextRace();
            }
        } catch (error) {
            console.error('Error loading next race:', error);
            this.setFallbackNextRace();
        }
    }

    startCountdown(raceDate, raceTime) {
        const raceDateTime = new Date(`${raceDate}T${raceTime}`);
        
        const updateCountdown = () => {
            const now = new Date().getTime();
            const distance = raceDateTime.getTime() - now;

            if (distance > 0) {
                const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));

                document.getElementById('days').textContent = days.toString().padStart(2, '0');
                document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
                document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
            } else {
                document.getElementById('days').textContent = '00';
                document.getElementById('hours').textContent = '00';
                document.getElementById('minutes').textContent = '00';
            }
        };

        updateCountdown();
        setInterval(updateCountdown, 60000); // Update every minute
    }
    
    setFallbackNextRace() {
        const titleElement = document.getElementById('nextRaceTitle');
        if (titleElement) {
            titleElement.textContent = 'Singapore Grand Prix 2025';
        }
    }

    async loadNextRacePredictions() {
        try {
            const response = await fetch(`${this.apiUrl}/race-winner-predictions`);
            const data = await response.json();
            
            this.renderNextRacePredictions(data);
            
        } catch (error) {
            console.error('Error loading next race predictions:', error);
        }
    }

    renderNextRacePredictions(data) {
        const container = document.getElementById('nextRacePredictions');
        if (!container) return;

        const predictions = data.predictions || [];
        
        container.innerHTML = predictions.slice(0, 5).map((prediction, index) => `
            <div class="prediction-item ${index === 0 ? 'winner' : ''}">
                <div class="driver-number">#${prediction.number || (index + 1)}</div>
                <div class="driver-name">${prediction.driver}</div>
                <div class="team-name">${prediction.team}</div>
                <div class="probability">${prediction.probability}%</div>
            </div>
        `).join('');
    }

    async loadAllRacePredictions() {
        try {
            const response = await fetch(`${this.apiUrl}/all-upcoming-predictions`);
            const data = await response.json();
            
            if (data.status === 'success' && data.races) {
                this.renderAllRacePredictions(data.races);
                this.renderFeaturedRace(data.races);
                
                // Update total races count
                const totalRacesElement = document.getElementById('totalRaces');
                if (totalRacesElement) {
                    totalRacesElement.textContent = data.total || data.races.length;
                }
            } else {
                throw new Error('Invalid API response format');
            }
            
        } catch (error) {
            console.error('Error loading all race predictions:', error);
            // Fallback in case of error
            const container = document.getElementById('allRacePredictions');
            if (container) {
                container.innerHTML = '<div class="error-message">Unable to load race predictions. Please try again later.</div>';
            }
        }
    }

    renderAllRacePredictions(races) {
        const container = document.getElementById('allRacePredictions');
        if (!container) return;

        container.innerHTML = races.map(race => `
            <div class="race-card">
                <div class="race-card-header">
                    <h3>${race.raceName || race.race}</h3>
                    <div class="race-card-date">${this.formatDate(race.date)} • Round ${race.round}</div>
                    <div class="race-circuit">${race.circuitName || race.circuit}</div>
                </div>
                
                <div class="predicted-winner">
                    <div class="winner-info">
                        <span class="winner-name">${race.predictions[0].driverName || race.predictions[0].driver}</span>
                        <span class="winner-team">(${race.predictions[0].teamName || race.predictions[0].team})</span>
                    </div>
                    <div class="winner-probability">${Math.round(race.predictions[0].probability * 100)}%</div>
                </div>

                <div class="top-3-predictions">
                    <h4>Top 3 Predictions:</h4>
                    ${race.predictions.slice(0, 3).map((driver, index) => `
                        <div class="top-3-item">
                            <span class="position">${index + 1}.</span>
                            <span class="driver">${driver.driverName || driver.driver}</span>
                            <span class="probability">${Math.round(driver.probability * 100)}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    renderFeaturedRace(races) {
        const container = document.getElementById('featuredRaceCard');
        if (!container || !races || races.length === 0) return;

        const nextRace = races[0];
        container.innerHTML = `
            <div class="featured-race-content">
                <div class="race-header">
                    <div class="race-info">
                        <h3>${nextRace.raceName || nextRace.race}</h3>
                        <p class="race-details">${this.formatDate(nextRace.date)} • Round ${nextRace.round}</p>
                        <p class="circuit-name">${nextRace.circuitName || nextRace.circuit}</p>
                    </div>
                </div>
                
                <div class="featured-predictions">
                    <h4>Top Contenders</h4>
                    <div class="winner-prediction">
                        <div class="driver-card favorite">
                            <span class="position">1st</span>
                            <div class="driver-info">
                                <div class="driver-name">${nextRace.predictions[0].driverName || nextRace.predictions[0].driver}</div>
                                <div class="team-name">${nextRace.predictions[0].teamName || nextRace.predictions[0].team}</div>
                            </div>
                            <div class="win-probability">${Math.round(nextRace.predictions[0].probability * 100)}%</div>
                        </div>
                    </div>
                    
                    <div class="contenders-list">
                        ${nextRace.predictions.slice(1, 4).map((pred, index) => `
                            <div class="contender">
                                <span class="pos">${index + 2}</span>
                                <span class="driver">${pred.driverName || pred.driver}</span>
                                <span class="team">${pred.teamName || pred.team}</span>
                                <span class="prob">${Math.round(pred.probability * 100)}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="race-stats">
                    <h4>Race Statistics</h4>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">Fastest Lap</span>
                            <span class="stat-value">1:20.654</span>
                            <span class="stat-detail">-0.173s vs record</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Current Record</span>
                            <span class="stat-value">1:20.827</span>
                            <span class="stat-detail">Charles Leclerc (2023)</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Average Lap</span>
                            <span class="stat-value">1:23.145</span>
                            <span class="stat-detail">Race pace estimate</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadTeamsAndDrivers() {
        try {
            const response = await fetch(`${this.apiUrl}/race-winner-predictions`);
            const data = await response.json();
            
            if (data.teams_2025) {
                this.renderTeamsAndDrivers(data.teams_2025);
            }
            
        } catch (error) {
            console.error('Error loading teams and drivers:', error);
        }
    }

    renderTeamsAndDrivers(teams) {
        const container = document.getElementById('teamsGrid');
        if (!container) return;

        const teamColors = {
            'Red Bull Racing': '#0600ef',
            'Ferrari': '#dc143c', 
            'McLaren': '#ff8700',
            'Mercedes': '#00d2be',
            'Aston Martin': '#006f62',
            'Alpine': '#0090ff',
            'Haas': '#ffffff',
            'Williams': '#005aff',
            'Racing Bulls': '#6692ff',
            'Sauber': '#52c41a'
        };

        container.innerHTML = Object.entries(teams).map(([team, drivers]) => `
            <div class="team-card">
                <div class="team-header">
                    <div class="team-logo" style="background: ${teamColors[team] || '#dc143c'}">
                        ${team.substring(0, 2).toUpperCase()}
                    </div>
                    <div class="team-name">${team}</div>
                </div>
                
                <div class="drivers-list">
                    ${drivers.map(driver => `
                        <div class="driver-item">
                            <i class="fas fa-user-circle"></i>
                            ${driver}
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
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

    // Animation for accuracy meters
    animateAccuracyMeters() {
        const meters = document.querySelectorAll('.meter-fill');
        meters.forEach(meter => {
            const width = meter.style.width;
            meter.style.width = '0%';
            setTimeout(() => {
                meter.style.width = width;
            }, 500);
        });
    }

    // Update countdown for next race
    updateCountdown() {
        const nextRaceDate = new Date('2025-09-21T12:00:00+04:00');
        const now = new Date();
        const timeRemaining = nextRaceDate - now;

        if (timeRemaining > 0) {
            const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));

            const countdownElement = document.getElementById('nextRaceCountdown');
            if (countdownElement) {
                countdownElement.innerHTML = `
                    <span class="countdown-days">${days}</span> days, 
                    <span class="countdown-hours">${hours}</span> hours, 
                    <span class="countdown-minutes">${minutes}</span> minutes remaining
                `;
            }
        }
    }

    async loadLivePredictions() {
        try {
            // Load race header info first
            await this.loadRaceHeader();
            
            // Load Winner Predictions
            await this.loadWinnerPredictions();
            
            // Load Podium Predictions  
            await this.loadPodiumPredictions();
            
            console.log('✅ Live predictions loaded');
        } catch (error) {
            console.error('❌ Error loading live predictions:', error);
        }
    }

    async loadRaceHeader() {
        try {
            const response = await fetch(`${this.apiUrl}/live-predictions`);
            const data = await response.json();
            
            if (data.race_info && data.model_accuracy) {
                // Update the single race header section
                const raceTitle = document.getElementById('raceTitle');
                const raceDate = document.getElementById('raceDate');
                const raceWeather = document.getElementById('raceWeather');
                const winnerAccuracy = document.getElementById('winnerAccuracy');
                const podiumAccuracy = document.getElementById('podiumAccuracy');
                const top10Accuracy = document.getElementById('top10Accuracy');
                
                if (raceTitle) raceTitle.textContent = data.race_info.name;
                if (raceDate) raceDate.textContent = data.race_info.date;
                if (raceWeather && data.race_info.weather) {
                    raceWeather.textContent = `${data.race_info.weather.temperature}, ${data.race_info.weather.conditions}`;
                }
                if (winnerAccuracy) winnerAccuracy.textContent = `${data.model_accuracy.race_winner}%`;
                if (podiumAccuracy) podiumAccuracy.textContent = `${data.model_accuracy.podium}%`;
                if (top10Accuracy) top10Accuracy.textContent = `${data.model_accuracy.top_10}%`;
                
                console.log('🏁 Race header loaded successfully:', data);
            }
        } catch (error) {
            console.error('❌ Error loading race header:', error);
            // Fallback to default values if API fails
            this.setDefaultRaceHeader();
        }
    }

    setDefaultRaceHeader() {
        // Single race header section
        const raceTitle = document.getElementById('raceTitle');
        const raceDate = document.getElementById('raceDate');
        const raceWeather = document.getElementById('raceWeather');
        const winnerAccuracy = document.getElementById('winnerAccuracy');
        const podiumAccuracy = document.getElementById('podiumAccuracy');
        const top10Accuracy = document.getElementById('top10Accuracy');
        
        if (raceTitle) raceTitle.textContent = 'Azerbaijan Grand Prix 2025';
        if (raceDate) raceDate.textContent = 'September 21, 2025';
        if (raceWeather) raceWeather.textContent = '22°C, Clear & Windy';
        if (winnerAccuracy) winnerAccuracy.textContent = '87.3%';
        if (podiumAccuracy) podiumAccuracy.textContent = '94.1%';
        if (top10Accuracy) top10Accuracy.textContent = '91.8%';
    }

    async loadPerformanceMetrics() {
        try {
            const response = await fetch(`${this.apiUrl}/performance-metrics`);
            const data = await response.json();
            
            if (data.overall_accuracy) {
                this.animateNumber(document.getElementById('overall-accuracy'), data.overall_accuracy, '%');
                this.setBarWidth('overall-accuracy-bar', data.overall_accuracy);
            }
            if (data.street_circuit_accuracy) {
                this.animateNumber(document.getElementById('street-circuit-accuracy'), data.street_circuit_accuracy, '%');
                this.setBarWidth('street-circuit-bar', data.street_circuit_accuracy);
            }
            if (data.podium_prediction_accuracy) {
                this.animateNumber(document.getElementById('podium-prediction-accuracy'), data.podium_prediction_accuracy, '%');
                this.setBarWidth('podium-prediction-bar', data.podium_prediction_accuracy);
            }
        } catch (error) {
            console.error('❌ Error loading performance metrics:', error);
            // Fallback to default values
            this.setDefaultPerformanceMetrics();
        }
    }

    setDefaultPerformanceMetrics() {
        this.animateNumber(document.getElementById('overall-accuracy'), 93.2, '%');
        this.setBarWidth('overall-accuracy-bar', 93.2);
        this.animateNumber(document.getElementById('street-circuit-accuracy'), 95.1, '%');
        this.setBarWidth('street-circuit-bar', 95.1);
        this.animateNumber(document.getElementById('podium-prediction-accuracy'), 91.8, '%');
        this.setBarWidth('podium-prediction-bar', 91.8);
    }

    setBarWidth(elementId, percentage) {
        const element = document.getElementById(elementId);
        if (element) {
            setTimeout(() => {
                element.style.width = percentage + '%';
                element.setAttribute('data-width', percentage);
            }, 500);
        }
    }

    async loadChampionshipData() {
        try {
            const response = await fetch(`${this.apiUrl}/championship-data`);
            const data = await response.json();
            
            if (data.leader) {
                const leaderElement = document.getElementById('championship-leader');
                const pointsLeadElement = document.getElementById('points-lead');
                if (leaderElement) leaderElement.textContent = data.leader;
                if (pointsLeadElement) pointsLeadElement.textContent = `+${data.points_lead} points`;
            }
            if (data.race_impact) {
                const impactElement = document.getElementById('race-impact-points');
                const changeElement = document.getElementById('standings-change');
                if (impactElement) impactElement.textContent = `+${data.race_impact.points}`;
                if (changeElement) changeElement.textContent = `+${data.race_impact.positions} positions`;
            }
        } catch (error) {
            console.error('❌ Error loading championship data:', error);
            this.setDefaultChampionshipData();
        }
    }

    setDefaultChampionshipData() {
        const leaderElement = document.getElementById('championship-leader');
        const pointsLeadElement = document.getElementById('points-lead');
        const impactElement = document.getElementById('race-impact-points');
        const changeElement = document.getElementById('standings-change');
        
        if (leaderElement) leaderElement.textContent = 'Max Verstappen';
        if (pointsLeadElement) pointsLeadElement.textContent = '+86 points';
        if (impactElement) impactElement.textContent = '+25';
        if (changeElement) changeElement.textContent = '+2 positions';
    }

    async loadPredictionData() {
        try {
            const response = await fetch(`${this.apiUrl}/live-predictions`);
            const data = await response.json();
            
            if (data.winner_predictions && data.winner_predictions.length >= 3) {
                const predictions = data.winner_predictions;
                
                // Update confidence
                const confidenceElement = document.getElementById('model-confidence');
                if (confidenceElement) confidenceElement.textContent = '87%';
                
                // Update top 3 predictions
                for (let i = 0; i < 3; i++) {
                    const driverElement = document.getElementById(`p${i+1}-driver`);
                    const probabilityElement = document.getElementById(`p${i+1}-probability`);
                    
                    if (predictions[i] && driverElement && probabilityElement) {
                        driverElement.textContent = predictions[i].driver;
                        probabilityElement.textContent = `${predictions[i].probability}%`;
                    }
                }
            }
        } catch (error) {
            console.error('❌ Error loading prediction data:', error);
            this.setDefaultPredictionData();
        }
    }

    setDefaultPredictionData() {
        const confidenceElement = document.getElementById('model-confidence');
        if (confidenceElement) confidenceElement.textContent = '87%';
        
        const defaultDrivers = ['Max Verstappen', 'Lando Norris', 'Charles Leclerc'];
        const defaultProbabilities = ['34%', '28%', '22%'];
        
        for (let i = 0; i < 3; i++) {
            const driverElement = document.getElementById(`p${i+1}-driver`);
            const probabilityElement = document.getElementById(`p${i+1}-probability`);
            
            if (driverElement) driverElement.textContent = defaultDrivers[i];
            if (probabilityElement) probabilityElement.textContent = defaultProbabilities[i];
        }
    }

    async loadKeyFactors() {
        try {
            const response = await fetch(`${this.apiUrl}/key-factors`);
            const data = await response.json();
            
            if (data.track_advantage) {
                const trackAdvantageElement = document.getElementById('track-advantage');
                if (trackAdvantageElement) trackAdvantageElement.textContent = data.track_advantage;
            }
            if (data.weather_influence) {
                const weatherInfluenceElement = document.getElementById('weather-influence');
                if (weatherInfluenceElement) weatherInfluenceElement.textContent = data.weather_influence;
            }
        } catch (error) {
            console.error('❌ Error loading key factors:', error);
            this.setDefaultKeyFactors();
        }
    }

    setDefaultKeyFactors() {
        const trackAdvantageElement = document.getElementById('track-advantage');
        const weatherInfluenceElement = document.getElementById('weather-influence');
        
        if (trackAdvantageElement) trackAdvantageElement.textContent = 'Red Bull';
        if (weatherInfluenceElement) weatherInfluenceElement.textContent = 'Medium';
    }

    async loadFastestLapCandidates() {
        try {
            const response = await fetch(`${this.apiUrl}/fastest-lap-predictions`);
            const data = await response.json();
            
            const container = document.getElementById('fastest-lap-candidates-list');
            if (container && data.candidates) {
                container.innerHTML = data.candidates.map((candidate, index) => `
                    <div class="candidate ${index === 0 ? 'favorite' : ''}">
                        <div class="candidate-info">
                            <div class="driver-details">
                                <span class="driver-name">${candidate.driver}</span>
                                <span class="team-name">${candidate.team}</span>
                            </div>
                            <div class="candidate-stats">
                                <span class="probability">${candidate.probability}%</span>
                                <span class="predicted-time">${candidate.predicted_time}</span>
                            </div>
                        </div>
                        ${index === 0 ? this.generateFormIndicators() : ''}
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('❌ Error loading fastest lap candidates:', error);
            this.setDefaultFastestLapCandidates();
        }
    }

    setDefaultFastestLapCandidates() {
        const container = document.getElementById('fastest-lap-candidates-list');
        if (container) {
            container.innerHTML = `
                <div class="candidate favorite">
                    <div class="candidate-info">
                        <div class="driver-details">
                            <span class="driver-name">Max Verstappen</span>
                            <span class="team-name">Red Bull Racing</span>
                        </div>
                        <div class="candidate-stats">
                            <span class="probability">34%</span>
                            <span class="predicted-time">1:20.654</span>
                        </div>
                    </div>
                    ${this.generateFormIndicators()}
                </div>
                <div class="candidate">
                    <div class="candidate-info">
                        <div class="driver-details">
                            <span class="driver-name">Lando Norris</span>
                            <span class="team-name">McLaren</span>
                        </div>
                        <div class="candidate-stats">
                            <span class="probability">28%</span>
                            <span class="predicted-time">1:20.789</span>
                        </div>
                    </div>
                </div>
                <div class="candidate">
                    <div class="candidate-info">
                        <div class="driver-details">
                            <span class="driver-name">Charles Leclerc</span>
                            <span class="team-name">Ferrari</span>
                        </div>
                        <div class="candidate-stats">
                            <span class="probability">22%</span>
                            <span class="predicted-time">1:20.912</span>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    generateFormIndicators() {
        return `
            <div class="form-indicators">
                <div class="form-factor">
                    <span class="factor-name">Sector 1</span>
                    <div class="sector-bar">
                        <div class="sector-fill" style="width: 95%"></div>
                    </div>
                </div>
                <div class="form-factor">
                    <span class="factor-name">Sector 2</span>
                    <div class="sector-bar">
                        <div class="sector-fill" style="width: 88%"></div>
                    </div>
                </div>
                <div class="form-factor">
                    <span class="factor-name">Sector 3</span>
                    <div class="sector-bar">
                        <div class="sector-fill" style="width: 92%"></div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadWinnerPredictions() {
        try {
            const response = await fetch(`${this.apiUrl}/race-winner-predictions`);
            const data = await response.json();
            
            const container = document.getElementById('winner-predictions');
            if (container && data.predictions) {
                container.innerHTML = `
                    <div class="predictions-header">
                        <div class="prediction-summary">
                            <span class="confidence-badge">High Confidence</span>
                            <span class="last-updated">Updated: ${new Date().toLocaleTimeString()}</span>
                        </div>
                    </div>
                    <div class="predictions-grid">
                        ${data.predictions.slice(0, 6).map((pred, index) => `
                            <div class="prediction-item ${index === 0 ? 'winner predicted-winner' : ''} ${index < 3 ? 'podium-position' : ''}">
                                <div class="position-indicator">
                                    <span class="position-number">${index + 1}</span>
                                    ${index === 0 ? '<i class="fas fa-crown"></i>' : ''}
                                    ${index < 3 ? '<i class="fas fa-medal"></i>' : ''}
                                </div>
                                <div class="driver-details">
                                    <div class="driver-info">
                                        <span class="driver-name">${pred.driver}</span>
                                        <span class="team-name">${pred.team}</span>
                                    </div>
                                    <div class="prediction-stats">
                                        <div class="probability-bar">
                                            <div class="probability-fill" style="width: ${pred.probability}%"></div>
                                        </div>
                                        <span class="probability-text">${pred.probability}%</span>
                                    </div>
                                </div>
                                <div class="additional-info">
                                    <span class="recent-form">Form: ${this.getDriverForm(pred.driver)}</span>
                                    <span class="odds">Odds: ${this.calculateOdds(pred.probability)}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="predictions-footer">
                        <div class="prediction-insights">
                            <div class="insight-item">
                                <i class="fas fa-chart-line"></i>
                                <span>Weather Factor: Low Impact</span>
                            </div>
                            <div class="insight-item">
                                <i class="fas fa-flag-checkered"></i>
                                <span>Track Conditions: Optimal</span>
                            </div>
                            <div class="insight-item">
                                <i class="fas fa-clock"></i>
                                <span>Next Update: 5 minutes</span>
                            </div>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading winner predictions:', error);
            const container = document.getElementById('winner-predictions');
            if (container) {
                container.innerHTML = '<div class="error-message">Unable to load predictions. Retrying in 30 seconds...</div>';
            }
        }
    }

    getDriverForm(driverName) {
        // Simulate driver form data
        const forms = ['Excellent', 'Good', 'Average', 'Poor'];
        return forms[Math.floor(Math.random() * forms.length)];
    }

    calculateOdds(probability) {
        const odds = 100 / probability;
        return odds.toFixed(1) + ':1';
    }

    async loadPodiumPredictions() {
        try {
            const response = await fetch(`${this.apiUrl}/race-winner-predictions`);
            const data = await response.json();
            
            const container = document.getElementById('podium-container');
            if (container && data.predictions) {
                container.innerHTML = `
                    <div class="podium-positions">
                        ${data.predictions.slice(0, 3).map((pred, index) => `
                            <div class="podium-position pos-${index + 1}">
                                <div class="position-number">${index + 1}</div>
                                <div class="driver-name">${pred.driver}</div>
                                <div class="team-name">${pred.team}</div>
                                <div class="probability">${pred.probability}%</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading podium predictions:', error);
        }
    }

    loadChampionshipImpact() {
        // Load championship impact data and update the containers
        const championshipData = {
            leader: "Max Verstappen",
            pointsLead: 86,
            raceImpactPoints: 25,
            standingsChange: "+2 positions",
            titleProbabilities: [
                { driver: "Max Verstappen", probability: 78 },
                { driver: "Lando Norris", probability: 15 },
                { driver: "Charles Leclerc", probability: 7 }
            ]
        };

        // Update championship leader info
        const leaderEl = document.getElementById('championship-leader');
        const leadEl = document.getElementById('points-lead');
        const impactEl = document.getElementById('race-impact-points');
        const changeEl = document.getElementById('standings-change');

        if (leaderEl) leaderEl.textContent = championshipData.leader;
        if (leadEl) leadEl.textContent = `+${championshipData.pointsLead} points`;
        if (impactEl) impactEl.textContent = `+${championshipData.raceImpactPoints}`;
        if (changeEl) changeEl.textContent = championshipData.standingsChange;

        // Render title probabilities
        const titleContainer = document.getElementById('title-probabilities');
        if (titleContainer) {
            titleContainer.innerHTML = championshipData.titleProbabilities.map(item => `
                <div class="title-prob-item">
                    <span class="driver-name">${item.driver}</span>
                    <div class="prob-bar">
                        <div class="prob-fill" style="width: ${item.probability}%"></div>
                    </div>
                    <span class="prob-value">${item.probability}%</span>
                </div>
            `).join('');
        }
    }

    loadLivePredictions() {
        // Update live prediction data
        const liveData = {
            modelConfidence: 87,
            predictions: [
                { driver: "Max Verstappen", probability: 34 },
                { driver: "Lando Norris", probability: 28 },
                { driver: "Charles Leclerc", probability: 22 }
            ]
        };

        const confEl = document.getElementById('model-confidence');
        if (confEl) confEl.textContent = `${liveData.modelConfidence}%`;
        
        const p1Driver = document.getElementById('p1-driver');
        const p1Prob = document.getElementById('p1-probability');
        if (p1Driver && p1Prob) {
            p1Driver.textContent = liveData.predictions[0].driver;
            p1Prob.textContent = `${liveData.predictions[0].probability}%`;
        }
        
        const p2Driver = document.getElementById('p2-driver');
        const p2Prob = document.getElementById('p2-probability');
        if (p2Driver && p2Prob) {
            p2Driver.textContent = liveData.predictions[1].driver;
            p2Prob.textContent = `${liveData.predictions[1].probability}%`;
        }
        
        const p3Driver = document.getElementById('p3-driver');
        const p3Prob = document.getElementById('p3-probability');
        if (p3Driver && p3Prob) {
            p3Driver.textContent = liveData.predictions[2].driver;
            p3Prob.textContent = `${liveData.predictions[2].probability}%`;
        }
    }

    loadWeatherData() {
        // Simulate weather API data
        const weatherData = {
            currentTemp: 24,
            condition: "Clear Sky",
            details: "15% humidity, 5 km/h wind",
            riskLevel: "Low Risk",
            forecastChange: "No change expected",
            icon: "fas fa-sun"
        };

        const tempEl = document.getElementById('current-temp');
        const condEl = document.getElementById('weather-condition');
        const detailsEl = document.getElementById('weather-details-text');
        const riskEl = document.getElementById('weather-risk');
        const forecastEl = document.getElementById('forecast-change');
        const iconEl = document.getElementById('weather-icon');

        if (tempEl) tempEl.textContent = `${weatherData.currentTemp}°C`;
        if (condEl) condEl.textContent = weatherData.condition;
        if (detailsEl) detailsEl.textContent = weatherData.details;
        if (riskEl) riskEl.textContent = weatherData.riskLevel;
        if (forecastEl) forecastEl.textContent = weatherData.forecastChange;
        if (iconEl) iconEl.className = weatherData.icon;
    }

    loadFastestLapData() {
        // Update fastest lap predictions
        const lapData = {
            predictedTime: "1:20.654",
            comparison: "-0.173s vs record"
        };

        const timeEl = document.getElementById('predicted-lap-time');
        const compEl = document.getElementById('lap-comparison');
        
        if (timeEl) timeEl.textContent = lapData.predictedTime;
        if (compEl) compEl.textContent = lapData.comparison;
    }

    async initEnhancedContainers() {
        // Initialize all enhanced containers with data
        try {
            this.loadChampionshipImpact();
            this.loadLivePredictions();
            this.loadWeatherData();
            this.loadFastestLapData();
            console.log('✅ Enhanced containers loaded successfully');
        } catch (error) {
            console.error('❌ Error loading enhanced containers:', error);
        }
    }
}

// Enhanced styling for prediction cards
const addPredictionCardStyles = () => {
    const style = document.createElement('style');
    style.textContent = `
        .top-3-predictions {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }
        
        .top-3-predictions h4 {
            color: var(--accent-white);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .top-3-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.3rem 0;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        .top-3-item .position {
            font-weight: 600;
            color: var(--primary-red);
            width: 20px;
        }
        
        .top-3-item .driver {
            flex: 1;
            color: var(--text-light);
        }
        
        .top-3-item .probability {
            color: var(--primary-red);
            font-weight: 600;
        }
        
        .winner-name {
            font-weight: 600;
            color: var(--accent-white);
        }
        
        .winner-team {
            color: var(--text-muted);
            font-size: 0.9rem;
        }
    `;
    document.head.appendChild(style);
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    addPredictionCardStyles();
    const app = new PredictionsApp();
    
    // Start countdown timer
    app.updateCountdown();
    setInterval(() => app.updateCountdown(), 60000); // Update every minute
    
    // Animate accuracy meters after a short delay
    setTimeout(() => app.animateAccuracyMeters(), 1000);
    
    // Initialize enhanced containers
    app.initEnhancedContainers();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PredictionsApp;
}