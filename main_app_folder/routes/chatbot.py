from flask import jsonify, request
import yaml
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import spacy

def init_app(app):
    spacy.load('en_core_web_sm')
    chatbot = ChatBot(
        'WebsiteNavigationBot',
        logic_adapters=[
            {
                'import_path': 'chatterbot.logic.BestMatch',
                'default_response': 'I am not sure how to respond to that.',
                'maximum_similarity_threshold': 0.90
            }
        ],
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
    )
    with open("./data/website_navigation.yml", 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Train the chatbot with the loaded conversations
    trainer = ListTrainer(chatbot)
    for conversation in data['conversations']:
        trainer.train(conversation)
    @app.route("/get_response", methods=['POST'])
    def get_response():
        # logging.debug("Received POST to /get_response")
        data = request.get_json()
        # logging.debug(f"Data received from frontend: {data}")

        if not data or 'message' not in data:
            # logging.error("No message found in received data")
            return jsonify({'error': 'Bad Request, message missing in JSON'}), 400

        user_message = data['message']
        # logging.debug(f"Received user message: {user_message}")
        response = chatbot.get_response(user_message)
        # logging.debug(f"Chatbot response: {response.text}")

        return jsonify({'message': str(response)})