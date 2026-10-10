
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from werkzeug.utils import secure_filename

from analyze_road import analyze_road

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the FloodLens API!",
        "status": "running"
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_image():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "Upload an image using the 'image' field."
        }), 400

    uploaded_file = request.files["image"]

    if not uploaded_file.filename:
        return jsonify({
            "success": False,
            "message": "No image was selected."
        }), 400

    extension = Path(uploaded_file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "success": False,
            "message": "Unsupported image format."
        }), 400

    safe_name = secure_filename(uploaded_file.filename)

    if not safe_name:
        return jsonify({
            "success": False,
            "message": "Invalid filename."
        }), 400

    image_path = UPLOAD_DIR / safe_name
    uploaded_file.save(image_path)

    try:
        result = analyze_road(str(image_path))

        if not result.get("ai_detection", {}).get("success"):
            return jsonify(result), 500

        output_name = Path(
            result["ai_detection"]["output_image"]
        ).name

        result["ai_detection"]["output_image"] = (
            f"/outputs/{output_name}"
        )

        result["ai_detection"]["output_image_url"] = (
            f"http://127.0.0.1:5000/outputs/{output_name}"
        )

        return jsonify(result)

    except Exception:
        app.logger.exception("Road analysis failed")
        return jsonify({
            "success": False,
            "message": "Analysis failed. Check the server terminal."
        }), 500


@app.route("/outputs/<path:filename>", methods=["GET"])
def get_output_image(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)

