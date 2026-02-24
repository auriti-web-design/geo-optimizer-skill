"""
Comprehensive unit tests for schema_injector.py

Tests all public functions:
- fill_template: placeholder replacement in schema templates
- schema_to_html_tag: dict to HTML <script> tag conversion
- extract_faq_from_html: FAQ extraction from HTML patterns (dt/dd, details/summary, classes)
- analyze_html_file: HTML analysis for existing/missing schemas
- generate_faq_schema: FAQ schema generation from items
- inject_schema_into_html: schema injection with backup, validation, edge cases
- print_analysis: output formatting

Author: Juan Camilo Auriti
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from schema_injector import (
    SCHEMA_TEMPLATES,
    fill_template,
    schema_to_html_tag,
    extract_faq_from_html,
    analyze_html_file,
    generate_faq_schema,
    inject_schema_into_html,
    print_analysis,
)


# ============================================================================
# fill_template TESTS
# ============================================================================


class TestFillTemplate:
    """Tests for the fill_template function."""

    def test_basic_placeholder_replacement(self):
        """Test that {{key}} placeholders are replaced with values."""
        template = {"name": "{{name}}", "url": "{{url}}"}
        values = {"name": "My Site", "url": "https://example.com"}

        result = fill_template(template, values)

        assert result["name"] == "My Site"
        assert result["url"] == "https://example.com"

    def test_nested_placeholder_replacement(self):
        """Test that placeholders in nested dicts are replaced."""
        template = {
            "name": "{{name}}",
            "author": {"@type": "Person", "name": "{{author}}"},
        }
        values = {"name": "My Article", "author": "Juan"}

        result = fill_template(template, values)

        assert result["name"] == "My Article"
        assert result["author"]["name"] == "Juan"

    def test_none_value_replaced_with_empty_string(self):
        """Test that None values become empty strings."""
        template = {"name": "{{name}}", "description": "{{description}}"}
        values = {"name": "Test", "description": None}

        result = fill_template(template, values)

        assert result["name"] == "Test"
        assert result["description"] == ""

    def test_missing_placeholder_not_replaced(self):
        """Test that unreferenced placeholders remain as-is."""
        template = {"name": "{{name}}", "url": "{{url}}"}
        values = {"name": "Test"}

        result = fill_template(template, values)

        assert result["name"] == "Test"
        assert result["url"] == "{{url}}"

    def test_website_template_fill(self):
        """Test filling the real website template."""
        template = SCHEMA_TEMPLATES["website"]
        values = {
            "name": "GEO Optimizer",
            "url": "https://geo.example.com",
            "description": "A toolkit for GEO",
        }

        result = fill_template(template, values)

        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "WebSite"
        assert result["name"] == "GEO Optimizer"
        assert result["url"] == "https://geo.example.com"
        assert result["description"] == "A toolkit for GEO"
        assert "urlTemplate" in json.dumps(result)

    def test_integer_value_converted_to_string(self):
        """Test that integer values are converted to string via str()."""
        template = {"count": "{{count}}"}
        values = {"count": 42}

        result = fill_template(template, values)

        assert result["count"] == "42"


# ============================================================================
# schema_to_html_tag TESTS
# ============================================================================


class TestSchemaToHtmlTag:
    """Tests for the schema_to_html_tag function."""

    def test_basic_schema_to_tag(self):
        """Test converting a simple schema dict to an HTML script tag."""
        schema = {"@context": "https://schema.org", "@type": "WebSite"}

        result = schema_to_html_tag(schema)

        assert result.startswith('<script type="application/ld+json">')
        assert result.endswith("</script>")
        assert '"@context": "https://schema.org"' in result
        assert '"@type": "WebSite"' in result

    def test_output_is_valid_json_inside_tag(self):
        """Test that the JSON inside the script tag is valid."""
        schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Test",
            "url": "https://example.com",
        }

        result = schema_to_html_tag(schema)

        # Extract JSON between the script tags
        json_str = result.replace('<script type="application/ld+json">\n', "").replace(
            "\n</script>", ""
        )
        parsed = json.loads(json_str)
        assert parsed == schema

    def test_unicode_characters_preserved(self):
        """Test that unicode characters are not ASCII-escaped."""
        schema = {"@context": "https://schema.org", "name": "Cafe Muller"}

        result = schema_to_html_tag(schema)

        assert "Cafe Muller" in result
        # ensure_ascii=False should preserve non-ASCII if present
        assert "\\u" not in result


# ============================================================================
# extract_faq_from_html TESTS
# ============================================================================


class TestExtractFaqFromHtml:
    """Tests for the extract_faq_from_html function."""

    def _make_soup(self, html):
        """Helper to create a BeautifulSoup object from HTML."""
        from bs4 import BeautifulSoup

        return BeautifulSoup(html, "html.parser")

    def test_extract_dt_dd_pattern(self):
        """Test FAQ extraction from <dt>/<dd> pairs."""
        html = """
        <dl>
            <dt>What is GEO Optimizer?</dt>
            <dd>GEO Optimizer is a toolkit for Generative Engine Optimization.</dd>
            <dt>How does it work exactly?</dt>
            <dd>It analyzes your website and provides recommendations for AI visibility.</dd>
        </dl>
        """
        soup = self._make_soup(html)
        faqs = extract_faq_from_html(soup)

        assert len(faqs) == 2
        assert faqs[0]["question"] == "What is GEO Optimizer?"
        assert "toolkit" in faqs[0]["answer"]

    def test_extract_details_summary_pattern(self):
        """Test FAQ extraction from <details>/<summary> elements."""
        html = """
        <details>
            <summary>What is generative engine optimization?</summary>
            <p>It is the process of optimizing content to be visible in AI search engines.</p>
        </details>
        <details>
            <summary>Why is GEO important for websites?</summary>
            <p>Because AI search engines are becoming a primary way users find information online.</p>
        </details>
        """
        soup = self._make_soup(html)
        faqs = extract_faq_from_html(soup)

        assert len(faqs) == 2
        assert "generative engine" in faqs[0]["question"].lower()

    def test_extract_faq_class_pattern(self):
        """Test FAQ extraction from elements with FAQ-related CSS classes."""
        html = """
        <div class="faq-item">
            <h3>What are the system requirements?</h3>
            <p>You need Python 3.8 or later and a modern web browser to run GEO Optimizer.</p>
        </div>
        <div class="faq-item">
            <h3>Is GEO Optimizer free to use?</h3>
            <p>Yes, GEO Optimizer is completely free and open source under the MIT license.</p>
        </div>
        """
        soup = self._make_soup(html)
        faqs = extract_faq_from_html(soup)

        assert len(faqs) == 2
        assert "system requirements" in faqs[0]["question"].lower()

    def test_short_questions_filtered_out(self):
        """Test that questions shorter than 6 chars are filtered out."""
        html = """
        <dl>
            <dt>FAQ</dt>
            <dd>This is a long enough answer to pass the filter check.</dd>
        </dl>
        """
        soup = self._make_soup(html)
        faqs = extract_faq_from_html(soup)

        assert len(faqs) == 0

    def test_short_answers_filtered_out(self):
        """Test that answers shorter than 11 chars are filtered out."""
        html = """
        <dl>
            <dt>What is this thing about?</dt>
            <dd>Short ans</dd>
        </dl>
        """
        soup = self._make_soup(html)
        faqs = extract_faq_from_html(soup)

        assert len(faqs) == 0

    def test_empty_html_returns_empty_list(self):
        """Test that empty HTML returns no FAQs."""
        soup = self._make_soup("<html><body></body></html>")
        faqs = extract_faq_from_html(soup)

        assert faqs == []

    def test_dt_without_dd_sibling_skipped(self):
        """Test that <dt> without a following <dd> sibling is skipped."""
        html = """
        <dl>
            <dt>Orphan question with no answer pair</dt>
        </dl>
        """
        soup = self._make_soup(html)
        faqs = extract_faq_from_html(soup)

        assert len(faqs) == 0


# ============================================================================
# analyze_html_file TESTS
# ============================================================================


class TestAnalyzeHtmlFile:
    """Tests for the analyze_html_file function."""

    def test_detects_existing_website_schema(self, tmp_path):
        """Test that an existing WebSite schema is detected."""
        schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Test",
            "url": "https://example.com",
        }
        html = f"""<html><head>
        <script type="application/ld+json">{json.dumps(schema)}</script>
        </head><body></body></html>"""

        html_file = tmp_path / "index.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        assert len(result["found_schemas"]) == 1
        assert result["found_types"] == ["WebSite"]
        assert "website" not in result["missing"]
        assert result["has_head"] is True

    def test_reports_missing_schemas(self, tmp_path):
        """Test that missing schemas are reported when no JSON-LD exists."""
        html = "<html><head></head><body><p>Hello</p></body></html>"

        html_file = tmp_path / "index.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        assert len(result["found_schemas"]) == 0
        assert "website" in result["missing"]
        assert "webapp" in result["missing"]
        assert "faq" in result["missing"]
        assert result["total_scripts"] == 0

    def test_detects_duplicate_schemas(self, tmp_path):
        """Test that duplicate schemas of the same type are flagged."""
        schema = json.dumps(
            {"@context": "https://schema.org", "@type": "WebSite", "name": "Test", "url": "https://example.com"}
        )
        html = f"""<html><head>
        <script type="application/ld+json">{schema}</script>
        <script type="application/ld+json">{schema}</script>
        </head><body></body></html>"""

        html_file = tmp_path / "duplicate.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        assert result["duplicates"].get("WebSite") == 2

    def test_malformed_jsonld_handled_gracefully(self, tmp_path):
        """Test that malformed JSON-LD does not crash the analysis."""
        html = """<html><head>
        <script type="application/ld+json">{this is not valid json</script>
        </head><body></body></html>"""

        html_file = tmp_path / "bad.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        assert len(result["found_schemas"]) == 0
        assert result["total_scripts"] == 1

    def test_malformed_jsonld_verbose_prints_warning(self, tmp_path, capsys):
        """Test that malformed JSON-LD prints a warning in verbose mode."""
        html = """<html><head>
        <script type="application/ld+json">{broken json}</script>
        </head><body></body></html>"""

        html_file = tmp_path / "bad.html"
        html_file.write_text(html, encoding="utf-8")

        analyze_html_file(str(html_file), verbose=True)

        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.out

    def test_array_schema_parsed(self, tmp_path):
        """Test that array-format JSON-LD (multiple schemas in one tag) is parsed."""
        schemas = [
            {"@context": "https://schema.org", "@type": "WebSite", "name": "Test", "url": "https://example.com"},
            {"@context": "https://schema.org", "@type": "Organization", "name": "Org", "url": "https://example.com"},
        ]
        html = f"""<html><head>
        <script type="application/ld+json">{json.dumps(schemas)}</script>
        </head><body></body></html>"""

        html_file = tmp_path / "array.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        assert len(result["found_schemas"]) == 2
        assert "WebSite" in result["found_types"]
        assert "Organization" in result["found_types"]

    def test_no_head_tag_detected(self, tmp_path):
        """Test that absence of <head> is correctly reported."""
        html = "<html><body><p>No head tag</p></body></html>"

        html_file = tmp_path / "nohead.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        assert result["has_head"] is False

    def test_extracts_faqs_when_faqpage_missing(self, tmp_path):
        """Test that FAQs are auto-extracted when FAQPage schema is absent."""
        html = """<html><head></head><body>
        <dl>
            <dt>What is GEO Optimizer used for?</dt>
            <dd>GEO Optimizer helps websites become visible to AI search engines like ChatGPT.</dd>
        </dl>
        </body></html>"""

        html_file = tmp_path / "faq.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        assert len(result["extracted_faqs"]) == 1
        assert "GEO Optimizer" in result["extracted_faqs"][0]["question"]


# ============================================================================
# generate_faq_schema TESTS
# ============================================================================


class TestGenerateFaqSchema:
    """Tests for the generate_faq_schema function."""

    def test_generates_valid_faqpage_schema(self):
        """Test that a valid FAQPage schema is generated from items."""
        items = [
            {"question": "What is GEO?", "answer": "Generative Engine Optimization"},
            {"question": "Why use GEO?", "answer": "To be visible in AI search engines"},
        ]

        schema = generate_faq_schema(items)

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "FAQPage"
        assert len(schema["mainEntity"]) == 2
        assert schema["mainEntity"][0]["@type"] == "Question"
        assert schema["mainEntity"][0]["name"] == "What is GEO?"
        assert schema["mainEntity"][0]["acceptedAnswer"]["@type"] == "Answer"
        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "Generative Engine Optimization"

    def test_empty_faq_items(self):
        """Test that an empty list produces a FAQPage with no mainEntity."""
        schema = generate_faq_schema([])

        assert schema["@type"] == "FAQPage"
        assert schema["mainEntity"] == []

    def test_single_faq_item(self):
        """Test generating schema from a single FAQ item."""
        items = [{"question": "Is this a test?", "answer": "Yes, this is indeed a test."}]

        schema = generate_faq_schema(items)

        assert len(schema["mainEntity"]) == 1
        assert schema["mainEntity"][0]["name"] == "Is this a test?"


# ============================================================================
# inject_schema_into_html TESTS
# ============================================================================


class TestInjectSchemaIntoHtml:
    """Tests for the inject_schema_into_html function."""

    VALID_SCHEMA = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Test Site",
        "url": "https://example.com",
    }

    def test_injects_schema_before_head_close(self, tmp_path):
        """Test that schema is injected into the <head> section."""
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "inject.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)):
            result = inject_schema_into_html(str(html_file), self.VALID_SCHEMA, backup=False)

        assert result is True

        content = html_file.read_text(encoding="utf-8")
        assert 'application/ld+json' in content
        assert '"@type": "WebSite"' in content

    def test_backup_created_with_copy(self, tmp_path):
        """Test that backup is created using copy (original file preserved)."""
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "backup_test.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)):
            result = inject_schema_into_html(str(html_file), self.VALID_SCHEMA, backup=True)

        assert result is True

        # Original file should still exist (shutil.copy2, not rename)
        assert html_file.exists()

        # Backup file should also exist
        backup_file = tmp_path / "backup_test.html.bak"
        assert backup_file.exists()

        # Backup should contain the original content (no schema)
        backup_content = backup_file.read_text(encoding="utf-8")
        assert "application/ld+json" not in backup_content

        # Original file should now contain the schema
        modified_content = html_file.read_text(encoding="utf-8")
        assert "application/ld+json" in modified_content

    def test_no_backup_when_disabled(self, tmp_path):
        """Test that no .bak file is created when backup=False."""
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "nobackup.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)):
            inject_schema_into_html(str(html_file), self.VALID_SCHEMA, backup=False)

        backup_file = tmp_path / "nobackup.html.bak"
        assert not backup_file.exists()

    def test_fails_when_no_head_tag(self, tmp_path):
        """Test that injection fails when there is no <head> tag."""
        html = "<html><body><p>No head</p></body></html>"
        html_file = tmp_path / "nohead.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)):
            result = inject_schema_into_html(str(html_file), self.VALID_SCHEMA, backup=False)

        assert result is False

    def test_fails_when_validation_fails(self, tmp_path):
        """Test that injection fails when schema validation fails."""
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "valfail.html"
        html_file.write_text(html, encoding="utf-8")

        with patch(
            "schema_validator.validate_jsonld",
            return_value=(False, "Missing required field: url"),
        ):
            result = inject_schema_into_html(str(html_file), {"@type": "WebSite"}, backup=False, validate=True)

        assert result is False

        # File should remain unmodified
        content = html_file.read_text(encoding="utf-8")
        assert "application/ld+json" not in content

    def test_skips_validation_when_disabled(self, tmp_path):
        """Test that validation is skipped when validate=False."""
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "noval.html"
        html_file.write_text(html, encoding="utf-8")

        # validate_jsonld should NOT be called at all
        with patch("schema_validator.validate_jsonld") as mock_validate:
            result = inject_schema_into_html(
                str(html_file), self.VALID_SCHEMA, backup=False, validate=False
            )

        assert result is True
        mock_validate.assert_not_called()

    def test_schema_type_list_handled(self, tmp_path):
        """Test that schema with @type as a list is handled for validation."""
        schema = {
            "@context": "https://schema.org",
            "@type": ["WebSite", "CreativeWork"],
            "name": "Test",
            "url": "https://example.com",
        }
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "listtype.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)) as mock_validate:
            result = inject_schema_into_html(str(html_file), schema, backup=False)

        assert result is True
        # Should pass schema_type as the first element lowercased
        mock_validate.assert_called_once_with(schema, "website", strict=False)

    def test_injected_json_is_valid(self, tmp_path):
        """Test that the injected JSON-LD is valid parseable JSON."""
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "valid_json.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)):
            inject_schema_into_html(str(html_file), self.VALID_SCHEMA, backup=False)

        content = html_file.read_text(encoding="utf-8")

        # Parse the file with BeautifulSoup and extract the JSON-LD
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "html.parser")
        script = soup.find("script", type="application/ld+json")
        assert script is not None

        parsed = json.loads(script.string.strip())
        assert parsed["@type"] == "WebSite"
        assert parsed["name"] == "Test Site"


# ============================================================================
# print_analysis TESTS
# ============================================================================


class TestPrintAnalysis:
    """Tests for the print_analysis function."""

    def test_prints_found_schemas(self, capsys):
        """Test that found schemas are printed."""
        analysis = {
            "found_schemas": [
                {"type": "WebSite", "data": {"url": "https://example.com", "name": "Test"}, "index": 0}
            ],
            "found_types": ["WebSite"],
            "missing": ["webapp", "faq"],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 1,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "SCHEMA ANALYSIS" in captured.out
        assert "Found 1 schema(s)" in captured.out
        assert "WebSite" in captured.out

    def test_prints_no_schemas_message(self, capsys):
        """Test that 'no schemas found' is printed when none exist."""
        analysis = {
            "found_schemas": [],
            "found_types": [],
            "missing": ["website", "webapp", "faq"],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 0,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "No JSON-LD schemas found" in captured.out

    def test_prints_duplicate_warning(self, capsys):
        """Test that duplicate schemas trigger a warning."""
        analysis = {
            "found_schemas": [
                {"type": "WebSite", "data": {}, "index": 0},
                {"type": "WebSite", "data": {}, "index": 1},
            ],
            "found_types": ["WebSite", "WebSite"],
            "missing": [],
            "extracted_faqs": [],
            "duplicates": {"WebSite": 2},
            "has_head": True,
            "total_scripts": 2,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "DUPLICATE SCHEMAS DETECTED" in captured.out
        assert "WebSite" in captured.out
        assert "2 instances" in captured.out

    def test_prints_suggested_schemas(self, capsys):
        """Test that missing schemas are suggested."""
        analysis = {
            "found_schemas": [],
            "found_types": [],
            "missing": ["website", "faq"],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 0,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "Suggested schemas to add" in captured.out
        assert "WEBSITE" in captured.out
        assert "FAQ" in captured.out

    def test_prints_extracted_faqs(self, capsys):
        """Test that extracted FAQs are printed with truncation."""
        analysis = {
            "found_schemas": [],
            "found_types": [],
            "missing": ["faq"],
            "extracted_faqs": [
                {"question": "Question one about something?", "answer": "Answer one"},
                {"question": "Question two about something?", "answer": "Answer two"},
                {"question": "Question three about something?", "answer": "Answer three"},
                {"question": "Question four about something?", "answer": "Answer four"},
            ],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 0,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "Auto-detected 4 FAQ items" in captured.out
        assert "Question one" in captured.out
        assert "and 1 more" in captured.out

    def test_verbose_prints_full_schema_json(self, capsys):
        """Test that verbose mode shows the full schema JSON."""
        analysis = {
            "found_schemas": [
                {
                    "type": "WebSite",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "WebSite",
                        "name": "Verbose Test",
                        "url": "https://example.com",
                    },
                    "index": 0,
                }
            ],
            "found_types": ["WebSite"],
            "missing": [],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 1,
        }

        print_analysis(analysis, verbose=True)
        captured = capsys.readouterr()

        assert "Full schema:" in captured.out
        assert "Verbose Test" in captured.out

    def test_prints_faqpage_question_count(self, capsys):
        """Test that FAQPage schema shows question count."""
        analysis = {
            "found_schemas": [
                {
                    "type": "FAQPage",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "FAQPage",
                        "mainEntity": [
                            {"@type": "Question", "name": "Q1"},
                            {"@type": "Question", "name": "Q2"},
                        ],
                    },
                    "index": 0,
                }
            ],
            "found_types": ["FAQPage"],
            "missing": ["website", "webapp"],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 1,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "questions: 2" in captured.out

    def test_prints_webapp_schema_details(self, capsys):
        """Test that WebApplication schema shows url and name."""
        analysis = {
            "found_schemas": [
                {
                    "type": "WebApplication",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "WebApplication",
                        "name": "GEO Tool",
                        "url": "https://geo.example.com",
                    },
                    "index": 0,
                }
            ],
            "found_types": ["WebApplication"],
            "missing": ["website", "faq"],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 1,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "WebApplication" in captured.out
        assert "url: https://geo.example.com" in captured.out
        assert "name: GEO Tool" in captured.out

    def test_prints_organization_schema_details(self, capsys):
        """Test that Organization schema shows name."""
        analysis = {
            "found_schemas": [
                {
                    "type": "Organization",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "Organization",
                        "name": "Auriti Design",
                        "url": "https://auritidesign.it",
                    },
                    "index": 0,
                }
            ],
            "found_types": ["Organization"],
            "missing": ["website", "webapp", "faq"],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 1,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "Organization" in captured.out
        assert "name: Auriti Design" in captured.out

    def test_prints_breadcrumb_schema_details(self, capsys):
        """Test that BreadcrumbList schema shows item count."""
        analysis = {
            "found_schemas": [
                {
                    "type": "BreadcrumbList",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "BreadcrumbList",
                        "itemListElement": [
                            {"@type": "ListItem", "position": 1, "name": "Home"},
                            {"@type": "ListItem", "position": 2, "name": "About"},
                        ],
                    },
                    "index": 0,
                }
            ],
            "found_types": ["BreadcrumbList"],
            "missing": ["website", "webapp", "faq"],
            "extracted_faqs": [],
            "duplicates": {},
            "has_head": True,
            "total_scripts": 1,
        }

        print_analysis(analysis)
        captured = capsys.readouterr()

        assert "BreadcrumbList" in captured.out
        assert "items: 2" in captured.out


# ============================================================================
# ADDITIONAL EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Additional edge case tests for higher coverage."""

    def test_inject_with_none_type_field(self, tmp_path):
        """Test injection when @type is neither str nor list (covers schema_type = None branch)."""
        schema = {
            "@context": "https://schema.org",
            "@type": 123,  # Not str or list
            "name": "Test",
        }
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "nonetype.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)) as mock_validate:
            result = inject_schema_into_html(str(html_file), schema, backup=False)

        assert result is True
        # schema_type should be None when @type is not str or list
        mock_validate.assert_called_once_with(schema, None, strict=False)

    def test_inject_with_empty_list_type(self, tmp_path):
        """Test injection when @type is an empty list (covers the conditional None branch)."""
        schema = {
            "@context": "https://schema.org",
            "@type": [],
            "name": "Test",
        }
        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "emptytype.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("schema_validator.validate_jsonld", return_value=(True, None)) as mock_validate:
            result = inject_schema_into_html(str(html_file), schema, backup=False)

        assert result is True
        # Empty list should result in schema_type = None
        mock_validate.assert_called_once_with(schema, None, strict=False)

    def test_analyze_script_with_no_string_content(self, tmp_path):
        """Test analyze_html_file when script tag has no string content (empty tag)."""
        html = """<html><head>
        <script type="application/ld+json"></script>
        </head><body></body></html>"""

        html_file = tmp_path / "empty_script.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        # Empty script tag should not produce any found schemas
        assert len(result["found_schemas"]) == 0
        assert result["total_scripts"] == 1

    def test_analyze_does_not_extract_faq_when_faqpage_present(self, tmp_path):
        """Test that FAQ extraction is skipped when FAQPage schema already exists."""
        faq_schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": "Q1"}],
        })
        html = f"""<html><head>
        <script type="application/ld+json">{faq_schema}</script>
        </head><body>
        <dl>
            <dt>What is GEO Optimizer used for?</dt>
            <dd>GEO Optimizer helps websites become visible to AI search engines like ChatGPT.</dd>
        </dl>
        </body></html>"""

        html_file = tmp_path / "has_faq.html"
        html_file.write_text(html, encoding="utf-8")

        result = analyze_html_file(str(html_file))

        # FAQPage is present, so extracted_faqs should be empty
        assert result["extracted_faqs"] == []
        assert "faq" not in result["missing"]

    def test_fill_template_preserves_static_fields(self):
        """Test that static fields (without placeholders) are preserved."""
        template = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "{{name}}",
        }
        values = {"name": "My Site"}

        result = fill_template(template, values)

        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "WebSite"
        assert result["name"] == "My Site"

    def test_schema_to_html_tag_with_complex_nested_schema(self):
        """Test schema_to_html_tag with a deeply nested FAQ schema."""
        schema = generate_faq_schema([
            {"question": "What is GEO?", "answer": "Generative Engine Optimization"},
        ])

        result = schema_to_html_tag(schema)

        assert "FAQPage" in result
        assert "What is GEO?" in result
        assert "Generative Engine Optimization" in result
        assert '<script type="application/ld+json">' in result

    def test_extract_faq_class_pattern_with_question_class(self):
        """Test FAQ extraction using elements with 'question' CSS class."""
        html = """
        <div class="qa-block">
            <div class="question-title">How do I install GEO Optimizer?</div>
            <p>Run pip install geo-optimizer from your terminal to install the package.</p>
        </div>
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        faqs = extract_faq_from_html(soup)

        assert len(faqs) == 1
        assert "install" in faqs[0]["question"].lower()

    def test_analyze_html_file_bs4_import_error(self, tmp_path):
        """Test that analyze_html_file exits when bs4 is not available."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<html></html>", encoding="utf-8")

        with patch.dict("sys.modules", {"bs4": None}):
            with pytest.raises(SystemExit):
                # Force reimport to trigger ImportError
                import importlib
                import schema_injector
                importlib.reload(schema_injector)
                schema_injector.analyze_html_file(str(html_file))

    def test_inject_schema_bs4_import_error(self, tmp_path):
        """Test that inject_schema_into_html returns False when bs4 is not available."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><head></head></html>", encoding="utf-8")

        schema = {"@context": "https://schema.org", "@type": "WebSite"}

        with patch("builtins.__import__", side_effect=_bs4_import_blocker):
            result = inject_schema_into_html(str(html_file), schema, backup=False, validate=False)

        assert result is False

    def test_analyze_generic_exception_in_script(self, tmp_path, capsys):
        """Test that a generic Exception in script parsing is handled gracefully."""
        # Create valid HTML with a script tag
        html = """<html><head>
        <script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebSite"}</script>
        </head><body></body></html>"""

        html_file = tmp_path / "exc.html"
        html_file.write_text(html, encoding="utf-8")

        # Patch json.loads to raise a generic Exception (not JSONDecodeError)
        original_loads = json.loads

        def patched_loads(s, *args, **kwargs):
            # Only raise for our script content, not for other json.loads calls
            if isinstance(s, str) and "@context" in s and "@type" in s and "WebSite" in s:
                raise TypeError("Simulated unexpected error")
            return original_loads(s, *args, **kwargs)

        with patch("json.loads", side_effect=patched_loads):
            result = analyze_html_file(str(html_file), verbose=True)

        captured = capsys.readouterr()
        assert "Error parsing script tag" in captured.out
        assert len(result["found_schemas"]) == 0

    def test_main_analyze_mode(self, tmp_path, capsys):
        """Test main() in --analyze mode."""
        from schema_injector import main

        schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Test",
            "url": "https://example.com",
        })
        html = f"""<html><head>
        <script type="application/ld+json">{schema}</script>
        </head><body></body></html>"""

        html_file = tmp_path / "main_analyze.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("sys.argv", ["schema_injector.py", "--file", str(html_file), "--analyze"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "SCHEMA ANALYSIS" in captured.out

    def test_main_generate_schema_output(self, capsys):
        """Test main() generating schema JSON output (no --inject)."""
        from schema_injector import main

        with patch("sys.argv", [
            "schema_injector.py",
            "--type", "website",
            "--name", "TestSite",
            "--url", "https://example.com",
            "--description", "A test site",
        ]):
            main()

        captured = capsys.readouterr()
        assert "application/ld+json" in captured.out
        assert "TestSite" in captured.out

    def test_main_astro_mode(self, capsys):
        """Test main() in --astro mode."""
        from schema_injector import main

        with patch("sys.argv", [
            "schema_injector.py",
            "--type", "website",
            "--name", "AstroSite",
            "--url", "https://astro.example.com",
            "--astro",
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "AstroSite" in captured.out
        assert "https://astro.example.com" in captured.out
        assert "BaseLayout.astro" in captured.out

    def test_main_no_args_shows_help(self, capsys):
        """Test main() with no arguments shows help and exits."""
        from schema_injector import main

        with patch("sys.argv", ["schema_injector.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_inject_mode(self, tmp_path, capsys):
        """Test main() in --inject mode with --no-validate."""
        from schema_injector import main

        html = "<html><head><title>Test</title></head><body></body></html>"
        html_file = tmp_path / "main_inject.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("sys.argv", [
            "schema_injector.py",
            "--file", str(html_file),
            "--type", "website",
            "--name", "InjectTest",
            "--url", "https://example.com",
            "--inject",
            "--no-backup",
            "--no-validate",
        ]):
            main()

        captured = capsys.readouterr()
        assert "Schema injected" in captured.out

        content = html_file.read_text(encoding="utf-8")
        assert "InjectTest" in content

    def test_main_faq_auto_extract(self, tmp_path, capsys):
        """Test main() with --type faq --auto-extract --inject."""
        from schema_injector import main

        html = """<html><head><title>FAQ</title></head><body>
        <dl>
            <dt>What is GEO Optimizer used for?</dt>
            <dd>GEO Optimizer helps websites become visible to AI search engines like ChatGPT.</dd>
        </dl>
        </body></html>"""

        html_file = tmp_path / "main_faq.html"
        html_file.write_text(html, encoding="utf-8")

        with patch("sys.argv", [
            "schema_injector.py",
            "--file", str(html_file),
            "--type", "faq",
            "--auto-extract",
            "--inject",
            "--no-backup",
            "--no-validate",
        ]):
            main()

        captured = capsys.readouterr()
        assert "Extracted 1 FAQ" in captured.out
        assert "Schema injected" in captured.out


def _bs4_import_blocker(name, *args, **kwargs):
    """Helper to block bs4 imports while allowing everything else."""
    if name == "bs4":
        raise ImportError("Simulated bs4 not installed")
    return original_import(name, *args, **kwargs)


original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__
