
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from werkzeug.utils import secure_filename

from analyze_road import analyze_road
from database import get_db_connection
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

@app.route("/api/reports", methods=["GET"])
def get_reports():
    connection = None

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT report_id, location_name, description,
                       latitude, longitude, severity, status,
                       created_at, updated_at
                FROM flood_reports
                ORDER BY created_at DESC;
            """)

            rows = cursor.fetchall()

            columns = [column[0] for column in cursor.description]
            reports = [
                dict(zip(columns, row))
                for row in rows
            ]

        return jsonify({
            "success": True,
            "count": len(reports),
            "reports": reports
        }), 200

    except Exception:
        app.logger.exception("Failed to fetch flood reports")
        return jsonify({
            "success": False,
            "message": "Could not fetch flood reports."
        }), 500

    finally:
        if connection is not None:
            connection.close()



@app.route("/api/reports", methods=["POST"])
def create_report():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Send report details as JSON."
        }), 400

    required_fields = [
        "location_name",
        "description",
        "severity"
    ]

    missing_fields = [
        field for field in required_fields
        if not isinstance(data.get(field), str)
        or not data[field].strip()
    ]

    if missing_fields:
        return jsonify({
            "success": False,
            "message": "Required fields are missing.",
            "missing_fields": missing_fields
        }), 400

    severity = data["severity"].strip().capitalize()

    if severity not in {"Low", "Medium", "High"}:
        return jsonify({
            "success": False,
            "message": "Severity must be Low, Medium, or High."
        }), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if (latitude is None) != (longitude is None):
        return jsonify({
            "success": False,
            "message": "Latitude and longitude must be provided together."
        }), 400

    if latitude is not None:
        if isinstance(latitude, bool) or isinstance(longitude, bool):
            return jsonify({
                "success": False,
                "message": "Coordinates must be numbers."
            }), 400

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Coordinates must be numbers."
            }), 400

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return jsonify({
                "success": False,
                "message": "Coordinates are out of range."
            }), 400

    import uuid
    from datetime import datetime, timezone

    report_id = f"FL-{uuid.uuid4().hex[:12].upper()}"
    now = datetime.now(timezone.utc)
    connection = None

    try:
        connection = get_db_connection()

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO flood_reports (
                        report_id, location_name, description,
                        latitude, longitude, severity, status,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING report_id, location_name, description,
                              latitude, longitude, severity, status,
                              created_at, updated_at;
                """, (
                    report_id,
                    data["location_name"].strip(),
                    data["description"].strip(),
                    latitude,
                    longitude,
                    severity,
                    "Unverified",
                    now,
                    now
                ))

                row = cursor.fetchone()
                columns = [column[0] for column in cursor.description]
                report = dict(zip(columns, row))

        return jsonify({
            "success": True,
            "message": "Flood report saved successfully.",
            "report": report
        }), 201

    except Exception:
        app.logger.exception("Failed to save flood report")
        return jsonify({
            "success": False,
            "message": "Could not save flood report."
        }), 500

    finally:
        if connection is not None:
            connection.close()


@app.route("/api/reports/<string:report_id>", methods=["PATCH"])
def update_report_status(report_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Send the new status as JSON."
        }), 400

    status = data.get("status")

    if not isinstance(status, str):
        return jsonify({
            "success": False,
            "message": "Status is required."
        }), 400

    status = status.strip().capitalize()

    if status not in {"Unverified", "Corroborated", "Resolved"}:
        return jsonify({
            "success": False,
            "message": "Status must be Unverified, Corroborated, or Resolved."
        }), 400

    connection = None

    try:
        connection = get_db_connection()

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE flood_reports
                    SET status = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE report_id = %s
                    RETURNING report_id, location_name, status, updated_at;
                """, (status, report_id))

                row = cursor.fetchone()

                if row is None:
                    return jsonify({
                        "success": False,
                        "message": "Flood report not found."
                    }), 404

                columns = [column[0] for column in cursor.description]
                report = dict(zip(columns, row))

        return jsonify({
            "success": True,
            "message": "Report status updated successfully.",
            "report": report
        }), 200

    except Exception:
        app.logger.exception("Failed to update report status")
        return jsonify({
            "success": False,
            "message": "Could not update report status."
        }), 500

    finally:
        if connection is not None:
            connection.close()

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

