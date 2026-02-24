"""
Comprehensive unit tests for generate_llms_txt.py script.

Tests critical functions for llms.txt generation including:
- URL skip patterns
- URL categorization
- URL to human label conversion
- llms.txt generation logic
- Sitemap fetching and parsing (mocked HTTP)
- Sitemap discovery (mocked HTTP)
- Page title fetching (mocked HTTP)
- CLI argument parsing and main flow

Author: Juan Camilo Auriti
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, mock_open

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_llms_txt import (
    should_skip,
    categorize_url,
    url_to_label,
    generate_llms_txt,
    fetch_sitemap,
    discover_sitemap,
    fetch_page_title,
    _ensure_deps,
    SKIP_PATTERNS,
    CATEGORY_PATTERNS,
    HEADERS,
)


# ============================================================================
# Ensure lazy deps are loaded before tests that use BeautifulSoup
# ============================================================================

@pytest.fixture(autouse=True)
def ensure_deps_loaded():
    """Ensure requests and BeautifulSoup are imported before each test."""
    _ensure_deps()


# ============================================================================
# should_skip() TESTS
# ============================================================================


class TestShouldSkip:
    """Tests for the should_skip URL filtering function."""

    def test_skip_wp_admin_url(self):
        """WordPress admin URLs should be skipped."""
        assert should_skip("https://example.com/wp-admin/") is True

    def test_skip_wp_content_url(self):
        """WordPress wp-content URLs should be skipped."""
        assert should_skip("https://example.com/wp-content/uploads/image.jpg") is True

    def test_skip_login_url(self):
        """Login URLs should be skipped."""
        assert should_skip("https://example.com/login") is True

    def test_skip_logout_url(self):
        """Logout URLs should be skipped."""
        assert should_skip("https://example.com/logout") is True

    def test_skip_register_url(self):
        """Registration URLs should be skipped."""
        assert should_skip("https://example.com/register") is True

    def test_skip_cart_url(self):
        """Cart URLs should be skipped."""
        assert should_skip("https://example.com/cart") is True

    def test_skip_checkout_url(self):
        """Checkout URLs should be skipped."""
        assert should_skip("https://example.com/checkout") is True

    def test_skip_account_url(self):
        """Account URLs should be skipped."""
        assert should_skip("https://example.com/account") is True

    def test_skip_user_url(self):
        """User profile URLs should be skipped."""
        assert should_skip("https://example.com/user/12345") is True

    def test_skip_xml_file(self):
        """XML file URLs should be skipped."""
        assert should_skip("https://example.com/feed.xml") is True

    def test_skip_json_file(self):
        """JSON file URLs should be skipped."""
        assert should_skip("https://example.com/data.json") is True

    def test_skip_rss_file(self):
        """RSS file URLs should be skipped."""
        assert should_skip("https://example.com/feed.rss") is True

    def test_skip_pdf_file(self):
        """PDF file URLs should be skipped."""
        assert should_skip("https://example.com/document.pdf") is True

    def test_skip_image_urls(self):
        """Image file URLs should be skipped."""
        assert should_skip("https://example.com/photo.jpg") is True
        assert should_skip("https://example.com/logo.png") is True

    def test_skip_css_file(self):
        """CSS file URLs should be skipped."""
        assert should_skip("https://example.com/style.css") is True

    def test_skip_js_file(self):
        """JavaScript file URLs should be skipped."""
        assert should_skip("https://example.com/app.js") is True

    def test_skip_tag_url(self):
        """Tag archive URLs should be skipped."""
        assert should_skip("https://example.com/tag/python") is True

    def test_skip_paginated_category(self):
        """Paginated category URLs should be skipped."""
        assert should_skip("https://example.com/category/tech/page/2") is True

    def test_skip_paginated_url(self):
        """Paginated archive URLs should be skipped."""
        assert should_skip("https://example.com/page/5") is True

    def test_skip_admin_url(self):
        """Admin URLs should be skipped."""
        assert should_skip("https://example.com/admin/dashboard") is True

    def test_no_skip_regular_blog_post(self):
        """Regular blog post URLs should not be skipped."""
        assert should_skip("https://example.com/blog/my-great-post") is False

    def test_no_skip_homepage(self):
        """Homepage should not be skipped."""
        assert should_skip("https://example.com/") is False

    def test_no_skip_about_page(self):
        """About page should not be skipped."""
        assert should_skip("https://example.com/about") is False

    def test_no_skip_product_page(self):
        """Product page should not be skipped."""
        assert should_skip("https://example.com/products/widget") is False

    def test_skip_is_case_insensitive(self):
        """Skip patterns should match regardless of case."""
        assert should_skip("https://example.com/Login") is True
        assert should_skip("https://example.com/ADMIN/panel") is True

    def test_skip_atom_feed(self):
        """Atom feed URLs should be skipped."""
        assert should_skip("https://example.com/feed.atom") is True


# ============================================================================
# categorize_url() TESTS
# ============================================================================


class TestCategorizeUrl:
    """Tests for the categorize_url function."""

    def test_blog_url(self):
        """Blog URLs should be categorized as Blog & Articles."""
        result = categorize_url("https://example.com/blog/post-title", "example.com")
        assert result == "Blog & Articles"

    def test_article_url(self):
        """Article URLs should be categorized as Articles."""
        result = categorize_url("https://example.com/articles/recent", "example.com")
        assert result == "Articles"

    def test_post_url(self):
        """Post URLs should be categorized as Posts."""
        result = categorize_url("https://example.com/post/123", "example.com")
        assert result == "Posts"

    def test_finance_url(self):
        """Finance URLs should be categorized as Finance Tools."""
        result = categorize_url("https://example.com/finance/mortgage-calc", "example.com")
        assert result == "Finance Tools"

    def test_health_url(self):
        """Health URLs should be categorized as Health & Wellness."""
        result = categorize_url("https://example.com/health/bmi", "example.com")
        assert result == "Health & Wellness"

    def test_math_url(self):
        """Math URLs should be categorized as Math."""
        result = categorize_url("https://example.com/math/algebra", "example.com")
        assert result == "Math"

    def test_calculator_url(self):
        """Calculator URLs should be categorized as Calculators."""
        result = categorize_url("https://example.com/calculators/tax", "example.com")
        assert result == "Calculators"

    def test_tool_url(self):
        """Tool URLs should be categorized as Tools."""
        result = categorize_url("https://example.com/tools/converter", "example.com")
        assert result == "Tools"

    def test_app_url(self):
        """App URLs should be categorized as Applications."""
        result = categorize_url("https://example.com/app/dashboard", "example.com")
        assert result == "Applications"

    def test_docs_url(self):
        """Documentation URLs should be categorized as Documentation."""
        result = categorize_url("https://example.com/docs/api", "example.com")
        assert result == "Documentation"

    def test_doc_url_singular(self):
        """Singular doc URL should also be categorized as Documentation."""
        result = categorize_url("https://example.com/doc/getting-started", "example.com")
        assert result == "Documentation"

    def test_guide_url(self):
        """Guide URLs should be categorized as Guides."""
        result = categorize_url("https://example.com/guide/setup", "example.com")
        assert result == "Guides"

    def test_tutorial_url(self):
        """Tutorial URLs should be categorized as Tutorials."""
        result = categorize_url("https://example.com/tutorials/basics", "example.com")
        assert result == "Tutorials"

    def test_product_url(self):
        """Product URLs should be categorized as Products."""
        result = categorize_url("https://example.com/products/widget", "example.com")
        assert result == "Products"

    def test_service_url(self):
        """Service URLs should be categorized as Services."""
        result = categorize_url("https://example.com/services/consulting", "example.com")
        assert result == "Services"

    def test_about_url(self):
        """About URLs should be categorized as About."""
        result = categorize_url("https://example.com/about", "example.com")
        assert result == "About"

    def test_contact_url(self):
        """Contact URLs should be categorized as Contact."""
        result = categorize_url("https://example.com/contact", "example.com")
        assert result == "Contact"

    def test_privacy_url(self):
        """Privacy URLs should be categorized as Privacy & Legal."""
        result = categorize_url("https://example.com/privacy", "example.com")
        assert result == "Privacy & Legal"

    def test_terms_url(self):
        """Terms URLs should be categorized as Terms."""
        result = categorize_url("https://example.com/terms", "example.com")
        assert result == "Terms"

    def test_homepage_root(self):
        """Root URL should be categorized as _homepage."""
        result = categorize_url("https://example.com/", "example.com")
        assert result == "_homepage"

    def test_homepage_empty_path(self):
        """URL with empty path should be categorized as _homepage."""
        result = categorize_url("https://example.com", "example.com")
        assert result == "_homepage"

    def test_top_level_page_main_pages(self):
        """Top-level page without matching category should be Main Pages."""
        result = categorize_url("https://example.com/pricing", "example.com")
        assert result == "Main Pages"

    def test_deep_url_without_category_is_other(self):
        """Deep URL without matching category pattern should be Other."""
        result = categorize_url("https://example.com/foo/bar/baz", "example.com")
        assert result == "Other"

    def test_categorization_is_case_insensitive(self):
        """Categorization should be case-insensitive on path."""
        result = categorize_url("https://example.com/Blog/Post-Title", "example.com")
        assert result == "Blog & Articles"


# ============================================================================
# url_to_label() TESTS
# ============================================================================


class TestUrlToLabel:
    """Tests for the url_to_label function."""

    def test_homepage_label(self):
        """Root URL should produce 'Homepage' label."""
        result = url_to_label("https://example.com/", "example.com")
        assert result == "Homepage"

    def test_homepage_no_trailing_slash(self):
        """URL with no path should produce 'Homepage' label."""
        result = url_to_label("https://example.com", "example.com")
        assert result == "Homepage"

    def test_simple_slug(self):
        """Simple slug should be converted to title case."""
        result = url_to_label("https://example.com/about-us", "example.com")
        assert result == "About Us"

    def test_underscore_slug(self):
        """Underscored slug should be converted to title case."""
        result = url_to_label("https://example.com/privacy_policy", "example.com")
        assert result == "Privacy Policy"

    def test_nested_path_uses_last_segment(self):
        """Nested path should use the last segment for the label."""
        result = url_to_label("https://example.com/blog/my-first-post", "example.com")
        assert result == "My First Post"

    def test_numeric_slug_uses_parent(self):
        """Numeric-only last segment should include parent path."""
        result = url_to_label("https://example.com/post/123", "example.com")
        assert result == "Post/123"

    def test_single_word_slug(self):
        """Single word slug should be title cased."""
        result = url_to_label("https://example.com/contact", "example.com")
        assert result == "Contact"

    def test_deeply_nested_path(self):
        """Deeply nested path still uses the last segment."""
        result = url_to_label("https://example.com/a/b/c/deep-page", "example.com")
        assert result == "Deep Page"


# ============================================================================
# generate_llms_txt() TESTS
# ============================================================================


class TestGenerateLlmsTxt:
    """Tests for the main generate_llms_txt function."""

    def test_basic_generation_with_site_name(self):
        """Generated output should start with given site name header."""
        urls = [
            {"url": "https://example.com/", "priority": 1.0, "title": None},
            {"url": "https://example.com/about", "priority": 0.8, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert result.startswith("# MySite")

    def test_description_in_blockquote(self):
        """Generated output should contain the description as a blockquote."""
        urls = [{"url": "https://example.com/", "priority": 1.0, "title": None}]
        result = generate_llms_txt(
            "https://example.com", urls,
            site_name="MySite",
            description="A great site for tools"
        )
        assert "> A great site for tools" in result

    def test_auto_generated_site_name(self):
        """When no site_name is given, it should be derived from the domain."""
        urls = [{"url": "https://example.com/", "priority": 1.0, "title": None}]
        result = generate_llms_txt("https://example.com", urls)
        assert "# Example" in result

    def test_auto_generated_description(self):
        """When no description is given, it should be auto-generated."""
        urls = [{"url": "https://example.com/", "priority": 1.0, "title": None}]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "> Website MySite available at https://example.com" in result

    def test_homepage_link_included(self):
        """Homepage should be linked at the top of the output."""
        urls = [
            {"url": "https://example.com/", "priority": 1.0, "title": None},
            {"url": "https://example.com/about", "priority": 0.5, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "[MySite](https://example.com/)" in result

    def test_skipped_urls_excluded(self):
        """URLs matching skip patterns should not appear in output."""
        urls = [
            {"url": "https://example.com/", "priority": 1.0, "title": None},
            {"url": "https://example.com/login", "priority": 0.5, "title": None},
            {"url": "https://example.com/wp-admin/", "priority": 0.5, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "/login" not in result
        assert "/wp-admin" not in result

    def test_external_urls_excluded(self):
        """URLs from a different domain should not appear in output."""
        urls = [
            {"url": "https://example.com/", "priority": 1.0, "title": None},
            {"url": "https://other-domain.com/page", "priority": 0.5, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "other-domain.com" not in result

    def test_duplicate_urls_deduplicated(self):
        """Duplicate URLs should only appear once."""
        urls = [
            {"url": "https://example.com/about", "priority": 0.8, "title": None},
            {"url": "https://example.com/about", "priority": 0.5, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert result.count("https://example.com/about") == 1

    def test_section_headers_generated(self):
        """Category sections should appear as markdown h2 headers."""
        urls = [
            {"url": "https://example.com/blog/post-1", "priority": 0.8, "title": None},
            {"url": "https://example.com/docs/api", "priority": 0.7, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "## Blog & Articles" in result
        assert "## Documentation" in result

    def test_optional_section_for_secondary_categories(self):
        """Privacy/Legal, Terms, Contact, Other should go under Optional."""
        urls = [
            {"url": "https://example.com/privacy", "priority": 0.3, "title": None},
            {"url": "https://example.com/terms", "priority": 0.3, "title": None},
            {"url": "https://example.com/contact", "priority": 0.3, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "## Optional" in result
        assert "Privacy & Legal" in result

    def test_max_urls_per_section_respected(self):
        """max_urls_per_section should limit URLs in each section."""
        urls = []
        for i in range(25):
            urls.append({
                "url": f"https://example.com/blog/post-{i}",
                "priority": 0.5,
                "title": None,
            })
        result = generate_llms_txt(
            "https://example.com", urls,
            site_name="MySite",
            max_urls_per_section=5
        )
        # Count blog links (each starts with "- [")
        blog_section = result.split("## Blog & Articles")[1].split("##")[0] if "## Blog & Articles" in result else ""
        link_count = blog_section.count("- [")
        assert link_count == 5

    def test_url_title_used_when_provided(self):
        """Pre-existing title in url_data should be used as label."""
        urls = [
            {"url": "https://example.com/about", "priority": 0.8, "title": "About Our Company"},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "[About Our Company]" in result

    def test_relative_url_resolved(self):
        """Relative URLs should be resolved against the base URL."""
        urls = [
            {"url": "/pricing", "priority": 0.5, "title": None},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        assert "https://example.com/pricing" in result

    def test_empty_urls_produces_header_only(self):
        """Empty URL list should produce just the header with no sections."""
        result = generate_llms_txt("https://example.com", [], site_name="MySite")
        assert "# MySite" in result
        assert "##" not in result.replace("# MySite", "")

    def test_fetch_titles_calls_fetch_page_title(self):
        """When fetch_titles=True, fetch_page_title should be called for URLs without title."""
        urls = [
            {"url": "https://example.com/about", "priority": 0.8, "title": None},
        ]
        with patch("generate_llms_txt.fetch_page_title", return_value="Fetched About Title") as mock_fetch:
            result = generate_llms_txt(
                "https://example.com", urls,
                site_name="MySite",
                fetch_titles=True
            )
            mock_fetch.assert_called_once_with("https://example.com/about")
            assert "[Fetched About Title]" in result

    def test_fetch_titles_not_called_when_title_exists(self):
        """When a title already exists, fetch_page_title should not be called."""
        urls = [
            {"url": "https://example.com/about", "priority": 0.8, "title": "Existing Title"},
        ]
        with patch("generate_llms_txt.fetch_page_title") as mock_fetch:
            result = generate_llms_txt(
                "https://example.com", urls,
                site_name="MySite",
                fetch_titles=True
            )
            mock_fetch.assert_not_called()
            assert "[Existing Title]" in result

    def test_urls_sorted_by_priority(self):
        """Higher priority URLs should appear before lower priority ones."""
        urls = [
            {"url": "https://example.com/blog/low-priority", "priority": 0.1, "title": "Low Priority"},
            {"url": "https://example.com/blog/high-priority", "priority": 0.9, "title": "High Priority"},
        ]
        result = generate_llms_txt("https://example.com", urls, site_name="MySite")
        high_pos = result.index("High Priority")
        low_pos = result.index("Low Priority")
        assert high_pos < low_pos

    def test_www_domain_stripping_for_site_name(self):
        """www. prefix should be stripped when auto-generating site name."""
        urls = [{"url": "https://www.example.com/", "priority": 1.0, "title": None}]
        result = generate_llms_txt("https://www.example.com", urls)
        assert "# Example" in result


# ============================================================================
# fetch_sitemap() TESTS
# ============================================================================


class TestFetchSitemap:
    """Tests for the fetch_sitemap function (mocked HTTP)."""

    def _mock_session(self, response):
        """Helper to create a mocked session that returns the given response."""
        mock_session = MagicMock()
        mock_session.get.return_value = response
        return mock_session

    def test_parse_regular_sitemap(self):
        """Regular sitemap XML should be parsed into URL data dicts."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <priority>1.0</priority>
    <lastmod>2025-01-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/about</loc>
    <priority>0.8</priority>
  </url>
