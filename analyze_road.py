
from pathlib import Path

from ai_detector import detect_potholes
from intelligence import analyze_pothole_detection


def analyze_road(image_path):
    """Run AI detection and generate a FloodLens hazard summary."""

    image = Path(image_path)

    if not image.is_file():
        return {
            "success": False,
            "message": f"Image not found: {image_path}"
        }

    # Step 1: Detect possible potholes in the image.
    detection_result = detect_potholes(str(image))

    # Step 2: Evaluate the detection using FloodLens intelligence.
    hazard_summary = analyze_pothole_detection(detection_result)

    # Step 3: Return one combined result.
    return {
        "image": image.name,
        "ai_detection": detection_result,
        "hazard_summary": hazard_summary
    }


if __name__ == "__main__":
    result = analyze_road("road.jpg")
    print("=== FLOODLENS ROAD ANALYSIS ===")
    print(result)
