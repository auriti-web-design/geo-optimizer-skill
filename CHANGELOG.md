# Changelog

All notable changes to GEO Optimizer are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/) · [SemVer](https://semver.org/)

---

## [Unreleased]

- PyPI package (`pip install geo-optimizer`)
- Weekly GEO score tracker with trend reporting
- Support for Hugo, Jekyll, Nuxt

---

## [1.3.0] — 2026-02-18

### Added

- `ai-context/kiro-steering.md` — Kiro steering file with `inclusion: fileMatch` + `fileMatchPattern` array; place in `.kiro/steering/`
- Kiro entry in `SKILL.md`, `README.md`, `docs/ai-context.md` (setup, frontmatter reference, platform comparison)
- `meta-externalagent` (Meta AI/Facebook/Instagram) added to `AI_BOTS` check in `geo_audit.py`
- `ai-context/cursor.mdc` — Cursor rules format with YAML frontmatter (`globs`, `alwaysApply`)
- `ai-context/windsurf.md` — Windsurf rules format with YAML frontmatter + glob activation
- `ai-context/claude-project.md` — full GEO context for Claude Projects (no size limit)
- `ai-context/chatgpt-custom-gpt.md` — compressed for ChatGPT GPT Builder (<8,000 chars)
- `ai-context/chatgpt-instructions.md` — ultra-compressed for ChatGPT Custom Instructions (<1,500 chars)
- Complete documentation suite (`docs/`) — 8 pages covering all scripts, methods, and platform setup
- `SKILL.md` — universal platform index with file table and quick-copy commands
- Professional README redesign: collapsible script docs, visual audit output sample, badges

### Fixed

- `ai-context/windsurf.md` — added YAML frontmatter with `description` and `globs` (Windsurf supports same format as Cursor; doc was incorrect)
- `docs/ai-context.md` — corrected claim that Windsurf doesn't support YAML frontmatter; updated Windsurf section
- `geo_audit.py` — schema scoring redistributed: `WebSite=10pt`, `FAQPage=10pt`, `WebApplication=5pt` (webapp is bonus, not core; blogs can now reach 100)
- `geo_audit.py` — score thresholds aligned to documentation: `>=91 EXCELLENT`, `>=71 GOOD`, `>=41 FAIR`, `<41 CRITICAL`
- `geo_audit.py` — score band note printed below score to explain each range
- `docs/geo-audit.md` — score band table and schema scoring description updated to match code
- `install.sh` — added note that `--dir` flag cannot be used with `curl | bash` (flag goes to `bash`, not the script)
- `README.md` / `docs/getting-started.md` — added note with correct custom-path install procedure
- Lazy dependency imports — `--help` always works even without dependencies installed
- Inline comment stripping in robots.txt parser (e.g. `User-agent: GPTBot # note`)
- Duplicate WebSite schema detection now emits a warning
- Removed all hardcoded site-specific references — fully generic examples throughout
- Removed all OpenClaw internal references — fully standalone tool

### Changed

- README rewritten as public-facing documentation (professional layout)
- `SKILL.md` rewritten as universal AI context index (all 6 platforms)
- All user-visible messages and script docstrings use `./geo` prefix consistently
- `update.sh` is now venv-aware

---

## [1.2.0] — 2026-02-18

### Changed

- Full English translation of all files (README, SKILL.md, inline comments, docstrings)
- README rewritten with cleaner structure, Quick Start path clarified

### Fixed

- Italian comments removed from scripts
- CHANGELOG rewritten for public audience (removed internal notes)
- `ai-bots-list.md` dates updated to 2026

---

## [1.1.0] — 2026-02-18

### Fixed

- Relative paths throughout — no more hardcoded absolute paths
- Duplicate `PerplexityBot` entry removed from `AI_BOTS` dict
- Astro examples made fully generic (no site-specific names)
- GEO score calculation now reflects actual achievable scores

### Changed

- SKILL.md updated with corrected paths and examples
- README sections improved for clarity

---

## [1.0.0] — 2026-02-18

### Added

**Scripts**
- `scripts/geo_audit.py` — automated GEO audit, scores any website 0–100
  - Checks: robots.txt (13 AI bots), /llms.txt (structure + links), JSON-LD schema (WebSite/WebApp/FAQPage), meta tags (title/description/canonical/OG), content quality (headings/statistics/citations)
  - Lazy dependency import — `--help` always works even without dependencies installed
  - Inline comment stripping in robots.txt parser (e.g. `User-agent: GPTBot # note`)
  - Duplicate WebSite schema detection with warning

- `scripts/generate_llms_txt.py` — auto-generates `/llms.txt` from XML sitemap
  - Auto-detects sitemap from robots.txt Sitemap directive
  - Supports sitemap index files (multi-sitemap)
  - Groups URLs by category (Tools, Finance, Blog, etc.)
  - Generates structured markdown with H1, blockquote, sections, links
  - Lazy dependency import — `--help` always works

- `scripts/schema_injector.py` — generates and injects JSON-LD schema
  - Schema types: website, webapp, faq, article, organization, breadcrumb
  - `--analyze`: checks existing HTML file for missing schemas (requires `--file`)
  - `--astro`: generates complete Astro BaseLayout snippet
  - `--inject`: injects directly into HTML file with automatic backup
  - `--faq-file`: generates FAQPage from JSON file
  - FAQ placeholder mode with `REPLACE:` markers and warning

**References** (`references/`)
- `princeton-geo-methods.md` — the 9 GEO methods with measured impact (Princeton KDD 2024)
- `ai-bots-list.md` — 25+ AI crawlers with purpose, vendor, and robots.txt snippets
- `schema-templates.md` — 8 ready-to-use JSON-LD templates with `YOUR_LANGUAGE_CODE` placeholder

**Tooling**
- `install.sh` — one-line installer: clones repo, creates Python venv, installs deps, creates `./geo` wrapper
- `update.sh` — one-command updater via `bash update.sh`
- `requirements.txt` — pinned: requests>=2.28.0, beautifulsoup4>=4.11.0, lxml>=4.9.0
- `SKILL.md` — platform index with file table and quick-copy commands
- Professional README: ASCII banner, collapsible script docs, visual audit output sample, GitHub badges
