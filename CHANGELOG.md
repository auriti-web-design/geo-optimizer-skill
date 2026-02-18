# Changelog

All notable changes to GEO Optimizer are documented here.  
Format: [SemVer](https://semver.org/) — `MAJOR.MINOR.PATCH`

---

## [1.2.0] — 2026-02-18

### Added
- `SKILL.md` rewritten as a universal AI context document — works with Claude Projects, ChatGPT Custom Instructions, Gemini Gems, Cursor Rules, Windsurf Rules
- Framework implementation examples: Astro, Next.js (full WebSite + WebApplication + FAQPage), WordPress
- `install.sh` — one-line installer with automatic Python venv setup and `./geo` wrapper
- `update.sh` — one-command updater (`bash update.sh`)
- `requirements.txt`, `LICENSE` (MIT), `.gitignore`
- "Why Star This Repo?" section in README with before/after comparison table
- "Requirements" section in README
- `## ✅ Requirements` section before Installation in README

### Changed
- Project renamed from "GEO Optimizer Skill" to **GEO Optimizer**
- All documentation fully translated to English
- README restructured: AI context section promoted to top, requirements visible before install
- Quick Start unified to use `./geo` wrapper consistently
- Installation: now uses isolated Python venv (compatible with all systems including Debian/Ubuntu)

### Fixed
- Removed all environment-specific absolute paths
- Removed duplicate `PerplexityBot` entry in robots.txt block
- Corrected GEO Score example in README (85/100, measured on real site)
- Removed all references to private projects and internal tooling

---

## [1.0.0] — 2026-02-18

### 🎉 First Release

Initial release of GEO Optimizer.

#### Included
- **`scripts/geo_audit.py`** — Automated GEO audit: scores your site 0–100, checks robots.txt, llms.txt, JSON-LD schema, meta tags, content quality
- **`scripts/generate_llms_txt.py`** — Auto-generates `llms.txt` from XML sitemap with URL categorization
- **`scripts/schema_injector.py`** — Generates and injects JSON-LD schema (WebSite, WebApplication, FAQPage, Article, Organization, BreadcrumbList)
- **`references/princeton-geo-methods.md`** — The 9 Princeton GEO methods with impact data and implementation examples
- **`references/ai-bots-list.md`** — Complete list of AI crawler user-agents (25+) with robots.txt snippets
- **`references/schema-templates.md`** — Ready-to-use JSON-LD templates for 8 schema types

---

## [Unreleased]

- GEO score tracker — weekly automated audit with trend reporting
- PyPI package (`pip install geo-optimizer`)
- Support for additional site frameworks (Hugo, Jekyll, Nuxt)
