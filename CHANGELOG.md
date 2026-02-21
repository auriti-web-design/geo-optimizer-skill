# Changelog

All notable changes to GEO Optimizer are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/) · [SemVer](https://semver.org/)

---

## [Unreleased]

### Planned

- JSON output format for `geo_audit.py` (--format json)
- Unit tests with pytest
- PyPI package (`pip install geo-optimizer`)
- Weekly GEO score tracker

---

## [1.1.0] — 2026-02-21

### Added — Infrastructure & Quality

- **GitHub Actions CI/CD** — `.github/workflows/ci.yml`
  - Test matrix: Python 3.8, 3.10, 3.12
  - Syntax check all scripts (py_compile)
  - Lint with flake8 (syntax errors fail build, warnings only)
  - Ready for pytest when tests exist
  
- **CONTRIBUTING.md** — Comprehensive contributor guide
  - Dev setup instructions
  - Conventional Commits standard
  - PR checklist and code style (PEP 8, line length 120)
  - Test writing guidelines
  - Release process (maintainers only)

- **Pinned dependencies** with upper bounds (security + reproducibility)
  - `requests>=2.28.0,<3.0.0`
  - `beautifulsoup4>=4.12.0,<5.0.0`
  - `lxml>=4.9.0,<6.0.0`

- **Improved .gitignore** — pytest_cache, coverage, IDE files, tox, eggs

### Added — Features

- `ai-context/kiro-steering.md` — Kiro steering file with `inclusion: fileMatch`
- Kiro entry in `SKILL.md`, `README.md`, `docs/ai-context.md`
- `meta-externalagent` (Meta AI) added to `AI_BOTS` in `geo_audit.py`

- **schema_injector.py v2.0** — Complete rewrite
  - `--analyze --verbose` — shows full JSON-LD schemas
  - Auto-extract FAQ from HTML (dt/dd, details/summary, CSS classes)
  - `--auto-extract` flag — generate FAQPage from detected FAQ
  - Duplicate schema detection with warnings
  - Better BeautifulSoup parsing (NavigableString + string)
  - Comprehensive error handling for malformed JSON
  - Professional structured output

### Changed — Security & UX

- **README install instructions** — secure method promoted first
  - Now: Download → Inspect → Run (recommended)
  - Then: Pipe to bash (quick but less secure)
  - Addresses enterprise security concerns

### Fixed

- **C1** `geo_audit.py` — score band 41–70 renamed from `FAIR` to `FOUNDATION` in both the printed label (`⚠️  FOUNDATION — Core elements missing…`) and the score band legend
- **C2** `geo_audit.py` — `--verbose` help string updated to `"coming soon — currently has no effect"` (was `"reserved — not yet implemented"`)
- **C2** `README.md` — `--verbose` example in Script Reference marked `# coming soon`
- **C2** `docs/geo-audit.md` — `--verbose` example replaced with coming-soon note; Flags table updated; score band label corrected to `Foundation`
- **C2** `docs/troubleshooting.md` — section 8 "Timeout error" removed the `--verbose` usage advice; replaced with note that `--verbose` is not yet implemented
- **C3** `ai-context/cursor.mdc` — `FacebookBot` → `meta-externalagent` in bot list
- **C3** `ai-context/windsurf.md` — `FacebookBot` → `meta-externalagent` in bot list
- **C3** `ai-context/kiro-steering.md` — `FacebookBot` → `meta-externalagent` in bot list
- **C3** `ai-context/claude-project.md` — `FacebookBot` → `meta-externalagent` in robots.txt block
- **C3** `ai-context/chatgpt-custom-gpt.md` — `FacebookBot` → `meta-externalagent` in robots.txt block
- **C4** `docs/ai-context.md` Windsurf section — format changed to "Plain Markdown — NO YAML frontmatter"; activation updated to "Windsurf UI → Customizations → Rules (4 modes)"; false `### Frontmatter reference` YAML block removed; 4-mode activation table added; platform comparison table updated to "UI activation"
- **I1** `ai-context/cursor.mdc` — `Use HowTo for: step-by-step tutorials` replaced with `Use Article for: blog posts, guides, tutorials`
- **I1** `ai-context/windsurf.md` — same HowTo → Article fix applied
- **I1** `ai-context/kiro-steering.md` — same HowTo → Article fix applied
- **I2** `README.md` — `## 📊 Sample Output` updated with realistic output matching actual script format: 🔍 banner, `============` section headers, bot format `✅ GPTBot allowed ✓`, progress bar `[█████████████████░░░] 85/100`, score label on separate line
- **I3** `ai-context/chatgpt-custom-gpt.md` — STEP 4 schema types extended from `(types: website, webapp, faq)` to `(types: website, webapp, faq, article, organization, breadcrumb)`
- **I4/M1** `SKILL.md` — `windsurf.md` row: size updated from `~4,000 chars` to `~4,500 chars`; Platform limit column updated from `Glob activation (same as Cursor)` to `12,000 chars (UI activation)`
- **I5** `ai-context/chatgpt-custom-gpt.md` — robots.txt block completed: added `claude-web`, `Perplexity-User`, `Applebot-Extended`, `Bytespider`, `cohere-ai`; `FacebookBot` replaced with `meta-externalagent`
- **M2** `ai-context/kiro-steering.md` — removed `"**/*.json"` from `fileMatchPattern` (too broad — matches all JSON files in project)

### Planned

- PyPI package (`pip install geo-optimizer`)
- `--verbose` implementation in `geo_audit.py`
- Weekly GEO score tracker with trend reporting
- Support for Hugo, Jekyll, Nuxt

---

## [1.0.0] — 2026-02-18

### Added

**Scripts**
- `scripts/geo_audit.py` — automated GEO audit, scores any website 0–100
  - Checks: robots.txt (AI bots), /llms.txt (structure + links), JSON-LD schema (WebSite/WebApp/FAQPage), meta tags (title/description/canonical/OG), content quality (headings/statistics/citations)
  - Lazy dependency import — `--help` always works even without dependencies installed
  - Inline comment stripping in robots.txt parser (e.g. `User-agent: GPTBot # note`)
  - Duplicate WebSite schema detection with warning

- `scripts/generate_llms_txt.py` — auto-generates `/llms.txt` from XML sitemap
  - Auto-detects sitemap from robots.txt Sitemap directive
  - Supports sitemap index files (multi-sitemap)
  - Groups URLs by category (Tools, Finance, Blog, etc.)
  - Generates structured markdown with H1, blockquote, sections, links

- `scripts/schema_injector.py` — generates and injects JSON-LD schema
  - Schema types: website, webapp, faq, article, organization, breadcrumb
  - `--analyze`: checks existing HTML file for missing schemas
  - `--astro`: generates complete Astro BaseLayout snippet
  - `--inject`: injects directly into HTML file with automatic backup
  - `--faq-file`: generates FAQPage from JSON file

**AI Context Files** (`ai-context/`)
- `claude-project.md` — full GEO context for Claude Projects (no size limit)
- `chatgpt-custom-gpt.md` — compressed for ChatGPT GPT Builder (<8,000 chars)
- `chatgpt-instructions.md` — ultra-compressed for ChatGPT Custom Instructions (<1,500 chars)
- `cursor.mdc` — Cursor rules format with YAML frontmatter (`globs`, `alwaysApply`)
- `windsurf.md` — Windsurf rules format (plain Markdown, same content as Cursor)

**References** (`references/`)
- `princeton-geo-methods.md` — the 9 GEO methods with measured impact (Princeton KDD 2024)
- `ai-bots-list.md` — 25+ AI crawlers with purpose, vendor, and robots.txt snippets
- `schema-templates.md` — 8 ready-to-use JSON-LD templates

**Documentation** (`docs/`)
- `index.md`, `getting-started.md`, `geo-audit.md`, `llms-txt.md`, `schema-injector.md`
- `ai-context.md`, `geo-methods.md`, `ai-bots-reference.md`, `troubleshooting.md`

**Tooling**
- `install.sh` — one-line installer: clones repo, creates Python venv, installs deps, creates `./geo` wrapper
- `update.sh` — one-command updater via `bash update.sh`
- `requirements.txt` — pinned: requests>=2.28.0, beautifulsoup4>=4.11.0, lxml>=4.9.0
- `SKILL.md` — platform index with file table and quick-copy commands
- Professional README: ASCII banner, collapsible script docs, visual audit output sample, badges
