# Import necessary packages
from flask import Flask, request, render_template, jsonify
from openai import OpenAI

# Set up Flask app
app = Flask(__name__)

# Create OpenAI client
api_key = "hack-with-upstage-solar-0420"  # Ensure this is a valid API key
client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")

# Define a function to interact with the OpenAI API
def ask_solar(context, question):
    response = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {
                "role": "user",
                "content": f"Answer the following question: {question} by using the following context: {context}"
            }
        ]
    )
    return response.choices[0].message.content


# Route for the main page with a simple form
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Route to handle form submissions
@app.route("/ask", methods=["POST"])
def ask():
    context = request.form["context"]
    question = request.form["question"]
    answer = ask_solar(context, question)
    return jsonify({"answer": answer})


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
