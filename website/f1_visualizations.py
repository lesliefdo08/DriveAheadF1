"""
F1 Interactive Visualizations with Plotly and Matplotlib
Professional charts for race predictions, driver performance, and analytics
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import io
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1Visualizations:
    """
    Professional F1 data visualizations using Plotly and Matplotlib
    Creates interactive charts for web integration
    """
    
    def __init__(self):
        # Set up plotting styles
        self.f1_colors = {
            'Red Bull Racing': '#1E41FF',
            'Ferrari': '#DC143C',
            'Mercedes': '#00D2BE',
            'McLaren': '#FF8700',
            'Aston Martin': '#006F62',
            'Alpine': '#0090FF',
            'Williams': '#005AFF',
            'AlphaTauri': '#2B4562',
            'Alfa Romeo': '#900000',
            'Haas': '#FFFFFF'
        }
        
        # Plotly theme configuration
        self.plotly_theme = {
            'template': 'plotly_white',
            'font': dict(family="Arial, sans-serif", size=12),
            'title': dict(font=dict(size=16, family="Arial Black"))
        }
    
    def create_race_prediction_chart(self, predictions_data: Dict) -> str:
        """Create interactive race prediction visualization"""
        try:
            if 'drivers' not in predictions_data:
                return self._create_empty_chart("No prediction data available")
            
            drivers = predictions_data['drivers'][:8]  # Top 8 for better display
            
            # Extract data for visualization
            driver_names = [d.get('driver_name', 'Unknown') for d in drivers]
            teams = [d.get('team', 'Unknown') for d in drivers]
            probabilities = [d.get('random_forest_podium_probability', 0) * 100 for d in drivers]
            positions = [d.get('random_forest_position_prediction', i+1) for i, d in enumerate(drivers)]
            form_scores = [d.get('recent_form', 5) for d in drivers]
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Podium Probability (%)', 'Predicted Race Position', 'Recent Form Score', 'Championship Points'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Podium probability bar chart
            colors = [self.f1_colors.get(team, '#808080') for team in teams]
            fig.add_trace(
                go.Bar(
                    x=driver_names,
                    y=probabilities,
                    name='Podium Probability',
                    marker_color=colors,
                    text=[f'{p:.1f}%' for p in probabilities],
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Position prediction scatter
            fig.add_trace(
                go.Scatter(
                    x=driver_names,
                    y=positions,
                    mode='markers+lines',
                    name='Predicted Position',
                    marker=dict(size=12, color=colors, line=dict(width=2)),
                    text=[f'P{int(p)}' for p in positions],
                    textposition='middle right'
                ),
                row=1, col=2
            )
            
            # Recent form radar-style chart
            fig.add_trace(
                go.Bar(
                    x=driver_names,
                    y=form_scores,
                    name='Recent Form',
                    marker_color=colors,
                    text=[f'{f:.1f}/10' for f in form_scores],
                    textposition='auto'
                ),
                row=2, col=1
            )
            
            # Championship points
            points = [d.get('points', 0) for d in drivers]
            fig.add_trace(
                go.Bar(
                    x=driver_names,
                    y=points,
                    name='Championship Points',
                    marker_color=colors,
                    text=[f'{p}pts' for p in points],
                    textposition='auto'
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text="F1 Race Prediction Analysis - ML Model Results",
                    font=dict(size=18, family="Arial Black"),
                    x=0.5
                ),
                height=800,
                showlegend=False,
                template='plotly_white',
                font=dict(family="Arial, sans-serif", size=11)
            )
            
            # Update axes
            fig.update_yaxes(title_text="Probability (%)", row=1, col=1)
            fig.update_yaxes(title_text="Position (1=Best)", row=1, col=2, autorange="reversed")
            fig.update_yaxes(title_text="Form Score (1-10)", row=2, col=1)
            fig.update_yaxes(title_text="Points", row=2, col=2)
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Error creating race prediction chart: {e}")
            return self._create_empty_chart("Error creating prediction visualization")
    
    def create_championship_standings_chart(self, standings_data: pd.DataFrame) -> str:
        """Create championship standings visualization"""
        try:
            if standings_data.empty:
                return self._create_empty_chart("No standings data available")
            
            # Sort by position
            standings_sorted = standings_data.sort_values('position').head(10)
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Championship Points', 'Wins vs Points'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Points bar chart
            colors = [self.f1_colors.get(team, '#808080') for team in standings_sorted['constructor']]
            
            fig.add_trace(
                go.Bar(
                    x=standings_sorted['driver_name'],
                    y=standings_sorted['points'],
                    name='Championship Points',
                    marker_color=colors,
                    text=standings_sorted['points'],
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Wins vs Points scatter
            fig.add_trace(
                go.Scatter(
                    x=standings_sorted['wins'],
                    y=standings_sorted['points'],
                    mode='markers+text',
                    name='Wins vs Points',
                    marker=dict(
                        size=15,
                        color=colors,
                        line=dict(width=2, color='white')
                    ),
                    text=standings_sorted['driver_name'].str.split().str[-1],  # Last name only
                    textposition='middle right'
                ),
                row=1, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text="F1 Championship Standings - Real-time Data",
                    font=dict(size=18, family="Arial Black"),
                    x=0.5
                ),
                height=500,
                showlegend=False,
                template='plotly_white'
            )
            
            fig.update_xaxes(title_text="Drivers", row=1, col=1, tickangle=45)
            fig.update_yaxes(title_text="Points", row=1, col=1)
            fig.update_xaxes(title_text="Race Wins", row=1, col=2)
            fig.update_yaxes(title_text="Championship Points", row=1, col=2)
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Error creating standings chart: {e}")
            return self._create_empty_chart("Error creating standings visualization")
    
    def create_driver_performance_trend(self, driver_data: Dict, historical_results: List[Dict] = None) -> str:
        """Create driver performance trend analysis"""
        try:
            if not driver_data:
                return self._create_empty_chart("No driver data available")
            
            # Create performance metrics visualization
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Career Statistics', 'Recent Form Trend', 'Performance Metrics', 'Season Progress'),
                specs=[[{"type": "xy"}, {"type": "xy"}],
                       [{"type": "scatterpolar"}, {"type": "xy"}]]
            )
            
            # Career stats pie chart (converted to bar for better display)
            career_stats = ['Wins', 'Podiums', 'Other Races']
            career_values = [
                driver_data.get('career_wins', 0),
                driver_data.get('career_podiums', 0) - driver_data.get('career_wins', 0),
                driver_data.get('career_races', 1) - driver_data.get('career_podiums', 0)
            ]
            
            fig.add_trace(
                go.Bar(
                    x=career_stats,
                    y=career_values,
                    name='Career Results',
                    marker_color=['#FFD700', '#C0C0C0', '#CD7F32']
                ),
                row=1, col=1
            )
            
            # Recent form trend (simulated data if not available)
            if historical_results and len(historical_results) > 0:
                race_dates = [r.get('date', '') for r in historical_results[-8:]]
                positions = [int(r.get('position', 10)) if r.get('position', '').isdigit() else 20 for r in historical_results[-8:]]
            else:
                race_dates = ['Race ' + str(i) for i in range(1, 9)]
                positions = [np.random.randint(1, 15) for _ in range(8)]
            
            fig.add_trace(
                go.Scatter(
                    x=race_dates,
                    y=positions,
                    mode='lines+markers',
                    name='Recent Positions',
                    line=dict(width=3),
                    marker=dict(size=8)
                ),
                row=1, col=2
            )
            
            # Performance radar chart
            categories = ['Speed', 'Consistency', 'Racecraft', 'Qualifying', 'Experience']
            values = [
                driver_data.get('win_percentage', 0) * 10,
                (10 - driver_data.get('recent_form_score', 5)) * 2,
                driver_data.get('podium_percentage', 0) * 10,
                driver_data.get('win_percentage', 0) * 8,
                min(10, driver_data.get('career_races', 1) / 50 * 10)
            ]
            
            fig.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Performance Profile'
                ),
                row=2, col=1
            )
            
            # Season progress (simulated)
            season_rounds = list(range(1, 23))
            cumulative_points = np.cumsum([np.random.randint(0, 25) for _ in season_rounds])
            
            fig.add_trace(
                go.Scatter(
                    x=season_rounds,
                    y=cumulative_points,
                    mode='lines+markers',
                    name='Season Points Progression',
                    fill='tonexty'
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text=f"Driver Analysis: {driver_data.get('name', 'Unknown Driver')}",
                    font=dict(size=18, family="Arial Black"),
                    x=0.5
                ),
                height=800,
                template='plotly_white'
            )
            
            # Update specific axes
            fig.update_yaxes(title_text="Count", row=1, col=1)
            fig.update_yaxes(title_text="Position", autorange="reversed", row=1, col=2)
            fig.update_yaxes(title_text="Cumulative Points", row=2, col=2)
            fig.update_xaxes(title_text="Race Rounds", row=2, col=2)
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Error creating driver performance chart: {e}")
            return self._create_empty_chart("Error creating driver visualization")
    
    def create_circuit_analysis_chart(self, circuit_data: Dict, lap_times: pd.DataFrame = None) -> str:
        """Create circuit characteristics and analysis visualization"""
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Circuit Characteristics', 'Lap Time Distribution', 'Sector Analysis', 'Historical Winners'),
                specs=[[{"type": "bar"}, {"type": "histogram"}],
                       [{"type": "bar"}, {"type": "pie"}]]
            )
            
            # Circuit characteristics
            characteristics = ['Overtaking Difficulty', 'Qualifying Importance', 'Tire Degradation', 'Power Importance']
            values = [
                circuit_data.get('overtaking_difficulty', 0.5) * 100,
                circuit_data.get('qualifying_importance', 0.6) * 100,
                circuit_data.get('tire_degradation_factor', 0.7) * 100,
                80 if 'street' in circuit_data.get('circuit_type', '').lower() else 60
            ]
            
            fig.add_trace(
                go.Bar(
                    x=characteristics,
                    y=values,
                    name='Circuit Factors',
                    marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                ),
                row=1, col=1
            )
            
            # Lap time distribution (simulated if no data)
            if lap_times is not None and not lap_times.empty:
                times = lap_times['best_lap_time'].dropna()
            else:
                base_time = circuit_data.get('lap_record', 90)
                times = np.random.normal(base_time + 2, 1, 100)
            
            fig.add_trace(
                go.Histogram(
                    x=times,
                    nbinsx=20,
                    name='Lap Times',
                    marker_color='#FFA07A'
                ),
                row=1, col=2
            )
            
            # Sector analysis (simulated)
            sectors = ['Sector 1', 'Sector 2', 'Sector 3']
            sector_times = [28.5, 35.2, 26.8]  # Example sector times
            
            fig.add_trace(
                go.Bar(
                    x=sectors,
                    y=sector_times,
                    name='Sector Times',
                    marker_color=['#FF9999', '#66B2FF', '#99FF99']
                ),
                row=2, col=1
            )
            
            # Historical winners pie chart
            teams = ['Ferrari', 'Red Bull Racing', 'Mercedes', 'McLaren', 'Others']
            wins = [3, 4, 2, 1, 2]  # Example data
            colors = ['#DC143C', '#1E41FF', '#00D2BE', '#FF8700', '#808080']
            
            fig.add_trace(
                go.Pie(
                    labels=teams,
                    values=wins,
                    name='Historical Winners',
                    marker_colors=colors
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text=f"Circuit Analysis: {circuit_data.get('circuit_name', 'Unknown Circuit')}",
                    font=dict(size=18, family="Arial Black"),
                    x=0.5
                ),
                height=800,
                template='plotly_white',
                showlegend=True
            )
            
            # Update axes
            fig.update_yaxes(title_text="Factor (%)", row=1, col=1)
            fig.update_xaxes(title_text="Lap Time (s)", row=1, col=2)
            fig.update_yaxes(title_text="Frequency", row=1, col=2)
            fig.update_yaxes(title_text="Time (s)", row=2, col=1)
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Error creating circuit analysis chart: {e}")
            return self._create_empty_chart("Error creating circuit visualization")
    
    def create_model_performance_chart(self, model_performance: Dict) -> str:
        """Create ML model performance visualization"""
        try:
            if not model_performance:
                return self._create_empty_chart("No model performance data available")
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Model Accuracy Scores', 'Model Types Distribution'),
                specs=[[{"type": "bar"}, {"type": "pie"}]]
            )
            
            # Model accuracy scores
            model_names = list(model_performance.keys())
            scores = [data.get('test_score', 0) for data in model_performance.values()]
            model_types = [data.get('model_type', 'unknown') for data in model_performance.values()]
            
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            
            fig.add_trace(
                go.Bar(
                    x=[name.replace('_', ' ').title() for name in model_names],
                    y=scores,
                    name='Model Accuracy',
                    marker_color=colors[:len(model_names)],
                    text=[f'{s:.3f}' for s in scores],
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Model types distribution
            type_counts = {}
            for mt in model_types:
                type_counts[mt] = type_counts.get(mt, 0) + 1
            
            fig.add_trace(
                go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    name='Model Types'
                ),
                row=1, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text="ML Model Performance Analysis",
                    font=dict(size=18, family="Arial Black"),
                    x=0.5
                ),
                height=500,
                template='plotly_white'
            )
            
            fig.update_yaxes(title_text="Accuracy Score", row=1, col=1)
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Error creating model performance chart: {e}")
            return self._create_empty_chart("Error creating model visualization")
    
    def _create_empty_chart(self, message: str) -> str:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            template='plotly_white',
            height=400
        )
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_matplotlib_summary(self, data: Dict) -> str:
        """Create matplotlib summary chart and return as base64 string"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Example plots - replace with actual data
            # Driver standings
            drivers = ['VER', 'HAM', 'LEC', 'SAI', 'RUS']
            points = [350, 280, 270, 260, 220]
            ax1.bar(drivers, points, color=['#1E41FF', '#00D2BE', '#DC143C', '#DC143C', '#00D2BE'])
            ax1.set_title('Championship Standings')
            ax1.set_ylabel('Points')
            
            # Performance trend
            races = range(1, 11)
            positions = [1, 2, 1, 3, 1, 2, 4, 1, 1, 2]
            ax2.plot(races, positions, marker='o', linewidth=3, markersize=8)
            ax2.set_title('Season Performance Trend')
            ax2.set_ylabel('Position')
            ax2.invert_yaxis()
            
            # Tire strategy analysis
            compounds = ['Soft', 'Medium', 'Hard']
            usage = [30, 45, 25]
            ax3.pie(usage, labels=compounds, autopct='%1.1f%%')
            ax3.set_title('Tire Strategy Distribution')
            
            # Lap time analysis
            laps = range(1, 51)
            lap_times = np.random.normal(90, 2, 50)
            ax4.plot(laps, lap_times, alpha=0.7)
            ax4.set_title('Lap Time Analysis')
            ax4.set_xlabel('Lap Number')
            ax4.set_ylabel('Lap Time (s)')
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')
            
            plt.close()
            
            return graphic
            
        except Exception as e:
            logger.error(f"Error creating matplotlib summary: {e}")
            return ""

