// DriveAhead Predictions Page JavaScript
class PredictionsApp {
    constructor() {
        this.apiUrl = '/api';
        this.init();
    }

    async init() {
        console.log('🏎️ Initializing DriveAhead Predictions Platform...');
        
        try {
            await this.loadNextRacePredictions();
            await this.loadAllRacePredictions();
            await this.loadTeamsAndDrivers();
            
            console.log('✅ All prediction data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading predictions:', error);
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
            
            this.renderAllRacePredictions(data.upcoming_races);
            
            // Update total races count
            const totalRacesElement = document.getElementById('totalRaces');
            if (totalRacesElement) {
                totalRacesElement.textContent = data.total_races;
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
                    <h3>${race.race}</h3>
                    <div class="race-card-date">${this.formatDate(race.date)} • ${race.location}</div>
                    <div class="race-circuit">${race.circuit}</div>
                </div>
                
                <div class="predicted-winner">
                    <div class="winner-info">
                        <span class="winner-name">${race.predictions[0].driver}</span>
                        <span class="winner-team">(${race.predictions[0].team})</span>
                    </div>
                    <div class="winner-probability">${race.predictions[0].probability}%</div>
                </div>

                <div class="top-3-predictions">
                    <h4>Top 3 Predictions:</h4>
                    ${race.predictions.slice(0, 3).map((driver, index) => `
                        <div class="top-3-item">
                            <span class="position">${index + 1}.</span>
                            <span class="driver">${driver.driver}</span>
                            <span class="probability">${driver.probability}%</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="race-card-footer">
                    <button class="prediction-details-btn" onclick="window.location.href='/predictions?race=${encodeURIComponent(race.race)}'">
                        <i class="fas fa-chart-line"></i>
                        View Details
                    </button>
                </div>
            </div>
        `).join('');
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
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PredictionsApp;
}