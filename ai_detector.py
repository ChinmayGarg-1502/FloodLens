from pathlib import Path
from ultralytics import YOLO

MODEL_URL = (
    "https://huggingface.co/peterhdd/"
    "pothole-detection-yolov8/resolve/main/best.pt"
)

# Load the model only once and reuse it.
_model = None


def get_model():
    global _model

    if _model is None:
        _model = YOLO(MODEL_URL)

    return _model


def detect_potholes(image_path, confidence=0.35):
    image = Path(image_path)

    if not image.is_file():
        return {
            "success": False,
            "message": f"Image not found: {image}"
        }

    if image.suffix.lower() not in {
        ".jpg", ".jpeg", ".png", ".webp"
    }:
        return {
            "success": False,
            "message": "Unsupported image format."
        }

    model = get_model()

    results = model.predict(
        source=str(image),
        conf=confidence,
        iou=0.4,
        verbose=False,
    )

    result = results[0]
    detections = []

    for box in result.boxes:
        class_id = int(box.cls[0].item())

        detections.append({
            "label": (
                "pothole"
                if class_id == 0
                else result.names[class_id]
            ),
            "confidence": round(
                float(box.conf[0].item()), 3
            ),
            "box": [
                round(float(value), 1)
                for value in box.xyxy[0].tolist()
            ]
        })

    output_image = image.with_name(
        image.stem + "_detected" + image.suffix
    )

    result.save(filename=str(output_image))

    return {
        "success": True,
        "potholes_found": len(detections),
        "detections": detections,
        "output_image": str(output_image)
    }


if __name__ == "__main__":
    print("=== FLOODLENS AI DETECTOR ===")
    print(detect_potholes("road.jpg"))