# Example usage
if __name__ == "__main__":
    viz = F1Visualizations()
    print("🎨 Testing F1 Visualizations...")
    
    # Test data
    test_predictions = {
        'drivers': [
            {'driver_name': 'Max Verstappen', 'team': 'Red Bull Racing', 'random_forest_podium_probability': 0.85, 'random_forest_position_prediction': 1, 'recent_form': 9.2, 'points': 350},
            {'driver_name': 'Lewis Hamilton', 'team': 'Mercedes', 'random_forest_podium_probability': 0.72, 'random_forest_position_prediction': 2, 'recent_form': 8.1, 'points': 280},
            {'driver_name': 'Charles Leclerc', 'team': 'Ferrari', 'random_forest_podium_probability': 0.68, 'random_forest_position_prediction': 3, 'recent_form': 7.9, 'points': 270}
        ]
    }
    
    # Test chart creation
    chart_html = viz.create_race_prediction_chart(test_predictions)
    print(f"Created prediction chart: {len(chart_html)} characters")
    
    model_perf = {
        'random_forest_position': {'test_score': 0.85, 'model_type': 'regression'},
        'xgboost_podium': {'test_score': 0.78, 'model_type': 'classification'}
    }
    
    perf_chart = viz.create_model_performance_chart(model_perf)
    print(f"Created performance chart: {len(perf_chart)} characters")