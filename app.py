from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Tnufa Extractor API is running"})

@app.route("/extract", methods=["POST"])
def extract():
    try:
        info = {
            "content_type": request.content_type,
            "content_length": request.content_length,
            "files_count": len(request.files),
            "file_keys": list(request.files.keys()),
            "data_len": len(request.data or b"")
        }

        if "file" in request.files:
            f = request.files["file"]
            content = f.read()
            info["file"] = {
                "filename": f.filename,
                "mimetype": f.mimetype,
                "size_bytes": len(content),
                "first_bytes": list(content[:8]),
            }

        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
