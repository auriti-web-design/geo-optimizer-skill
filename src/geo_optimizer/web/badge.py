"""
Generatore Badge SVG dinamico per GEO Score.

Genera un badge SVG simile a Shields.io con il GEO Score del sito.
Embeddabile in README, footer, portfolio.

Uso in Markdown:
    [![GEO Score](https://geo.auritidesign.it/badge?url=https://yoursite.com)](https://geo.auritidesign.it/)
"""

import html as html_lib

# Colori per fascia di score
BAND_COLORS = {
    "excellent": "#22c55e",  # Verde scuro
    "good": "#06b6d4",  # Ciano
    "foundation": "#eab308",  # Arancione
    "critical": "#ef4444",  # Rosso
}

# Lunghezza massima label per prevenire abusi
_MAX_LABEL_LENGTH = 50


def _svg_escape(text: str) -> str:
    """Escape caratteri speciali XML/SVG per prevenire XSS.

    Converte <, >, &, " e ' nelle entità XML corrispondenti.
    """
    return html_lib.escape(text, quote=True)


def generate_badge_svg(score: int, band: str, label: str = "GEO Score") -> str:
    """Genera badge SVG con score e colore per fascia.

    Args:
        score: Punteggio 0-100.
        band: Fascia (excellent, good, foundation, critical).
        label: Etichetta lato sinistro del badge (max 50 char, sanitizzata).

    Returns:
        Stringa SVG completa.
    """
    # Valida band contro whitelist
    if band not in BAND_COLORS:
        band = "critical"
    color = BAND_COLORS[band]

    # Clamp score nel range valido
    score = max(0, min(100, score))
    score_text = f"{score}/100"

    # Tronca e sanitizza label contro XSS
    label = label[:_MAX_LABEL_LENGTH]
    safe_label = _svg_escape(label)

    # Calcola larghezze basate sul testo originale (non escapato)
    label_width = len(label) * 6.5 + 12
    score_width = len(score_text) * 7 + 12
    total_width = label_width + score_width

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{safe_label}: {score_text}">
  <title>{safe_label}: {score_text}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{score_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text aria-hidden="true" x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{safe_label}</text>
    <text x="{label_width / 2}" y="14">{safe_label}</text>
    <text aria-hidden="true" x="{label_width + score_width / 2}" y="15" fill="#010101" fill-opacity=".3">{score_text}</text>
    <text x="{label_width + score_width / 2}" y="14">{score_text}</text>
  </g>
</svg>"""
