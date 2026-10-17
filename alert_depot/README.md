# 007-1 Alert depot on risk

Runs on the box (ESP32 MicroPython in Wokwi) and on desktop Python for tests,
the same way as `read_temp/`.

## Who owns what

| File | Owner | Covers |
|---|---|---|
| `contracts.py` | shared — change only with Sia, Pun and Gramma agreeing | names and data shapes |
| `alert_config.py`, `alert_thresholds.json` | Sia | AC4 |
| `detect_risk.py` | Sia | AC1, AC2 |
| `detect_handoff_risk.py` | Pun | AC3 |
| `alert_sender.py` | Pun | AC5 (offline queue) |
| `test_*.py`, `test_data/` | Gramma | all |

Only edit the files you own.

## Run the tests

From inside this folder:

```
python -m unittest -v
```

Tests must not use a real network, real hardware or the real clock.

## Planned functions

- `alert_config.load_alert_config(path)` → config dict (Sia)
- `detect_risk.detect_risk(history, config)` → list of risk-event dicts (Sia)
- `detect_handoff_risk.detect_handoff_risk(handoff)` → risk-event dict or `None` (Pun)
- `alert_sender.AlertSender(network, depot)` with `send(event)`, `flush()`,
  `pending_count()` (Pun)

Required behavior for each: `docs/decisions-and-open-questions.md`.
