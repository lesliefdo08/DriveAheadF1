# DriveAhead F1 Analytics Platform 🏎️

A professional, real-time Formula 1 analytics platform featuring live race countdown, professional telemetry interface, AI predictions, and comprehensive F1 data integration.

## 🚀 Features

### 🕐 Live Race Countdown
- **Real-time Timer**: Live countdown to next race (00DAYS : 00HOURS : 00MINUTES)
- **Dynamic Status**: Race weekend status detection and updates
- **Live Timestamps**: Real-time clock updates every second

### 🏁 Professional Telemetry Interface
- **F1 Broadcast Design**: Professional glass panels with backdrop blur
- **Ultra-fast Updates**: 1-second telemetry refresh for live racing feel
- **Team Colors**: 2025 F1 team-specific color coding
- **12-Column Grid**: Professional driver leaderboard layout

### 📊 Advanced Analytics
- **AI Race Predictions**: Machine learning powered winner predictions
- **Live Standings**: Real-time driver and constructor championships
- **Performance Metrics**: Comprehensive F1 analytics and insights
- **Professional Styling**: Orbitron font and F1 color scheme

### 🎨 Modern Design
- **Professional UI**: F1 broadcast-style interface
- **Responsive Layout**: Optimized for all devices
- **Smooth Animations**: CSS transitions and gradients
- **Enhanced UX**: Glass panels, shadows, and professional typography

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