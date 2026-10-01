## Summary

Describe the problem and the focused change made to solve it.

## Component

- [ ] Dashboard
- [ ] FastAPI server
- [ ] Infrastructure or messaging
- [ ] ROS 2 workspace
- [ ] ESP32 firmware
- [ ] Documentation

## Validation

- [ ] `npm run build` passes when dashboard code changed.
- [ ] Python sources compile when server or ROS code changed.
- [ ] `docker compose config --quiet` passes when deployment files changed.
- [ ] Simulation and live-data behavior remain clearly distinguishable.
- [ ] No secrets, personal data, recordings, or generated artifacts were committed.

## Safety and compatibility

Document robot-motion, emergency-stop, sensor-calibration, API, MQTT-topic, database, or configuration compatibility concerns. Write `None` when they do not apply.

## Screenshots or logs

Attach sanitized evidence when it helps reviewers verify the change.
