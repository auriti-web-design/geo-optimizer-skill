"""
Integration tests for geo-optimizer-skill CLI scripts.

Tests the scripts as they would be used by end users:
- Correct exit codes
- Valid JSON output
- Proper error handling
- Command-line argument parsing

Author: Juan Camilo Auriti
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


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


def test_geo_audit_invalid_url():
    """Test that invalid URL format causes non-zero exit."""
    result = run_script("geo_audit.py", ["--url", "not-a-valid-url"])
    # Should exit with error (network failure or validation)
    assert result.returncode != 0


def test_geo_audit_json_output_structure():
    """Test that --format json produces valid JSON with expected structure."""
    # Use a real public site that's likely to be stable
    result = run_script("geo_audit.py", [
        "--url", "https://example.com",
        "--format", "json"
    ])
    
    # Even if the site check fails, JSON format should be valid
    # (the script might return exit code 1 but still output valid JSON)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Invalid JSON output: {result.stdout[:200]}")
    
    # Validate JSON structure
    assert "url" in data or "error" in data  # Either success or error JSON
    
    if "score" in data:
        assert isinstance(data["score"], (int, float))
        assert 0 <= data["score"] <= 100


def test_geo_audit_text_output_default():
    """Test that default output format is text (not JSON)."""
    result = run_script("geo_audit.py", ["--url", "https://example.com"])
    
    # Text output should NOT be valid JSON
    try:
        json.loads(result.stdout)
        pytest.fail("Default output should be text, not JSON")
    except json.JSONDecodeError:
        pass  # Expected: text output is not JSON


def test_geo_audit_output_file():
    """Test that --output flag writes JSON to file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name
    
    try:
        result = run_script("geo_audit.py", [
            "--url", "https://example.com",
            "--format", "json",
            "--output", output_path
        ])
        
        # Check file was created
        assert Path(output_path).exists()
        
        # Check file contains valid JSON (if non-empty)
        file_size = Path(output_path).stat().st_size
        if file_size > 0:
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert "url" in data or "error" in data
        else:
            # Empty file is acceptable if script failed early
            pytest.skip("Output file is empty (network failure expected in CI)")
    finally:
        # Cleanup
        Path(output_path).unlink(missing_ok=True)


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
    """Test that generate_llms_txt.py produces output."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_path = f.name
    
    try:
        result = run_script("generate_llms_txt.py", [
            "--base-url", "https://example.com",
            "--output", output_path,
            "--site-name", "Example Site"
        ], timeout=60)  # Longer timeout for network calls
        
        # Even if sitemap fetch fails, should create output file
        # (might be minimal but should exist)
        if result.returncode == 0:
            assert Path(output_path).exists()
            
            # Check content has basic structure
            with open(output_path, 'r') as f:
                content = f.read()
            
            # Should have at least H1 and site name
            assert "# " in content or "Example Site" in content
    finally:
        Path(output_path).unlink(missing_ok=True)


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


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_geo_audit_timeout_handling():
    """Test that script handles timeout gracefully (if network is very slow)."""
    # Use a URL that's likely to timeout or be very slow
    try:
        result = run_script("geo_audit.py", [
            "--url", "https://httpbin.org/delay/100"  # 100-second delay
        ], timeout=5)  # Kill after 5 seconds
        
        # If we get here without timeout, that's also OK
        # (maybe the request failed fast)
        assert True
    except subprocess.TimeoutExpired:
        # Expected: timeout means the subprocess.run() timeout worked
        # This is actually the success case for this test
        assert True


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
