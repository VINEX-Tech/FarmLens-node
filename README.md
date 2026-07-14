# FarmLens Node

Hardware-side of the FarmLens system: the Raspberry Pi edge server and the ESP32
sensor firmware, as two subfolders of one repo.

**Suez Canal University · Faculty of Engineering**
Abdel Rahman M. El-Saied · Mohamed Elsayed

---

## Overview

FarmLens is a solar-powered edge-AI field node for real-time crop health monitoring:
camera-based disease detection (YOLOv11n INT8) fused with soil moisture and water
stress sensor readings into a single risk score, logged for export traceability.

## Components

| Folder | What it is | Status |
|---|---|---|
| [`rpi/`](rpi/README.md) | Python/FastAPI server on a Raspberry Pi 4 — camera capture, AI inference, sensor fusion, SQLite logging, REST API + web dashboard on port 8000 | Active — this is what the app connects to today |
| [`firmware/`](firmware/README.md) | ESP32-S2 (LOLIN S2 Mini) firmware, C++/PlatformIO — will POST real sensor readings to the RPi over WiFi | Dormant — no ESP32 hardware exists yet |

Currently only the Raspberry Pi + a phone running the FarmLens app exist in software
form — no physical field hardware has been assembled yet. The RPi self-generates mock
sensor and inference data (see the "known gap" note in `rpi/README.md`) so the whole
system works end-to-end without needing real hardware. Once the ESP32 and sensors are
wired up, flashing `firmware/` will make the RPi pick up real sensor readings
automatically — no changes needed to `rpi/api.py` or `rpi/fusion.py`.

See [`PLAN.md`](PLAN.md) for the hardware assembly order and what unblocks each
pending experiment.

---

## API Contract (served by `rpi/`, port 8000)

This is the same contract documented in the `FarmLens-app` repo's README — the two
must stay in sync.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard (HTML) |
| GET | `/api/status` | Node health — uptime, ESP32 status, camera |
| POST | `/api/sensor` | ESP32 (or the future mock generator) posts sensor data here |
| GET | `/api/live` | Current sensor + AI data — app polls every 5s |
| GET | `/api/logs?limit=50` | Cycle history (newest first, max 200) |
| GET | `/api/image/{cycle_id}` | JPEG image for a specific cycle |
| GET | `/api/snapshot` | Fresh live camera frame |
| GET | `/api/settings` | Current fusion weights |
| POST | `/api/settings` | Update fusion weights live (no restart) |

Response shape for a cycle is documented as a schema in
[`rpi/schema.py`](rpi/schema.py) (`CycleResult`). See `docs/ARCHITECTURE.md` for the
full data-flow diagram and fusion formula.

---

## Security notes from this reorg

- `rpi/.env` is no longer tracked in git — copy `rpi/.env.example` to `rpi/.env` and
  edit it locally.
- `firmware/src/main.cpp` no longer hardcodes WiFi credentials — copy
  `firmware/include/secrets.h.example` to `firmware/include/secrets.h` and edit it
  locally. `secrets.h` is gitignored.
- The WiFi password that was previously hardcoded in git history is considered
  exposed (it lived in the old, now-abandoned repo history) — rotate it if it's still
  in use on your network.

---

## Related repos

- `FarmLens-app` — Flutter companion app (this repo's primary consumer)
- `FarmLens-Platform` — future cloud aggregator for multiple field nodes (not yet in
  use)

## License

All rights reserved. See [`LICENSE`](LICENSE) — this code may not be copied,
modified, or reused without written permission from the copyright holder.

## Team

Abdel Rahman M. El-Saied · Mohamed Elsayed
Suez Canal University, Faculty of Engineering
