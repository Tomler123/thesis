from flask import Blueprint, jsonify, redirect, request, render_template, url_for, session
from main_app_folder.models.outcomes import Outcome
from main_app_folder.utils import helpers
from main_app_folder.extensions import db
import json

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
def calendar():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    outcomes = Outcome.query.filter_by(UserID=user_id).all()
    all_dates = [outcome.Day for outcome in outcomes]
    return render_template('calendar.html', all_dates=json.dumps(all_dates))

@calendar_bp.route('/get_outcomes', methods=['POST'])
def get_outcomes():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    day_clicked = request.json.get('day')
    outcomes = Outcome.query.filter_by(UserID=user_id, Day=day_clicked).all()
    outcomes_data = [
        {"id": outcome.ID, "name": outcome.Name, "amount": outcome.Cost, "fulfilled": outcome.Fulfilled}
        for outcome in outcomes
    ]
    return jsonify(outcomes_data)

@calendar_bp.route('/update_outcome_status', methods=['POST'])
def update_outcome_status():
    data = request.get_json()
    out_id = data['out_id']
    status = data['status']
    try:
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE outcomes
            SET Fulfilled = ?
            WHERE ID = ?
            """, (status, out_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({'success': True, 'message': 'Status updated'})

@calendar_bp.route('/get_outcomes_status_by_day', methods=['POST'])
def get_outcomes_status_by_day():
    user_id = session.get('user_id')
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


@calendar_bp.route('/reset_finances', methods=['POST'])
def reset_finances():
    user_id = session.get('user_id')
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
