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

## [1.1.0] — 2026-02-18

### 🔧 Fix & Miglioramenti

- **Fix critico**: rimossi tutti i path assoluti hardcoded dal SKILL.md — ora tutti i comandi usano path relativi (`python scripts/...`)
- **Fix**: rimosso `source /home/openclaw/...` dal Quick Start — ora basta `pip install requests beautifulsoup4`
- **Fix**: rimosso duplicato `PerplexityBot` nel blocco robots.txt
- **Fix**: sezione "Implementazione Astro" generalizzata — rimossi riferimenti a `calcfast.online`, aggiunti props `siteUrl`/`siteName`/`isTool` generici
- **Fix**: GEO Score nel README aggiornato con dato reale da script (85/100, non 78)
- **Miglioramento**: Quick Start nel README include step `git clone`
- **Bump version**: `1.0.0` → `1.1.0`

## [Unreleased]

- EN language support per SKILL.md (audience internazionale ClawHub)
- ClawHub marketplace listing
- Automated weekly GEO score tracker cron
- Test end-to-end su siti diversi da CalcFast
