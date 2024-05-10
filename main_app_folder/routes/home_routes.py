from flask import render_template 

def init_app(app):
    @app.route('/')
    @app.route('/home')
    def home(): 
        return render_template('home.html')