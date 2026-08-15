# Bright Data + OpenCode Self-Healing Scraper Canary

This project gives you a controlled canary site and a benchmark harness for testing Bright Data Scraper Studio self-healing while using OpenCode as the inspection/orchestration layer.

## Architecture

Canary site -> Bright Data scraper -> JSON result -> semantic validator -> OpenCode detects regression -> `brightdata scraper heal` -> approval -> rerun -> validator.

Bright Data's CLI has first-class `scraper create`, `scraper run`, `scraper heal`, and `scraper approve` commands. The heal operation keeps the same `collector_id` and normally stops at a human approval gate; `--auto-approve` is available for autonomous trials.

## Files

- `canary_site/`: FastAPI canary with seven markup variants.
- `bench/validate.py`: strict semantic validator against the known dataset.
- `opencode/AGENTS.md`: OpenCode project instructions.
- `opencode/HEAL_PROMPT.md`: repair/evaluation procedure.
- `canary_site/render.yaml`: optional Render deployment definition.

## Local canary

```bash
cd brightdata-self-healing-canary
python -m venv .venv
source .venv/bin/activate
pip install -r canary_site/requirements.txt
uvicorn canary_site.app:app --host 0.0.0.0 --port 8080
```

The page is `http://localhost:8080/`. Bright Data needs to reach the site from the public internet, so for actual CLI scraper tests deploy it publicly (Render is one option) or expose your local server through a secure tunnel.

Set an admin token when deployed:

```bash
export CANARY_ADMIN_TOKEN='a-long-random-token'
```

Change variants on the deployed canary without changing its URL:

```bash
curl -X POST \
  -H "X-Canary-Token: $CANARY_ADMIN_TOKEN" \
  https://YOUR_CANARY_HOST/admin/variant/class_rename
```

Return to baseline:

```bash
curl -X POST \
  -H "X-Canary-Token: $CANARY_ADMIN_TOKEN" \
  https://YOUR_CANARY_HOST/admin/variant/baseline
```

## Bright Data CLI setup

Bright Data currently documents Node.js >=20 for the CLI. Install with:

```bash
npm install -g @brightdata/cli
brightdata login
brightdata budget
```

Or use `brightdata login --api-key ...` / `BRIGHTDATA_API_KEY` in non-interactive environments.

## Create the scraper

Once the canary is publicly reachable, run:

```bash
export CANARY_URL='https://YOUR_CANARY_HOST/'

brightdata scraper create "$CANARY_URL" \
  'Extract every product card from the catalog. Return exactly these fields for every product: id, name, price as an integer number of INR, currency, category, rating as a number, and in_stock as a boolean. Do not infer values that are not present on the page.' \
  --name self-healing-canary --pretty -o outputs/create.json
```

Capture the collector id:

```bash
export COLLECTOR_ID=$(python - <<'PY'
import json
print(json.load(open('outputs/create.json'))['collector_id'])
PY
)
echo "$COLLECTOR_ID"
```

## Baseline test

```bash
brightdata scraper run "$COLLECTOR_ID" "$CANARY_URL" --pretty -o outputs/baseline.json
python bench/validate.py outputs/baseline.json
```

Do not proceed to mutation trials unless baseline validation passes.

## OpenCode

OpenCode can initialize a project with `/init`, which creates `AGENTS.md`, and the CLI supports `opencode run "..."` for non-interactive prompts. Its configuration supports instruction files and MCP servers.

From the repository root:

```bash
opencode
```

Then ask:

```text
Run the self-healing benchmark for the current canary variant. Do not edit canary_site. Run the scraper, validate the JSON semantically, and if it fails use Bright Data scraper heal with a precise prompt. Stop at the approval gate, inspect preview_result, approve only if the preview satisfies the schema, rerun, validate, and record the result.
```

For automation from a shell/CI job, use `opencode run "..."` as documented by OpenCode.

## Benchmark protocol

Use the same collector across all variants so you measure repair of one production-like scraper, not repeated scraper generation.

Recommended variants:

1. `class_rename` - classes and item attribute names change.
2. `nested` - information moves into a definition-list structure.
3. `attribute_rename` - the currency data attribute changes.
4. `text_noise` - marketing/noise nodes are inserted and semantics are exposed as prose.
5. `reorder` - fields move around and price changes representation to a currency-formatted string.
6. `hard_semantic` - labels are paraphrased and item identifiers/classes change.

For each trial:

```text
Set canary variant -> run scraper -> validate -> heal -> approve -> run -> validate
```

Record:

- pre-heal pass/fail
- heal status (`awaiting_approval`, `done`, `failed`, etc.)
- approval required (yes/no)
- post-heal pass/fail
- number of heal attempts
- wall-clock recovery time
- output row count
- field-level correctness
- whether the fix generalized to the next unseen mutation

### Generalization test

After a scraper heals on variant A, do **not** reset or recreate it. Move directly to variant B. This tests whether a fix is robust or overfit.

A stronger protocol is:

`baseline -> A -> B -> C -> D -> E -> F -> baseline`

with a fresh clone of the collector as a control group. Compare the self-healing collector with the untouched control collector on every mutation.

## Metrics

Define:

- **Detection rate** = broken variants correctly identified / broken variants.
- **Healing success rate** = variants passing validation after an accepted heal / healing attempts.
- **Recovery rate** = post-heal semantic passes / injected breakages.
- **MTTR** = median time from first failed validation to a passing post-heal validation.
- **Approval rate** = trials requiring human approval / successful heals.
- **Regression rate** = previously passing variants broken by a later heal.
- **Generalization rate** = unseen mutations passed without another heal / unseen mutations tested.

The key metric is not "did Bright Data say done?" It is **semantic recovery against the oracle** (`/expected` + `bench/validate.py`).

## Important Bright Data behavior

`brightdata scraper heal` is deliberately not a fully autonomous detector: you inspect the output and call heal when it is wrong. The default flow stops at `awaiting_approval`; `--auto-approve` skips that gate. This project keeps both modes separate so you can benchmark human-in-the-loop and autonomous healing independently.
