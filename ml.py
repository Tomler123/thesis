import yfinance as yf
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Function to fetch historical stock price data
def fetch_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data

# Function to preprocess stock data
def preprocess_data(stock_data):
    # Calculate daily returns
    stock_data['Return'] = stock_data['Adj Close'].pct_change()
    
    # Label data: 1 if the stock gained 20% in the next 60 days, 0 otherwise
    stock_data['Target'] = np.where(stock_data['Adj Close'].shift(-60) / stock_data['Adj Close'] >= 1.1, 1, 0)
    
    # Drop NaN values and unnecessary columns
    stock_data.dropna(inplace=True)
    
    return stock_data


def log_reg(ticker):

    start_date = '2023-01-01'
    end_date = '2024-01-01'
    stock_data = fetch_stock_data(ticker, start_date, end_date)

# Preprocess the data
    stock_data = preprocess_data(stock_data)

# Split data into features (X) and target variable (y)
    X = stock_data[['Return']].values.reshape(-1, 1)
    y = stock_data['Target'].values

# Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

# Train logistic regression model
    model = LogisticRegression()
    model.fit(X_train_scaled, y_train)

# Predict probabilities
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

# Set threshold for classification
    threshold = 0.5
    y_pred = (y_pred_proba > threshold).astype(int)

# Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

# Plot the logistic regression curve
    plt.figure(figsize=(10, 6))

# Plot data points
    plt.scatter(X_test_scaled, y_test, color='blue', label='Actual')

# Plot logistic regression curve
    X_range = np.linspace(X_test_scaled.min(), X_test_scaled.max(), 100)
    probabilities = model.predict_proba(X_range.reshape(-1, 1))[:, 1]
    plt.plot(X_range, probabilities, color='red', label='Logistic Regression Curve')

    plt.xlabel('Daily Return')
    plt.ylabel('Probability')
    plt.title(f'Logistic Regression for {ticker}')
    plt.legend()
    plt.show()

if __name__=="__main__":
    if(len(sys.argv) == 2):
        log_reg(sys.argv[1])

