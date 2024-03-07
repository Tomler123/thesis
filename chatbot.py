import asyncio
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity

app = Flask(__name__)

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about adapters.
SETTINGS = BotFrameworkAdapterSettings("", "")
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Catch-all for messages
@app.route("/api/messages", methods=["POST"])
def messages():
    # Main bot message handler.
    if "application/json" in request.headers["Content-Type"]:
        request_body = request.json
    else:
        return jsonify({"error": "Only application/json content type is supported"}), 415

    activity = Activity().deserialize(request_body)

    async def turn_call_back(turn_context: TurnContext):
        # Echo back to the user whatever they typed.
        await turn_context.send_activity(Activity(type=Activity.type_message, text=f"Echo: {turn_context.activity.text}"))

    task = asyncio.ensure_future(ADAPTER.process_activity(activity, "", turn_call_back))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)

    return "Message processed"

if __name__ == '__main__':
    app.run(debug=True, port=3978)
