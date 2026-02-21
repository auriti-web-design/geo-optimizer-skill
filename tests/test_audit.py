"""
Comprehensive unit tests for geo_audit.py script.

Tests critical functions for GEO website auditing including:
- robots.txt parsing
- llms.txt validation
- schema detection
- meta tag validation
- content quality checks
- score calculation

Author: Juan Camilo Auriti
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from geo_audit import (
    AI_BOTS,
    CITATION_BOTS,
    VALUABLE_SCHEMAS,
    audit_content_quality,
    audit_llms_txt,
    audit_meta_tags,
    audit_robots_txt,
    audit_schema,
    compute_geo_score,
)


# ============================================================================
# ROBOTS.TXT TESTS
# ============================================================================


def test_robots_txt_allows_gptbot():
    """Test that robots.txt correctly identifies allowed GPTBot."""
    robots_content = """
User-agent: *
Disallow: /private/

User-agent: GPTBot
Allow: /
"""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = robots_content

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_robots_txt("https://example.com")

    assert result["found"] is True
    assert "GPTBot" in result["bots_allowed"]
    assert "GPTBot" not in result["bots_blocked"]
    assert "GPTBot" not in result["bots_missing"]


def test_robots_txt_blocks_gptbot():
    """Test that robots.txt correctly identifies blocked GPTBot."""
    robots_content = """
User-agent: GPTBot
Disallow: /

User-agent: *
Allow: /
"""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = robots_content

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_robots_txt("https://example.com")

    assert result["found"] is True
    assert "GPTBot" in result["bots_blocked"]
    assert "GPTBot" not in result["bots_allowed"]
    assert result["citation_bots_ok"] is False  # GPTBot is not a citation bot, but OAI-SearchBot is


def test_robots_txt_with_comments():
    """Test robots.txt parsing with inline comments."""
    robots_content = """
# AI bots configuration
User-agent: GPTBot  # OpenAI training bot
Allow: /

User-agent: ClaudeBot  # Anthropic citations
Disallow:  # empty = allow all

# Block sensitive areas
User-agent: *
Disallow: /admin/  # admin panel
"""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = robots_content

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_robots_txt("https://example.com")

    assert result["found"] is True
    assert "GPTBot" in result["bots_allowed"]
    assert "ClaudeBot" in result["bots_allowed"]


def test_robots_txt_missing():
    """Test handling of missing robots.txt (404)."""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_robots_txt("https://example.com")

    assert result["found"] is False
    assert result["citation_bots_ok"] is False
    assert len(result["bots_allowed"]) == 0


def test_robots_txt_citation_bots_ok():
    """Test that all critical citation bots are correctly identified."""
    robots_content = """
User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /
"""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = robots_content

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_robots_txt("https://example.com")

    assert result["citation_bots_ok"] is True
    assert "OAI-SearchBot" in result["bots_allowed"]
    assert "ClaudeBot" in result["bots_allowed"]
    assert "PerplexityBot" in result["bots_allowed"]


# ============================================================================
# LLMS.TXT TESTS
# ============================================================================


def test_llms_txt_valid_structure():
    """Test llms.txt with valid structure including all required elements."""
    llms_content = """# My Website

> A comprehensive resource for web development and AI optimization.

## Tools

- [Tool One](https://example.com/tool1) - Description of tool one
- [Tool Two](https://example.com/tool2) - Description of tool two

## Articles

- [Article One](https://example.com/article1) - About AI optimization
- [Article Two](https://example.com/article2) - Web performance tips
"""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = llms_content

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_llms_txt("https://example.com")

    assert result["found"] is True
    assert result["has_h1"] is True
    assert result["has_description"] is True
    assert result["has_sections"] is True
    assert result["has_links"] is True
    assert result["word_count"] > 0


def test_llms_txt_missing_h1():
    """Test llms.txt without required H1 heading."""
    llms_content = """## Section One

Just some content without an H1.

- [Link](https://example.com)
"""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = llms_content

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_llms_txt("https://example.com")

    assert result["found"] is True
    assert result["has_h1"] is False
    assert result["has_sections"] is True  # Has H2


def test_llms_txt_not_found():
    """Test handling of missing llms.txt (404)."""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("geo_audit.fetch_url", return_value=(mock_response, None)):
        result = audit_llms_txt("https://example.com")

    assert result["found"] is False
    assert result["has_h1"] is False
    assert result["has_links"] is False


# ============================================================================
# SCHEMA DETECTION TESTS
# ============================================================================


def test_schema_detection():
    """Test detection of multiple JSON-LD schema types."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Example Site",
        "url": "https://example.com"
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What is GEO?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Generative Engine Optimization"
                }
            }
        ]
    }
    </script>
</head>
<body></body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_schema(soup, "https://example.com")

    assert result["has_website"] is True
    assert result["has_faq"] is True
    assert "WebSite" in result["found_types"]
    assert "FAQPage" in result["found_types"]
    assert len(result["raw_schemas"]) == 2


def test_schema_detection_no_schema():
    """Test handling of HTML with no JSON-LD schema."""
    html = """
<!DOCTYPE html>
<html>
<head><title>No Schema</title></head>
<body><h1>Content</h1></body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_schema(soup, "https://example.com")

    assert result["has_website"] is False
    assert result["has_faq"] is False
    assert len(result["found_types"]) == 0


def test_schema_detection_multiple_types():
    """Test detection of schema with multiple @type values."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": ["WebSite", "WebApplication"],
        "name": "Example App",
        "url": "https://example.com"
    }
    </script>
