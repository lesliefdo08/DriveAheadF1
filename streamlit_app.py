import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="DriveAhead F1 Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for F1 styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #ff1e1e 0%, #ff6b6b 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #ff1e1e;
    }
    .prediction-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏎️ DriveAhead F1 Analytics Platform</h1>
    <p>Real-time Formula 1 Predictions & Performance Analytics</p>
</div>
""", unsafe_allow_html=True)

# API Functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_f1_data(endpoint):
    """Fetch data from Jolpica F1 API"""
    try:
        if endpoint == "next_race":
            url = "http://api.jolpi.ca/ergast/f1/2025.json"
            response = requests.get(url)
            data = response.json()
            races = data['MRData']['RaceTable']['Races']
            next_race = next((race for race in races if datetime.strptime(race['date'], '%Y-%m-%d') > datetime.now()), races[0])
            return next_race
        elif endpoint == "driver_standings":
            url = "http://api.jolpi.ca/ergast/f1/current/driverStandings.json"
            response = requests.get(url)
            data = response.json()
            return data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        elif endpoint == "constructor_standings":
            url = "http://api.jolpi.ca/ergast/f1/current/constructorStandings.json"
            response = requests.get(url)
            data = response.json()
            return data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Sidebar
st.sidebar.title("🏁 Navigation")
page = st.sidebar.selectbox("Choose Page", ["🏠 Dashboard", "🔮 Live Predictions", "📊 Driver Standings", "🏆 Constructor Standings"])

if page == "🏠 Dashboard":
    st.title("F1 Dashboard")
    
    # Next Race Info
    next_race = fetch_f1_data("next_race")
    if next_race:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Next Race", next_race['raceName'])
        with col2:
            st.metric("Circuit", next_race['Circuit']['circuitName'])
        with col3:
            st.metric("Date", next_race['date'])
    
    # Quick Stats
    st.subheader("Quick Analytics")
    col1, col2 = st.columns(2)
    
    with col1:
        driver_standings = fetch_f1_data("driver_standings")
        if driver_standings:
            leader = driver_standings[0]
            st.markdown(f"""
            <div class="prediction-box">
                <h3>Championship Leader</h3>
                <h2>{leader['Driver']['givenName']} {leader['Driver']['familyName']}</h2>
                <p>{leader['points']} points</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        constructor_standings = fetch_f1_data("constructor_standings")
        if constructor_standings:
            leader = constructor_standings[0]
            st.markdown(f"""
            <div class="prediction-box">
                <h3>Constructors Leader</h3>
                <h2>{leader['Constructor']['name']}</h2>
                <p>{leader['points']} points</p>
            </div>
            """, unsafe_allow_html=True)

elif page == "🔮 Live Predictions":
    st.title("Live Race Predictions")
    
    # Horizontal Layout as requested
    st.subheader("Analytics Dashboard - Horizontal Layout")
    
    # Create horizontal containers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏁 Team Performance")
        teams_data = [
            {"Team": "Red Bull Racing", "Win Probability": 85, "Performance": 92},
            {"Team": "Ferrari", "Win Probability": 75, "Performance": 88},
            {"Team": "Mercedes", "Win Probability": 65, "Performance": 82},
            {"Team": "McLaren", "Win Probability": 45, "Performance": 76}
        ]
        
        teams_df = pd.DataFrame(teams_data)
        
        # Create performance chart
        fig = px.bar(teams_df, x='Team', y='Win Probability', 
                    color='Performance', 
                    title="Race Win Probability by Team",
                    color_continuous_scale='Reds')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Performance Metrics")
        
        # Performance indicators
        metrics = ["Qualifying Pace", "Race Pace", "Strategy", "Reliability"]
        values = [88, 92, 85, 90]
        
        fig = go.Figure(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name='Performance'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            height=400,
            title="Overall Performance Radar"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Race Prediction
    st.subheader("🏆 Next Race Winner Prediction")
    
    prediction_col1, prediction_col2, prediction_col3 = st.columns(3)
    
    with prediction_col1:
        st.markdown("""
        <div class="prediction-box">
            <h3>🥇 Most Likely Winner</h3>
            <h2>Max Verstappen</h2>
            <p>78% Win Probability</p>
        </div>
        """, unsafe_allow_html=True)
    
    with prediction_col2:
        st.markdown("""
        <div class="prediction-box">
            <h3>🥈 Second Favorite</h3>
            <h2>Charles Leclerc</h2>
            <p>65% Podium Chance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with prediction_col3:
        st.markdown("""
        <div class="prediction-box">
            <h3>🥉 Dark Horse</h3>
            <h2>Lando Norris</h2>
            <p>45% Top 5 Finish</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "📊 Driver Standings":
    st.title("Driver Championship Standings")
    
    driver_standings = fetch_f1_data("driver_standings")
    if driver_standings:
        # Create DataFrame
        drivers_data = []
        for standing in driver_standings:
            drivers_data.append({
                "Position": int(standing['position']),
                "Driver": f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}",
                "Team": standing['Constructors'][0]['name'],
                "Points": int(standing['points']),
                "Wins": int(standing['wins'])
            })
        
        df = pd.DataFrame(drivers_data)
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Points chart
        fig = px.bar(df.head(10), x='Driver', y='Points', 
                    color='Points',
                    title="Top 10 Drivers - Championship Points",
                    color_continuous_scale='Reds')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

elif page == "🏆 Constructor Standings":
    st.title("Constructor Championship Standings")
    
    constructor_standings = fetch_f1_data("constructor_standings")
    if constructor_standings:
        # Create DataFrame
        constructors_data = []
        for standing in constructor_standings:
            constructors_data.append({
                "Position": int(standing['position']),
                "Constructor": standing['Constructor']['name'],
                "Points": int(standing['points']),
                "Wins": int(standing['wins'])
            })
        
        df = pd.DataFrame(constructors_data)
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Points chart
        fig = px.pie(df, values='Points', names='Constructor',
                    title="Constructor Championship Points Distribution")
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🏎️ **DriveAhead F1 Analytics** - Powered by Streamlit | Data from Jolpica F1 API")