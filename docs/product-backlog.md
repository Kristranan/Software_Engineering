# Product backlog

Source: the team's Sprint Planning worksheet and presentation deck. Sprint 1 rows
follow the latest version (007-1, 003-1, 002-1 in Sprint 1).

## Prioritized product backlog

| Priority | ID | Story | Size (SP) | Sprint |
|---|---|---|---|---|
| 1 | 007-1 | Alert depot on risk | 5 | 1 |
| 2 | 003-1 | Read temp. at interval | 5 | 1 |
| 3 | 002-1 | Add destination | 1 | 1 |
| 4 | 003-2 | Store readings locally | 5 | **not assigned** — see note |
| 5 | 004-1 | Accumulate heat exposure | 2 | 2 |
| 6 | 004-2 | Accumulate freeze exposure | 2 | 2 |
| 7 | 004-3 | Compare against vaccine profile | 5 | 2 |
| 8 | 004-4 | Calculate remaining buffer | 5 | 3 |
| 9 | 001-1 | Assign vaccine type to shipment | 2 | 2 |
| 9 | 007-2 | Flag shipment as unknown | 3 | 3 |
| 10 | 002-2 | Change destination | 2 | 3 |
| 11 | 002-3 | Delete destination | 1 | 4 |

Note: 003-2 was in Sprint 1 until 007-1 moved into Sprint 1. Its new sprint has not
been decided. Sprints 2–4 above come from the deck and have not been re-planned since.

Velocity: 12 SP per sprint (baseline estimate, no history yet).

## Acceptance criteria

**007-1 Alert depot on risk**
- Alert is sent when remaining buffer falls below a configurable threshold
- Alert is sent when buffer depletes faster than expected
- Alert is sent immediately when a box shows red at handoff
- Thresholds are configurable without code change

**003-1 Read temp. at interval**
- Temperature is read at a configurable interval
- Reading continues without external power or network
- Failed reads are logged, not silently skipped

**002-1 Add destination**
- Operator can add a clinic as the shipment destination
- Only registered clinics can be selected
- Destination is stored with the shipment record

**003-2 Store readings locally**
- Every reading is written to on-box storage
- Storage holds at least one full transit cycle
- Readings survive power interruption

**004-1 Accumulate heat exposure**
- Time above the upper threshold accumulates continuously
- Accumulation resumes correctly after power interruption

**004-2 Accumulate freeze exposure**
- Time below the lower threshold accumulates separately from heat
- Freeze events are not offset by later warming

**004-3 Compare against vaccine profile**
- Accumulated exposure is compared to the loaded profile
- Heat and freeze are evaluated against their own limits
- Comparison runs entirely on the box

**004-4 Calculate remaining buffer**
- Remaining tolerance is calculated after each reading
- Buffer reaches zero exactly when the profile limit is exceeded
- Value is available to the indicator and to sync

**001-1 Assign vaccine type to shipment**
- Operator selects a vaccine type when creating a shipment
- Shipment cannot be dispatched without a type assigned
- Selected type is stored with the shipment record

**007-2 Flag shipment as unknown**
- Shipment is flagged when no reading is received for a configurable period
- Shipment is flagged when arrival is overdue with no sign-off
- Flagged shipments display as unknown, never as safe

**002-2 Change destination**
- Destination can be changed before dispatch
- Change is recorded with timestamp and user
- Change after dispatch is rejected

**002-3 Delete destination**
- Destination can be removed before dispatch
- Shipment is blocked from dispatch while no destination is set

## INVEST check (from the worksheet)

| ID | Original story | Issue found | Decision |
|---|---|---|---|
| 001 | Assign vaccine type to shipment | – | Keep |
| 002 | Assign destination | Not Small | Split (add / change / delete) |
| 003 | Keep temperature log active | Not Small, Not Estimable | Split |
| 004 | Computes exposure | Not Small, Not Estimable, Not Independent | Split + Rewrite |
| 005 | Works fully offline | Not Small, Not Estimable | Split |
| 006 | Show green/red sign | Not Independent | Rewrite |
| 007 | Alert depot | Not Independent | Split + Rewrite |
| 008 | Records the handoff | Not Negotiable, Not Independent | Rewrite |
| 009 | Sign-off | Not Testable | Clarify |
| 010 | Readable reports via phone | Not Independent, Not Testable | Clarify + Rewrite |
| 011 | Sync on signal | Not Independent, Not Small, Not Estimable | Split + Rewrite |

Stories 005, 006, 008–011 were not rewritten into the groomed backlog yet, so the
backlog has no story for showing green/red, recording the handoff, or syncing.
"Works fully offline" (005) behaves like a non-functional requirement that applies
to every story.