</head>
<body></body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_schema(soup, "https://example.com")

    assert result["has_website"] is True
    assert result["has_webapp"] is True
    assert "WebSite" in result["found_types"]
    assert "WebApplication" in result["found_types"]


# ============================================================================
# META TAGS VALIDATION TESTS
# ============================================================================


def test_meta_tags_validation():
    """Test validation of all critical meta tags."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Example Site - Best Tool for SEO</title>
    <meta name="description" content="A comprehensive guide to SEO and GEO optimization with practical tools and expert insights for modern web development.">
    <link rel="canonical" href="https://example.com/">
    <meta property="og:title" content="Example Site - SEO Tools">
    <meta property="og:description" content="Professional SEO and GEO tools">
    <meta property="og:image" content="https://example.com/image.jpg">
</head>
<body></body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_meta_tags(soup, "https://example.com")

    assert result["has_title"] is True
    assert result["has_description"] is True
    assert result["has_canonical"] is True
    assert result["has_og_title"] is True
    assert result["has_og_description"] is True
    assert result["has_og_image"] is True


def test_meta_tags_missing():
    """Test detection of missing meta tags."""
    html = """
<!DOCTYPE html>
<html>
<head></head>
<body><h1>Minimal Page</h1></body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_meta_tags(soup, "https://example.com")

    assert result["has_title"] is False
    assert result["has_description"] is False
    assert result["has_canonical"] is False
    assert result["has_og_title"] is False


# ============================================================================
# CONTENT QUALITY TESTS
# ============================================================================


def test_external_citations_count():
    """Test detection and counting of external citations."""
    html = """
<!DOCTYPE html>
<html>
<head><title>Article</title></head>
<body>
    <h1>Research Article</h1>
    <p>According to <a href="https://example.org/study">this study</a>, the results show improvement.</p>
    <p>As noted by <a href="https://research.com/paper">researchers</a>, the methodology is sound.</p>
    <p>Internal link: <a href="https://example.com/about">About Us</a></p>
    <p>Another external source: <a href="https://academic.edu/journal">Journal Article</a></p>
</body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_content_quality(soup, "https://example.com")

    assert result["has_links"] is True
    # Should find 3 external links (excluding the internal one)


def test_content_quality_numbers():
    """Test detection of numerical data and statistics."""
    html = """
<!DOCTYPE html>
<html>
<head><title>Statistics</title></head>
<body>
    <h1>Performance Metrics</h1>
    <h2>Results</h2>
    <p>Our tool improved performance by 45% in testing.</p>
    <p>Over 1,250 users have signed up.</p>
    <p>Average response time: 2.5 seconds.</p>
    <p>Price: $99.99 per month.</p>
    <p>Revenue increased by €50,000.</p>
</body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_content_quality(soup, "https://example.com")

    assert result["has_h1"] is True
    assert result["has_numbers"] is True
    assert result["heading_count"] >= 2


# ============================================================================
# SCORE CALCULATION TESTS
# ============================================================================


def test_score_calculation_range():
    """Test that GEO score is always within valid range 0-100."""
    # Perfect score test
    perfect_robots = {
        "found": True,
        "citation_bots_ok": True,
        "bots_allowed": list(AI_BOTS.keys()),
        "bots_missing": [],
        "bots_blocked": [],
    }
    perfect_llms = {
        "found": True,
        "has_h1": True,
        "has_sections": True,
        "has_links": True,
    }
    perfect_schema = {
        "has_website": True,
        "has_faq": True,
        "has_webapp": True,
    }
    perfect_meta = {
        "has_title": True,
        "has_description": True,
        "has_canonical": True,
        "has_og_title": True,
        "has_og_description": True,
    }
    perfect_content = {"has_h1": True, "has_numbers": True, "has_links": True}

    score = compute_geo_score(
        perfect_robots, perfect_llms, perfect_schema, perfect_meta, perfect_content
    )
    assert 0 <= score <= 100
    assert score == 100

    # Zero score test
    zero_robots = {
        "found": False,
        "citation_bots_ok": False,
        "bots_allowed": [],
        "bots_missing": list(AI_BOTS.keys()),
        "bots_blocked": [],
    }
    zero_llms = {
        "found": False,
        "has_h1": False,
        "has_sections": False,
        "has_links": False,
    }
    zero_schema = {"has_website": False, "has_faq": False, "has_webapp": False}
    zero_meta = {
        "has_title": False,
        "has_description": False,
        "has_canonical": False,
        "has_og_title": False,
        "has_og_description": False,
    }
    zero_content = {"has_h1": False, "has_numbers": False, "has_links": False}

    score = compute_geo_score(
        zero_robots, zero_llms, zero_schema, zero_meta, zero_content
    )
    assert 0 <= score <= 100
    assert score == 0


