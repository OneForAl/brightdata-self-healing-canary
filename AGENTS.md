# Self-Healing Scraper Benchmark Agent

This repository benchmarks Bright Data Scraper Studio's AI self-healing against controlled website mutations.

## Safety / measurement rules
- Treat `canary_site/app.py` as the source of truth for expected data.
- Never edit the canary during a heal trial.
- Do not silently weaken the validator to make a failed trial pass.
- Record before/after results and heal status in `outputs/`.
- Prefer human approval mode unless a trial explicitly tests autonomous mode.
- A successful heal means semantic correctness, not merely non-empty output.

## Commands
- Start local canary: `uvicorn canary_site.app:app --reload --port 8080`
- Create scraper: `brightdata scraper create CANARY_URL "Extract ..." --name canary-catalog`
- Run scraper: `brightdata scraper run COLLECTOR_ID CANARY_URL --pretty -o outputs/run.json`
- Validate: `python bench/validate.py outputs/run.json`
- Heal: `brightdata scraper heal COLLECTOR_ID "..." --url CANARY_URL --pretty -o outputs/heal.json`
- Approve: `brightdata scraper approve COLLECTOR_ID --url CANARY_URL --pretty -o outputs/approve.json`
