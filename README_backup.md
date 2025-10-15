# DriveAhead F1 Analytics Platform# DriveAhead F1 Analytics Platform# DriveAhead F1 Analytics Platform 🏎️



A professional, real-time Formula 1 analytics platform featuring live race countdown, professional telemetry interface, AI predictions, and comprehensive F1 data integration.



## OverviewA professional Formula 1 analytics and prediction platform powered by machine learning algorithms. Built with Flask, featuring real-time race data, predictive modeling, and comprehensive F1 analytics.A professional, real-time Formula 1 analytics platform featuring live race countdown, professional telemetry interface, AI predictions, and comprehensive F1 data integration.



DriveAhead is an advanced F1 analytics system that leverages three powerful machine learning algorithms (Random Forest, XGBoost, and Logistic Regression) to deliver accurate race predictions and comprehensive performance insights.



## Features## Overview## 🚀 Features



### Live Race Countdown

- Real-time Timer: Live countdown to next race (00DAYS : 00HOURS : 00MINUTES)

- Dynamic Status: Race weekend status detection and updatesDriveAhead is an advanced F1 analytics system that leverages three powerful machine learning algorithms (Random Forest, XGBoost, and Logistic Regression) to deliver accurate race predictions and comprehensive performance insights.### 🕐 Live Race Countdown

- Live Timestamps: Real-time clock updates every second

- **Real-time Timer**: Live countdown to next race (00DAYS : 00HOURS : 00MINUTES)

### Professional Telemetry Interface

- F1 Broadcast Design: Professional glass panels with backdrop blur## Key Features- **Dynamic Status**: Race weekend status detection and updates

- Ultra-fast Updates: 1-second telemetry refresh for live racing feel

- Team Colors: 2025 F1 team-specific color coding- **Live Timestamps**: Real-time clock updates every second

- 12-Column Grid: Professional driver leaderboard layout

### Machine Learning Predictions

### Advanced Analytics

- AI Race Predictions: Machine learning powered winner predictions- Race position prediction using regression models### 🏁 Professional Telemetry Interface

- Live Standings: Real-time driver and constructor championships

- Performance Metrics: Comprehensive F1 analytics and insights- Winner prediction with 97%+ accuracy- **F1 Broadcast Design**: Professional glass panels with backdrop blur

- Professional Styling: Orbitron font and F1 color scheme

- Podium finish prediction- **Ultra-fast Updates**: 1-second telemetry refresh for live racing feel

### Modern Design

- Professional UI: F1 broadcast-style interface- Optimized model selection (saves only the 3 best-performing models)- **Team Colors**: 2025 F1 team-specific color coding

- Responsive Layout: Optimized for all devices

- Smooth Animations: CSS transitions and gradients- **12-Column Grid**: Professional driver leaderboard layout

- Enhanced UX: Glass panels, shadows, and professional typography

### Real-time F1 Data

## Technology Stack

- Live race countdown with precise timing### 📊 Advanced Analytics

- **Backend**: Flask (Python 3.11+)

- **Frontend**: HTML5, CSS3, Vanilla JavaScript- Current driver and constructor standings- **AI Race Predictions**: Machine learning powered winner predictions

- **Machine Learning**: scikit-learn, XGBoost, pandas, numpy

- **Data Source**: Jolpica F1 API (Ergast F1 API)- Race schedule and results- **Live Standings**: Real-time driver and constructor championships

- **Styling**: Modern CSS Grid, Flexbox, Tailwind CSS

- **Deployment**: Render.com (Web Service)- Telemetry data visualization- **Performance Metrics**: Comprehensive F1 analytics and insights



## Installation- Next race information- **Professional Styling**: Orbitron font and F1 color scheme



### Prerequisites

- Python 3.11 or higher

- pip package manager### Professional Interface### 🎨 Modern Design

- Git

- Modern, responsive web design- **Professional UI**: F1 broadcast-style interface

### Local Setup

- Real-time data updates- **Responsive Layout**: Optimized for all devices

1. **Clone the repository**

   ```bash- Interactive charts and visualizations- **Smooth Animations**: CSS transitions and gradients

   git clone https://github.com/lesliefdo08/DriveAheadF1.git

   cd DriveAheadF1- Mobile-optimized layout- **Enhanced UX**: Glass panels, shadows, and professional typography

   ```



2. **Create a virtual environment**

   ```bash## Technology Stack## 🛠️ Technology Stack

   python -m venv .venv

   

   # Windows

   .venv\Scripts\activate### Backend- **Backend**: Flask (Python)

   

   # macOS/Linux- Python 3.11+- **Frontend**: HTML5, CSS3, Vanilla JavaScript

   source .venv/bin/activate

   ```- Flask 3.0.3- **Data Source**: Jolpica F1 API (Ergast F1 API)



