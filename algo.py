# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance as yf
import sys
import subprocess
def main(stock,type):




    # Download data from Yahoo Finance

    
   
    yf.pdr_override()
    stock_symbol = stock

    if type=='long' :
        #Dates for long term investment
        start_date = '2023-01-01'
        end_date = '2024-01-01'
    else:
        #Dates for short term investment
        start_date = '2024-01-01'
        end_date = '2024-01-22' 
  
    df = pdr.get_data_yahoo(stock_symbol, start=start_date, end=end_date)

    

    # Define inputs and columns
    df['Date'] = pd.to_datetime(df.index)
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day

    target_column = 'Close'
    features = ['Year', 'Month', 'Day']

    # Split the data into training and testing sets
    train_size = int(len(df) * 0.8)
    train_data, test_data = df[:train_size], df[train_size:]

    X_train, y_train = train_data[features], train_data[target_column]
    X_test, y_test = test_data[features], test_data[target_column]

    # Train a Linear Regression model
    model = LinearRegression()
    model.fit(X_train, y_train)


#     command = [
#     'python3 ',
#     './ml.py ',
#     X_train,
#     ' ',
#     y_train
#     ]
#   #  print(X_train)
#    # print(y_train[:,1])
#     str1=""
#     str1=str1.join(command)
    #predictions2=subprocess.getoutput(str1)
    #print(predictions2)

    # Make predictions on the test set
    predictions = model.predict(X_test)
    
    print(predictions)

    # Evaluate the model
    mse = mean_squared_error(y_test, predictions)
    print(f'Mean Squared Error: {mse}')

    # Plot the results
    plt.figure(figsize=(12, 6))
    plt.plot(test_data['Date'], y_test, label='Actual Prices')
    plt.plot(test_data['Date'], predictions, label='Predicted Prices')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title('Stock Price Prediction')
    plt.legend()
    plt.show()


if __name__=="__main__":
    if(len(sys.argv)==3):
        main(sys.argv[1],sys.argv[2])
