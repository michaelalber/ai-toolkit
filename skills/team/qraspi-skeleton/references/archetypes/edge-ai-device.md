# Archetype: Edge AI / IoT (Raspberry Pi or Jetson, hardware-coupled, constrained runtime)

A new project that runs on a device. Hardware coupling **breaks the "runnable skeleton in CI"
assumption**: `deploy` targets a device, not a container, and the test harness is constrained by the
runtime. This archetype is why the exit gate has a carve-out (#9 in the plan).

## Stack it instantiates (from the ADRs)
Python on Pi/Jetson, the ADR-chosen inference runtime (TFLite / TensorRT / ONNX), the camera/sensor
capture layer, a result-publishing transport (MQTT / HTTP). Confirm the device + runtime against the
accepted ADRs.

## Repo layer (the recipe)
- Layout: `src/<pkg>/{capture,inference,publish}/`, `tests/`, a per-device `SYSTEM.md`, the Pi/Jetson
  install target convention.
- Entrypoint: capture -> inference (a stub or tiny model) -> publish, end-to-end (the walking slice),
  doing minimal real work.
- Health/smoke: a host-runnable test that feeds a fixture frame through capture -> inference -> publish
  with the camera/device mocked, asserting a real result object.
- Observability hook: structured logging + a heartbeat/health publish.
- Secure-by-default: no secrets on the device image; TLS on the publish transport; least-privilege
  device access.

## Slice layer (delegate)
Compose the Edge/IoT skills: `edge-cv-pipeline` (OpenCV + TFLite), `jetson-deploy` or the Pi install
target, `sensor-integration`, `model-optimization` per the ADR runtime.

## Fitness gates typical here (wire via `fitness-functions`)
Host-runnable only: lint, type, coverage on the device-independent logic, model-size/latency budget
gate (static check against the ADR threshold). Dependency-direction gate so `capture`/`publish` never
import `inference` internals.

## CI-green carve-out (HARDWARE)
**CI-green covers build + unit + lint + fitness gates on the host runner.** The device-deploy step
(`deploy` to the Pi/Jetson, on-device smoke) is a **DOCUMENTED MANUAL gate** in `skeleton.md`, NOT
auto-run -- the skeleton is executable up to the hardware boundary. Record the manual deploy/verify
steps under `hardware_manual_gate`; `ci_green` reflects only the host-runnable gates.
