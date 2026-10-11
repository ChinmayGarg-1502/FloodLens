-- Fictional demo records only. Do not present these as verified incidents.
INSERT INTO flood_reports
  (report_id, location_name, description, latitude, longitude, severity, status, created_at, updated_at)
VALUES
  ('FL-DEMO-001', 'Example Road, Sector 15', 'Water accumulating near the junction',
   28.6139, 77.2090, 'High', 'Unverified', '2026-10-11T08:00:00Z', '2026-10-11T08:00:00Z'),
  ('FL-DEMO-002', 'Example Market Road', 'Rainwater covering part of the road',
   28.6200, 77.2150, 'Medium', 'Unverified', '2026-10-11T08:15:00Z', '2026-10-11T08:15:00Z')
ON CONFLICT (report_id) DO NOTHING;