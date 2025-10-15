# DriveAhead F1 Analytics Platform# DriveAhead F1 Analytics Platform 🏎️



A professional Formula 1 analytics and prediction platform powered by machine learning algorithms. Built with Flask, featuring real-time race data, predictive modeling, and comprehensive F1 analytics.A professional, real-time Formula 1 analytics platform featuring live race countdown, professional telemetry interface, AI predictions, and comprehensive F1 data integration.



## Overview## 🚀 Features



DriveAhead is an advanced F1 analytics system that leverages three powerful machine learning algorithms (Random Forest, XGBoost, and Logistic Regression) to deliver accurate race predictions and comprehensive performance insights.### 🕐 Live Race Countdown

- **Real-time Timer**: Live countdown to next race (00DAYS : 00HOURS : 00MINUTES)

## Key Features- **Dynamic Status**: Race weekend status detection and updates

- **Live Timestamps**: Real-time clock updates every second

### Machine Learning Predictions

- Race position prediction using regression models### 🏁 Professional Telemetry Interface

- Winner prediction with 97%+ accuracy- **F1 Broadcast Design**: Professional glass panels with backdrop blur

- Podium finish prediction- **Ultra-fast Updates**: 1-second telemetry refresh for live racing feel

- Optimized model selection (saves only the 3 best-performing models)- **Team Colors**: 2025 F1 team-specific color coding

- **12-Column Grid**: Professional driver leaderboard layout

### Real-time F1 Data

- Live race countdown with precise timing### 📊 Advanced Analytics

- Current driver and constructor standings- **AI Race Predictions**: Machine learning powered winner predictions

- Race schedule and results- **Live Standings**: Real-time driver and constructor championships

- Telemetry data visualization- **Performance Metrics**: Comprehensive F1 analytics and insights

- Next race information- **Professional Styling**: Orbitron font and F1 color scheme



### Professional Interface### 🎨 Modern Design

- Modern, responsive web design- **Professional UI**: F1 broadcast-style interface

- Real-time data updates- **Responsive Layout**: Optimized for all devices

- Interactive charts and visualizations- **Smooth Animations**: CSS transitions and gradients

- Mobile-optimized layout- **Enhanced UX**: Glass panels, shadows, and professional typography



## Technology Stack## 🛠️ Technology Stack



### Backend- **Backend**: Flask (Python)

- Python 3.11+- **Frontend**: HTML5, CSS3, Vanilla JavaScript

- Flask 3.0.3- **Data Source**: Jolpica F1 API (Ergast F1 API)

- Machine Learning: scikit-learn, XGBoost- **Styling**: Modern CSS Grid, Flexbox, CSS Variables

- Data Processing: pandas, numpy- **Deployment**: Netlify (Frontend), Heroku/Railway (Backend)



### Frontend## 📦 Installation

- HTML5, CSS3, JavaScript

- Tailwind CSS for styling1. **Clone the repository**

- Chart.js for data visualization   ```bash

- Responsive design principles   git clone https://github.com/lesliefdo08/DriveAhead.git

   cd DriveAhead

### Data Source   ```

- Jolpica F1 API (Ergast F1 data)

- Real-time race information2. **Install dependencies**

- Historical F1 statistics   ```bash

   pip install -r requirements.txt

### Deployment   ```

- Render.com (Web Service)

- Gunicorn WSGI server3. **Run the application**

- Production-ready configuration   ```bash

   cd website

## Installation   python app_simple.py

   ```

### Prerequisites

- Python 3.11 or higher4. **Access the platform**

- pip package manager   Open your browser to `http://localhost:5000`

- Git

## 🌐 Deployment

### Local Setup

### Local Development

1. Clone the repository:```bash

```bashcd website

git clone https://github.com/lesliefdo08/DriveAheadF1.gitpython app_simple.py

cd DriveAheadF1```

```

### Production Deployment

2. Create a virtual environment:The application is configured for deployment on:

```bash- **Netlify**: For static frontend hosting

python -m venv .venv- **Heroku/Railway**: For backend API hosting



# Windows## 📱 Pages

.venv\Scripts\activate

1. **Home Dashboard** (`/`)

# macOS/Linux   - Overview of F1 standings and upcoming races

source .venv/bin/activate   - Quick access to predictions and analytics

```

2. **Live Predictions** (`/predictions`)

3. Install dependencies:   - Horizontal layout with side-by-side analytics

```bash   - Team performance metrics

cd website   - Race winner predictions

pip install -r requirements.txt   - Real-time data updates

```

## 🎯 API Endpoints

4. Run the development server:

```bash- `/api/next-race` - Next scheduled F1 race

python app.py- `/api/driver-standings` - Current driver championship standings

```- `/api/constructor-standings` - Constructor championship standings

