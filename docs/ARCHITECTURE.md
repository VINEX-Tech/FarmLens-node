# Architecture

## Three-tier system

```
┌───────────────┐   POST /api/sensor    ┌──────────────────┐   REST (port 8000)   ┌──────────────┐
│  firmware/    │ ────────────────────> │  rpi/             │ <──────────────────> │  FarmLens    │
│  ESP32 sensor │   every 5s            │  FastAPI server   │                      │  app         │
│  bridge       │                       │  (this repo)      │                      │  (separate   │
│  (dormant —   │                       │                   │                      │  repo)       │
│  no hardware  │                       │                   │                      │              │
│  yet)         │                       │                   │                      │              │
└───────────────┘                       └──────────────────┘                      └──────────────┘
```

Later, once multiple real field RPi nodes are deployed, each `rpi/` instance also reports up to `FarmLens-Platform` (currently just a scaffold + roadmap). That link doesn't exist yet.

## Data flow inside `rpi/`

```
firmware/ (POST /api/sensor)  ──┐
                                 ├──► fusion.update_sensor() ──► fusion.compute() ──► api.py (/api/live, /api/logs)
inference.py (AI_MODE=mock      │         (thread-safe store)         │
  or tflite)  ─────────────────┘                                      │
                                                                        ▼
                                                              logger.py (SQLite) + camera.py (JPEG)
```

`fusion.update_sensor()` is the single injection point for sensor readings. It's currently only called from the `POST /api/sensor` handler in `api.py`. **This means sensor values stay frozen until either real firmware exists, or a mock generator calls this function directly** — see the "known gap" note in `rpi/README.md`.

## Fusion formula

```
Cs        = 0.6 × moisture_stress + 0.4 × water_stress
Ccombined = w1 × Cv + w2 × Cs        (defaults: w1=0.6, w2=0.4)
Alert     = Ccombined > theta         (default theta=0.5)
```

`Cv` (AI confidence) is already self-mocked in `rpi/inference.py` when `AI_MODE=mock` — a random walk, no model needed. `Cs` (sensor stress) has no self-mocking yet.

## Planned: mock sensor mode

Not yet implemented — this is the next concrete task for this repo, done on the Raspberry Pi:

- New `rpi/mock_sensor.py` module: a background thread that ports the sine-wave sensor simulation already proven in `firmware/src/main.cpp` (`updateMockSensors()`), calling `fusion.update_sensor(...)` directly in-process every ~5s instead of over HTTP.
- New `SENSOR_MODE=mock|esp32` config knob in `.env` / `config.py`, same pattern as the existing `AI_MODE=mock|tflite`. `main.py` starts the mock thread only when `SENSOR_MODE=mock` (default). When `SENSOR_MODE=esp32`, it's a no-op and real firmware POSTs take over exactly as today.
- Zero changes needed to `api.py` or `fusion.py` — `POST /api/sensor` keeps working once real firmware is flashed.

## Known follow-ups (not yet done — intentionally left as-is during this reorg)

- `rpi/mock_sensor.py` (above) — the main functional gap.
- `rpi/install.sh` has a redundant hardcoded `pip install fastapi "uvicorn[standard]"` line alongside `requirements.txt` — should just use `pip install -r requirements.txt`.
- No authentication on the API yet. `FarmLens-Platform`'s roadmap already anticipates per-node API keys for when nodes report to the cloud; this repo's local API will likely need the same before going to real field deployments.
