"""
Formatter GitHub Actions per output audit GEO.

Genera output con annotazioni ``::notice`` e ``::warning`` per
integrazione nativa con GitHub Actions. Usato con ``geo audit --format github``.
"""

from geo_optimizer.models.config import SCORING
from geo_optimizer.models.results import AuditResult


def format_audit_github(result: AuditResult) -> str:
    """Formatta AuditResult con annotazioni GitHub Actions."""
    lines = []

    # Score principale
    band_labels = {
        "excellent": "EXCELLENT",
        "good": "GOOD",
        "foundation": "FOUNDATION",
        "critical": "CRITICAL",
    }
    band_label = band_labels.get(result.band, result.band.upper())

    if result.score >= 71:
        lines.append(f"::notice::GEO Score: {result.score}/100 ({band_label}) — {result.url}")
    elif result.score >= 41:
        lines.append(f"::warning::GEO Score: {result.score}/100 ({band_label}) — {result.url}")
    else:
        lines.append(f"::error::GEO Score: {result.score}/100 ({band_label}) — {result.url}")

    # Check individuali
    checks = [
        ("Robots.txt", _robots_score(result), 20, result.robots.citation_bots_ok),
        ("llms.txt", _llms_score(result), 20, result.llms.found and result.llms.has_h1),
        ("Schema JSON-LD", _schema_score(result), 25, result.schema.has_website),
        ("Meta Tags", _meta_score(result), 20, result.meta.has_title and result.meta.has_description),
        ("Content Quality", _content_score(result), 15, result.content.has_h1),
    ]

    for name, score, max_score, passed in checks:
        if not passed:
            lines.append(f"::warning::{name}: {score}/{max_score}")

    # Raccomandazioni
    for rec in result.recommendations:
        lines.append(f"::warning::{rec}")

    return "\n".join(lines)


def _robots_score(r: AuditResult) -> int:
    if r.robots.citation_bots_ok:
        return SCORING["robots_found"] + SCORING["robots_citation_ok"]
    if r.robots.bots_allowed:
        return SCORING["robots_found"] + SCORING["robots_some_allowed"]
    if r.robots.found:
        return SCORING["robots_found"]
    return 0


def _llms_score(r: AuditResult) -> int:
    s = SCORING["llms_found"] if r.llms.found else 0
    s += SCORING["llms_h1"] if r.llms.has_h1 else 0
    s += SCORING["llms_sections"] if r.llms.has_sections else 0
    s += SCORING["llms_links"] if r.llms.has_links else 0
    return s


def _schema_score(r: AuditResult) -> int:
    s = SCORING["schema_website"] if r.schema.has_website else 0
    s += SCORING["schema_faq"] if r.schema.has_faq else 0
    s += SCORING["schema_webapp"] if r.schema.has_webapp else 0
    return s


def _meta_score(r: AuditResult) -> int:
    s = SCORING["meta_title"] if r.meta.has_title else 0
    s += SCORING["meta_description"] if r.meta.has_description else 0
    s += SCORING["meta_canonical"] if r.meta.has_canonical else 0
    s += SCORING["meta_og"] if (r.meta.has_og_title and r.meta.has_og_description) else 0
    return s


def _content_score(r: AuditResult) -> int:
    s = SCORING["content_h1"] if r.content.has_h1 else 0
    s += SCORING["content_numbers"] if r.content.has_numbers else 0
    s += SCORING["content_links"] if r.content.has_links else 0
    return s
