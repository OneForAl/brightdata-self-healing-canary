# Bright Data self-healing canary — Vercel deployment

This is the Vercel-compatible version of the canary site.

## Deploy

Deploy this directory as the root of your Vercel project. Vercel will detect `api/index.py` as a Python Function. The rewrite maps `/` and the other public paths to that function.

## Configure a mutation

In Vercel Project Settings → Environment Variables, set:

`CANARY_VARIANT=baseline`

Deploy. Verify:

`https://YOUR-DOMAIN/health`

Then change `CANARY_VARIANT` to one of:

- baseline
- class_rename
- nested
- attribute_rename
- text_noise
- reorder
- hard_semantic

Redeploy after each change. Keep the public URL unchanged.

## Important benchmark note

Vercel Functions are stateless/serverless, so the old `/admin/variant/<variant>` runtime mutation design is not appropriate here. For a Vercel canary, change the environment variable and redeploy each variant. The scraper still sees the same URL.
