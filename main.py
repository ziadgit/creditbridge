# Import necessary packages
from flask import Flask, request, render_template, jsonify
from openai import OpenAI

# Set up Flask app
app = Flask(__name__)

# Create OpenAI client
api_key = "hack-with-upstage-solar-0420"  # Ensure this is a valid API key
client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")

# Initialize a log to store questions, answers, and groundedness results
log = []

# Define a function to interact with the OpenAI API for asking questions
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

# Define a function to check groundedness
def check_groundedness(context, question, answer):
    response = client.chat.completions.create(
        model="solar-1-mini-answer-verification",
        messages=[
            {"role": "user", "content": context},
            {"role": "assistant", "content": f"{question} {answer}"}
        ]
    )
    return response.choices[0].message.content


# Route for the main page with a simple form
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Route to handle form submissions for asking questions and checking groundedness simultaneously
@app.route("/ask", methods=["POST"])
def ask_and_check():
    context = request.form["context"]
    question = request.form["question"]

    # Get the answer from OpenAI
    answer = ask_solar(context, question)

    # Check for groundedness
    groundedness_result = check_groundedness(context, question, answer)

    # Append the question, answer, and groundedness result to the log
    log.append({
        "context": context,
        "question": question,
        "answer": answer,
        "groundedness_result": groundedness_result
    })

    # Return both the answer and the groundedness result
    return jsonify({"answer": answer, "groundedness_result": groundedness_result})


# Route to retrieve the log of responses
@app.route("/log", methods=["GET"])
def get_log():
    return jsonify(log)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
