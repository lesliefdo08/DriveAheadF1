import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Response Types
export interface DriverStanding {
  position: string;
  driver: string;
  team: string;
  points: number;
  wins: number;
}

export interface ConstructorStanding {
  position: string;
  team: string;
  points: number;
  wins: number;
}

export interface StandingsResponse {
  drivers: DriverStanding[];
  constructors: ConstructorStanding[];
  last_updated: string;
  season: string;
  round: string;
  source: string;
}

export interface NextRaceResponse {
  name: string;
  circuit: string;
  location: string;
  country: string;
  date: string;
  time: string;
  round: number;
}

export interface Prediction {
  driver: string;
  team: string;
  probability: number;
  predicted_position: number;
  confidence: string;
  odds: string;
  score?: number;
  current_points?: number;
  wins?: number;
}

export interface PredictionsResponse {
  predictions: Prediction[];
  winner_prediction: {
    driver: string;
    confidence: number;
    reasoning: string;
    breakdown: any;
  };
  next_race: any;
  last_updated: string;
  model_type: string;
  source: string;
  season: string;
  round: string;
}

export interface TelemetryData {
  [driverNumber: string]: {
    position: number;
    driver_acronym: string;
    driver_name: string;
    team_name: string;
    gap_to_leader: string;
    interval: string;
    last_lap_time: string;
    best_lap_time: string;
    sectors: Array<{
      time: string;
      status: string;
    }>;
    speed_trap: number;
    tire_compound: string;
    tire_age: number;
    drs_enabled: boolean;
    in_pit: boolean;
    pit_out: boolean;
    throttle_percent: number;
    brake_pressure: number;
  } | {
    session_name: string;
    lap_number: number;
    weather: {
      air_temp: string;
      track_temp: string;
      humidity: string;
      wind_speed: string;
    };
  };
}

export interface RaceScheduleResponse {
  races: Array<{
    round: string;
    race_name: string;
    circuit_name: string;
    locality: string;
    country: string;
    date: string;
    time: string;
  }>;
  total_races: number;
  last_updated: string;
  season: string;
  source: string;
}

// API Functions
export const apiService = {
  // Status
  async getStatus() {
    const response = await api.get('/api/status');
    return response.data;
  },

  // Standings
  async getStandings(): Promise<StandingsResponse> {
    const response = await api.get('/api/standings');
    return response.data;
  },

  // Next Race
  async getNextRace(): Promise<NextRaceResponse> {
    const response = await api.get('/api/next-race');
    return response.data.race;
  },

  // Last Race
  async getLastRace() {
    const response = await api.get('/api/last-race');
    return response.data;
  },

  // Predictions
  async getPredictions(): Promise<PredictionsResponse> {
    const response = await api.get('/api/predictions');
    return response.data;
  },

  async getWinnerPrediction() {
    const response = await api.get('/api/predictions/winner');
    return response.data;
  },

  async getAllRacePredictions() {
    const response = await api.get('/api/predictions/all-races');
    return response.data;
  },

  async getPredictionHistory() {
    const response = await api.get('/api/predictions/history');
    return response.data;
  },

  async getPredictionAccuracy() {
    const response = await api.get('/api/predictions/accuracy');
    return response.data;
  },

  // Telemetry
  async getTelemetry(): Promise<TelemetryData> {
    const response = await api.get('/api/telemetry');
    return response.data;
  },

  async getTrackData() {
    const response = await api.get('/api/telemetry/track-data');
    return response.data;
  },

  async getDriverTelemetry(driverNumber: number) {
    const response = await api.get(`/api/telemetry/driver/${driverNumber}`);
    return response.data;
  },

  async getSectorTimes() {
    const response = await api.get('/api/telemetry/sectors');
    return response.data;
  },

  async getLivePositions() {
    const response = await api.get('/api/telemetry/live-positions');
    return response.data;
  },

  // Race Schedule
  async getRaceSchedule(): Promise<RaceScheduleResponse> {
    const response = await api.get('/api/race-schedule');
    return response.data;
  },
};

export default apiService;