3. **Install dependencies**- Machine Learning: scikit-learn, XGBoost- **Styling**: Modern CSS Grid, Flexbox, CSS Variables

   ```bash

   cd website- Data Processing: pandas, numpy- **Deployment**: Netlify (Frontend), Heroku/Railway (Backend)

   pip install -r requirements.txt

   ```



4. **Run the application**### Frontend## 📦 Installation

   ```bash

   python app.py- HTML5, CSS3, JavaScript

   ```

- Tailwind CSS for styling1. **Clone the repository**

5. **Access the platform**

   Open your browser to `http://localhost:5000`- Chart.js for data visualization   ```bash



## Machine Learning Training- Responsive design principles   git clone https://github.com/lesliefdo08/DriveAhead.git



The platform uses an optimized ML training system that trains three algorithms and intelligently saves only the best-performing models.   cd DriveAhead



### Train Models### Data Source   ```



```bash- Jolpica F1 API (Ergast F1 data)

python train_models_clean.py

```- Real-time race information2. **Install dependencies**



### Training Process- Historical F1 statistics   ```bash

- Generates 3000 realistic F1 training samples

- Trains Random Forest, XGBoost, and Logistic Regression   pip install -r requirements.txt

- Evaluates using MAE (position) and Accuracy (winner/podium)

- Saves only the 3 best models plus scaler and encoders### Deployment   ```



### Model Performance- Render.com (Web Service)

- Position Prediction: MAE < 1.4

- Winner Prediction: 97%+ accuracy- Gunicorn WSGI server3. **Run the application**

- Podium Prediction: 95%+ accuracy

- Production-ready configuration   ```bash

## Project Structure

   cd website

```

DriveAhead F1/## Installation   python app_simple.py

├── website/

│   ├── app.py                 # Flask application   ```

│   ├── requirements.txt       # Python dependencies

│   ├── templates/            # HTML templates### Prerequisites

│   │   ├── index.html

│   │   ├── telemetry.html- Python 3.11 or higher4. **Access the platform**

│   │   ├── standings.html

│   │   └── predictions.html- pip package manager   Open your browser to `http://localhost:5000`

│   ├── static/               # Static assets

│   │   ├── css/- Git

│   │   ├── js/

│   │   └── images/## 🌐 Deployment

│   └── cache/                # Cache directory

├── models/                    # Trained ML models### Local Setup

├── train_models_clean.py     # ML training script

├── render.yaml               # Render deployment config### Local Development

└── README.md                 # This file

```1. Clone the repository:```bash



## API Endpoints```bashcd website



### Data Endpointsgit clone https://github.com/lesliefdo08/DriveAheadF1.gitpython app_simple.py

- `GET /api/status` - API status and health check

- `GET /api/next-race` - Next upcoming race informationcd DriveAheadF1```

- `GET /api/race-schedule` - Full season schedule

- `GET /api/last-race` - Most recent completed race```

- `GET /api/standings` - Current championship standings

- `GET /api/telemetry` - Live telemetry data### Production Deployment



### Prediction Endpoints2. Create a virtual environment:The application is configured for deployment on:

- `GET /api/predictions` - ML-powered race predictions

- `GET /api/predictions/winner` - Winner prediction with confidence```bash- **Netlify**: For static frontend hosting



## Pagespython -m venv .venv- **Heroku/Railway**: For backend API hosting



1. **Home Dashboard** (`/`)

   - Overview of F1 standings and upcoming races

   - Quick access to predictions and analytics# Windows## 📱 Pages



2. **Live Telemetry** (`/telemetry`).venv\Scripts\activate

   - Real-time race data and driver positions

   - Professional F1 broadcast-style interface1. **Home Dashboard** (`/`)



3. **Standings** (`/standings`)# macOS/Linux   - Overview of F1 standings and upcoming races

   - Driver and constructor championship tables

   - Historical performance datasource .venv/bin/activate   - Quick access to predictions and analytics



4. **Live Predictions** (`/predictions`)```

   - AI-powered race winner predictions

   - Probability charts and confidence metrics2. **Live Predictions** (`/predictions`)



## Configuration3. Install dependencies:   - Horizontal layout with side-by-side analytics



### Environment Variables```bash   - Team performance metrics



```bashcd website   - Race winner predictions

# API Configuration

JOLPICA_API_BASE=http://api.jolpi.ca/ergast/f1pip install -r requirements.txt   - Real-time data updates

API_TIMEOUT=10

API_CACHE_TTL=300```



# Flask Configuration## 🎯 API Endpoints

FLASK_ENV=production

SECRET_KEY=your-secret-key-here4. Run the development server:



