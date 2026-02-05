import numpy as np
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# ===== ANOMALY DETECTION =====
def health_score(row):
    score = row["reef_health_baseline"] - (row["sst"] * 1.5 + row["dhw"] * 5)
    return max(score, 0)

def detect_anomaly(series):
    model = IsolationForest(contamination=0.1)
    preds = model.fit_predict(series.values.reshape(-1, 1))
    return preds[-1] == -1

# ===== LSTM FORECASTING =====
def build_lstm(input_shape=(30, 1)):
    """
    Build LSTM model for time-series forecasting (SST, pH)
    """
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        LSTM(32),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    return model

def create_sequences(series, window=30):
    """
    Create sequences for LSTM training
    """
    X, y = [], []
    for i in range(len(series) - window):
        X.append(series[i:i+window])
        y.append(series[i+window])
    return np.array(X), np.array(y)

def train_lstm(series, window=30, epochs=10, batch_size=16):
    """
    Train LSTM model on time-series data
    """
    X, y = create_sequences(series, window=window)
    model = build_lstm(input_shape=(window, 1))
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
    return model

def forecast_lstm(model, last_n_values, steps_ahead=7):
    """
    Forecast future values using trained LSTM
    """
    forecasts = []
    current_sequence = last_n_values[-30:].reshape(1, 30, 1)
    
    for _ in range(steps_ahead):
        pred = model.predict(current_sequence, verbose=0)
        forecasts.append(pred[0, 0])
        current_sequence = np.append(current_sequence[:, 1:, :], [[[pred[0, 0]]]], axis=1)
    
    return np.array(forecasts)
