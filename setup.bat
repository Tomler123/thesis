@echo off
REM Set up virtual environment for Flask and install dependencies
python -m venv venv
call venv\Scripts\activate

REM Install TensorFlow and other dependencies
pip install --upgrade pip
REM rempip install tensorflow -force
pip install flask matplotlib flask_sqlalchemy pyodbc flask_wtf wtforms flask_mail numpy pandas yfinance -force
REM pip install scikit-learn -force
pip install email_validator -force


REM Inform the user that Flask dependencies are installed
echo Flask dependencies installation complete.

REM Start Flask app in a new command window
start "Flask App" cmd /k "cd C:\Users\nikol\Desktop\Thesis_Uni\thesis && call venv\Scripts\activate && echo Starting Flask app... && python app.py"

REM Go into the chatbot production setup directory and setup Rasa
cd ..
cd chatbot_prod
call setupRasa.bat

REM Start Rasa server in a new command window from the prod directory where it's set up
start "Rasa Server" cmd /k "cd C:\Users\nikol\Desktop\Thesis_Uni\chatbot_prod\prod && call venv\Scripts\activate && echo Starting Rasa server... && rasa run --enable-api --cors '*' --debug"

echo Setup complete. Flask and Rasa are running.