# Decisions, contracts and open questions

## Decisions made

- The product is built as a software mockup. Sensor, network signal and remaining
  buffer are simulated. Box-side code runs on ESP32 MicroPython in Wokwi.
- Sprint 1 = 007-1, 003-1, 002-1 (11 SP). 003-2 moved out of Sprint 1.
- 007-1 is split: Sia = detection + thresholds, Pun = red alert at handoff +
  sending with an offline queue, Gramma = test data and tests.
- Gramma writes the unit and acceptance tests for Sia's and Pun's code; Sia and Pun
  do not write duplicate unit tests.
- 007-1 is written in Python (MicroPython-compatible) in `alert_depot/`, with
  `unittest`, the same way as `read_temp/`. An earlier TypeScript + Vitest setup was
  dropped before any story code was written.
- Shared names and data shapes live in `alert_depot/contracts.py`.

## Function contracts for 007-1

Records are plain dicts; keys and constants are defined in `alert_depot/contracts.py`.

Sia:
- `alert_config.load_alert_config(path)` → config dict
  (`low_buffer_threshold_pct`, `max_depletion_pct_per_hour`); default file
  `alert_depot/alert_thresholds.json`.
- `detect_risk.detect_risk(history, config)` → list of risk-event dicts.
  Evaluates only the newest snapshot (last item), using the one before it for the
  depletion rate. Returns `[]` when there is no risk; may return two events.

Pun:
- `detect_handoff_risk.detect_handoff_risk(handoff)` → risk-event dict or `None`
- `alert_sender.AlertSender(network, depot)` with `send(event)`, `flush()`,
  `pending_count()`

## Required behavior

detect_handoff_risk:
- status `RED` → a `RED_AT_HANDOFF` event with the same `device_id`,
  `shipment_id` and `timestamp_s` as the handoff
- status `GREEN` → `None`
- no clock, no network, no side effects

AlertSender:
- online: the depot receives the alert immediately
- offline: the alert is queued; nothing is delivered
- after the signal returns, `flush()` delivers queued alerts
- alerts reach the depot in the order they were sent
- no alert is lost; calling `flush()` twice never delivers one twice
- `flush()` while offline does nothing
- uses only `network.is_online()` and `depot.receive(event)`

detect_risk:
- `LOW_BUFFER` when newest `remaining_buffer_pct` < `low_buffer_threshold_pct`
  (also with a single snapshot)
- `FAST_DEPLETION` when the depletion rate > `max_depletion_pct_per_hour`
  (needs two snapshots)
- `device_id`, `shipment_id`, `timestamp_s` copied from the newest snapshot
- pure function: no file reading, no clock, no network

## Assumptions (agreed for Sprint 1, still need team confirmation)

- A1. "Falls below" means strictly less than the threshold (30 → no alert,
  29.9 → alert).
- A2. "Faster than expected" means the depletion rate is above a configured maximum:
  rate = (previous % − current %) ÷ ((newest timestamp_s − previous timestamp_s) ÷ 3600).
- A3. Remaining buffer is a percentage, 0–100. The real unit will be decided with
  story 004-4.
- A4. Thresholds 30% and 5%/hour are test values, not product values.
- A5. An alert queued while offline is delivered exactly once after reconnection.

## Proposed details not yet agreed with Gramma

- C1. `LOW_BUFFER` value = remaining %; `FAST_DEPLETION` value = rate in %/hour.
- C2. When both happen at once, the order is `LOW_BUFFER` then `FAST_DEPLETION`.
- C3. If the two newest snapshots have the same `timestamp_s` or are out of order,
  skip the `FAST_DEPLETION` check (no division by zero).

## Open questions

1. **Red button meaning (for the Product Owner, via Aleef).** When the box shows red
   at handoff, does the nurse's button press mean "accept" or "quarantine"? The
   canvas also notes the ministry must confirm whether red means strict quarantine
   or quarantine-pending-review. This affects how the handoff is recorded, not
   whether the red alert is sent.
2. **Repeated alerts.** If the buffer stays below the threshold for several readings,
   should the depot get one alert or one per reading? The acceptance criteria do not
   say. For now every event passed to `send()` is delivered.
3. **Power cut.** Queued alerts surviving a power cut need on-box storage (003-2),
   which is not in Sprint 1. For now the queue lives in memory.
4. **Bad config file.** `read_temp/config.py` falls back to defaults when its file is
   missing or invalid, so the box keeps working. Should `load_alert_config` do the
   same, or raise an error? Recommended: follow `read_temp/config.py`. Sia decides
   with the team.
5. **003-2 sprint.** Not re-assigned after it left Sprint 1.
6. **Missing story.** 004-3 compares against "the loaded profile", but no story loads
   a vaccine tolerance profile onto the box ("Load profile" is on the story map only).
7. **Missing stories from INVEST.** Show green/red, record the handoff and sync on
   signal were marked Rewrite/Clarify but are not yet in the groomed backlog.
8. **Slides out of date.** The presentation deck still shows the old Sprint 1
   (003-1, 003-2, 002-1) and 007-1 in Sprint 4.
9. **Canvas epic.** The Scrum canvas epic text still says "parcel box" and "red means
   send back to depot", which contradicts the product definition.
10. **Repo hygiene.** `add_destination/node_modules/` is committed (about 1,000
    files) because `.gitignore` has no `node_modules/` line. Owner of
    `add_destination/` should remove it from git.
