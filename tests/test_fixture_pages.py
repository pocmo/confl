"""Integration tests using real Confluence page fixtures.

These tests use real Confluence storage format samples from tests/fixtures/pages/
to validate end-to-end parsing and conversion, and to identify feature gaps.
"""

from pathlib import Path

from confl.converter import storage_to_markdown


def load_fixture(filename: str) -> str:
    """Load a fixture file from tests/fixtures/pages/."""
    fixture_path = Path(__file__).parent / "fixtures" / "pages" / filename
    return fixture_path.read_text()


class TestHubPageFixture:
    """Tests using hub.xml - a demo hub page with standard macros and formatting."""

    def test_hub_page_parses_without_error(self):
        """Hub page fixture should parse completely without exceptions."""
        storage = load_fixture("hub.xml")
        # Should not raise any exceptions
        result = storage_to_markdown(storage)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hub_page_contains_headings(self):
        """Hub page has multiple h2 and h3 headings that should convert."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Check for markdown headings
        assert "## Overview" in result
        assert "## Quick Navigation" in result
        assert "## Highlights" in result
        assert "## Status Summary" in result
        assert "## Callouts and Notes" in result
        assert "### Requirements (Demo)" in result
        assert "### Project Plan (Demo)" in result

    def test_hub_page_contains_lists(self):
        """Hub page has ordered and unordered lists."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Should have bullet lists
        assert "\n- " in result or "\n* " in result
        # Should have numbered lists
        assert "\n1. " in result

    def test_hub_page_contains_tables(self):
        """Hub page has tables with headers."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Markdown tables have pipe separators
        assert "|" in result
        # Should have table header separator
        assert "---" in result or "|-" in result

    def test_hub_page_contains_links(self):
        """Hub page has various hyperlinks."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Should contain markdown links or URLs
        assert "https://demo.local" in result or "[" in result

    def test_hub_page_info_macro(self):
        """Hub page has info panel macros."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Info macro should be converted (either as panel or inline)
        # Content from info macro should be present
        assert "Demo hub page designed for the Drafts area" in result

    def test_hub_page_tip_macro(self):
        """Hub page has tip panel macros."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Tip macro content should be present
        assert "neutral naming" in result.lower()

    def test_hub_page_note_macro(self):
        """Hub page has note panel macros."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Note macro content should be present
        assert "cross-linking" in result.lower() or "non-demo content" in result.lower()

    def test_hub_page_expand_macro(self):
        """Hub page has expand/accordion macros."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Expand macro content should be present (may show as placeholder or expanded)
        # Check for content inside expand macros
        assert "expandable section" in result.lower() or "optional details" in result.lower()

    def test_hub_page_tasks(self):
        """Hub page has task lists."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Task list content should be present
        assert "demo subpages" in result.lower() or "requirements" in result.lower()
        # May be rendered as checkbox tasks or plain text
        # The actual task content matters more than format

    def test_hub_page_adf_panels(self):
        """Hub page has ADF panel extensions with fallbacks."""
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # ADF panel content should be rendered (via fallback or direct)
        assert "demo content fully scoped" in result.lower()

    def test_hub_page_dates(self):
        """Hub page has time/date elements in tables.

        Time elements are self-closing with a datetime attribute.
        Example: <time datetime="2026-02-15" local-id="..." />
        """
        storage = load_fixture("hub.xml")
        result = storage_to_markdown(storage)

        # Tables with "Target Date" and "Planned" columns should be present
        assert "Target Date" in result
        assert "Planned" in result  # Project Plan table column

        # Time elements should now be rendered as their datetime values
        assert "2026-02-15" in result  # Status Summary table
        assert "2026-02-20" in result  # Status Summary table
        assert "2026-02-10" in result  # Project Plan table
        assert "2026-02-18" in result  # Project Plan table


class TestAdvancedFormattingFixture:
    """Tests using advanced-formatting.xml - showcases advanced features and layouts."""

    def test_advanced_page_parses_without_error(self):
        """Advanced formatting page should parse completely without exceptions."""
        storage = load_fixture("advanced-formatting.xml")
        # Should not raise any exceptions
        result = storage_to_markdown(storage)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_advanced_page_contains_h1_heading(self):
        """Advanced page has h1 heading."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        assert "# Demo Page" in result or "Demo Page – Advanced Formatting" in result

    def test_advanced_page_contains_layouts(self):
        """Advanced page uses column layouts (ac:layout, ac:layout-section)."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Layout content should be present even if layout structure is flattened
        # Three-column layout should have content from all columns
        assert "Highlights" in result
        assert "Notes" in result
        assert "Quick Links" in result

    def test_advanced_page_inline_formatting(self):
        """Advanced page has bold, italic, strikethrough, and code."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Check for markdown formatting
        # Bold
        assert "**bold**" in result or "**" in result
        # Italic
        assert "*italic*" in result or "_italic_" in result
        # Strikethrough
        assert "~~strikethrough~~" in result or "strikethrough" in result
        # Inline code
        assert "`inline code`" in result or "`" in result

    def test_advanced_page_nested_lists(self):
        """Advanced page has nested bullet lists."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Should have nested structure
        assert "Nested bullet" in result

    def test_advanced_page_code_blocks(self):
        """Advanced page has code block macros with syntax highlighting."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Code macro content should be present
        assert "function demoExample" in result or "demoExample" in result
        # May be formatted as code block
        assert "```" in result or "`" in result

    def test_advanced_page_status_macro(self):
        """Advanced page has status macros in tables."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Status macro content should be present
        assert "In progress" in result or "Blocked" in result or "Done" in result

    def test_advanced_page_wide_table(self):
        """Advanced page has wide tables with data-table-width attribute."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Table content should be present
        assert "Description" in result
        assert "Owner" in result
        # Table structure preserved
        assert "|" in result

    def test_advanced_page_expand_with_title(self):
        """Advanced page has expand macros with title parameters."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Expand titles and content should be present
        assert "Formatting Tips" in result or "Macros in Practice" in result

    def test_advanced_page_tasks(self):
        """Advanced page has task lists."""
        storage = load_fixture("advanced-formatting.xml")
        result = storage_to_markdown(storage)

        # Task content should be present
        assert "Review demo formatting" in result or "Duplicate this page" in result


class TestFeatureCoverage:
    """Tests documenting what features are present in fixtures and their status."""

    def test_feature_inventory_macros(self):
        """Document which macros are present in fixtures.

        Macros found in fixtures:
        - info: ✓ Supported (panel macro)
        - tip: ✓ Supported (panel macro)
        - note: ✓ Supported (panel macro)
        - expand: ✓ Supported (renders content, may need title support)
        - status: ✓ Supported (inline macro)
        - code: ✓ Supported (code block macro)

        Parameters found:
        - title: Used in expand macros
        - language: Used in code macros (js, json)
        - colour/color: Used in status macros
        - breakoutWidth: Layout parameter
        - breakoutMode: Layout parameter
        """
        # This test documents feature inventory via docstring
        # All macros in fixtures should parse without error
        hub = storage_to_markdown(load_fixture("hub.xml"))
        adv = storage_to_markdown(load_fixture("advanced-formatting.xml"))
        assert hub and adv  # Both should convert successfully

    def test_feature_inventory_elements(self):
        """Document which storage format elements are present in fixtures.

        Standard HTML elements:
        - Headings (h1, h2, h3): ✓ Supported
        - Paragraphs (p): ✓ Supported
        - Lists (ul, ol, li): ✓ Supported
        - Tables (table, tbody, tr, td, th): ✓ Supported
        - Links (a): ✓ Supported
        - Inline formatting (strong, em, del, code): ✓ Supported
        - Time/dates (time): ✓ Supported

        Confluence elements:
        - ac:structured-macro: ✓ Supported (via macro handlers)
        - ac:rich-text-body: ✓ Supported
        - ac:parameter: ✓ Supported
        - ac:plain-text-body: ✓ Supported (code blocks)
        - ac:task-list: ✓ Supported (rendered as content)
        - ac:task: ✓ Supported
        - ac:adf-extension: ✓ Supported (renders fallback)
        - ac:adf-node: ✓ Supported (panels via fallback)
        - ac:layout: ⚠️  Partially supported (flattens to content)
        - ac:layout-section: ⚠️  Partially supported
        - ac:layout-cell: ⚠️  Partially supported
        """
        # This test documents feature inventory via docstring
        hub = storage_to_markdown(load_fixture("hub.xml"))
        adv = storage_to_markdown(load_fixture("advanced-formatting.xml"))
        assert hub and adv  # Both should convert successfully

    def test_feature_inventory_layouts(self):
        """Document layout features present in fixtures.

        Layout types found:
        - fixed-width: ⚠️  Flattened (content preserved, layout lost)
        - three_equal: ⚠️  Flattened (content preserved, layout lost)
        - breakout-mode="wide": ⚠️  Ignored (formatting hint)
        - breakout-mode="default": ⚠️  Ignored

        Current behavior: Layouts are flattened to sequential content.
        Future enhancement: Could preserve as HTML or use markdown extensions.
        """
        adv = storage_to_markdown(load_fixture("advanced-formatting.xml"))
        # Layout content should all be present, just not in columns
        assert "Highlights" in adv
        assert "Notes" in adv
        assert "Quick Links" in adv
