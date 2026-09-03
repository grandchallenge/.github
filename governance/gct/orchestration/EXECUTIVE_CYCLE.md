# GCT Executive Orchestration Cycle

## 1. Event-driven default

GCT should not imitate a calendar-heavy corporation. The primary operating model is event-driven: changes in evidence, opportunity, risk, authority, or portfolio state trigger executive work.

Recurring reviews exist to catch drift, not to manufacture activity.

## 2. Matter intake

Every material matter begins with:

```text
matter_id
origin
enterprise question
affected programme/assets
current exact state
urgency with reason
reversibility
known authority boundary
requested decision/output
```

GCT-COO/CONDUCTOR classifies the matter:

- `ROUTINE_EXECUTION`
- `RESEARCH_OPTION`
- `PRODUCT_OPTION`
- `COMMERCIAL_OPTION`
- `TRUST_RISK`
- `CORPORATE_ADMIN`
- `FOUNDER_RESERVED`
- `GCL_CONSTITUTIONAL_ROUTE`
- `DISPOSAL_REVIEW`

## 3. Selective cabinet dispatch

Do not invoke every office for every matter.

Examples:

- architecture change: CTO + CTA + COO; CSO if research semantics change;
- new scientific line: CSO + CTO + CPO; CTA for claim boundary;
- productization: CPO + CTO + CCP + CTA;
- public launch: CCO + CTA + CPO + relevant technical/scientific sponsor;
- contract/pilot: CCP + CPO + CTO + FLO + CTA;
- hiring trigger: PCO + COO + relevant executive sponsor;
- portfolio retirement: sponsor + COO + CPO/CSO as relevant + synthesis.

## 4. Executive synthesis

A synthesis session receives role findings and produces:

- current state;
- material disagreement;
- recommended disposition;
- finite work package or Founder decision memo;
- authority route;
- next decisive action;
- artifact updates.

## 5. GCL routing

If the matter requires consequential GCL research/engineering:

1. produce a `GCL_MANDATE` record;
2. bind the relevant GCT sponsors;
3. define decision-relevant evidence rather than desired conclusions;
4. route into existing GCL/INTELLECT/programme governance;
5. record the mandate in the GCT mandate register;
6. await/obtain a governed return packet;
7. update enterprise disposition without altering the returned claim status.

## 6. Execution routing

For bounded implementation, commission an Executor/Codex session with:

- exact repo/base state;
- issue/work-package identity;
- objective;
- non-goals;
- required artifacts;
- tests/checks;
- claim boundary;
- stop conditions;
- expected return packet.

## 7. Independent review

Where review independence matters:

```text
sponsor/author session
      ↓
implementation
      ↓ exact head
Independent Adversary session
      ↓ correction if needed
exact new head
      ↓
Independent Referee session
      ↓
applicable authority/merge gate
```

A changed exact head invalidates review evidence when governing policy requires exact identity. Re-review the changed head rather than narratively carrying approval forward.

## 8. Founder route

If Founder authority is required, CONDUCTOR produces one decision memo. While pending, continue only separable non-binding work that preserves optionality.

## 9. Completion

A matter is not complete when an agent says it is complete. Completion requires the applicable observable state:

- artifact integrated or intentionally retained outside integration;
- checks/readback completed;
- review obligations discharged;
- authority action recorded when required;
- executive registers updated;
- next consequence recorded;
- stale branches/issues/temporary records disposed of according to policy.

## 10. Recurring rhythms

### Daily/continuous

CONDUCTOR watches active blockers, exact-state drift, expiring exceptions, failed required checks, and Founder-reserved queue changes.

### Weekly

Produce a compact `EXECUTIVE_PACKET`:

1. portfolio movements;
2. strongest new evidence;
3. strongest disconfirming evidence;
4. work completed;
5. blocked matters;
6. trust/risk changes;
7. commercial option changes;
8. resource/capability pressure;
9. Founder decisions actually required;
10. next decisive actions.

### Monthly

Portfolio disposition review. Every active programme must re-earn `ACTIVE` or a stronger state. Explicitly consider `HOLD`, `NARROW`, and `RETIRE`.

### Quarterly

Enterprise thesis review:

- What became a durable capability?
- What remains merely promising?
- Which capabilities are becoming products/platforms?
- Which research options gained/lost value?
- What should GCT own, license, partner, open, spin out, or stop?
- Where is Jamie Steeg still a recurring operational bottleneck that should be converted into a delegation or control?

## 11. Operating metrics

Prefer decision-quality and loop-closure metrics over activity counts:

- median idea→discriminating-fixture time;
- reproducible fixture rate;
- exact-head review completion rate;
- routine matters completed without Founder interruption;
- Founder escalation precision (fraction truly requiring reserved authority);
- stale-work retirement rate;
- review debt created per agent implementation;
- public claim exceptions/outages;
- time from evidenced capability→productization decision;
- reusable infrastructure gained per major programme;
- portfolio capital/compute consumed per decision-relevant evidence unit where measurable.
