# Telegram Demo Hardening Plan

## Goal

Make the Telegram bot demo credible end to end:

- meal/body-metric messages should log into the longevity database
- report and insight questions should read real stored data
- trial prompts should trigger the actual multi-agent trial workflow
- Telegram output should be stable and compelling enough for a 2-3 minute screen-recorded demo

## Dry-Run Findings

- The bot can reply in a longevity-themed voice after `/longevity`.
- The current Telegram flow is still mostly prose-first, not workflow-first.
- Meal logging messages are not reliably writing rows into `diet_entries`.
- Weekly reports are not clearly pulling from the actual stored week.
- The DB already contains enough demo data for the key scenes:
  - protein/sleep insight
  - completed Protein-Sleep Quality Trial
  - active Creatine-Cognition Trial
- Skill loading had a path issue when the skill resolved outside the workspace root.

## Ranked Task List

1. [ ] Fix skill loading so the Telegram runtime consistently discovers and uses the local `longevity` skill without path warnings.
   This is the first gate. If the skill is not loaded deterministically, nothing downstream is trustworthy.
2. [ ] Trace Telegram message handling and confirm `/longevity` enters the intended longevity workflow rather than only changing tone.
   Right now the bot sounds like a longevity coach, but it does not yet behave like the structured longevity system.
3. [ ] Implement diet logging dispatch so meal messages create `diet_entries` rows with timestamp, meal type, description, and macro estimates.
   This unlocks the first two scenes of the demo and proves the bot is writing to the real database.
4. [ ] Implement breakfast/lunch/dinner inference rules for casual meal messages when explicit meal type is missing.
   The scripted demo depends on effortless casual inputs, not rigid command syntax.
5. [ ] Implement multi-input body-metric parsing so messages like `Weight 72.3kg this morning, slept 7.5 hours, resting HR 57` write separate `body_metrics` rows.
   This unlocks the body-metrics scene and proves multi-entity parsing works.
6. [ ] Add idempotent regression checks for meal logging and multi-metric logging.
   We need a safety net before tightening prompt behavior further.
7. [ ] Make `Weekly report` query the real database and synthesize diet, exercise, sleep, biomarkers, and active-trial state instead of producing generic advice.
   This is the actual "wow" moment, so it needs to be DB-backed rather than improvised.
8. [ ] Include concrete trend numbers in reports when data exists.
   The report should feel analytical, not hand-wavy.
9. [ ] Add literature citation formatting that is concise and demo-friendly.
   We want evidence-rich answers without turning the bot into a wall of text.
10. [ ] Make the protein-sleep question pull the existing `insights` record and present the stored effect size / p-value cleanly.
    This is the key bridge from "tracker" to "insight engine."
11. [ ] Ensure the experiment-design prompt triggers the intended trial pipeline across `shixiao`, `yuanpan`, and `yizheng`.
    This is the differentiator scene, so it needs to hit the actual multi-agent design flow.
12. [ ] Ensure `How's my creatine trial going?` reads the real active trial and summarizes status, phase, and compliance.
    The active trial already exists in the DB; the bot needs to expose it reliably.
13. [ ] Reduce Telegram response sprawl so demo messages land as crisp structured outputs rather than long essay-style replies.
    Even correct logic will demo poorly if the responses are too sprawling.
14. [ ] Decide whether Telegram streaming should stay `partial` or switch to a cleaner mode for screen recording.
    This is mostly presentation polish after behavior is correct.
15. [ ] Add a deterministic demo-reset path so we can start from a clean Telegram chat and known DB state before recording.
    This prevents flaky rehearsal and avoids contaminating the final take.
16. [ ] Document the exact demo script that matches the implemented behavior.
    The recording script should be the last thing we lock once the product behavior is real.

## What I Think Is Going On

The current gap looks like a workflow integration problem, not a data problem.

- The data layer already exists and is populated.
- The domain prompt is rich and clearly describes a structured logging/reporting system.
- Telegram messages do reach the bot and produce themed replies.
- But the replies are often prose-first and generic, which strongly suggests the runtime is not consistently invoking the full database-backed workflow for each intent.

My working model is:

- `Telegram transport` is mostly fine.
- `Skill activation` is fragile and was partially broken by the out-of-root skill path.
- `Intent -> DB action` execution is incomplete or not being enforced hard enough.
- `Report/insight/trial` prompts are falling back to plausible coaching prose instead of being forced through concrete reads from SQLite.

So the gap is not:

- "we need more demo data"
- or "the bot cannot talk in a longevity voice"

The gap is:

- "the bot is not yet behaving like a real application layer over the longevity database"

## Suggested Implementation Order

1. Fix skill/runtime loading and message dispatch.
2. Get meal logging and body-metric logging writing to SQLite.
3. Make report and insight queries pull real DB state.
4. Wire trial proposal and trial status flows.
5. Tighten Telegram formatting and rehearse the final demo script.

## Demo Acceptance Criteria

- A lunch message creates a new diet entry and returns a concise nutrition/log summary.
- A multi-metric message creates the expected `body_metrics` rows.
- `Weekly report` references real weekly trends from the DB.
- The protein-sleep question surfaces the stored protein/sleep insight.
- The experiment-design prompt produces a real N-of-1 design flow, not generic advice.
- The creatine-trial question reports on the active trial from the DB.
- The whole Telegram script can be recorded in one pass without awkward failures or misleading improvisation.
