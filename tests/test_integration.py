"""
Integration tests for geo-optimizer-skill CLI scripts.

Tests the scripts as they would be used by end users:
- Correct exit codes
- Valid JSON output
- Proper error handling
- Command-line argument parsing

All network calls are mocked -- no real HTTP requests are made.

Author: Juan Camilo Auriti
"""

import json
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.legacy

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

# Add scripts directory to path for direct imports
sys.path.insert(0, str(SCRIPTS_DIR))


def run_script(script_name, args, timeout=30):
    """
    Run a script and return CompletedProcess.

    Args:
        script_name (str): Script filename (e.g., 'geo_audit.py')
        args (list): Command-line arguments
        timeout (int): Timeout in seconds

    Returns:
        subprocess.CompletedProcess
    """
    cmd = [sys.executable, str(SCRIPTS_DIR / script_name)] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )


# ============================================================================
# MOCK HELPERS
# ============================================================================

SAMPLE_HTML = """\
<!DOCTYPE html>
<html>
<head>
    <title>Example Domain</title>
    <meta name="description" content="This domain is for use in illustrative examples in documents." />
    <meta property="og:title" content="Example Domain" />
    <meta property="og:description" content="This domain is for use in illustrative examples." />
    <meta property="og:image" content="https://example.com/image.png" />
    <link rel="canonical" href="https://example.com" />
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Example",
        "url": "https://example.com"
    }
    </script>
</head>
<body>
    <h1>Example Domain</h1>
    <h2>About this site</h2>
    <h3>Details</h3>
    <p>This domain is for use in illustrative examples in documents.
    You may use this domain in literature without prior coordination or asking for permission.
    It has been established by IANA with 1000 users and a 99.9% uptime record since 2004.
    The site receives approximately 500,000 visits per month.</p>
    <p>More information: <a href="https://www.iana.org/domains/example">IANA reference</a></p>
</body>
</html>"""

SAMPLE_ROBOTS_TXT = """\
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /
"""

SAMPLE_LLMS_TXT = """\
# Example Site

> This is an example site for documentation purposes.

## Main Pages

- [Homepage](https://example.com)
- [About](https://example.com/about)

## Documentation

- [Getting Started](https://example.com/docs/getting-started)
"""

SAMPLE_SITEMAP_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/</loc>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://example.com/about</loc>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://example.com/docs/getting-started</loc>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://example.com/blog/first-post</loc>
        <priority>0.5</priority>
    </url>
