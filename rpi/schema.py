"""
FarmLens Cycle Result Schema
=============================
Documents the dict shape returned by `fusion.compute()` (fusion.py) — the same
payload served at GET /api/live, stored per-cycle in SQLite (logger.py), and
(per FarmLens-Platform/docs/ROADMAP.md) the intended POST /api/v1/nodes/{node_id}/telemetry
body once the Platform starts ingesting real field nodes.

This is documentation, not a runtime dependency: fusion.compute() still returns
a plain dict so it stays trivial to swap in real AI (see its own docstring).
Anything consuming the shape (FastAPI response models, the Platform ingestion
API, tests) should validate against CycleResult instead of hand-copying fields.
"""
from pydantic import BaseModel


class CycleResult(BaseModel):
    ts: int                    # Unix timestamp of this fusion cycle
    node_id: str                # NODE_ID of the reporting RPi node
    moisture_raw: int           # Raw ESP32 ADC reading, soil moisture probe
    moisture_pct: float          # Soil moisture, 0-100%
    water_raw: int              # Raw ESP32 ADC reading, water level probe
    water_pct: float             # Water level, 0-100%
    moisture_stress: int         # 1 if moisture_pct < MOISTURE_STRESS_THRESHOLD, else 0
    water_stress: int            # 1 if water_pct < WATER_STRESS_THRESHOLD, else 0
    cs: float                    # Soil stress score: 0.6*moisture_stress + 0.4*water_stress
    cv: float                    # Visual AI detection confidence, 0-1
    ccombined: float              # w1*cv + w2*cs, clamped to 1.0 (fusion.py DEFAULT_W1/W2)
    alert: bool                  # True if ccombined > theta (fusion.py DEFAULT_THETA)
    detection_class: str         # e.g. "Tomato_healthy", "Tomato_late_blight"
    detection_conf: float        # Same value as cv (kept distinct for API clarity)
    cycle_id: str                # f"{NODE_ID}-{timestamp}" — unique per cycle
    has_image: bool               # True if a JPEG was captured for this cycle
    fault: int                    # 1 if no ESP32 data received yet, else 0