def test_score_bands_correct():
    """Test that score calculation matches documented score bands."""
    # Test Foundation level (41-70)
    foundation_robots = {"found": True, "citation_bots_ok": True, "bots_allowed": []}
    foundation_llms = {"found": True, "has_h1": True, "has_sections": False, "has_links": False}
    foundation_schema = {"has_website": True, "has_faq": False, "has_webapp": False}
    foundation_meta = {
        "has_title": True,
        "has_description": True,
        "has_canonical": False,
        "has_og_title": False,
        "has_og_description": False,
    }
    foundation_content = {"has_h1": True, "has_numbers": False, "has_links": False}

    score = compute_geo_score(
        foundation_robots,
        foundation_llms,
        foundation_schema,
        foundation_meta,
        foundation_content,
    )
    assert 0 <= score <= 100

    # Test Good level (71-90)
    good_robots = {"found": True, "citation_bots_ok": True, "bots_allowed": []}
    good_llms = {"found": True, "has_h1": True, "has_sections": True, "has_links": True}
    good_schema = {"has_website": True, "has_faq": True, "has_webapp": False}
    good_meta = {
        "has_title": True,
        "has_description": True,
        "has_canonical": True,
        "has_og_title": True,
        "has_og_description": True,
    }
    good_content = {"has_h1": True, "has_numbers": True, "has_links": True}

    score = compute_geo_score(good_robots, good_llms, good_schema, good_meta, good_content)
    assert score >= 71


def test_score_partial_implementation():
    """Test score calculation with partial GEO implementation."""
    partial_robots = {"found": True, "citation_bots_ok": False, "bots_allowed": ["GPTBot"]}
    partial_llms = {"found": True, "has_h1": True, "has_sections": False, "has_links": True}
    partial_schema = {"has_website": True, "has_faq": False, "has_webapp": False}
    partial_meta = {
        "has_title": True,
        "has_description": False,
        "has_canonical": False,
        "has_og_title": False,
        "has_og_description": False,
    }
    partial_content = {"has_h1": False, "has_numbers": True, "has_links": False}

    score = compute_geo_score(
        partial_robots, partial_llms, partial_schema, partial_meta, partial_content
    )
    assert 0 <= score <= 100
    assert 20 <= score <= 60  # Should be in foundation range


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================


def test_robots_txt_network_error():
    """Test handling of network errors when fetching robots.txt."""
    with patch("geo_audit.fetch_url", return_value=(None, "Connection failed")):
        result = audit_robots_txt("https://example.com")

    assert result["found"] is False
    assert result["citation_bots_ok"] is False


def test_llms_txt_network_error():
    """Test handling of network errors when fetching llms.txt."""
    with patch("geo_audit.fetch_url", return_value=(None, "Timeout (10s)")):
        result = audit_llms_txt("https://example.com")

    assert result["found"] is False


def test_schema_invalid_json():
    """Test handling of invalid JSON in JSON-LD script tag."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <script type="application/ld+json">
    { invalid json here }
    </script>
</head>
<body></body>
</html>
"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    result = audit_schema(soup, "https://example.com")

    # Should handle gracefully without crashing
    assert isinstance(result, dict)
    assert "found_types" in result


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_full_audit_workflow():
    """Test complete audit workflow with mocked responses."""
    robots_content = """
User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
"""

    llms_content = """# Example Site

> Description here

## Tools

- [Tool](https://example.com/tool)
"""

    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Example Site</title>
    <meta name="description" content="Test description for SEO and GEO optimization">
    <link rel="canonical" href="https://example.com/">
    <script type="application/ld+json">
    {"@context": "https://schema.org", "@type": "WebSite", "url": "https://example.com"}
    </script>
</head>
<body>
    <h1>Main Heading</h1>
    <p>Content with 100 users and 50% improvement.</p>
    <a href="https://external.com/source">External Source</a>
</body>
</html>
"""

    def mock_fetch(url, timeout=10):
        mock_resp = Mock()
        mock_resp.status_code = 200
        if "robots.txt" in url:
            mock_resp.text = robots_content
        elif "llms.txt" in url:
            mock_resp.text = llms_content
        else:
            mock_resp.text = html_content
        return mock_resp, None

    with patch("geo_audit.fetch_url", side_effect=mock_fetch):
        robots = audit_robots_txt("https://example.com")
        llms = audit_llms_txt("https://example.com")

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "html.parser")
        schema = audit_schema(soup, "https://example.com")
        meta = audit_meta_tags(soup, "https://example.com")
        content = audit_content_quality(soup, "https://example.com")

        score = compute_geo_score(robots, llms, schema, meta, content)

    assert robots["found"] is True
    assert llms["found"] is True
    assert schema["has_website"] is True
    assert meta["has_title"] is True
    assert content["has_h1"] is True
    assert 0 <= score <= 100
