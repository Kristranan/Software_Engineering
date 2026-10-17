# Sprint 1 plan

## Sprint Goal

"The box reads temperature on schedule, and the depot is alerted as soon as a
shipment is at risk."

## Capacity (10-day sprint)

| Team | Days available | Days for Scrum activities | Available effort-hours |
|---|---|---|---|
| All 6 members | 42 | 12 | 76–135 |

Per-person availability is kept in the team's sprint worksheet, not in this repo.
Team members are listed by nickname only (see Hours per person below).

Velocity: 12 SP per sprint (baseline; no history yet).
Committed: 11 SP, 78 effort-hours (1 SP buffer).
Note: 78 hours is above the low end of capacity (76). The buffer is in story points,
not hours.

## Sprint backlog and tasks

### 007-1 Alert depot on risk — 5 SP, 33 h

| Task | Hours | Owner | Covers |
|---|---|---|---|
| Define alert thresholds as configurable settings | 5 | Sia | AC4 |
| Detect low buffer or abnormal depletion rate | 8 | Sia | AC1, AC2 |
| Trigger immediate alert when box shows red at handoff | 5 | Pun | AC3 |
| Send alert to depot, queued until signal returns | 7 | Pun | AC5 (hidden work) |
| Unit test + acceptance test with simulated buffer | 8 | Gramma | all |

Gramma also prepares the simulated buffer data on day 1 and reviews code for the
other stories.

### 003-1 Read temp. at interval — 5 SP, 35 h

| Task | Hours | Owner |
|---|---|---|
| Design configurable interval setting + config storage | 4 | Plai |
| Implement sensor read driver | 10 | Shogun |
| Implement scheduler that reads on interval without external power/network | 8 | Plai |
| Log failed reads (never skip silently) | 5 | Shogun |
| Unit test + acceptance test (split 4 + 4, each tests the other's code) | 8 | Shogun, Plai |

No real sensor yet: Shogun starts with a mock sensor.

### 002-1 Add destination — 1 SP, 10 h

| Task | Hours | Owner |
|---|---|---|
| Destination selection UI (registered clinics only) | 3 | Aleef |
| Validate that only registered clinics can be selected | 2 | Aleef |
| Store destination with the shipment record | 2 | Aleef |
| Unit test + acceptance test | 3 | Aleef |

### Hours per person

| Person | Hours |
|---|---|
| Sia | 13 |
| Pun | 12 |
| Gramma | 8 |
| Shogun | 19 |
| Plai | 16 |
| Aleef | 10 |
| **Total** | **78** |

## Definition of Done

- Code is merged
- Unit tests pass
- Acceptance Criteria pass
- No critical defects remain
- The Product Owner accepts the Story

## Events

- Sprint Planning: role-play meeting on Google Meet.
- Daily Scrum: every day at 9:00, 15 minutes, same Google Meet link. Three
  questions: What did I do yesterday? What will I do today? What is blocking me?
- Sprint Review and Sprint Retrospective: day 10.

## Risks

1. Sensor hardware not available — mitigated with a mock sensor; Aleef follows up.
2. 007-1 depends on 004-4 (remaining buffer, Sprint 3) — 007-1 is built and tested
   with simulated buffer values; the real calculation plugs in later.
3. Open question for the Product Owner about the red button (see
   `decisions-and-open-questions.md`).
