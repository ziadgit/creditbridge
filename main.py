from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from openai import OpenAI
import datetime

app = Flask(__name__)

# MongoDB configuration
mongo_client = MongoClient("mongodb+srv://pk:tapnPo7N8EwS8xQL@serverlessinstance0.g44mumz.mongodb.net/")  # Insert your MongoDB URI
db = mongo_client["solar_app"]  # Database name
answers_collection = db["answers"]  # Collection to store answers

# Ensure text index is created once
def ensure_text_index():
    index_info = answers_collection.index_information()  # Retrieve existing indexes
    has_text_index = False

    for idx in index_info.values():
        if "key" in idx:
            # Check if any index has a text type
            if isinstance(idx["key"], list) and any("text" in key for key, _ in idx["key"]):
                has_text_index = True
                break

    if not has_text_index:  # Create text index if not found
        answers_collection.create_index([("answer", "text")])

ensure_text_index()  # Ensure indexes are created when the app starts

# OpenAI configuration
api_key = "hack-with-upstage-solar-0420"  # Insert your OpenAI API key
client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")

# Function to interact with OpenAI for asking questions
# Function to interact with OpenAI for asking questions
def ask_solar(context, question):
    context_str = " ".join(context)
    response = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {
                "role": "user",
                "content": f"Answer the following question: {question} using this context: {context_str}"
            }
        ]
    )
    return response.choices[0].message.content

# Function to check groundedness
def check_groundedness(context, question, answer):
    context_str = " ".join(context)
    response = client.chat.completions.create(
        model="solar-1-mini-answer-verification",
        messages=[
            {"role": "user", "content": context_str},
            {"role": "assistant", "content": f"{question} {answer}"}
        ]
    )
    return response.choices[0].message.content

# Main page to ask questions
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Endpoint to ask questions and check groundedness
@app.route("/ask", methods=["POST"])
def ask_and_check():
    context_list = request.form.getlist("context")
    question = request.form["question"]

    answer = ask_solar(context_list, question)
    groundedness_result = check_groundedness(context_list, question, answer)

    # Save to MongoDB
    answer_record = {
        "context": context_list,
        "question": question,
        "answer": answer,
        "groundedness_result": groundedness_result,
        "timestamp": datetime.datetime.now()
    }
    answers_collection.insert_one(answer_record)

    return jsonify({
        "answer": answer,
        "groundedness_result": groundedness_result
    })

# Endpoint to get a log of responses stored in MongoDB
@app.route("/log", methods=["GET"])
def get_log():
    results = list(answers_collection.find())
    for result in results:
        result["_id"] = str(result["_id"])  # Convert ObjectId to string
    return jsonify(results)

# Endpoint to render the search page
@app.route("/search_view", methods=["GET"])
def search_view():
    return render_template("atlas.html")

# Endpoint to search for answers in MongoDB
@app.route("/search", methods=["GET"])
def search_answers():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "No search query provided."}), 400

    # Search for answers in MongoDB
    results = answers_collection.find({"$text": {"$search": query}}).sort("score", -1)

    response_data = []
    for result in results:
        result["_id"] = str(result["_id"])  # Convert ObjectId to string
        response_data.append({
            "question": result.get("question"),
            "answer": result.get("answer"),
            "groundedness_result": result.get("groundedness_result"),
            "timestamp": result.get("timestamp")
        })

    return jsonify(response_data)  # Always return response data, even if empty

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)