</urlset>
"""


def _make_mock_response(text, status_code=200, content=None):
    """Create a mock HTTP response."""
    resp = Mock()
    resp.status_code = status_code
    resp.text = text
    resp.content = (content or text).encode("utf-8") if isinstance(text, str) else text
    resp.headers = {"Content-Type": "text/html"}
    resp.elapsed = Mock()
    resp.elapsed.total_seconds = Mock(return_value=0.1)
    return resp


# ============================================================================
# GEO_AUDIT.PY INTEGRATION TESTS
# ============================================================================


def test_geo_audit_help():
    """Test that --help works and exits with code 0."""
    result = run_script("geo_audit.py", ["--help"])
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower() or "geo audit" in result.stdout.lower()


def test_geo_audit_missing_url():
    """Test that missing --url argument causes non-zero exit."""
    result = run_script("geo_audit.py", [])
    assert result.returncode != 0


@pytest.mark.network
def test_geo_audit_invalid_url():
    """Test that invalid URL format causes non-zero exit."""
    result = run_script("geo_audit.py", ["--url", "not-a-valid-url"])
    # Should exit with error (network failure or validation)
    assert result.returncode != 0


def test_geo_audit_json_output_structure():
    """Test that --format json produces valid JSON with expected structure."""
    import geo_audit

    homepage_resp = _make_mock_response(SAMPLE_HTML)
    robots_resp = _make_mock_response(SAMPLE_ROBOTS_TXT)
    llms_resp = _make_mock_response(SAMPLE_LLMS_TXT)

    def mock_fetch_url(url, timeout=10):
        if "robots.txt" in url:
            return robots_resp, None
        elif "llms.txt" in url:
            return llms_resp, None
        else:
            return homepage_resp, None

    with patch.object(geo_audit, "fetch_url", side_effect=mock_fetch_url), \
         patch("sys.argv", ["geo_audit.py", "--url", "https://example.com", "--format", "json"]):
        # Capture stdout
        captured = StringIO()
        with patch("sys.stdout", captured):
            try:
                geo_audit.main()
            except SystemExit:
                pass

    output = captured.getvalue()
    data = json.loads(output)

    # Validate JSON structure
    assert "url" in data
    assert "score" in data
    assert isinstance(data["score"], (int, float))
    assert 0 <= data["score"] <= 100
    assert "band" in data
    assert "checks" in data
    assert "recommendations" in data

    # Validate check sections exist
    expected_checks = ["robots_txt", "llms_txt", "schema_jsonld", "meta_tags", "content"]
    for check in expected_checks:
        assert check in data["checks"], f"Missing check section: {check}"
        assert "score" in data["checks"][check]
        assert "max" in data["checks"][check]
        assert "passed" in data["checks"][check]
        assert "details" in data["checks"][check]


def test_geo_audit_text_output_default():
    """Test that default output format is text (not JSON)."""
    import geo_audit

    homepage_resp = _make_mock_response(SAMPLE_HTML)
    robots_resp = _make_mock_response(SAMPLE_ROBOTS_TXT)
    llms_resp = _make_mock_response(SAMPLE_LLMS_TXT)

    def mock_fetch_url(url, timeout=10):
        if "robots.txt" in url:
            return robots_resp, None
        elif "llms.txt" in url:
            return llms_resp, None
        else:
            return homepage_resp, None

    with patch.object(geo_audit, "fetch_url", side_effect=mock_fetch_url), \
         patch("sys.argv", ["geo_audit.py", "--url", "https://example.com"]):
        captured = StringIO()
        with patch("sys.stdout", captured):
            try:
                geo_audit.main()
            except SystemExit:
                pass

    output = captured.getvalue()

    # Text output should NOT be valid JSON
    try:
        json.loads(output)
        pytest.fail("Default output should be text, not JSON")
    except json.JSONDecodeError:
        pass  # Expected: text output is not JSON

    # Text output should contain score information
    assert "GEO" in output or "score" in output.lower() or "/100" in output


def test_geo_audit_output_file():
    """Test that --output flag writes JSON to file."""
    import geo_audit

    homepage_resp = _make_mock_response(SAMPLE_HTML)
    robots_resp = _make_mock_response(SAMPLE_ROBOTS_TXT)
    llms_resp = _make_mock_response(SAMPLE_LLMS_TXT)

    def mock_fetch_url(url, timeout=10):
        if "robots.txt" in url:
            return robots_resp, None
        elif "llms.txt" in url:
            return llms_resp, None
        else:
            return homepage_resp, None

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name

    try:
        with patch.object(geo_audit, "fetch_url", side_effect=mock_fetch_url), \
             patch("sys.argv", [
                 "geo_audit.py", "--url", "https://example.com",
                 "--format", "json", "--output", output_path
             ]):
            captured = StringIO()
            with patch("sys.stdout", captured):
                try:
                    geo_audit.main()
                except SystemExit:
                    pass

        # Check file was created
        assert Path(output_path).exists()

        # Check file contains valid JSON
        file_size = Path(output_path).stat().st_size
        assert file_size > 0, "Output file should not be empty"

        with open(output_path, 'r') as f:
            data = json.load(f)

        assert "url" in data
        assert "score" in data
        assert "checks" in data
    finally:
        Path(output_path).unlink(missing_ok=True)


def test_geo_audit_json_network_error():
    """Test that JSON output handles network errors gracefully."""
    import geo_audit

    def mock_fetch_url(url, timeout=10):
        return None, "Connection refused"

    with patch.object(geo_audit, "fetch_url", side_effect=mock_fetch_url), \
         patch("sys.argv", [
             "geo_audit.py", "--url", "https://example.com", "--format", "json"
         ]):
        captured = StringIO()
        with patch("sys.stdout", captured):
            with pytest.raises(SystemExit) as exc_info:
                geo_audit.main()

        assert exc_info.value.code == 1

    output = captured.getvalue()
    data = json.loads(output)
    assert "error" in data
    assert "url" in data


def test_geo_audit_score_range():
    """Test that the computed score falls within valid range for a well-configured site."""
    import geo_audit

    homepage_resp = _make_mock_response(SAMPLE_HTML)
    robots_resp = _make_mock_response(SAMPLE_ROBOTS_TXT)
    llms_resp = _make_mock_response(SAMPLE_LLMS_TXT)

    def mock_fetch_url(url, timeout=10):
        if "robots.txt" in url:
            return robots_resp, None
        elif "llms.txt" in url:
            return llms_resp, None
        else:
            return homepage_resp, None

    with patch.object(geo_audit, "fetch_url", side_effect=mock_fetch_url), \
         patch("sys.argv", [
             "geo_audit.py", "--url", "https://example.com", "--format", "json"
         ]):
        captured = StringIO()
        with patch("sys.stdout", captured):
            try:
                geo_audit.main()
            except SystemExit:
                pass

    output = captured.getvalue()
    data = json.loads(output)

    score = data["score"]
    assert 0 <= score <= 100
    # With our mocked data (robots OK, llms OK, WebSite schema, meta tags, content)
    # the score should be reasonably high
    assert score > 40, f"Score {score} unexpectedly low for a well-configured mock site"


# ============================================================================
# GENERATE_LLMS_TXT.PY INTEGRATION TESTS
# ============================================================================


def test_generate_llms_txt_help():
    """Test that generate_llms_txt.py --help works."""
    result = run_script("generate_llms_txt.py", ["--help"])
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower() or "llms.txt" in result.stdout.lower()


def test_generate_llms_txt_missing_base_url():
    """Test that missing --base-url causes error."""
    result = run_script("generate_llms_txt.py", [])
    assert result.returncode != 0


def test_generate_llms_txt_output():
    """Test that generate_llms_txt.py produces correct output with mocked sitemap."""
    import generate_llms_txt

    sitemap_urls = [
        {"url": "https://example.com/", "lastmod": None, "priority": 1.0, "title": None},
        {"url": "https://example.com/about", "lastmod": None, "priority": 0.8, "title": None},
        {"url": "https://example.com/docs/guide", "lastmod": None, "priority": 0.7, "title": None},
        {"url": "https://example.com/blog/hello-world", "lastmod": None, "priority": 0.5, "title": None},
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_path = f.name

    try:
        with patch.object(generate_llms_txt, "discover_sitemap",
                          return_value="https://example.com/sitemap.xml"), \
             patch.object(generate_llms_txt, "fetch_sitemap",
                          return_value=sitemap_urls), \
             patch("sys.argv", [
                 "generate_llms_txt.py",
                 "--base-url", "https://example.com",
                 "--output", output_path,
                 "--site-name", "Example Site"
             ]):
            generate_llms_txt.main()

        assert Path(output_path).exists()

        with open(output_path, 'r') as f:
            content = f.read()

        # Should have H1 with site name
        assert "# Example Site" in content

        # Should have blockquote description
        assert "> " in content

        # Should contain links
        assert "example.com" in content

    finally:
        Path(output_path).unlink(missing_ok=True)


def test_generate_llms_txt_no_sitemap_creates_minimal():
    """Test that missing sitemap produces minimal llms.txt."""
    import generate_llms_txt

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_path = f.name

    try:
        with patch.object(generate_llms_txt, "discover_sitemap",
                          return_value=None), \
             patch("sys.argv", [
                 "generate_llms_txt.py",
                 "--base-url", "https://example.com",
                 "--output", output_path,
                 "--site-name", "Example Site"
             ]):
            generate_llms_txt.main()

        assert Path(output_path).exists()

        with open(output_path, 'r') as f:
            content = f.read()

        # Minimal output should still have H1 and a homepage link
        assert "# Example Site" in content
        assert "Homepage" in content or "example.com" in content

    finally:
        Path(output_path).unlink(missing_ok=True)


def test_generate_llms_txt_stdout():
    """Test that llms.txt output goes to stdout when --output is not specified."""
    import generate_llms_txt

    sitemap_urls = [
        {"url": "https://example.com/", "lastmod": None, "priority": 1.0, "title": None},
        {"url": "https://example.com/about", "lastmod": None, "priority": 0.8, "title": None},
    ]

    with patch.object(generate_llms_txt, "discover_sitemap",
                      return_value="https://example.com/sitemap.xml"), \
         patch.object(generate_llms_txt, "fetch_sitemap",
                      return_value=sitemap_urls), \
         patch("sys.argv", [
             "generate_llms_txt.py",
             "--base-url", "https://example.com",
             "--site-name", "Example Site"
         ]):
        captured = StringIO()
        with patch("sys.stdout", captured):
            generate_llms_txt.main()

    output = captured.getvalue()
    assert "# Example Site" in output


# ============================================================================
# SCHEMA_INJECTOR.PY INTEGRATION TESTS
# ============================================================================


def test_schema_injector_help():
    """Test that schema_injector.py --help works."""
    result = run_script("schema_injector.py", ["--help"])
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower() or "schema" in result.stdout.lower()


def test_schema_injector_analyze_mode():
    """Test that --analyze mode works without modifying file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "url": "https://example.com",
        "name": "Example"
    }
    </script>
