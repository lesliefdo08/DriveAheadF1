# DriveAhead F1 Analytics Platform

A professional, real-time Formula 1 analytics platform featuring live race countdown, professional telemetry interface, AI predictions, and comprehensive F1 data integration.

## Overview

DriveAhead is an advanced F1 analytics system that leverages three powerful machine learning algorithms (Random Forest, XGBoost, and Logistic Regression) to deliver accurate race predictions and comprehensive performance insights.

## Features

### Live Race Countdown
- Real-time Timer: Live countdown to next race (00DAYS : 00HOURS : 00MINUTES)
- Dynamic Status: Race weekend status detection and updates
- Live Timestamps: Real-time clock updates every second

### Professional Telemetry Interface
- F1 Broadcast Design: Professional glass panels with backdrop blur
- Ultra-fast Updates: 1-second telemetry refresh for live racing feel
- Team Colors: 2025 F1 team-specific color coding
- 12-Column Grid: Professional driver leaderboard layout

### Advanced Analytics
- AI Race Predictions: Machine learning powered winner predictions
- Live Standings: Real-time driver and constructor championships
- Performance Metrics: Comprehensive F1 analytics and insights
- Professional Styling: Orbitron font and F1 color scheme

### Modern Design
- Professional UI: F1 broadcast-style interface
- Responsive Layout: Optimized for all devices
- Smooth Animations: CSS transitions and gradients
- Enhanced UX: Glass panels, shadows, and professional typography

## Technology Stack

- **Backend**: Flask (Python 3.11+)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Machine Learning**: scikit-learn, XGBoost, pandas, numpy
- **Data Source**: Jolpica F1 API (Ergast F1 API)
- **Styling**: Modern CSS Grid, Flexbox, Tailwind CSS
- **Deployment**: Render.com (Web Service)

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/lesliefdo08/DriveAheadF1.git
   cd DriveAheadF1
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd website
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the platform**
   Open your browser to `http://localhost:5000`

## Machine Learning Training

The platform uses an optimized ML training system that trains three algorithms and intelligently saves only the best-performing models.

### Train Models

```bash
python train_models_clean.py
```

### Training Process
- Generates 3000 realistic F1 training samples
- Trains Random Forest, XGBoost, and Logistic Regression
- Evaluates using MAE (position) and Accuracy (winner/podium)
- Saves only the 3 best models plus scaler and encoders

### Model Performance
- Position Prediction: MAE < 1.4
- Winner Prediction: 97%+ accuracy
- Podium Prediction: 95%+ accuracy

## Project Structure

```
DriveAhead F1/
├── website/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── templates/            # HTML templates
│   │   ├── index.html
│   │   ├── telemetry.html
│   │   ├── standings.html
│   │   └── predictions.html
│   ├── static/               # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── cache/                # Cache directory
├── models/                    # Trained ML models
├── train_models_clean.py     # ML training script
├── render.yaml               # Render deployment config
└── README.md                 # This file
```

## API Endpoints

### Data Endpoints
- `GET /api/status` - API status and health check
- `GET /api/next-race` - Next upcoming race information
- `GET /api/race-schedule` - Full season schedule
- `GET /api/last-race` - Most recent completed race
- `GET /api/standings` - Current championship standings
- `GET /api/telemetry` - Live telemetry data

### Prediction Endpoints
- `GET /api/predictions` - ML-powered race predictions
- `GET /api/predictions/winner` - Winner prediction with confidence

## Pages

1. **Home Dashboard** (`/`)
   - Overview of F1 standings and upcoming races
   - Quick access to predictions and analytics

2. **Live Telemetry** (`/telemetry`)
   - Real-time race data and driver positions
   - Professional F1 broadcast-style interface

3. **Standings** (`/standings`)
   - Driver and constructor championship tables
   - Historical performance data

4. **Live Predictions** (`/predictions`)
   - AI-powered race winner predictions
   - Probability charts and confidence metrics

## Configuration

### Environment Variables

```bash
# API Configuration
JOLPICA_API_BASE=http://api.jolpi.ca/ergast/f1
API_TIMEOUT=10
API_CACHE_TTL=300

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Performance Settings
DATA_REFRESH_INTERVAL=30000
CACHE_ENABLED=true
```

## Deployment

### Render.com Deployment

1. Push code to GitHub repository
2. Connect repository to Render.com
3. Configure environment variables
4. Deploy using `render.yaml` configuration

Detailed instructions: See `RENDER_ENV_VARS.txt` for required environment variables.

## ML Optimization

**Problem**: Traditional approaches save all trained models (8+ files), consuming unnecessary storage.

**Solution**: Intelligent selection algorithm that:
1. Trains all three algorithms
2. Evaluates performance rigorously
3. Saves ONLY the best-performing model for each task
4. Results in 60-70% reduction in storage usage

**Impact**:
- Storage: ~50MB to ~20MB per training session
- Files saved: 8 models to 3 models + 2 supporting files
- Performance: Maintained at 97%+ accuracy

## Performance Features

- Caching: Intelligent API response caching
- Error Recovery: Automatic retry mechanisms
- Responsive Loading: Progressive data loading
- Optimized Assets: Minified CSS and efficient JavaScript

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <process_id> /F
   ```

2. **Module not found errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **API rate limiting**
   - Implement caching to reduce API calls
   - Use fallback data when API is unavailable

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## About

DriveAhead brings the excitement of Formula 1 to your fingertips with real-time analytics, predictions, and comprehensive race data. Built with modern web technologies for optimal performance and user experience.

## Contact

- GitHub: [@lesliefdo08](https://github.com/lesliefdo08)
- Repository: [DriveAheadF1](https://github.com/lesliefdo08/DriveAheadF1)

## Project Status

**Current Version**: 2.0.0  
**Status**: Production Ready  
**Last Updated**: October 15, 2025

---

Built with precision for Formula 1 enthusiasts and data scientists.
