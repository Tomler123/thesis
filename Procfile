web: gunicorn app:app --log-file -
worker: gunicorn -b 0.0.0.0:8080 rasa_core.run -c chatbot_prod/prod/config.yml --enable-api --cors '*' --debug