</urlset>"""
        mock_response = Mock()
        mock_response.content = xml_content
        mock_response.raise_for_status = Mock()

        mock_session = self._mock_session(mock_response)

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert len(urls) == 2
        assert urls[0]["url"] == "https://example.com/"
        assert urls[0]["priority"] == 1.0
        assert urls[0]["lastmod"] == "2025-01-01"
        assert urls[1]["url"] == "https://example.com/about"
        assert urls[1]["priority"] == 0.8
        assert urls[1]["lastmod"] is None

    def test_parse_sitemap_index(self):
        """Sitemap index should recursively fetch sub-sitemaps."""
        index_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-2.xml</loc>
  </sitemap>
</sitemapindex>"""

        sub_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page-1</loc>
  </url>
</urlset>"""

        mock_index_response = Mock()
        mock_index_response.content = index_xml
        mock_index_response.raise_for_status = Mock()

        mock_sub_response = Mock()
        mock_sub_response.content = sub_xml
        mock_sub_response.raise_for_status = Mock()

        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_index_response, mock_sub_response, mock_sub_response]

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap-index.xml")

        # Two sub-sitemaps each with 1 URL = 2 URLs total
        assert len(urls) == 2
        assert all(u["url"] == "https://example.com/page-1" for u in urls)

    def test_empty_sitemap(self):
        """Empty sitemap should return an empty list."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>"""
        mock_response = Mock()
        mock_response.content = xml_content
        mock_response.raise_for_status = Mock()

        mock_session = self._mock_session(mock_response)

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert urls == []

    def test_malformed_xml_returns_empty(self):
        """Malformed XML should return an empty list (no URLs parsed)."""
        mock_response = Mock()
        mock_response.content = b"<this is not valid xml"
        mock_response.raise_for_status = Mock()

        mock_session = self._mock_session(mock_response)

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert urls == []

    def test_network_error_returns_empty(self):
        """Network error during sitemap fetch should return an empty list."""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Connection refused")

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert urls == []

    def test_http_error_returns_empty(self):
        """HTTP error (e.g. 404) should return an empty list."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")

        mock_session = self._mock_session(mock_response)

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert urls == []

    def test_url_without_loc_skipped(self):
        """URL entries without a <loc> tag should be skipped."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/valid</loc>
  </url>
