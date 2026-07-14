# FarmLens-node — Hardware Assembly Plan

Software (ESP32 firmware, RPi FastAPI server, fusion logic) is done and validated
against mock hardware — see `docs/ARCHITECTURE.md`. Nothing physical exists yet.
This is the build order to get from zero to a working node, sequenced to unblock
the paper's 3 pending experiments (latency/power, wiper SSIM, ETRACE) as early
as possible rather than waiting for a fully finished node.

Locked hardware spec: **Raspberry Pi 4 + YOLOv11n INT8** (see
`FarmLens-docs/startup/grants/r2b-proposal.md` §4 and `roadmap.html` §3.1).

## 1. Order hardware

- [ ] Raspberry Pi 4 (4GB+), official power supply, microSD (32GB+)
- [ ] RPi Camera Module (v2 or HQ) or USB webcam (`CAMERA_BACKEND=opencv` fallback already supported in `rpi/config.py`)
- [ ] ESP32 dev board (any WROOM variant matching `firmware/platformio.ini`)
- [ ] Capacitive soil moisture sensor + water-level sensor (analog, matches `firmware/src/main.cpp` GPIO reads)
- [ ] Solar panel (25–100W) + charge controller + 12V/21Ah battery
- [ ] Wiper mechanism parts: low-RPM high-torque DC servo, threaded rod or rack-and-pinion drive, microfiber brush, small cleaning-fluid dispenser (none of this exists in code or hardware yet — new build from scratch)
- [ ] IP65 enclosure (ASA+PC-FR or equivalent)

## 2. Assemble the RPi4 node (unblocks latency/power experiment first)

- [ ] Flash Raspberry Pi OS Bookworm 64-bit, run `rpi/install.sh` per `rpi/README.md`
- [ ] Attach camera, confirm `picamera2` backend reports `camera_ready: true` at `/api/status`
- [ ] Run in `AI_MODE=mock` first to confirm the full stack (camera → API → app) works on real hardware before touching AI
- [ ] **Experiment 1 unlocked here:** bench-measure real INT8 inference latency and active power draw once a trained model is loaded (see §4) — replaces the `~170ms / ~3.2W` projected placeholders in `roadmap.html` with a real number

## 3. Bring up the ESP32 sensor bridge

- [ ] Flash `firmware/src/main.cpp` to the ESP32, wire the two analog sensors to the GPIOs it already expects
- [ ] Point its WiFi POST target at the RPi4's `/api/sensor` endpoint (replaces `SENSOR_MODE=mock` — see `docs/ARCHITECTURE.md`'s "Planned: mock sensor mode" section, which is a stopgap for exactly this gap)
- [ ] Confirm `esp32_connected()` in `fusion.py` returns true and real moisture/water readings flow into `/api/live`

## 4. Train and deploy the real model

- [ ] Collect/label a real dataset (start with PlantVillage + PlantDoc per `roadmap.html` §3.2, then add real Ismailia field images per the paper's future-work note)
- [ ] Train YOLOv11n, export + INT8-quantize per `roadmap.html` §4.2
- [ ] Drop the exported model at `rpi/models/plant_disease.tflite`, set `AI_MODE=tflite` in `.env`, restart — `rpi/inference.py` already has the loading path built, just untested against a real model file
- [ ] Record the real mAP number — replaces the `90.2%` design-target figure

## 5. Build and mount the wiper (unblocks SSIM experiment)

- [ ] Build the wiper mechanism (§1) and mount it over the camera lens + PV array
- [ ] No trigger code exists yet — add a scheduled or vision-triggered wiper cycle (roadmap.html §2.4 suggests triggering off a YOLOv11-detected drop in image clarity as a lens-occlusion proxy; this is new code, not yet started)
- [ ] **Experiment 2 unlocked here:** measure real before/after SSIM and solar-recovery % — replaces the `0.61 → 0.94` / `+11.3%` design-target figures

## 6. Wire up ETRACE logging (unblocks ETRACE experiment)

- [ ] No ETRACE integration code exists yet in this repo — `logger.py`'s SQLite schema would need extending with GPS + pesticide-record fields per `roadmap.html` §3.4's log schema sketch
- [ ] **Experiment 3 unlocked here:** run a bench or short field trial and confirm real auto-generated ETRACE-compatible log entries — replaces the `168/168 cycles` design-target figure

## 7. Field/bench trial

- [ ] Once 2–6 are done, run the actual latency/power bench test + SSIM cycle test + ETRACE trial together as a single real experiment pass, feeding results into `FarmLens-docs/research/paper/experiment-log.md`
