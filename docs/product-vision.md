# Product vision

Copied from the team's `Product-vision.pdf` and the Sprint 1 presentation deck.
Wording is kept as the team wrote it.

## Product Vision Board (Roman Pichler template)

### Vision
- To monitor the vaccine temperature and deliver vaccines to different places
  without it being expired.
- Every person can now have the equal opportunity to get vaccinated, even in rural
  areas where vaccines are hard to access.

### Target group
Primary users:
- Clinic nurses — receive shipments, decide use-or-discard. Low tech comfort, basic
  smartphone only, some clinics have no computer at all. The critical user at the
  critical moment.
- Fatima (Program Manager) — monitors shipments in transit, makes viability calls,
  reports upward.
- Depot managers (×3 zones) — dispatch shipments, manage drivers.
- Drivers — physically closest to the cargo, currently blind to its condition.

Customer: hospitals and rural clinics.

### Needs
- The system must continuously track temperatures and send alerts immediately.
- Devices must operate and alert offline without relying on an internet connection.
- The system must assess vaccine viability based on the specific rules of each
  vaccine type.
- The solution must require minimal to zero effort from clinic nurses.

### Product
- A smart cold box device — logs temperature, holds vaccine-specific tolerance
  rules, computes viability on the box.
- Green / Red external indicator + one physical button for sign-off. Visible before
  the box is opened. Two states only:
  - Green — safe to use, accept the shipment
  - Red — quarantine, do not open, call the depot
- Depot dashboard — all in-transit shipments ranked by remaining thermal buffer.
- Driver's phone as data relay — syncs the audit trail when signal returns.

### Business goals
- Ensure vaccine safety and effectiveness by monitoring temperature throughout
  transportation.
- Detect and respond to temperature issues in real time before vaccines are damaged.
- Reduce vaccine waste and patient safety risks through consistent and reliable
  quality decisions.
- Improve operational efficiency and compliance with better monitoring and reporting.
- Create a sustainable system that clinic staff can easily use without increasing
  their workload.
- Move toward preventive monitoring by using route and environmental data to reduce
  future incidents.

## Product Vision Statement

| | |
|---|---|
| For | Hospitals and rural clinics |
| Who | need to transport and store vaccines without losing potency to temperature excursions — often in areas with unreliable internet or power |
| The | Smart Cold Box is a self-contained cold-chain monitoring and verification device — a transport box with an onboard temperature logger, vaccine-specific tolerance rules stored locally, an external status indicator, and a single sign-off button |
| That | continuously logs temperature from dispatch to handoff; computes viability on the device against that shipment's vaccine type, using cumulative exposure rather than a single threshold; displays a decision, not data — readable before the box is opened; records the handoff with one button press (timestamp, device ID, verdict); works fully offline, the audit trail syncs later via the driver's phone |
| Unlike | traditional cold boxes or basic data loggers, which only record temperature and leave viability judgment to staff |
| Our product | computes vaccine viability automatically on the device itself, requires zero internet connection and minimal effort from nurses, and syncs the audit trail via the driver's phone once signal returns |

Example: a shipment of measles vaccine sits 3 hours in a stalled vehicle. The box
tracks the cumulative exposure, compares it to that vaccine's tolerance profile, and
shows red on arrival. The nurse quarantines it and calls the depot — no chart
reading, no guesswork, and the excursion is already logged for the ministry report.

## Scrum Product Canvas

- Name: Smart Cold Box
- Personas: Fatima Al-Sayed (Program Manager) — see `persona-fatima.md`

### How personas live the product
- Clinic nurses glance at a green/red light and press one button on handoff — no
  charts, no judgment calls, zero added workload.
- Fatima gets a live dashboard of in-transit shipments instead of piecing things
  together from paper logs after the fact.
- Depot managers see shipment condition remotely via the synced audit trail instead
  of relying on phone calls.
- Drivers just carry the box — their phone auto-syncs the audit trail once signal
  returns, no manual reporting.

### Constraints
User:
- Clinic nurses: low tech comfort, basic smartphone only, senior nurses
  uncomfortable with anything beyond phone calls.
- Depot managers: medium comfort, won't troubleshoot or read a manual.
- Nurses are at capacity — any added step will be bypassed.

Regulatory & compliance:
- Tolerance rules must follow manufacturer data and national EPI policy, externally
  configurable, not hardcoded.
- Ministry must confirm whether Red means strict quarantine or
  quarantine-pending-review.
- Hardware must never override physical VVM endpoints.
- Audit trail must be tamper-proof to be defensible to ministry and donors.

Organizational:
- Ministry pressure for visible progress quickly — risk of corner-cutting.
- Donor-funded: unit cost must scale across every box on every route.
- Fatima has no authority over clinic nurses — adoption cannot be mandated.

### Epic (as written on the canvas) — NEEDS CORRECTION
The canvas still has an early draft: "The parcel box can monitor temperature to
ensure the freshness of the product. Green means the product is ready to be shipped.
Red means do not open or send back to depot. The temperature inside the box can be
tracked all the time."

This contradicts the Product section above: green means safe to use at the clinic,
red means quarantine and call the depot (the decision to send back is not the
nurse's). Not yet corrected by the team.

## Story map

Themes and high-level capabilities, left to right along the shipment journey:

| Theme | Capability | Lower-level capabilities |
|---|---|---|
| Dispatch | Pack & dispatch | Assign vaccine type to shipment · Assign destination · Load profile · Validate the destination |
| Transit | Monitor in transit | Keep temperature log active · Computes exposure · Works fully offline · Logged excursion |
| Transit | Check status and alerts | Show green/red sign · Alert depot · Sending defects back to depot · Failed to sync status · Keep record of each status |
| Handoff | Receive & verify | Records the handoff · Sign-off · Order for another address · Let the nurse verify the product |
| Post-delivery | View reports | Readable reports via phone · Sync on signal · Excursion logged for the ministry report · Route analysis · Aggregate totals |

The first deliverable slice on the map was drawn before Sprint Planning. The actual
Sprint 1 scope is in `sprint-1-plan.md`.
