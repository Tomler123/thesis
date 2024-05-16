from flask import jsonify, redirect, request, render_template, url_for, session, session
from main_app_folder.utils import helpers
import json

def init_app(app):
    @app.route('/calendar')
    def calendar():
        # Assuming you have the user_id from the session
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        
        # Connect to the database
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        
        # Fetch both outcome and expense dates
        cursor.execute("""
            SELECT Day AS date FROM outcomes WHERE UserID=?
        """, (user_id))
        
        # Fetch all dates from the cursor
        all_dates = [row.date for row in cursor.fetchall()]
        
        # Close the connection
        cursor.close()
        conn.close()

        # Render the calendar template and pass the dates
        return render_template('calendar.html', all_dates=json.dumps(all_dates))

    @app.route('/get_outcomes', methods=['POST'])
    def get_outcomes():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        day_clicked = request.json.get('day')
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ID, Name, Cost, Fulfilled
            FROM outcomes
            WHERE UserID = ? AND Day = ?
        """, (user_id, day_clicked))

        outcomes = [
            {"id": row.ID, "name": row.Name, "amount": row.Cost, "fulfilled": bool(row.Fulfilled)}
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        return jsonify(outcomes)

    @app.route('/update_outcome_status', methods=['POST'])
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

    @app.route('/get_outcomes_status_by_day', methods=['POST'])
    def get_outcomes_status_by_day():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Day, 
                CAST(CASE WHEN COUNT(Fulfilled) = SUM(CAST(Fulfilled AS INT)) THEN 1 ELSE 0 END AS BIT) AS AllFulfilled
            FROM outcomes
            WHERE UserID = ?
            GROUP BY Day
        """, (user_id,))

        day_fulfillment_status = {str(row.Day): row.AllFulfilled for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()

        return jsonify(day_fulfillment_status)

    @app.route('/reset_finances', methods=['POST'])
    def reset_finances():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        try:
            conn = helpers.get_db_connection()
            cursor = conn.cursor()

            # Update the `Fulfilled` status for "Subscription" and "Expense"
            cursor.execute("""
                UPDATE outcomes
                SET Fulfilled = 0
                WHERE UserID = ? AND Type IN ('Subscription', 'Expense', 'Income')
                """, (user_id,))

            conn.commit()
            return jsonify({'success': True, 'message': 'All subscriptions and expenses have been reset.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()