from flask import Blueprint, jsonify, redirect, request, render_template, url_for, session
import json

from main_app_folder.models.outcomes import Outcome
from main_app_folder.extensions import db

# creating blueprint
calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
def calendar():
    user_id = session.get('user_id')
    # check if the user is logged in
    if not user_id:
        return redirect(url_for('auth.login'))
    
    outcomes = Outcome.query.filter_by(UserID=user_id).all()
    all_dates = [outcome.Day for outcome in outcomes]
    
    return render_template('calendar.html', all_dates=json.dumps(all_dates))

# this function gets all the finances from the table for the user
@calendar_bp.route('/get_outcomes', methods=['POST'])
def get_outcomes():
    user_id = session.get('user_id')
    # check if the user is logged in
    if not user_id:
        return redirect(url_for('auth.login'))

    day_clicked = request.json.get('day')
    outcomes = Outcome.query.filter_by(UserID=user_id, Day=day_clicked).all()
    outcomes_data = [
        {"id": outcome.ID, "name": outcome.Name, "amount": outcome.Cost, "fulfilled": outcome.Fulfilled}
        for outcome in outcomes
    ]
    
    return jsonify(outcomes_data)

# this function is used to toggle finance fulfillment status
@calendar_bp.route('/update_outcome_status', methods=['POST'])
def update_outcome_status():
    user_id = session.get('user_id')
    # check if the user is logged in
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    out_id = data['out_id']
    status = data['status']

    try:
        outcome = Outcome.query.filter_by(ID=out_id, UserID=user_id).first()
        if outcome:
            outcome.Fulfilled = status
            db.session.commit()
            return jsonify({'success': True, 'message': 'Status updated'})
        else:
            return jsonify({'success': False, 'message': 'Outcome not found'}), 404
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# this function gets fulfillment status of each finance
@calendar_bp.route('/get_outcomes_status_by_day', methods=['POST'])
def get_outcomes_status_by_day():
    user_id = session.get('user_id')
    # check if the user is logged in
    if not user_id:
        return redirect(url_for('auth.login'))
    
    outcomes = Outcome.query.filter_by(UserID=user_id).all()
    day_fulfillment_status = {}
    
    for outcome in outcomes:
        day = str(outcome.Day)
        
        if day not in day_fulfillment_status:
            day_fulfillment_status[day] = True
        
        if not outcome.Fulfilled:
            day_fulfillment_status[day] = False
    
    return jsonify(day_fulfillment_status)

# this function is to reset finance status
@calendar_bp.route('/reset_finances', methods=['POST'])
def reset_finances():
    user_id = session.get('user_id')
    # check if the user is logged in
    if not user_id:
        return redirect(url_for('auth.login'))
    try:
        outcomes = Outcome.query.filter(Outcome.UserID == user_id, Outcome.Type.in_(['Subscription', 'Expense', 'Income'])).all()
        for outcome in outcomes:
            outcome.Fulfilled = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'All subscriptions and expenses have been reset.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
