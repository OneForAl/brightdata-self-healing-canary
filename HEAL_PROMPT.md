You are operating a Bright Data scraper self-healing benchmark.

Goal: maintain the scraper so it returns exactly 3 catalog products with these semantic fields:
- id
- name
- price (integer INR amount)
- currency
- category
- rating
- in_stock (boolean)

Workflow:
1. Run the existing scraper against CANARY_URL using `brightdata scraper run COLLECTOR_ID CANARY_URL --pretty -o outputs/run.json`.
2. Run `python bench/validate.py outputs/run.json`.
3. If validation fails, inspect the canary page with `brightdata scrape CANARY_URL -f html -o outputs/page.html`.
4. Call `brightdata scraper heal COLLECTOR_ID` with a precise description of what changed and what the correct schema is. Include `--url CANARY_URL`.
5. Prefer the approval-gate mode first. Review `preview_result` and only approve when it satisfies all semantic fields.
6. After approval, rerun the scraper and validator.
7. Record the iteration: variant, validation result before heal, heal status, whether approval was needed, result after heal, and elapsed wall-clock time.

Do not change the canary application during a repair trial. The benchmark is measuring the scraper's ability to recover from site-side changes.
