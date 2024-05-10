
# import queue
# import threading

# from flask import render_template
# from main_app_folder.ai_algorithms import stock_algo
# from main_app_folder.forms import forms

# def init_app(app):
#     @app.route('/stock_prediction', methods=['GET', 'POST'])
#     def stock_prediction():
#         # Create an instance of the form class
#         form = forms.StockPredictionForm()

#         if form.validate_on_submit():
#             # Get the stock name from the form
#             stock_name = form.stock_name.data
#             result_queue = queue.Queue()
#             # Call the main function from algo.py with stock_name
#             t =threading.Thread(target=stock_algo.main, args=(stock_name, result_queue))
#             t.start()
#             t.join()
#             # Construct paths to the images
#             loss_plot_base64, predictions_plot_base64, extended_predictions_plot_base64 = result_queue.get() if not result_queue.empty() else (None, None, None)
            
#             # Render the template with the paths to the generated images
#             return render_template('stock_prediction.html',
#                                 stock_name=stock_name,
#                                 loss_plot_base64=loss_plot_base64,
#                                 predictions_plot_base64=predictions_plot_base64,
#                                 extended_predictions_plot_base64=extended_predictions_plot_base64,
#                                 form=form)
        
#         # If it's a GET request or the form is not valid, render the form
#         return render_template('stock_prediction.html', form=form)
