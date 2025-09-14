# DriveAhead F1 Analytics Platform 🏎️

A modern, real-time Formula 1 analytics platform providing comprehensive race predictions, driver standings, constructor performance data, and live race insights.

## 🚀 Features

### Live Predictions Dashboard
- **Horizontal Analytics Layout**: Side-by-side team performance and analytics containers
- **Real-time Race Predictions**: AI-powered predictions for upcoming F1 races
- **Performance Metrics**: Detailed driver and constructor analytics
- **Interactive Visualizations**: Modern charts and progress indicators

### Comprehensive F1 Data
- **Driver Standings**: Live championship standings with points tracking
- **Constructor Standings**: Team performance and championship positions
- **Race Schedule**: Complete F1 calendar with race information
- **Historical Results**: Past race results and performance analysis

### Modern UI/UX
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Smooth Animations**: Professional transitions and loading states
- **Error Handling**: Robust error states with retry mechanisms
- **Dark Theme**: Modern F1-inspired design aesthetic

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Source**: Jolpica F1 API (Ergast F1 API)
- **Styling**: Modern CSS Grid, Flexbox, CSS Variables
- **Deployment**: Netlify (Frontend), Heroku/Railway (Backend)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lesliefdo08/DriveAhead.git
   cd DriveAhead
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   cd website
   python app_simple.py
   ```

4. **Access the platform**
   Open your browser to `http://localhost:5000`

## 🌐 Deployment

### Local Development
```bash
cd website
python app_simple.py
```

### Production Deployment
The application is configured for deployment on:
- **Netlify**: For static frontend hosting
- **Heroku/Railway**: For backend API hosting

## 📱 Pages

1. **Home Dashboard** (`/`)
   - Overview of F1 standings and upcoming races
   - Quick access to predictions and analytics

2. **Live Predictions** (`/predictions`)
   - Horizontal layout with side-by-side analytics
   - Team performance metrics
   - Race winner predictions
   - Real-time data updates

## 🎯 API Endpoints

- `/api/next-race` - Next scheduled F1 race
- `/api/driver-standings` - Current driver championship standings
- `/api/constructor-standings` - Constructor championship standings
- `/api/race-winner-predictions` - AI race winner predictions
- `/api/all-upcoming-predictions` - Complete prediction data
- `/api/race-schedule` - F1 race calendar

## 🔧 Configuration

The application uses environment-based configuration with fallback to default settings. All F1 data is sourced from the reliable Jolpica F1 API.

## 🚀 Performance Features

- **Caching**: Intelligent API response caching
- **Error Recovery**: Automatic retry mechanisms
- **Responsive Loading**: Progressive data loading
- **Optimized Assets**: Minified CSS and efficient JavaScript

## 📄 License

This project is open source and available under the MIT License.

## 🏁 About

DriveAhead brings the excitement of Formula 1 to your fingertips with real-time analytics, predictions, and comprehensive race data. Built with modern web technologies for optimal performance and user experience.

---

**Developed with ❤️ for F1 fans worldwide** 🏎️💨