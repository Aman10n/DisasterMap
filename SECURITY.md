# Security policy

DisasterMap controls interfaces that can eventually influence robot motion and can process sensitive mission data. Security reports are taken seriously even while the project remains a research prototype.

## Supported versions

Security fixes are applied to the latest commit on the `main` branch. No separately supported release line exists yet.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose credentials, systems, device control, location data, or victim information.

Use [GitHub private vulnerability reporting](https://github.com/Aman10n/DisasterMap/security/advisories/new) and include:

- the affected component and commit;
- the prerequisites and reproducible steps;
- the realistic impact;
- sanitized logs or proof-of-concept material;
- any suggested mitigation.

Do not include active credentials, personal data, or real mission evidence. Allow reasonable time for investigation and remediation before public disclosure.

## Security-sensitive areas

Extra care is required for changes involving:

- teleoperation, navigation, emergency stop, or actuator commands;
- MQTT topic authorization and message validation;
- authentication, authorization, sessions, and CORS;
- WebSocket clients and untrusted payloads;
- MinIO buckets, reports, recordings, and evidence;
- firmware updates and device provisioning;
- Docker ports, secrets, and network exposure.

## Development configuration

The checked-in Mosquitto and API settings prioritize local development. Anonymous MQTT access and broad CORS must not be exposed to an untrusted network. A deployment must add unique credentials, least-privilege ACLs, TLS, authenticated API access, audit logging, secret management, and independent robot safety controls.

## Safety disclaimer

A software security fix does not establish physical safety. Robot motion, gas sensing, survivor detection, and emergency behavior require independent engineering review and controlled validation before use around people.
