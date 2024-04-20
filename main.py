from flask import Flask, request, render_template, jsonify
from openai import OpenAI

app = Flask(__name__)

api_key = "hack-with-upstage-solar-0420"  # Ensure you replace this with your valid API key
client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")

# Initialize a log to store questions, answers, and groundedness results
log = []

# Function to interact with OpenAI for asking questions
def ask_solar(context, question):
    context_str = " ".join(context)  # Convert context list to a single string
    response = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {
                "role": "user",
                "content": f"Answer the following question: {question} by using the following context: {context_str}"
            }
        ]
    )
    return response.choices[0].message.content

# Function to check groundedness
def check_groundedness(context, question, answer):
    context_str = " ".join(context)  # Convert context list to a single string
    response = client.chat.completions.create(
        model="solar-1-mini-answer-verification",
        messages=[
            {"role": "user", "content": context_str},
            {"role": "assistant", "content": f"{question} {answer}"}
        ]
    )
    return response.choices[0].message.content

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask_and_check():
    context_list = request.form.getlist("context")  # Get all context inputs
    question = request.form["question"]

    answer = ask_solar(context_list, question)
    groundedness_result = check_groundedness(context_list, question, answer)

    if not answer:
        answer = "No answer provided."
    if not groundedness_result:
        groundedness_result = "No groundedness result provided."

    log.append({
        "context": context_list,
        "question": question,
        "answer": answer,
        "groundedness_result": groundedness_result
    })

    return jsonify({
        "answer": answer,
        "groundedness_result": groundedness_result
    })

@app.route("/log", methods=["GET"])
def get_log():
    return jsonify(log)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)  # Set to True to enable debugging