/**
 * DriveAhead Frontend Configuration
 * Centralized configuration to minimize hardcoding in JavaScript
 */

class DriveAheadConfig {
    constructor() {
        // API Configuration
        this.API_BASE_URL = '/api';
        this.API_TIMEOUT = 10000; // 10 seconds
        this.API_RETRY_ATTEMPTS = 3;
        this.API_RETRY_DELAY = 1000; // 1 second
        
        // Data Loading Delays (in milliseconds)
        this.LOADING_DELAYS = {
            CRITICAL_DATA: 0,
            RACE_WINNER_PREDICTION: 500,
            RACE_SCHEDULE: 800,
            DASHBOARD_PREDICTIONS: 1000,
            MINI_PREDICTIONS: 1200,
            CONSTRUCTOR_CHAMPIONSHIP: 1500,
            MODEL_PERFORMANCE: 2000,
            LIVE_F1_DATA: 2500,
            REAL_TIME_INSIGHTS: 3000,
            COMPLETED_RACES: 3500
        };
        
        // Championship Update Intervals
        this.CHAMPIONSHIP_UPDATES = {
            IMMEDIATE: 0,
            FALLBACK_PRIMARY: 2000,
            FALLBACK_SECONDARY: 4000
        };
        
        // UI Constants
        this.UI_CONSTANTS = {
            DATA_REFRESH_INTERVAL: 30000, // 30 seconds
            LOADING_TIMEOUT: 5000, // 5 seconds
            CHART_ANIMATION_DURATION: 1000, // 1 second
            FADE_DURATION: 300,
            SLIDE_DURATION: 500
        };
        
        // Chart Colors
        this.CHART_COLORS = {
            PRIMARY: '#dc143c',
            SECONDARY: '#ffffff',
            ACCENT: '#ff6b6b',
            BACKGROUND: 'rgba(220, 20, 60, 0.1)',
            GRID: 'rgba(255, 255, 255, 0.1)',
            TEXT: '#888888'
        };
        
        // Team Colors
        this.TEAM_COLORS = {
            'McLaren': '#ff8000',
            'Ferrari': '#dc143c',
            'Red Bull Racing': '#0600ef',
            'Mercedes': '#00d2be',
            'Aston Martin': '#006f62',
            'Alpine': '#0090ff',
            'Haas': '#ffffff',
            'RB': '#6692ff',
            'Williams': '#005aff',
            'Kick Sauber': '#52c41a'
        };
        
        // Fallback Data
        this.FALLBACK_DATA = {
            CONSTRUCTOR_STANDINGS: [
                { position: 1, team: 'McLaren', points: 640 },
                { position: 2, team: 'Ferrari', points: 619 },
                { position: 3, team: 'Red Bull Racing', points: 581 },
                { position: 4, team: 'Mercedes', points: 468 },
                { position: 5, team: 'Aston Martin', points: 86 }
            ],
            
            CHAMPIONSHIP_INSIGHTS: {
                leader: 'McLaren',
                pointsGap: 337,
                titleFight: 'Clear Leader',
                trend: 'Rising'
            },
            
            MODEL_PERFORMANCE: {
                accuracy: 89.2,
                precision: 91.5,
                recall: 87.3,
                f1_score: 89.3,
                total_predictions: 1247,
                correct_predictions: 1112
            },
            
            NEXT_RACE: {
                name: "Qatar Airways Azerbaijan Grand Prix",
                circuit: "Baku City Circuit",
                country: "Azerbaijan",
                date: "2025-09-21",
                race_time_ist: "17:00"
            }
        };
        
        // Message Templates
        this.MESSAGES = {
            LOADING: {
                DRIVER_STANDINGS: 'Loading driver standings...',
                CONSTRUCTOR_STANDINGS: 'Loading constructor standings...',
                RACE_RESULTS: 'Loading race results...',
                PREDICTIONS: 'Loading predictions...',
                TELEMETRY: 'Loading telemetry data...',
                CHAMPIONSHIP_INSIGHTS: 'Loading championship insights...'
            },
            
            ERROR: {
                API_UNAVAILABLE: 'Unable to load data. Please try again later.',
                NETWORK_ERROR: 'Network error. Check your connection.',
                DATA_FORMAT_ERROR: 'Invalid data format received.',
                TIMEOUT_ERROR: 'Request timed out. Please try again.',
                GENERIC_ERROR: 'An error occurred. Please refresh the page.'
            },
            
            SUCCESS: {
                DATA_LOADED: 'Data loaded successfully',
                STANDINGS_UPDATED: 'Standings updated',
                PREDICTIONS_LOADED: 'Predictions loaded'
            }
        };
    }
    
    /**
     * Get API endpoint URL
     * @param {string} endpoint - The endpoint path
     * @returns {string} Full API URL
     */
    getApiUrl(endpoint) {
        return `${this.API_BASE_URL}/${endpoint}`;
    }
    
    /**
     * Get team color by name
     * @param {string} teamName - The team name
     * @returns {string} Team color hex code
     */
    getTeamColor(teamName) {
        return this.TEAM_COLORS[teamName] || this.CHART_COLORS.PRIMARY;
    }
    
    /**
     * Get loading delay for a specific component
     * @param {string} component - The component name
     * @returns {number} Delay in milliseconds
     */
    getLoadingDelay(component) {
        const key = component.toUpperCase().replace(/-/g, '_');
        return this.LOADING_DELAYS[key] || 0;
    }
    
    /**
     * Get message by category and type
     * @param {string} category - Message category (LOADING, ERROR, SUCCESS)
     * @param {string} type - Message type
     * @returns {string} Message text
     */
    getMessage(category, type) {
        const categoryUpper = category.toUpperCase();
        const typeUpper = type.toUpperCase().replace(/-/g, '_');
        
        if (this.MESSAGES[categoryUpper] && this.MESSAGES[categoryUpper][typeUpper]) {
            return this.MESSAGES[categoryUpper][typeUpper];
        }
        
        return this.MESSAGES.ERROR.GENERIC_ERROR;
    }
    
    /**
     * Check if environment is development
     * @returns {boolean} True if development environment
     */
    isDevelopment() {
        return location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    }
    
    /**
     * Get configuration based on environment
     * @returns {object} Environment-specific configuration
     */
    getEnvironmentConfig() {
        if (this.isDevelopment()) {
            return {
                ...this.UI_CONSTANTS,
                DATA_REFRESH_INTERVAL: 10000, // More frequent in dev
                LOADING_TIMEOUT: 3000 // Shorter timeout in dev
            };
        }
        
        return this.UI_CONSTANTS;
    }
}

// Global configuration instance
const CONFIG = new DriveAheadConfig();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DriveAheadConfig, CONFIG };
}