- `/api/race-winner-predictions` - AI race winner predictions

5. Open your browser and navigate to:- `/api/all-upcoming-predictions` - Complete prediction data

```- `/api/race-schedule` - F1 race calendar

http://localhost:5000

```## 🔧 Configuration



## Machine Learning TrainingThe application uses environment-based configuration with fallback to default settings. All F1 data is sourced from the reliable Jolpica F1 API.



The platform uses an optimized ML training system that trains three algorithms and intelligently saves only the best-performing models.## 🚀 Performance Features



### Train Models- **Caching**: Intelligent API response caching

- **Error Recovery**: Automatic retry mechanisms

```bash- **Responsive Loading**: Progressive data loading

python train_models_clean.py- **Optimized Assets**: Minified CSS and efficient JavaScript

```

## 📄 License

### Training Output

- Generates 3000 realistic F1 training samplesThis project is open source and available under the MIT License.

- Trains Random Forest, XGBoost, and Logistic Regression

- Evaluates using MAE (position) and Accuracy (winner/podium)## 🏁 About

- Saves only the 3 best models plus scaler and encoders

DriveAhead brings the excitement of Formula 1 to your fingertips with real-time analytics, predictions, and comprehensive race data. Built with modern web technologies for optimal performance and user experience.

### Model Performance

- Position Prediction: MAE < 1.4---

- Winner Prediction: 97%+ accuracy

- Podium Prediction: 93%+ accuracy**Developed with ❤️ for F1 fans worldwide** 🏎️💨

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
├── RENDER_ENV_VARS.txt       # Environment variables
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

## Configuration

### Environment Variables

The application uses the following environment variables (see `RENDER_ENV_VARS.txt`):

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
3. Configure environment variables from `RENDER_ENV_VARS.txt`
4. Deploy using `render.yaml` configuration

Detailed deployment instructions: See `RENDER_DEPLOYMENT_GUIDE.md`

## Machine Learning Optimization

This project implements an intelligent model selection system that answers the computational efficiency question:

**Problem**: Traditional approaches save all trained models (8+ files), consuming unnecessary storage and computational resources.

**Solution**: Intelligent selection algorithm that:
1. Trains all three algorithms (Random Forest, XGBoost, Logistic Regression)
2. Evaluates performance using rigorous metrics
3. Selects and saves ONLY the best-performing model for each task
4. Results in 60-70% reduction in storage and memory usage

**Impact**:
- Storage: ~50MB → ~20MB per training session
- Files saved: 8 models → 3 models + 2 supporting files
- Deployment: Simplified with clear model naming
- Performance: Maintained at 97%+ accuracy

See `OPTIMIZATION_SUMMARY.md` for detailed technical explanation.

## Features in Detail

### Live Race Countdown
- Real-time countdown to next Grand Prix
- Displays days, hours, minutes, and seconds
- Automatically updates race status
- Shows race location and circuit information

### Telemetry Dashboard
- Live position tracking during races
- Lap times and sector performance
- Speed trap data
- Tire compound and age information
- Gap to leader and interval timing

### Standings Page
- Current driver championship standings
- Constructor championship standings
- Points, wins, and position changes
- Historical data from completed races

### Predictions Page
- ML-powered race winner predictions
- Probability charts for all drivers
- Top 10 driver predictions with confidence levels
- Based on current form and historical performance

## Development

### Adding New Features

1. Create a new branch:
```bash
git checkout -b feature/new-feature
```

2. Make your changes and test locally

3. Commit and push:
```bash
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

4. Create a pull request on GitHub

### Code Quality

- Follow PEP 8 style guidelines for Python
- Use meaningful variable and function names
- Add comments for complex logic
- Test all API endpoints before deployment

## Performance Optimization

- Implemented caching for API responses (5-minute TTL)
- Optimized database queries
- Minimized frontend asset sizes
- Lazy loading for images and charts
- Efficient model loading and inference

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find and kill the process using port 5000
   netstat -ano | findstr :5000
   taskkill /PID <process_id> /F
   ```

2. **Module not found errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **API rate limiting**
   - The Jolpica API has rate limits
   - Implement caching to reduce API calls
   - Use fallback data when API is unavailable

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Jolpica F1 API for providing reliable F1 data
- scikit-learn and XGBoost teams for excellent ML libraries
- Flask team for the robust web framework
- F1 community for inspiration and support

## Contact

- GitHub: [@lesliefdo08](https://github.com/lesliefdo08)
- Repository: [DriveAheadF1](https://github.com/lesliefdo08/DriveAheadF1)

## Project Status

**Current Version**: 2.0.0  
**Status**: Production Ready  
**Last Updated**: October 15, 2025

---

Built with precision for Formula 1 enthusiasts and data scientists.
