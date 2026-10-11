-- FloodLens: PostgreSQL table for flood reports
-- Run this on the "floodlens" database.

CREATE TABLE IF NOT EXISTS flood_reports (
  report_id     TEXT PRIMARY KEY,
  location_name TEXT NOT NULL,
  description   TEXT NOT NULL,
  latitude      DOUBLE PRECISION,
  longitude     DOUBLE PRECISION,
  severity      TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High')),
  status        TEXT NOT NULL CHECK (status IN ('Unverified', 'Corroborated', 'Resolved')),
  created_at    TIMESTAMPTZ NOT NULL,
  updated_at    TIMESTAMPTZ NOT NULL,
  CHECK ((latitude IS NULL) = (longitude IS NULL)),
  CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
  CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);