# Performance Settings```bash- `/api/next-race` - Next scheduled F1 race

DATA_REFRESH_INTERVAL=30000

CACHE_ENABLED=truepython app.py- `/api/driver-standings` - Current driver championship standings

```

```- `/api/constructor-standings` - Constructor championship standings

## Deployment

- `/api/race-winner-predictions` - AI race winner predictions

### Render.com Deployment

5. Open your browser and navigate to:- `/api/all-upcoming-predictions` - Complete prediction data

1. Push code to GitHub repository

2. Connect repository to Render.com```- `/api/race-schedule` - F1 race calendar

3. Configure environment variables

4. Deploy using `render.yaml` configurationhttp://localhost:5000



Detailed instructions: See `RENDER_DEPLOYMENT_GUIDE.md````## 🔧 Configuration



## ML Optimization



**Problem**: Traditional approaches save all trained models (8+ files), consuming unnecessary storage.## Machine Learning TrainingThe application uses environment-based configuration with fallback to default settings. All F1 data is sourced from the reliable Jolpica F1 API.



**Solution**: Intelligent selection algorithm that:

1. Trains all three algorithms

2. Evaluates performance rigorouslyThe platform uses an optimized ML training system that trains three algorithms and intelligently saves only the best-performing models.## 🚀 Performance Features

3. Saves ONLY the best-performing model for each task

4. Results in 60-70% reduction in storage usage



**Impact**:### Train Models- **Caching**: Intelligent API response caching

- Storage: ~50MB to ~20MB per training session

- Files saved: 8 models to 3 models + 2 supporting files- **Error Recovery**: Automatic retry mechanisms

- Performance: Maintained at 97%+ accuracy

```bash- **Responsive Loading**: Progressive data loading

## Performance Features

python train_models_clean.py- **Optimized Assets**: Minified CSS and efficient JavaScript

- Caching: Intelligent API response caching

- Error Recovery: Automatic retry mechanisms```

- Responsive Loading: Progressive data loading

- Optimized Assets: Minified CSS and efficient JavaScript## 📄 License



## Troubleshooting### Training Output



### Common Issues- Generates 3000 realistic F1 training samplesThis project is open source and available under the MIT License.



1. **Port already in use**- Trains Random Forest, XGBoost, and Logistic Regression

   ```bash

   # Windows- Evaluates using MAE (position) and Accuracy (winner/podium)## 🏁 About

   netstat -ano | findstr :5000

   taskkill /PID <process_id> /F- Saves only the 3 best models plus scaler and encoders

   ```

DriveAhead brings the excitement of Formula 1 to your fingertips with real-time analytics, predictions, and comprehensive race data. Built with modern web technologies for optimal performance and user experience.

2. **Module not found errors**

   ```bash### Model Performance

   pip install -r requirements.txt --upgrade

   ```- Position Prediction: MAE < 1.4---



3. **API rate limiting**- Winner Prediction: 97%+ accuracy

   - Implement caching to reduce API calls

   - Use fallback data when API is unavailable- Podium Prediction: 93%+ accuracy**Developed with ❤️ for F1 fans worldwide** 🏎️💨



## Contributing## Project Structure



Contributions are welcome! Please:```

1. Fork the repositoryDriveAhead F1/

2. Create a feature branch├── website/

3. Make your changes│   ├── app.py                 # Flask application

4. Submit a pull request│   ├── requirements.txt       # Python dependencies

│   ├── templates/            # HTML templates

## License│   │   ├── index.html

│   │   ├── telemetry.html

This project is open source and available under the MIT License.│   │   ├── standings.html

│   │   └── predictions.html

## About│   ├── static/               # Static assets

│   │   ├── css/

DriveAhead brings the excitement of Formula 1 to your fingertips with real-time analytics, predictions, and comprehensive race data. Built with modern web technologies for optimal performance and user experience.│   │   ├── js/

│   │   └── images/

## Contact│   └── cache/                # Cache directory

├── models/                    # Trained ML models

- GitHub: [@lesliefdo08](https://github.com/lesliefdo08)├── train_models_clean.py     # ML training script

- Repository: [DriveAheadF1](https://github.com/lesliefdo08/DriveAheadF1)├── render.yaml               # Render deployment config

├── RENDER_ENV_VARS.txt       # Environment variables

## Project Status└── README.md                 # This file

```

**Current Version**: 2.0.0  

**Status**: Production Ready  ## API Endpoints

**Last Updated**: October 15, 2025

### Data Endpoints

---- `GET /api/status` - API status and health check

- `GET /api/next-race` - Next upcoming race information

Built with precision for Formula 1 enthusiasts and data scientists.- `GET /api/race-schedule` - Full season schedule

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
