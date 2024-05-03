REM @echo off
REM REM Set up virtual environment for Flask and install dependencies
REM python -m venv venv
REM call venv\Scripts\activate
REM 
REM REM Install TensorFlow and other dependencies
REM pip install --upgrade pip
REM REM rempip install tensorflow -force
REM pip install flask matplotlib flask_sqlalchemy pyodbc flask_wtf wtforms flask_mail numpy pandas yfinance -force
REM REM pip install scikit-learn -force
REM pip install email_validator -force
REM 
REM 
REM REM Inform the user that Flask dependencies are installed
REM echo Flask dependencies installation complete.
REM 
REM REM Start Flask app in a new command window
REM start "Flask App" cmd /k "cd C:\Users\nikol\Desktop\Thesis_Uni\thesis && call venv\Scripts\activate && echo Starting Flask app... && python app.py"
REM 
REM REM Go into the chatbot production setup directory and setup Rasa
REM cd ..
REM cd chatbot_prod
REM call setupRasa.bat
REM 
REM REM Start Rasa server in a new command window from the prod directory where it's set up
REM start "Rasa Server" cmd /k "cd C:\Users\nikol\Desktop\Thesis_Uni\chatbot_prod\prod && call venv\Scripts\activate && echo Starting Rasa server... && rasa run --enable-api --cors '*' --debug"
REM 
REM echo Setup complete. Flask and Rasa are running.