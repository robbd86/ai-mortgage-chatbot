from flask import Flask, request, jsonify, send_from_directory
import openai
import os

app = Flask(__name__, static_folder="../static")
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def serve_chatbot():
    return send_from_directory(app.static_folder, "chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    prompt = f"""
    You are a helpful AI assistant for a UK mortgage broker.
    Provide general guidance only. If the user asks for financial advice, include a disclaimer.

    User: {user_input}
    Assistant:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.6
    )
    reply = response.choices[0].message.content
    return jsonify({"response": reply})
