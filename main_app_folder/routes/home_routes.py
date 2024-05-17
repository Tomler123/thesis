from flask import render_template 
from main_app_folder import app
# def init_app(app):
#     @app.route('/')
#     @app.route('/home')
#     def home(): 
#         return render_template('home.html')

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')