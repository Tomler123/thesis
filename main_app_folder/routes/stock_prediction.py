from flask import Blueprint, render_template, request, redirect, session, url_for, flash, get_flashed_messages
from main_app_folder.ai_algorithms.stock_algo import main as stock_algo_main
from main_app_folder.forms.forms import StockPredictionForm
import yfinance as yf

stock_prediction_bp = Blueprint('stock_prediction', __name__)

@stock_prediction_bp.route('/stock_prediction', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        flash('Please log in to view your loans.')
        return redirect(url_for('auth.login'))
    form = StockPredictionForm()
    if form.validate_on_submit():
        stock = form.stock_name.data
        try:
            final_prediction = stock_algo_main(stock)
            last_close_price = yf.Ticker(stock).history(period="1d")['Close'].iloc[-1]
            prediction_text = "The prediction indicates that the stock price will increase ↑ in the future." if final_prediction > last_close_price else "The prediction indicates that the stock price will decrease ↓ in the future."
            return render_template('stock_prediction.html', form=form, graph=True, prediction_text=prediction_text)
        except ValueError as e:
            flash(str(e), 'stock_prediction_error')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'stock_prediction_error')
    return render_template('stock_prediction.html', form=form, graph=False)
