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

## Task List

- [ ] Fix skill loading so the Telegram runtime consistently discovers and uses the local `longevity` skill without path warnings.
- [ ] Trace Telegram message handling and confirm `/longevity` enters the intended longevity workflow rather than only changing tone.
- [ ] Implement diet logging dispatch so meal messages create `diet_entries` rows with timestamp, meal type, description, and macro estimates.
- [ ] Implement breakfast/lunch/dinner inference rules for casual meal messages when explicit meal type is missing.
- [ ] Implement multi-input body-metric parsing so messages like `Weight 72.3kg this morning, slept 7.5 hours, resting HR 57` write separate `body_metrics` rows.
- [ ] Add idempotent regression checks for meal logging and multi-metric logging.
- [ ] Make `Weekly report` query the real database and synthesize diet, exercise, sleep, biomarkers, and active-trial state instead of producing generic advice.
- [ ] Include concrete trend numbers in reports when data exists.
- [ ] Add literature citation formatting that is concise and demo-friendly.
- [ ] Make the protein-sleep question pull the existing `insights` record and present the stored effect size / p-value cleanly.
- [ ] Ensure the experiment-design prompt triggers the intended trial pipeline across `shixiao`, `yuanpan`, and `yizheng`.
- [ ] Ensure `How's my creatine trial going?` reads the real active trial and summarizes status, phase, and compliance.
- [ ] Reduce Telegram response sprawl so demo messages land as crisp structured outputs rather than long essay-style replies.
- [ ] Decide whether Telegram streaming should stay `partial` or switch to a cleaner mode for screen recording.
- [ ] Add a deterministic demo-reset path so we can start from a clean Telegram chat and known DB state before recording.
- [ ] Document the exact demo script that matches the implemented behavior.

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
