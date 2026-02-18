# Using SKILL.md as AI Context

`SKILL.md` is a context document that turns any AI assistant into a GEO specialist. It's not a file you deploy to your website — it's a file you give to an AI so it can understand the GEO Optimizer toolkit and help you use it.

Once loaded, the AI knows:
- What GEO is and why it matters
- All three scripts and their flags
- The 9 Princeton methods and their impact
- How to generate `robots.txt` blocks, `llms.txt`, and JSON-LD schema for your specific site

---

## Platform Setup

### Claude Projects

1. Go to [claude.ai](https://claude.ai) → click **Projects** in the sidebar
2. Create a new Project (e.g. "GEO Optimizer")
3. Click **Add content** → **Upload file** → select `SKILL.md`
4. Start a new conversation inside that Project

Claude will have persistent context of `SKILL.md` across every conversation in that Project.

### ChatGPT Custom Instructions

1. Go to [chat.openai.com](https://chat.openai.com) → click your avatar → **Custom Instructions**
2. In the **"What would you like ChatGPT to know about you?"** field, paste the full contents of `SKILL.md`
3. Save and start a new conversation

Note: Custom Instructions have a character limit. If `SKILL.md` is too long, paste the most important sections (the script reference and the 9 methods).

### Gemini Gems

1. Go to [gemini.google.com](https://gemini.google.com) → click **Gems** in the sidebar
2. Click **New Gem** → give it a name (e.g. "GEO Optimizer")
3. In the **Instructions** field, paste the full contents of `SKILL.md`
4. Save the Gem and open it to start a conversation

### Cursor Rules

1. In your project root, create the file `.cursor/rules/geo-optimizer.md`
2. Paste the full contents of `SKILL.md` into that file
3. Cursor automatically loads rules from `.cursor/rules/` for all AI interactions in the project

```bash
mkdir -p .cursor/rules
cp ~/geo-optimizer-skill/SKILL.md .cursor/rules/geo-optimizer.md
```

### Windsurf Rules

1. In your project root, create the file `.windsurf/rules/geo-optimizer.md`
2. Paste the full contents of `SKILL.md` into that file
3. Windsurf loads rules from `.windsurf/rules/` for Cascade AI interactions

```bash
mkdir -p .windsurf/rules
cp ~/geo-optimizer-skill/SKILL.md .windsurf/rules/geo-optimizer.md
```

---

## Platform Comparison

| Platform | Persistence | Best for |
|----------|------------|---------|
| Claude Projects | Project-scoped, persistent | Ongoing GEO work on a specific site |
| ChatGPT Custom Instructions | Account-wide | Quick queries, one-off tasks |
| Gemini Gems | Gem-scoped, persistent | Parallel usage alongside Claude |
| Cursor Rules | Project-scoped, file-based | In-editor schema generation, code injection |
| Windsurf Rules | Project-scoped, file-based | Same as Cursor |

---

## Prompts That Work Well

Copy and paste these directly after loading `SKILL.md`.

**Audit:**
```
Audit my site at https://example.com and give me a prioritized action list.
```

**Generate llms.txt:**
```
Generate llms.txt for my site. Here's my sitemap: https://example.com/sitemap.xml
Site name: MySite
Description: Free calculators for finance and math
```

**Add FAQPage schema:**
```
Add FAQPage schema to this HTML page:
[paste your HTML here]

The page is about mortgage calculators. Write 5 GEO-optimized FAQs.
```

**Write GEO-optimized FAQs:**
```
My site is about personal finance calculators. Write 6 FAQs for GEO optimization.
Each answer should include a specific number, formula, or data point.
Format as JSON ready for the --faq-file flag.
```

**Review robots.txt:**
```
Review my robots.txt for AI bot configuration:
[paste your robots.txt here]

Tell me which citation bots are missing and give me the fixed file.
```

**Generate schema for a specific page:**
```
Generate WebApplication + FAQPage schema for this page:
URL: https://example.com/finance/compound-interest
Title: Compound Interest Calculator
Description: Calculate compound interest growth over time.

Include 4 FAQs about compound interest with specific formulas.
```

---

## Limitations

The AI cannot run the scripts directly — it has no access to your terminal or files. What it can do:

- **Generate commands** ready for you to paste and run
- **Write schema JSON** that you copy into your HTML
- **Write FAQs in JSON format** compatible with `--faq-file`
- **Analyze pasted HTML or robots.txt** and suggest fixes
- **Explain any concept** from the 9 GEO methods in detail

When the AI says *"run this command"*, you run it in your terminal. The AI handles the thinking; the scripts handle the execution.