</urlset>"""
        mock_response = Mock()
        mock_response.content = xml_content
        mock_response.raise_for_status = Mock()

        mock_session = self._mock_session(mock_response)

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert len(urls) == 1
        assert urls[0]["url"] == "https://example.com/valid"

    def test_invalid_priority_defaults_to_0_5(self):
        """Invalid priority values should default to 0.5."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
    <priority>not-a-number</priority>
  </url>
</urlset>"""
        mock_response = Mock()
        mock_response.content = xml_content
        mock_response.raise_for_status = Mock()

        mock_session = self._mock_session(mock_response)

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert len(urls) == 1
        assert urls[0]["priority"] == 0.5

    def test_relative_loc_resolved(self):
        """Relative <loc> values should be resolved against the sitemap URL."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>/relative-page</loc>
  </url>
</urlset>"""
        mock_response = Mock()
        mock_response.content = xml_content
        mock_response.raise_for_status = Mock()

        mock_session = self._mock_session(mock_response)

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap.xml")

        assert len(urls) == 1
        assert urls[0]["url"] == "https://example.com/relative-page"

    def test_sitemap_index_limits_to_10_sub_sitemaps(self):
        """Sitemap index should process at most 10 sub-sitemaps."""
        sitemap_entries = ""
        for i in range(15):
            sitemap_entries += f"""
  <sitemap>
    <loc>https://example.com/sitemap-{i}.xml</loc>
  </sitemap>"""

        index_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</sitemapindex>""".encode()

        sub_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
  </url>
