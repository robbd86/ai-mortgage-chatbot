from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Check if OpenAI API key is available
api_key = os.getenv("OPENAI_API_KEY")
use_openai = False

if api_key is not None and api_key != "your_openai_api_key_here":
    try:
        # Initialize OpenAI client if API key is available
        client = OpenAI(api_key=api_key)
        use_openai = True
        print("OpenAI API key loaded successfully.")
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}")
        client = None
else:
    print("WARNING: No valid OpenAI API key found. Using fallback responses.")
    client = None

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('static', 'chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Define fallback responses with mortgage disclaimer
    mortgage_responses = [
        "Based on typical mortgage scenarios, your question about mortgages would be answered by considering factors like interest rates, loan terms, and credit scores. DISCLAIMER: This information is for educational purposes only. Please consult with a qualified mortgage advisor for personalized advice based on your specific situation.",
        "Mortgage professionals would typically analyze your financial situation including income, debt, and credit history when addressing this question. DISCLAIMER: This information is for educational purposes only. Please consult with a qualified mortgage advisor for personalized advice based on your specific situation.",
        "Understanding mortgage options involves considering fixed vs. adjustable rates, term length, and down payment requirements. Your specific situation would need personalized evaluation. DISCLAIMER: This information is for educational purposes only. Please consult with a qualified mortgage advisor for personalized advice based on your specific situation.",
        "Mortgage affordability typically depends on your debt-to-income ratio, credit score, and available down payment. DISCLAIMER: This information is for educational purposes only. Please consult with a qualified mortgage advisor for personalized advice based on your specific situation.",
        "When considering mortgage applications, lenders typically review credit history, employment stability, and existing debt obligations. DISCLAIMER: This information is for educational purposes only. Please consult with a qualified mortgage advisor for personalized advice based on your specific situation."
    ]
    
    # Process the message based on API key availability
    if use_openai and client is not None:
        try:
            # Add disclaimer to the prompt
            system_message = """You are a helpful mortgage chatbot assistant. 
            Provide informative responses about mortgage topics and always include a disclaimer in your response: 
            "DISCLAIMER: This information is for educational purposes only. 
            Please consult with a qualified mortgage advisor for personalized advice based on your specific situation."
            Keep your responses concise and professional."""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500
            )
            
            bot_response = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            bot_response = random.choice(mortgage_responses)
    else:
        # Use fallback responses if no API key is available
        bot_response = random.choice(mortgage_responses)
    
    # Log the conversation
    log_conversation(user_message, bot_response)
    
    return jsonify({"response": bot_response})

def log_conversation(user_message, bot_response):
    """Log conversation to a file for future training or analysis"""
    log_entry = {
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": str(datetime.now())
    }
    
    try:
        with open("conversation_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Error logging conversation: {e}")

if __name__ == '__main__':
    # Create log file directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Start the Flask application
    print("Starting AI Chatbot. Access it at http://127.0.0.1:5000")
    app.run(debug=True)