</head>
<body>Test</body>
</html>""")
        test_file = f.name

    try:
        result = run_script("schema_injector.py", [
            "--file", test_file,
            "--analyze"
        ])

        # Should succeed
        assert result.returncode == 0

        # Should mention the found schema
        assert "WebSite" in result.stdout or "schema" in result.stdout.lower()

        # File should not be modified (no .bak created)
        assert not Path(test_file + ".bak").exists()
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_schema_injector_inject_validation_fail():
    """Test that invalid schema injection is blocked by validation."""
    # This test is skipped because schema_injector.py currently doesn't
    # validate template placeholders ({{url}}) before injection.
    # The validation happens on the final schema dict, which may have
    # placeholders replaced with empty strings.
    #
    # To properly test this, we would need to inject a manually crafted
    # invalid schema dict, which is not exposed via CLI.
    pytest.skip("CLI doesn't expose direct schema dict injection for validation testing")


def test_schema_injector_astro_mode():
    """Test that --astro mode generates Astro component code."""
    result = run_script("schema_injector.py", [
        "--type", "website",
        "--name", "Test Site",
        "--url", "https://test.com",
        "--astro"
    ])

    # Should succeed
    assert result.returncode == 0

    # Should contain Astro component syntax
    assert "---" in result.stdout  # Astro frontmatter
    assert "StructuredData" in result.stdout or "@type" in result.stdout


def test_schema_injector_inject_mode():
    """Test that --inject mode writes schema into the HTML file."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>Test</body>
