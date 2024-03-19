import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import yfinance as yf
import sys

def main(stock):
    # Define the stock symbol and time range
    start_date = '2023-01-01'
    end_date = '2024-01-01'

    # Fetch stock data
    stock_data = fetch_stock_data(stock, start_date, end_date)

    # Extend the end date by 10 days for predictions
    extended_end_date = pd.to_datetime(end_date) + pd.Timedelta(days=10)

    # Define hyperparameters and sequence length
    seq_length = 30
    epochs = 100
    batch_size = 64

    # Preprocess the data   
    prices = stock_data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    # Create sequences and labels
    X, y = create_sequences(scaled_prices, seq_length)

    # Split the data into training and testing sets
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Build the LSTM model
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(seq_length, 1)),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=1)
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test))

    # Predictions
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    y_test = scaler.inverse_transform(y_test)

    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    # plt.savefig('loss_plot.png')  # Save the plot as an image
    plt.savefig('static/images/loss_plot.png')  # Save the plot as an image
    plt.close()

    # Predictions
    plt.plot(y_test, label='Actual Prices')
    plt.plot(predictions, label='Predicted Prices')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    # plt.savefig('predictions_plot.png')  # Save the plot as an image
    plt.savefig('static/images/predictions_plot.png') # save to images folder
    plt.close()

    # Predict beyond the end date by 10 days
    last_sequence = scaled_prices[-seq_length:]
    extended_predictions = []
    for _ in range(10):
        prediction = model.predict(last_sequence.reshape(1, seq_length, 1))
        extended_predictions.append(prediction[0, 0])
        last_sequence = np.append(last_sequence[1:], prediction, axis=0)

    # Inverse transform the predicted prices
    extended_predictions = scaler.inverse_transform(np.array(extended_predictions).reshape(-1, 1))

    # Plot the extended predictions
    plt.plot(extended_predictions, label='Extended Predictions')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.savefig('static/images/extended_predictions_plot.png') # save to images folder
    # plt.savefig('extended_predictions_plot.png')  # Save the plot as an image
    plt.close()


# Define function to create input sequences and labels
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

# Function to fetch stock data from Yahoo Finance
def fetch_stock_data(symbol, start_date, end_date):
    stock = yf.download(symbol, start=start_date, end=end_date)
    return stock

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        main(sys.argv[1])
