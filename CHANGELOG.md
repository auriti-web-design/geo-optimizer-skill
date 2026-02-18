# Changelog — geo-optimizer

All notable changes to this skill will be documented here.

Format: [SemVer](https://semver.org/) — `MAJOR.MINOR.PATCH`

---

## [1.0.0] — 2026-02-18

### 🎉 First Release

Initial complete implementation of the GEO Optimizer skill for OpenClaw.

#### Included
- **SKILL.md** — Full workflow based on Princeton GEO research (9 methods)
- **`scripts/geo_audit.py`** — Automated GEO audit: robots.txt, llms.txt, schema, meta tags
- **`scripts/generate_llms_txt.py`** — Auto-generates `llms.txt` from sitemap or manual URL list
- **`scripts/schema_injector.py`** — Injects WebApplication + FAQPage JSON-LD schema into HTML
- **`references/princeton-geo-methods.md`** — Summary of the 9 Princeton GEO optimization methods
- **`references/ai-bots-list.md`** — Complete list of AI crawler User-Agents (GPTBot, PerplexityBot, etc.)
- **`references/schema-templates.md`** — Ready-to-use JSON-LD schema templates

#### Proven results (tested on calcfast.online)
- `robots.txt` updated with 8 AI crawlers
- `llms.txt` generated with 60+ calculators and structured fiscal data
- FAQPage + WebApplication schema on top calculators
- Google Indexing API integration (150 URL/day quota-safe)

---

## [Unreleased]

- EN language support for llms.txt generation
- ClawHub marketplace listing
- Automated weekly GEO score tracker cron
