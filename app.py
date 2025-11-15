from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Tnufa Extractor API v2"})

@app.route("/extract", methods=["POST"])
def extract():
    return jsonify({"status": "always_ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
