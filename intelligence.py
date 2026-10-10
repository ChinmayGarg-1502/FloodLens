
from datetime import datetime, timezone


def is_outdated(reported_at, max_age_hours=48):
    """Return True if a hazard report is older than 48 hours."""

    report_time = datetime.fromisoformat(
        reported_at.replace("Z", "+00:00")
    )

    if report_time.tzinfo is None:
        report_time = report_time.replace(tzinfo=timezone.utc)

    age = datetime.now(timezone.utc) - report_time.astimezone(
        timezone.utc
    )

    return age.total_seconds() > max_age_hours * 3600


def calculate_trust_score(
    confirmations=0,
    disputes=0,
    has_photo=False
):
    """Calculate a prototype trust score from 0 to 100."""

    score = 30
    score += min(max(confirmations, 0), 5) * 8
    score -= min(max(disputes, 0), 5) * 10

    if has_photo:
        score += 10

    return max(0, min(100, score))


def classify_hazard_risk(severity, trust_score, confirmations=0):
    """Estimate hazard priority using severity and report evidence."""

    severity_points = {
        "low": 20,
        "medium": 50,
        "high": 80
    }

    severity = severity.lower()

    if severity not in severity_points:
        raise ValueError("Severity must be low, medium, or high")

    risk_score = severity_points[severity]

    if trust_score >= 70:
        risk_score += 10

    if confirmations >= 3:
        risk_score += 10

    risk_score = min(100, risk_score)

    if risk_score >= 70:
        level = "HIGH"
    elif risk_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": level
    }


def verify_report(confirmations=0, disputes=0):
    """Summarize community feedback."""

    if confirmations > disputes:
        status = "COMMUNITY_SUPPORTED"
    elif disputes > confirmations:
        status = "NEEDS_REVIEW"
    else:
        status = "UNCONFIRMED"

    return {
        "confirmations": confirmations,
        "disputes": disputes,
        "verification_status": status
    }


if __name__ == "__main__":
    now = datetime.now(timezone.utc).isoformat()

    trust = calculate_trust_score(
        confirmations=4,
        disputes=1,
        has_photo=True
    )

    print("=== FLOODLENS INTELLIGENCE TEST ===")
    print("Trust score:", trust)
    print("Report outdated:", is_outdated(now))
    print(
        "Hazard risk:",
        classify_hazard_risk("high", trust, confirmations=4)
    )
    print(
        "Community verification:",
        verify_report(confirmations=4, disputes=1)
    )

def analyze_pothole_detection(detection_result):
    """Convert AI detections into a FloodLens hazard summary."""

    if not detection_result.get("success"):
        return {
            "success": False,
            "message": "AI image detection failed."
        }

    detections = detection_result.get("detections", [])
    pothole_count = len(detections)

    if pothole_count == 0:
        severity = "low"
    elif pothole_count <= 2:
        severity = "medium"
    else:
        severity = "high"

    risk = classify_hazard_risk(
        severity=severity,
        trust_score=30,
        confirmations=0
    )

    return {
        "success": True,
        "hazard_type": "pothole",
        "potholes_detected": pothole_count,
        "severity_estimate": severity,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "message": (
            f"AI detected {pothole_count} possible pothole(s). "
            "Please verify the result."
        )
    }