</html>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        test_file = f.name

    try:
        result = run_script("schema_injector.py", [
            "--file", test_file,
            "--type", "website",
            "--name", "Test Site",
            "--url", "https://test.com",
            "--inject",
            "--no-backup"
        ])

        # Should succeed
        assert result.returncode == 0

        # Read the modified file
        with open(test_file, 'r') as f:
            modified = f.read()

        # Should now contain a JSON-LD script tag
        assert "application/ld+json" in modified
        assert "WebSite" in modified
        assert "Test Site" in modified
    finally:
        Path(test_file).unlink(missing_ok=True)
        # Clean up potential backup
        Path(test_file + ".bak").unlink(missing_ok=True)


def test_schema_injector_generate_json_output():
    """Test that --type without --inject prints the JSON-LD tag to stdout."""
    result = run_script("schema_injector.py", [
        "--type", "website",
        "--name", "My Site",
        "--url", "https://mysite.com",
        "--description", "A test site"
    ])

    assert result.returncode == 0

    # Should contain the script tag with schema
    assert "application/ld+json" in result.stdout
    assert "WebSite" in result.stdout
    assert "My Site" in result.stdout
    assert "https://mysite.com" in result.stdout


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_geo_audit_connection_error_handling():
    """Test that the script handles connection errors gracefully."""
    import geo_audit

    def mock_fetch_url(url, timeout=10):
        return None, "Connection refused after 3 retries"

    with patch.object(geo_audit, "fetch_url", side_effect=mock_fetch_url), \
         patch("sys.argv", ["geo_audit.py", "--url", "https://unreachable.example.com"]):
        captured = StringIO()
        with patch("sys.stdout", captured):
            with pytest.raises(SystemExit) as exc_info:
                geo_audit.main()

        # Should exit with non-zero code
        assert exc_info.value.code != 0


def test_geo_audit_robots_not_found():
    """Test behavior when robots.txt returns 404."""
    import geo_audit

    homepage_resp = _make_mock_response(SAMPLE_HTML)
    robots_404 = _make_mock_response("Not Found", status_code=404)
    llms_404 = _make_mock_response("Not Found", status_code=404)

    def mock_fetch_url(url, timeout=10):
        if "robots.txt" in url:
            return robots_404, None
        elif "llms.txt" in url:
            return llms_404, None
        else:
            return homepage_resp, None

    with patch.object(geo_audit, "fetch_url", side_effect=mock_fetch_url), \
         patch("sys.argv", [
             "geo_audit.py", "--url", "https://example.com", "--format", "json"
         ]):
        captured = StringIO()
        with patch("sys.stdout", captured):
            try:
                geo_audit.main()
            except SystemExit:
                pass

    output = captured.getvalue()
    data = json.loads(output)

    # Should still produce valid JSON with lower score
    assert data["checks"]["robots_txt"]["details"]["found"] is False
    assert data["checks"]["llms_txt"]["details"]["found"] is False
    assert data["score"] < 100


# ============================================================================
# CROSS-SCRIPT TESTS
# ============================================================================


def test_scripts_are_executable():
    """Test that all main scripts are executable and have shebang."""
    scripts = ["geo_audit.py", "generate_llms_txt.py", "schema_injector.py"]

    for script_name in scripts:
        script_path = SCRIPTS_DIR / script_name
        assert script_path.exists(), f"{script_name} not found"

        # Check shebang
        with open(script_path, 'r') as f:
            first_line = f.readline()

        assert first_line.startswith("#!/usr/bin/env python3"), \
            f"{script_name} missing proper shebang"


def test_all_scripts_help_exits_zero():
    """Test that all scripts return exit code 0 for --help."""
    scripts = ["geo_audit.py", "generate_llms_txt.py", "schema_injector.py"]

    for script_name in scripts:
        result = run_script(script_name, ["--help"])
        assert result.returncode == 0, \
            f"{script_name} --help returned {result.returncode}: {result.stderr}"
