# The 9 Princeton GEO Methods

Research-backed content optimization techniques for AI citation visibility, from the Princeton KDD 2024 study.

---

## Background

**Paper:** "GEO: Generative Engine Optimization" — Aggarwal et al., KDD 2024  
**Link:** [arxiv.org/abs/2311.09735](https://arxiv.org/abs/2311.09735)  
**Dataset:** [generative-engines.com/GEO](https://generative-engines.com/GEO/)  
**Methodology:** 10,000 real queries across diverse domains on Perplexity.ai; GPT-4 simulated responses

The study measured three signals: word count overlap (how much of your content appears in the AI response), rank position (where your source is cited), and citation frequency.

**Key finding:** Certain content modifications significantly increase the probability of being cited. The top method produces up to +115% visibility for rank-5 citation positions.

---

## Method 1 — Cite Sources

**Measured impact: +30–115% AI visibility**

Link to authoritative external sources inline in your content. This is the single highest-impact method in the study. AI engines use citations as a trust signal: if your page already cites authoritative sources, it looks more credible and is more likely to be cited itself.

**Apply when:** Making any factual claim — statistics, cause-effect statements, comparisons, medical or financial advice.

```diff
- Fixed-rate mortgages are safer during periods of inflation.
+ According to the [Federal Reserve](https://federalreserve.gov), fixed-rate mortgages
+ better protect borrowers during inflationary periods exceeding 3%, as they lock in
+ the rate before central bank adjustments take effect.
```

Prefer linking to: academic papers, government domains (`.gov`, `.edu`), industry reports, official vendor documentation.

---

## Method 2 — Statistics

**Measured impact: +40% average AI visibility**

Replace vague claims with specific, verifiable numerical data. AI engines prefer content with concrete facts — numbers, percentages, dates, study results — because they are easy to extract and verify.

**Apply when:** Describing frequency, scale, comparison, cost, or performance of anything.

```diff
- Many Americans invest in mutual funds.
+ 34.2% of Americans hold mutual fund shares (Morningstar, 2024),
+ with total assets under management exceeding $23 trillion —
+ up from $19.6 trillion in 2020.
```

Always specify the source and year. Avoid statistics older than 3 years unless they are historical baselines.

---

## Method 3 — Quotation Addition

**Measured impact: +30–40% AI visibility**

Include direct quotes from domain experts, researchers, or official documents. Quotation marks signal attribution and verifiability, which AI engines interpret as a quality signal.

**Apply when:** Covering YMYL (Your Money, Your Life) topics — finance, health, legal. Also effective for history and science.

```diff
- A fixed rate is a good choice when market rates are low.
+ "A fixed rate is the right choice when market rates fall below the historical
+ 10-year average," notes John Smith, Head of Mortgage Lending at Bloomberg (2024).
+ "Locking in a low rate protects borrowers from the volatility typical of
+ central bank tightening cycles."
```

Format: `"Quote" — Name, Role, Organization, Year`

---

## Method 4 — Authoritative Tone

**Measured impact: +6–12% average AI visibility**

Write with an expert voice. Eliminate vague hedging language and replace it with precise, structured explanations. Use the format: definition → how it works → practical implications.

**Apply when:** Explaining any technical concept, process, or recommendation.

```diff
- A mortgage might be right for you if you need to buy a house and you
- don't have all the money.
+ A mortgage is a long-term financing instrument (15–30 years) secured by
+ a lien on the property. The monthly payment covers principal reduction
+ and interest calculated on the agreed rate — fixed (constant APR) or
+ variable (indexed to SOFR or Euribor with a bank spread).
```

Eliminate: "often", "generally", "might", "could be", "in some cases". Replace with precise scope statements: "in 80% of cases", "for loans above $500,000", "when the LTV exceeds 80%".

---

## Method 5 — Fluency Optimization

**Measured impact: +15–30% AI visibility**

Improve text flow and readability. LLMs extract information more reliably from well-structured, grammatically correct prose. Choppy or error-prone text is harder to parse and cite.

**Apply when:** Revising any existing page — this is a universal improvement.

```diff
- The mortgage calculation, which is done by the bank, depends on the rate.
- The rate can be fixed or variable. You need to choose.
+ The monthly payment calculation depends primarily on the rate type selected.
+ A fixed rate guarantees stable payments throughout the loan term, while a
+ variable rate adjusts periodically based on market benchmarks such as SOFR
+ — meaning payments can increase or decrease over time.
```

Target: sentences of 15–25 words. Use logical connectives: "therefore", "however", "consequently", "in particular". Each paragraph should have a clear topic sentence.

---

## Method 6 — Easy-to-Understand

**Measured impact: +8–15% AI visibility**

Simplify without losing precision. AI engines can more reliably extract and paraphrase content that is clearly explained. Add brief in-context definitions for technical terms.

**Apply when:** Your audience includes non-experts, or when you cover jargon-heavy topics.

```diff
- The loan-to-value ratio influences the LTV of collateral guarantees.
+ The loan-to-value ratio (LTV) measures how much of the property price
+ you are borrowing. An LTV of 80% means you finance 80% of the home's
+ value, with the remaining 20% as your down payment. Most lenders
+ require private mortgage insurance (PMI) for LTVs above 80%.
```

Two-level structure: plain explanation first, technical details second. Add a glossary section for pages with 5+ domain-specific terms.

---

## Method 7 — Unique Words

**Measured impact: +5–8% AI visibility**

Vary vocabulary. Avoid repeating the same term in consecutive sentences; use contextually appropriate synonyms. A varied vocabulary signals content quality to language models.

**Apply when:** Reviewing finished content for over-repetition. Lower priority than methods 1–6.

```diff
- The calculator calculates your mortgage calculation automatically.
- You can calculate different calculation scenarios.
+ The calculator computes your mortgage payment automatically.
+ You can model different repayment scenarios and compare outcomes.
```

Note: this method has lower impact than the others — prioritize it last.

---

## Method 8 — Technical Terms

**Measured impact: +5–10% for specialized queries**

Use correct, industry-standard terminology. Relevant for expert users searching with technical vocabulary. Works best in combination with Authoritative and Cite Sources.

**Apply when:** Your audience includes professionals or experts; for finance, health, science, legal content.

```diff
- The loan interest rate changes based on the market.
+ The loan's variable APR (Annual Percentage Rate) adjusts quarterly
+ based on the SOFR 3-month benchmark plus the bank's credit spread,
+ following standard French amortization for each recalculated period.
```

Include official acronyms with their full form on first use: `APR (Annual Percentage Rate)`, `LTV (Loan-to-Value)`, `EBITDA`.

---

## Method 9 — Keyword Stuffing ⚠️

**Measured impact: Neutral or NEGATIVE**

The Princeton study tested keyword density manipulation — forcefully repeating target keywords throughout the content. The result: no significant improvement in AI visibility, and in some cases a net negative effect by degrading fluency scores.

This is a carryover from traditional SEO. **Do not apply it for GEO.**

Instead: use Fluency Optimization + Cite Sources + Statistics.

---

## Implementation Strategy

### Phase 1 — Quick Wins (Days 1–3)

Focus on the two highest-ROI methods first.

1. **Statistics** — Go through your top 5 pages. Find every vague claim ("many users", "significant improvement") and replace it with a specific number. Add the source and year.
2. **Cite Sources** — Add 2–3 inline links to authoritative sources per page. Use `According to [Source](URL), ...` format.
3. **Fluency** — Paste each page through Grammarly or LanguageTool. Fix errors and break up sentences over 40 words.

### Phase 2 — Structural Optimization (Days 4–10)

4. **Quotation Addition** — Find 1–2 quotable experts per topic. Add direct quotes with attribution.
5. **Authoritative Tone** — Rewrite introductions and summaries using the definition → explanation → implication structure.
6. **Technical Terms** — Audit your use of acronyms and jargon. Add full forms on first use.

### Phase 3 — Fine Tuning (Ongoing)

7. **Easy-to-Understand** — Add inline definitions for technical terms. Build a glossary page.
8. **Unique Words** — Final pass to remove repeated words and vary vocabulary.

---

## Impact by Domain

| Method | Finance | Health | Science | History | Media |
|--------|---------|--------|---------|---------|-------|
| Cite Sources | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Statistics | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Quotation Addition | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Authoritative Tone | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| Fluency Optimization | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Easy-to-Understand | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ |
| Technical Terms | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| Unique Words | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| Keyword Stuffing | ❌ | ❌ | ❌ | ❌ | ❌ |

⭐⭐⭐ High impact · ⭐⭐ Moderate · ⭐ Low · ❌ Avoid

---

## References

- Paper: [https://arxiv.org/abs/2311.09735](https://arxiv.org/abs/2311.09735)
- GEO-bench dataset: [https://generative-engines.com/GEO/](https://generative-engines.com/GEO/)
- KDD 2024 Conference: August 25–29, 2024, Barcelona
