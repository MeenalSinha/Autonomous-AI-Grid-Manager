"""
Short-Term Forecasting Module
LSTM-based prediction for solar, wind, and load
"""

import numpy as np
import torch
import torch.nn as nn
from collections import deque
from typing import Tuple, List


class LSTMForecaster(nn.Module):
    """LSTM network for time series forecasting"""
    
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 2):
        super(LSTMForecaster, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Linear(hidden_dim, 3)  # Predict solar, wind, load
    
    def forward(self, x):
        # x shape: (batch, sequence, features)
        lstm_out, _ = self.lstm(x)
        
        # Take last time step
        last_output = lstm_out[:, -1, :]
        
        # Prediction
        prediction = self.fc(last_output)
        
        return prediction


class ShortTermForecaster:
    """
    Short-term forecasting for renewable generation and load
    Uses LSTM to predict next-step values
    """
    
    def __init__(self, sequence_length: int = 10):
        self.sequence_length = sequence_length
        
        # Feature dimensions: time, solar, wind, load, cloud, wind_speed, temp
        self.input_dim = 7
        
        # LSTM model
        self.model = LSTMForecaster(self.input_dim)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        
        # Data buffer
        self.history = deque(maxlen=1000)
        
        # Training flag
        self.is_trained = False
    
    def update_history(self, time_of_day: float, solar: float, wind: float, 
                       load: float, cloud_cover: float, wind_speed: float, 
                       temperature: float):
        """Add new observation to history"""
        observation = np.array([
            time_of_day / 24.0,  # Normalize
            solar / 500.0,
            wind / 300.0,
            load / 1000.0,
            cloud_cover,
            wind_speed / 25.0,
            temperature / 50.0
        ])
        
        self.history.append(observation)
    
    def predict(self, horizon: int = 1) -> Tuple[float, float, float]:
        """
        Predict future values
        
        Args:
            horizon: Number of steps ahead to predict
        
        Returns:
            (solar_pred, wind_pred, load_pred)
        """
        if len(self.history) < self.sequence_length:
            # Not enough data, return naive forecast
            if len(self.history) > 0:
                last_obs = self.history[-1]
                return (
                    last_obs[1] * 500.0,  # Solar
                    last_obs[2] * 300.0,  # Wind
                    last_obs[3] * 1000.0  # Load
                )
            else:
                return (0.0, 0.0, 400.0)
        
        # Prepare input sequence
        sequence = np.array(list(self.history)[-self.sequence_length:])
        sequence_tensor = torch.FloatTensor(sequence).unsqueeze(0)
        
        # Predict
        with torch.no_grad():
            self.model.eval()
            prediction = self.model(sequence_tensor).numpy()[0]
        
        # De-normalize
        solar_pred = prediction[0] * 500.0
        wind_pred = prediction[1] * 300.0
        load_pred = prediction[2] * 1000.0
        
        return (solar_pred, wind_pred, load_pred)
    
    def train(self, epochs: int = 50):
        """
        Train the LSTM model on historical data
        
        Note: Online retraining for demonstration purposes.
        Production deployment would use:
        - Rolling time windows
        - Incremental learning
        - Separate train/validation splits
        - Learning rate scheduling
        """
        if len(self.history) < self.sequence_length + 10:
            return
        
        # Prepare training data
        X, y = [], []
        
        history_array = np.array(list(self.history))
        
        for i in range(len(history_array) - self.sequence_length - 1):
            X.append(history_array[i:i+self.sequence_length])
            # Target: next step's solar, wind, load
            y.append(history_array[i+self.sequence_length, [1, 2, 3]])
        
        X = torch.FloatTensor(np.array(X))
        y = torch.FloatTensor(np.array(y))
        
        # Training loop
        self.model.train()
        
        for epoch in range(epochs):
            # Forward pass
            predictions = self.model(X)
            loss = nn.MSELoss()(predictions, y)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        
        self.is_trained = True
    
    def get_forecast_horizon(self, steps: int = 6) -> List[Tuple[float, float, float]]:
        """
        Get multi-step forecast
        
        Args:
            steps: Number of steps to forecast
        
        Returns:
            List of (solar, wind, load) predictions
        """
        forecasts = []
        
        # Use current history
        current_sequence = list(self.history)[-self.sequence_length:]
        
        for _ in range(steps):
            if len(current_sequence) < self.sequence_length:
                break
            
            # Predict next step
            sequence_tensor = torch.FloatTensor(np.array(current_sequence)).unsqueeze(0)
            
            with torch.no_grad():
                self.model.eval()
                prediction = self.model(sequence_tensor).numpy()[0]
            
            # De-normalize
            solar_pred = prediction[0] * 500.0
            wind_pred = prediction[1] * 300.0
            load_pred = prediction[2] * 1000.0
            
            forecasts.append((solar_pred, wind_pred, load_pred))
            
            # Update sequence for next prediction
            # Assume time advances by 0.1 hours
            last_time = current_sequence[-1][0]
            next_time = (last_time + 0.1 / 24.0) % 1.0
            
            # Create next observation (with predictions)
            next_obs = np.array([
                next_time,
                prediction[0],
                prediction[1],
                prediction[2],
                current_sequence[-1][4],  # Assume cloud cover stays same
                current_sequence[-1][5],  # Assume wind speed stays same
                current_sequence[-1][6]   # Assume temperature stays same
            ])
            
            # Shift sequence
            current_sequence.append(next_obs)
            current_sequence = current_sequence[-self.sequence_length:]
        
        return forecasts


class NaiveForecaster:
    """
    Baseline forecaster using simple heuristics
    For comparison with LSTM
    """
    
    def __init__(self):
        self.history = deque(maxlen=100)
    
    def update_history(self, time_of_day: float, solar: float, wind: float, load: float):
        """Add observation"""
        self.history.append({
            'time': time_of_day,
            'solar': solar,
            'wind': wind,
            'load': load
        })
    
    def predict(self) -> Tuple[float, float, float]:
        """Predict using persistence (last value)"""
        if len(self.history) == 0:
            return (0.0, 0.0, 400.0)
        
        last = self.history[-1]
        return (last['solar'], last['wind'], last['load'])
    
    def predict_moving_average(self, window: int = 5) -> Tuple[float, float, float]:
        """Predict using moving average"""
        if len(self.history) < window:
            return self.predict()
        
        recent = list(self.history)[-window:]
        
        solar_avg = np.mean([obs['solar'] for obs in recent])
        wind_avg = np.mean([obs['wind'] for obs in recent])
        load_avg = np.mean([obs['load'] for obs in recent])
        
        return (solar_avg, wind_avg, load_avg)
    
    def predict_seasonal(self, time_of_day: float) -> Tuple[float, float, float]:
        """Predict using seasonal patterns"""
        # Find similar times of day in history
        similar_times = [
            obs for obs in self.history
            if abs(obs['time'] - time_of_day) < 1.0  # Within 1 hour
        ]
        
        if len(similar_times) == 0:
            return self.predict()
        
        solar_avg = np.mean([obs['solar'] for obs in similar_times])
        wind_avg = np.mean([obs['wind'] for obs in similar_times])
        load_avg = np.mean([obs['load'] for obs in similar_times])
        
        return (solar_avg, wind_avg, load_avg)


class WeatherPredictor:
    """
    Simple weather prediction model
    Predicts cloud cover and wind speed
    """
    
    def __init__(self):
        self.cloud_history = deque(maxlen=50)
        self.wind_history = deque(maxlen=50)
    
    def update(self, cloud_cover: float, wind_speed: float):
        """Update with new observation"""
        self.cloud_history.append(cloud_cover)
        self.wind_history.append(wind_speed)
    
    def predict_cloud(self) -> float:
        """Predict next cloud cover value"""
        if len(self.cloud_history) < 2:
            return 0.3  # Default
        
        # Simple auto-regressive model
        last_value = self.cloud_history[-1]
        trend = self.cloud_history[-1] - self.cloud_history[-2]
        
        # Predict with mean reversion
        prediction = last_value + 0.3 * trend + 0.1 * (0.3 - last_value)
        
        return np.clip(prediction, 0, 1)
    
    def predict_wind(self) -> float:
        """Predict next wind speed"""
        if len(self.wind_history) < 2:
            return 10.0  # Default
        
        # Simple auto-regressive model
        last_value = self.wind_history[-1]
        trend = self.wind_history[-1] - self.wind_history[-2]
        
        # Predict with mean reversion
        prediction = last_value + 0.3 * trend + 0.1 * (10.0 - last_value)
        
        return np.clip(prediction, 0, 25)


class EnsembleForecaster:
    """
    Ensemble forecaster combining multiple methods
    """
    
    def __init__(self):
        self.lstm_forecaster = ShortTermForecaster()
        self.naive_forecaster = NaiveForecaster()
        self.weather_predictor = WeatherPredictor()
        
        # Weights for ensemble
        self.weights = {
            'lstm': 0.6,
            'naive': 0.2,
            'seasonal': 0.2
        }
    
    def update(self, time_of_day: float, solar: float, wind: float, 
               load: float, cloud_cover: float, wind_speed: float, 
               temperature: float):
        """Update all forecasters"""
        self.lstm_forecaster.update_history(
            time_of_day, solar, wind, load, 
            cloud_cover, wind_speed, temperature
        )
        self.naive_forecaster.update_history(time_of_day, solar, wind, load)
        self.weather_predictor.update(cloud_cover, wind_speed)
    
    def predict(self) -> Tuple[float, float, float]:
        """Ensemble prediction"""
        # LSTM prediction
        lstm_pred = self.lstm_forecaster.predict()
        
        # Naive prediction
        naive_pred = self.naive_forecaster.predict()
        
        # Seasonal prediction
        time = self.naive_forecaster.history[-1]['time'] if self.naive_forecaster.history else 12.0
        seasonal_pred = self.naive_forecaster.predict_seasonal(time)
        
        # Weighted average
        solar = (
            self.weights['lstm'] * lstm_pred[0] +
            self.weights['naive'] * naive_pred[0] +
            self.weights['seasonal'] * seasonal_pred[0]
        )
        
        wind = (
            self.weights['lstm'] * lstm_pred[1] +
            self.weights['naive'] * naive_pred[1] +
            self.weights['seasonal'] * seasonal_pred[1]
        )
        
        load = (
            self.weights['lstm'] * lstm_pred[2] +
            self.weights['naive'] * naive_pred[2] +
            self.weights['seasonal'] * seasonal_pred[2]
        )
        
        return (solar, wind, load)
    
    def train_lstm(self):
        """Train the LSTM component"""
        self.lstm_forecaster.train()