</urlset>"""

        mock_index_response = Mock()
        mock_index_response.content = index_xml
        mock_index_response.raise_for_status = Mock()

        mock_sub_response = Mock()
        mock_sub_response.content = sub_xml
        mock_sub_response.raise_for_status = Mock()

        # First call returns the index, next 10 calls return sub-sitemaps
        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_index_response] + [mock_sub_response] * 10

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            urls = fetch_sitemap("https://example.com/sitemap-index.xml")

        # 10 sub-sitemaps, 1 URL each = 10 URLs
        assert len(urls) == 10


# ============================================================================
# discover_sitemap() TESTS
# ============================================================================


class TestDiscoverSitemap:
    """Tests for the discover_sitemap function (mocked HTTP)."""

    def test_discover_from_robots_txt(self):
        """Sitemap URL in robots.txt should be discovered."""
        robots_response = Mock()
        robots_response.text = "User-agent: *\nDisallow:\nSitemap: https://example.com/sitemap.xml"

        mock_session = MagicMock()
        mock_session.get.return_value = robots_response

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = discover_sitemap("https://example.com")

        assert result == "https://example.com/sitemap.xml"

    def test_discover_from_robots_txt_case_insensitive(self):
        """Sitemap directive in robots.txt should be found case-insensitively."""
        robots_response = Mock()
        robots_response.text = "User-agent: *\nDisallow:\nsitemap: https://example.com/my-sitemap.xml"

        mock_session = MagicMock()
        mock_session.get.return_value = robots_response

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = discover_sitemap("https://example.com")

        assert result == "https://example.com/my-sitemap.xml"

    def test_discover_from_common_path(self):
        """When robots.txt has no sitemap, common paths should be tried."""
        robots_response = Mock()
        robots_response.text = "User-agent: *\nDisallow:"

        head_404 = Mock()
        head_404.status_code = 404

        head_200 = Mock()
        head_200.status_code = 200

        mock_session = MagicMock()
        mock_session.get.return_value = robots_response
        # First common path (/sitemap.xml) returns 200
        mock_session.head.return_value = head_200

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = discover_sitemap("https://example.com")

        assert result == "https://example.com/sitemap.xml"

    def test_discover_no_sitemap_found(self):
        """When no sitemap is found, None should be returned."""
        robots_response = Mock()
        robots_response.text = "User-agent: *\nDisallow:"

        head_404 = Mock()
        head_404.status_code = 404

        mock_session = MagicMock()
        mock_session.get.return_value = robots_response
        mock_session.head.return_value = head_404

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = discover_sitemap("https://example.com")

        assert result is None

    def test_discover_robots_txt_network_error(self):
        """Network error on robots.txt should fall through to common paths."""
        head_200 = Mock()
        head_200.status_code = 200

        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Connection error")
        mock_session.head.return_value = head_200

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = discover_sitemap("https://example.com")

        assert result == "https://example.com/sitemap.xml"

    def test_discover_all_common_paths_fail(self):
        """When all common paths also error, None should be returned."""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Connection error")
        mock_session.head.side_effect = Exception("Connection error")

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = discover_sitemap("https://example.com")

        assert result is None


# ============================================================================
# fetch_page_title() TESTS
# ============================================================================


class TestFetchPageTitle:
    """Tests for the fetch_page_title function (mocked HTTP)."""

    def test_fetch_title_tag(self):
        """Title from <title> tag should be returned."""
        mock_response = Mock()
        mock_response.text = "<html><head><title>My Great Page</title></head><body></body></html>"

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = fetch_page_title("https://example.com/page")

        assert result == "My Great Page"

    def test_fetch_h1_fallback(self):
        """When no <title>, the <h1> tag should be used as fallback."""
        mock_response = Mock()
        mock_response.text = "<html><body><h1>Page Heading</h1></body></html>"

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = fetch_page_title("https://example.com/page")

        assert result == "Page Heading"

    def test_fetch_no_title_or_h1(self):
        """When neither <title> nor <h1> exists, None should be returned."""
        mock_response = Mock()
        mock_response.text = "<html><body><p>Just a paragraph</p></body></html>"

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = fetch_page_title("https://example.com/page")

        assert result is None

    def test_fetch_network_error_returns_none(self):
        """Network error should return None without raising."""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Timeout")

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = fetch_page_title("https://example.com/page")

        assert result is None

    def test_fetch_title_with_whitespace(self):
        """Title with leading/trailing whitespace should be stripped."""
        mock_response = Mock()
        mock_response.text = "<html><head><title>  Spaced Title  </title></head></html>"

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        with patch("http_utils.create_session_with_retry", return_value=mock_session):
            result = fetch_page_title("https://example.com/page")

        assert result == "Spaced Title"


# ============================================================================
# main() / CLI TESTS
# ============================================================================


class TestMainCLI:
    """Tests for the main() CLI entry point."""

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap", return_value="https://example.com/sitemap.xml")
    @patch("generate_llms_txt.fetch_sitemap", return_value=[
        {"url": "https://example.com/", "priority": 1.0, "title": None},
        {"url": "https://example.com/about", "priority": 0.8, "title": None},
    ])
    def test_main_stdout_output(self, mock_fetch, mock_discover, mock_deps, capsys):
        """Main should print llms.txt to stdout when no --output is given."""
        from generate_llms_txt import main

        with patch("sys.argv", ["generate_llms_txt.py", "--base-url", "https://example.com"]):
            main()

        captured = capsys.readouterr()
        assert "# Example" in captured.out

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap", return_value="https://example.com/sitemap.xml")
    @patch("generate_llms_txt.fetch_sitemap", return_value=[
        {"url": "https://example.com/", "priority": 1.0, "title": None},
    ])
    def test_main_file_output(self, mock_fetch, mock_discover, mock_deps, tmp_path):
        """Main should write llms.txt to a file when --output is given."""
        from generate_llms_txt import main

        output_file = tmp_path / "llms.txt"
        with patch("sys.argv", [
            "generate_llms_txt.py", "--base-url", "https://example.com",
            "--output", str(output_file)
        ]):
            main()

        assert output_file.exists()
        content = output_file.read_text()
        assert "# Example" in content

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap", return_value=None)
    def test_main_no_sitemap_creates_minimal(self, mock_discover, mock_deps, capsys):
        """When no sitemap is found and no --sitemap given, minimal llms.txt is produced."""
        from generate_llms_txt import main

        with patch("sys.argv", [
            "generate_llms_txt.py", "--base-url", "https://example.com",
            "--site-name", "MySite"
        ]):
            main()

        captured = capsys.readouterr()
        assert "# MySite" in captured.out
        assert "[Homepage](https://example.com)" in captured.out

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap", return_value="https://example.com/sitemap.xml")
    @patch("generate_llms_txt.fetch_sitemap", return_value=[])
    def test_main_empty_sitemap_exits(self, mock_fetch, mock_discover, mock_deps):
        """When sitemap is found but has no URLs, main should sys.exit(1)."""
        from generate_llms_txt import main

        with patch("sys.argv", ["generate_llms_txt.py", "--base-url", "https://example.com"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap", return_value="https://example.com/sitemap.xml")
    @patch("generate_llms_txt.fetch_sitemap", return_value=[
        {"url": "https://example.com/", "priority": 1.0, "title": None},
    ])
    def test_main_adds_https_if_missing(self, mock_fetch, mock_discover, mock_deps, capsys):
        """Base URL without scheme should have https:// prepended."""
        from generate_llms_txt import main

        with patch("sys.argv", ["generate_llms_txt.py", "--base-url", "example.com"]):
            main()

        captured = capsys.readouterr()
        assert "https://example.com" in captured.out

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap", return_value=None)
    def test_main_no_sitemap_file_output(self, mock_discover, mock_deps, tmp_path):
        """When no sitemap found, minimal llms.txt should be written to file."""
        from generate_llms_txt import main

        output_file = tmp_path / "llms.txt"
        with patch("sys.argv", [
            "generate_llms_txt.py", "--base-url", "https://example.com",
            "--output", str(output_file),
            "--site-name", "TestSite",
            "--description", "A test site"
        ]):
            main()

        assert output_file.exists()
        content = output_file.read_text()
        assert "# TestSite" in content
        assert "> A test site" in content

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap")
    @patch("generate_llms_txt.fetch_sitemap", return_value=[
        {"url": "https://example.com/", "priority": 1.0, "title": None},
    ])
    def test_main_explicit_sitemap_skips_discovery(self, mock_fetch, mock_discover, mock_deps, capsys):
        """Providing --sitemap should skip auto-discovery."""
        from generate_llms_txt import main

        with patch("sys.argv", [
            "generate_llms_txt.py", "--base-url", "https://example.com",
            "--sitemap", "https://example.com/custom-sitemap.xml"
        ]):
            main()

        mock_discover.assert_not_called()
        mock_fetch.assert_called_once_with("https://example.com/custom-sitemap.xml")

    @patch("generate_llms_txt._ensure_deps")
    @patch("generate_llms_txt.discover_sitemap", return_value="https://example.com/sitemap.xml")
    @patch("generate_llms_txt.fetch_sitemap", return_value=[
        {"url": "https://example.com/", "priority": 1.0, "title": None},
    ])
    def test_main_custom_site_name_and_description(self, mock_fetch, mock_discover, mock_deps, capsys):
        """Custom --site-name and --description should appear in output."""
        from generate_llms_txt import main

        with patch("sys.argv", [
            "generate_llms_txt.py", "--base-url", "https://example.com",
            "--site-name", "CustomName",
            "--description", "Custom description here"
        ]):
            main()

        captured = capsys.readouterr()
        assert "# CustomName" in captured.out
        assert "> Custom description here" in captured.out


