import matplotlib
matplotlib.use('Agg')

from datetime import datetime, timedelta
import sys
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def normalize(data):
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    return (data - mean) / std

def train_test_split(data, target, test_size=0.2):
    split = int(data.shape[0] * (1 - test_size))
    return data[:split], data[split:], target[:split], target[split:]

def euclidean_distance(a, b):
    return np.sqrt(np.sum((a - b) ** 2))

def knn_predict(X_train, y_train, X_test, k=5):
    predictions = []
    for test_point in X_test:

        distances = np.array([euclidean_distance(test_point, train_point) for train_point in X_train])

        nearest_indices = distances.argsort()[:k]
        nearest_targets = y_train[nearest_indices]

        prediction = np.mean(nearest_targets)
        predictions.append(prediction)
    return np.array(predictions)


def mean_squared_error(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)


def predict_future_prices(X_train, y_train, last_known_point, days, k=5):
    future_predictions = []
    current_point = last_known_point
    for _ in range(days):
        distances = np.array([euclidean_distance(current_point, train_point) for train_point in X_train])
        nearest_indices = distances.argsort()[:k]
        nearest_targets = y_train[nearest_indices]
        next_prediction = np.mean(nearest_targets)
        future_predictions.append(next_prediction)

        current_point = np.concatenate([current_point[1:], [next_prediction]])

    return np.array(future_predictions)

def main(stock):

    data = yf.download(stock, start=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), end=datetime.now().strftime('%Y-%m-%d'))

    if data.empty:
        raise ValueError("No data found for the given stock ticker.")


    data['Date'] = data.index
    data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    data = data.dropna()


    features = data[['Open', 'High', 'Low', 'Volume']].values
    target = data['Close'].values
    features_normalized = normalize(features)
    X_train, X_test, y_train, y_test = train_test_split(features_normalized, target)

    k = 5
    predictions = knn_predict(X_train, y_train, X_test, k)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)

    last_known_features = features_normalized[-1]
    future_days = 10
    future_predictions = predict_future_prices(X_train, y_train, last_known_features, future_days, k)
    

    future_dates = pd.date_range(start=data['Date'].iloc[-1] + pd.Timedelta(days=1), periods=future_days)


    plt.figure(figsize=(14, 7))
    plt.plot(data.index[len(X_train):], y_test, label='Actual Prices', color='b')
    plt.plot(data.index[len(X_train):], predictions, label='Predicted Prices', color='r', linestyle='--')
    plt.plot(future_dates, future_predictions, label='Future Predictions', color='g', linestyle='--')
    plt.title('Stock Price Prediction using k-NN')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.savefig('main_app_folder/static/images/stock_prediction.png')
    plt.close()

    return future_predictions[-1]

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        main(sys.argv[1])
