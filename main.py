from flask import Flask, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS


import sys
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


load_dotenv()
app = Flask(__name__)
application = app
CORS(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the generative model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction=(
        "You are AIKO, a friendly and intelligent AI capable of answering all questions accurately. Your responses are always based on verifiable facts, providing clear and reliable information to anyone who asks. Deliver answers in the following format: Use concise and clear paragraphs. Include headings or bullet points where necessary, without excessive spacing between points. Avoid unnecessary blank lines between paragraphs and bullet points. Ensure the text is easy to read and neatly formatted. You can adjust the language based on the question asked." 
    ),
)

# Initialize chat session
chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": ["hi\n"]},
        {
            "role": "model",
            "parts": [
                "Halo! ? 😊\n",
            ],
        },
    ]
)

def save_chat_history(user_input, bot_response):
    with open("chat_history.txt", "a", encoding="utf-8") as file:
        file.write(f"User: {user_input}\n")
        file.write(f"Bot: {bot_response}\n")
        file.write("-" * 20 + "\n")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get("message", "")
        if not user_input:
            return jsonify({"error": "Message field is required"}), 400

        # Send user input to chatbot
        response = chat_session.send_message(user_input)

        # Get plain text response
        response_text = response.text

        # Save chat history to file with UTF-8 encoding
        save_chat_history(user_input, response_text)

        # Return response
        return jsonify({"response": response_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
