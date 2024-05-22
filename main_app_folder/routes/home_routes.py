from flask import Blueprint, redirect, render_template, url_for

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def root():
    return redirect(url_for('home.home'))

@home_bp.route('/home')
def home():
    return render_template('home.html')