# ============================================================================
# _ensure_deps() TESTS
# ============================================================================


class TestEnsureDeps:
    """Tests for the _ensure_deps lazy import function."""

    def test_ensure_deps_sets_globals(self):
        """After calling _ensure_deps, requests and BeautifulSoup should be set."""
        import generate_llms_txt as mod
        # Reset globals to trigger re-import
        original_requests = mod.requests
        mod.requests = None
        try:
            mod._ensure_deps()
            assert mod.requests is not None
            assert mod.BeautifulSoup is not None
        finally:
            mod.requests = original_requests

    def test_ensure_deps_noop_when_already_loaded(self):
        """When requests is already loaded, _ensure_deps should be a no-op."""
        import generate_llms_txt as mod
        original = mod.requests
        assert original is not None  # already loaded by autouse fixture
        mod._ensure_deps()
        # Should still be the same object
        assert mod.requests is original

    def test_ensure_deps_exits_on_import_error(self):
        """When dependencies are missing, _ensure_deps should sys.exit(1)."""
        import generate_llms_txt as mod
        original_requests = mod.requests
        mod.requests = None
        try:
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                with pytest.raises(SystemExit) as exc_info:
                    mod._ensure_deps()
                assert exc_info.value.code == 1
        finally:
            mod.requests = original_requests
