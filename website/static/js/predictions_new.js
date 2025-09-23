class PredictionsApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; 
        this.init();
    }

    async init() {
        try {
            await this.loadInitialData();
            this.setupEventListeners();
            this.startPeriodicUpdates();
            this.initializeAnimations();
        } catch (error) {
            console.error('Error initializing predictions app:', error);
            this.showErrorMessage('Failed to load predictions data');
        }
    }

    async loadInitialData() {
        const loadingPromises = [
            this.loadFeaturedRace(),
            this.loadAllRaces(),
            this.loadTeams(),
            this.updateStats()
        ];

        await Promise.allSettled(loadingPromises);
    }

    async fetchWithCache(url, maxAge = this.cacheTimeout) {
        const cacheKey = url;
        const cached = this.cache.get(cacheKey);
        
        if (cached && (Date.now() - cached.timestamp) < maxAge) {
            return cached.data;
        }

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.cache.set(cacheKey, {
                data,
                timestamp: Date.now()
            });
            
            return data;
        } catch (error) {
            console.error(`Fetch error for ${url}:`, error);
            // Return cached data if available, even if expired
            if (cached) {
                return cached.data;
            }
            throw error;
        }
    }

    async loadFeaturedRace() {
        try {
            const response = await this.fetchWithCache(`${this.apiBaseUrl}/next-race-prediction`);
            
            if (!response || !response.race) {
                throw new Error('Invalid race data');
            }

            this.renderFeaturedRace(response);
        } catch (error) {
            console.error('Error loading featured race:', error);
            this.renderFeaturedRaceError();
        }
    }

    renderFeaturedRace(data) {
        const container = document.getElementById('featuredRaceCard');
        if (!container) return;

        const race = data.race;
        const predictions = data.predictions || [];

        container.innerHTML = `
            <div class="race-header">
                <div class="race-info">
                    <h3>${race.raceName || 'Race Information Unavailable'}</h3>
                    <p class="circuit-name">${race.circuitName || 'Circuit TBD'} • ${this.formatDate(race.date)}</p>
                </div>
                <div class="race-countdown">
                    <span class="countdown-text">${this.calculateDaysUntil(race.date)} days remaining</span>
                </div>
            </div>
            
            <div class="predictions-grid">
                ${predictions.slice(0, 3).map((pred, index) => `
                    <div class="prediction-item ${index === 0 ? 'winner' : ''}">
                        <span class="driver-position">${this.getPositionOrdinal(index + 1)}</span>
                        <div class="driver-name">${pred.driverName || 'TBD'}</div>
                        <div class="driver-team">${pred.teamName || 'Team TBD'}</div>
                        <div class="prediction-confidence">${(pred.probability * 100).toFixed(1)}%</div>
                    </div>
                `).join('')}
            </div>

            <div class="circuit-analysis">
                <h4><i class="fas fa-chart-line"></i> Circuit Analysis</h4>
                <div class="analysis-grid">
                    <div class="analysis-item">
                        <i class="fas fa-road"></i>
                        <span>${race.circuitType || 'Circuit Type Unknown'}</span>
                    </div>
                    <div class="analysis-item">
                        <i class="fas fa-car-side"></i>
                        <span>Overtaking: ${race.overtakingDifficulty || 'Medium'}</span>
                    </div>
                    <div class="analysis-item">
                        <i class="fas fa-cloud-sun"></i>
                        <span>${race.weather || 'Weather TBD'}</span>
                    </div>
                    <div class="analysis-item">
                        <i class="fas fa-clock"></i>
                        <span>Lap Record: ${race.lapRecord || 'TBD'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderFeaturedRaceError() {
        const container = document.getElementById('featuredRaceCard');
        if (!container) return;

        container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Unable to Load Featured Race</h3>
                <p>We're having trouble loading the next race information. Please try again later.</p>
                <button class="retry-btn" onclick="predictionsApp.loadFeaturedRace()">
                    <i class="fas fa-refresh"></i> Retry
                </button>
            </div>
        `;
    }

    async loadAllRaces() {
        try {
            const response = await this.fetchWithCache(`${this.apiBaseUrl}/all-upcoming-predictions`);
            
            if (!response || !Array.isArray(response.races)) {
                throw new Error('Invalid races data');
            }

            this.renderAllRaces(response.races);
        } catch (error) {
            console.error('Error loading all races:', error);
            this.renderAllRacesError();
        }
    }

    renderAllRaces(races) {
        const container = document.getElementById('allRacePredictions');
        if (!container) return;

        if (!races || races.length === 0) {
            container.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No Upcoming Races</h3>
                    <p>All races for this season have been completed.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = races.map(race => `
            <div class="race-card" data-race-id="${race.round}">
                <div class="race-header">
                    <div class="race-info">
                        <h3>${race.raceName || 'Race TBD'}</h3>
                        <p class="circuit-name">${race.circuitName || 'Circuit TBD'} • ${this.formatDate(race.date)}</p>
                    </div>
                    <div class="race-countdown">${this.calculateDaysUntil(race.date)} days</div>
                </div>
                
                <div class="predictions-grid">
                    ${(race.predictions || []).slice(0, 3).map((pred, index) => `
                        <div class="prediction-item">
                            <span class="driver-position">${index + 1}</span>
                            <div class="driver-name">${pred.driverName || 'TBD'}</div>
                            <div class="driver-team">${pred.teamName || 'Team TBD'}</div>
                            <div class="prediction-confidence">${(pred.probability * 100).toFixed(1)}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');

        // Add staggered animation to race cards
        this.animateRaceCards();
    }

    renderAllRacesError() {
        const container = document.getElementById('allRacePredictions');
        if (!container) return;

        container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Unable to Load Race Predictions</h3>
                <p>We're having trouble loading the race predictions. Please try again later.</p>
                <button class="retry-btn" onclick="predictionsApp.loadAllRaces()">
                    <i class="fas fa-refresh"></i> Retry
                </button>
            </div>
        `;
    }

    async loadTeams() {
        try {
            const teamsData = await this.fetchWithCache(`${this.apiBaseUrl}/teams`);
            this.renderTeams(teamsData);
        } catch (error) {
            console.error('Error loading teams:', error);
            this.renderTeamsError();
        }
    }

    renderTeams(teamsData) {
        const container = document.getElementById('teamsGrid');
        if (!container) return;

        const teams = teamsData?.teams || this.getDefaultTeams();

        container.innerHTML = teams.map(team => `
            <div class="team-card" data-team="${team.constructorId}">
                <div class="team-header">
                    <div class="team-color" style="background-color: ${team.color}"></div>
                    <span class="team-name">${team.name}</span>
                </div>
                <ul class="drivers-list">
                    ${team.drivers.map(driver => `
                        <li>${driver.name}</li>
                    `).join('')}
                </ul>
            </div>
        `).join('');
    }

    renderTeamsError() {
        const container = document.getElementById('teamsGrid');
        if (!container) return;

        container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">
                    <i class="fas fa-users-slash"></i>
                </div>
                <h3>Unable to Load Teams</h3>
                <p>Team information is currently unavailable.</p>
            </div>
        `;
    }

    getDefaultTeams() {
        return [
            {
                constructorId: 'mercedes',
                name: 'Mercedes-AMG PETRONAS',
                color: 'var(--mercedes-color)',
                drivers: [
                    { name: 'Lewis Hamilton' },
                    { name: 'George Russell' }
                ]
            },
            {
                constructorId: 'red_bull',
                name: 'Oracle Red Bull Racing',
                color: 'var(--redbull-color)',
                drivers: [
                    { name: 'Max Verstappen' },
                    { name: 'Sergio Pérez' }
                ]
            },
            {
                constructorId: 'ferrari',
                name: 'Scuderia Ferrari',
                color: 'var(--ferrari-color)',
                drivers: [
                    { name: 'Charles Leclerc' },
                    { name: 'Carlos Sainz Jr.' }
                ]
            },
            {
                constructorId: 'mclaren',
                name: 'McLaren F1 Team',
                color: 'var(--mclaren-color)',
                drivers: [
                    { name: 'Lando Norris' },
                    { name: 'Oscar Piastri' }
                ]
            },
            {
                constructorId: 'alpine',
                name: 'BWT Alpine F1 Team',
                color: 'var(--alpine-color)',
                drivers: [
                    { name: 'Esteban Ocon' },
                    { name: 'Pierre Gasly' }
                ]
            }
        ];
    }

    async updateStats() {
        try {
            const stats = await this.fetchWithCache(`${this.apiBaseUrl}/prediction-stats`);
            this.renderStats(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
            this.renderDefaultStats();
        }
    }

    renderStats(stats) {
        const elements = {
            totalRaces: document.getElementById('totalRaces'),
            modelAccuracy: document.querySelector('.stat-number:nth-child(2)'),
            totalTeams: document.querySelector('.stat-number:nth-child(3)'),
            totalDrivers: document.querySelector('.stat-number:nth-child(4)')
        };

        if (elements.totalRaces) {
            elements.totalRaces.textContent = stats?.remainingRaces || '4';
        }
    }

    renderDefaultStats() {
        // Stats are already in HTML, no action needed for defaults
    }

    // Utility functions
    formatDate(dateString) {
        if (!dateString) return 'Date TBD';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });
        } catch (error) {
            return 'Date TBD';
        }
    }

    calculateDaysUntil(dateString) {
        if (!dateString) return 'TBD';
        
        try {
            const raceDate = new Date(dateString);
            const today = new Date();
            const diffTime = raceDate - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays < 0) return 'Completed';
            if (diffDays === 0) return 'Today';
            if (diffDays === 1) return '1 day';
            
            return Math.max(0, diffDays);
        } catch (error) {
            return 'TBD';
        }
    }

    getPositionOrdinal(position) {
        const suffixes = ['th', 'st', 'nd', 'rd'];
        const mod100 = position % 100;
        const mod10 = position % 10;
        
        if (mod100 >= 11 && mod100 <= 13) {
            return position + 'th';
        }
        
        return position + (suffixes[mod10] || 'th');
    }

    // Animation functions
    initializeAnimations() {
        this.animateMeters();
        this.observeElements();
    }

    animateMeters() {
        const meters = document.querySelectorAll('.meter-fill[data-width]');
        meters.forEach(meter => {
            const width = meter.getAttribute('data-width');
            setTimeout(() => {
                meter.style.width = width + '%';
            }, 500);
        });
    }

    animateRaceCards() {
        const cards = document.querySelectorAll('.race-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }

    observeElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.team-card, .performance-card').forEach(el => {
            observer.observe(el);
        });
    }

    // Event handlers
    setupEventListeners() {
        // Refresh button handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('retry-btn')) {
                e.preventDefault();
                this.handleRetry(e.target);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.refreshAllData();
            }
        });
    }

    async handleRetry(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Retrying...';
        button.disabled = true;

        try {
            await this.loadInitialData();
        } catch (error) {
            console.error('Retry failed:', error);
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    async refreshAllData() {
        this.cache.clear();
        await this.loadInitialData();
    }

    // Periodic updates
    startPeriodicUpdates() {
        // Update data every 5 minutes
        setInterval(() => {
            this.loadInitialData();
        }, 5 * 60 * 1000);

        // Update countdowns every minute
        setInterval(() => {
            this.updateCountdowns();
        }, 60 * 1000);
    }

    updateCountdowns() {
        document.querySelectorAll('.race-countdown').forEach(element => {
            const raceCard = element.closest('.race-card');
            if (raceCard) {
                const raceId = raceCard.getAttribute('data-race-id');
                // Update countdown logic here if needed
            }
        });
    }

    showErrorMessage(message) {
        // Create or update a global error message
        let errorContainer = document.getElementById('globalError');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = 'globalError';
            errorContainer.className = 'global-error';
            document.body.appendChild(errorContainer);
        }

        errorContainer.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-circle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        errorContainer.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorContainer.parentElement) {
                errorContainer.remove();
            }
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
let predictionsApp;

document.addEventListener('DOMContentLoaded', () => {
    predictionsApp = new PredictionsApp();
});

// Export for global access
window.predictionsApp = predictionsApp;