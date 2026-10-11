FloodLens Database

Database choice

Amazon DynamoDB for the deployed application.

Table

"FloodReports"

Primary key

"reportId" — String, unique for each report.

Required fields

- "reportId"
- "locationName"
- "description"
- "severity"
- "status"
- "createdAt"
- "updatedAt"

Latitude and longitude are optional for text-only reports but must be supplied and validated for reports displayed at a precise map location.

Allowed values

- Severity: "Low", "Medium", "High"
- Status: "Unverified", "Corroborated", "Resolved"

Timestamp format

ISO 8601 UTC, for example "2026-10-11T08:00:00Z".

API contract

- "POST /reports" — create a report.
- "GET /reports" — list recent reports.
- "PATCH /reports/{reportId}" — update report status.

The backend must validate incoming data and generate unique report IDs. New reports start with status "Unverified". Only authorized application logic should change report status.

Sample data

"sample_reports.json" contains fictional demonstration records. These must not be presented as verified real-world incidents.