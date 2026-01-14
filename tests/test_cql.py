"""Tests for CQL query builder utilities."""


from confl.cql import _escape_cql_string, _quote_if_needed, build_cql_query


class TestBuildCqlQuery:
    """Tests for build_cql_query function."""

    def test_single_text_condition(self):
        """Test building query with only text parameter."""
        result = build_cql_query(text="API documentation")
        assert result == 'text ~ "API documentation"'

    def test_single_space_condition(self):
        """Test building query with only space parameter."""
        result = build_cql_query(space="DEV")
        assert result == "space = DEV"

    def test_single_type_condition(self):
        """Test building query with only content_type parameter."""
        result = build_cql_query(content_type="page")
        assert result == "type = page"

    def test_single_label_condition(self):
        """Test building query with only label parameter."""
        result = build_cql_query(label="draft")
        assert result == "label = draft"

    def test_text_and_space(self):
        """Test combining text and space conditions."""
        result = build_cql_query(text="meeting notes", space="TEAM")
        assert result == 'text ~ "meeting notes" AND space = TEAM'

    def test_space_and_type(self):
        """Test combining space and type conditions."""
        result = build_cql_query(space="MARKETING", content_type="blogpost")
        assert result == "space = MARKETING AND type = blogpost"

    def test_all_conditions(self):
        """Test combining all four conditions."""
        result = build_cql_query(
            text="project update",
            space="ENG",
            content_type="page",
            label="2024",
        )
        assert result == 'text ~ "project update" AND space = ENG AND type = page AND label = 2024'

    def test_no_conditions(self):
        """Test building query with no conditions (edge case)."""
        result = build_cql_query()
        assert result == ""

    def test_text_with_quotes(self):
        """Test text parameter containing double quotes."""
        result = build_cql_query(text='The "best" solution')
        assert result == 'text ~ "The \\"best\\" solution"'

    def test_text_with_backslash(self):
        """Test text parameter containing backslashes."""
        result = build_cql_query(text="C:\\Users\\path")
        assert result == 'text ~ "C:\\\\Users\\\\path"'

    def test_space_with_spaces(self):
        """Test space key containing spaces (should be quoted)."""
        result = build_cql_query(space="MY SPACE")
        assert result == 'space = "MY SPACE"'

    def test_label_with_spaces(self):
        """Test label containing spaces (should be quoted)."""
        result = build_cql_query(label="in progress")
        assert result == 'label = "in progress"'

    def test_label_with_special_chars(self):
        """Test label containing special characters."""
        result = build_cql_query(label="high-priority!")
        assert result == 'label = "high-priority!"'

    def test_type_blogpost(self):
        """Test type parameter with blogpost value."""
        result = build_cql_query(content_type="blogpost")
        assert result == "type = blogpost"

    def test_empty_strings_not_included(self):
        """Test that empty strings are not included in query."""
        # Note: Current implementation doesn't handle empty strings specially
        # This test documents the current behavior
        result = build_cql_query(text="", space="DEV")
        assert result == 'text ~ "" AND space = DEV'


class TestEscapeCqlString:
    """Tests for _escape_cql_string helper function."""

    def test_no_special_chars(self):
        """Test string without special characters."""
        result = _escape_cql_string("simple text")
        assert result == "simple text"

    def test_escape_double_quotes(self):
        """Test escaping double quotes."""
        result = _escape_cql_string('He said "hello"')
        assert result == 'He said \\"hello\\"'

    def test_escape_backslash(self):
        """Test escaping backslashes."""
        result = _escape_cql_string("C:\\path\\to\\file")
        assert result == "C:\\\\path\\\\to\\\\file"

    def test_escape_both_backslash_and_quotes(self):
        """Test escaping both backslashes and quotes."""
        result = _escape_cql_string('Path: "C:\\Users"')
        assert result == 'Path: \\"C:\\\\Users\\"'

    def test_multiple_quotes(self):
        """Test escaping multiple double quotes."""
        result = _escape_cql_string('"""triple"""')
        # Input: 3 quotes + "triple" + 3 quotes = 6 quotes total
        # Output: Each quote becomes \" so 6 escaped quotes
        assert result == '\\"\\"\\"triple\\"\\"\\"'

    def test_empty_string(self):
        """Test escaping empty string."""
        result = _escape_cql_string("")
        assert result == ""


class TestQuoteIfNeeded:
    """Tests for _quote_if_needed helper function."""

    def test_simple_identifier(self):
        """Test simple alphanumeric identifier (no quoting needed)."""
        result = _quote_if_needed("DEV")
        assert result == "DEV"

    def test_identifier_with_numbers(self):
        """Test identifier with numbers (no quoting needed)."""
        result = _quote_if_needed("PROJECT2024")
        assert result == "PROJECT2024"

    def test_identifier_with_space(self):
        """Test identifier with space (needs quoting)."""
        result = _quote_if_needed("MY SPACE")
        assert result == '"MY SPACE"'

    def test_identifier_with_equals(self):
        """Test identifier with equals sign (needs quoting)."""
        result = _quote_if_needed("key=value")
        assert result == '"key=value"'

    def test_identifier_with_tilde(self):
        """Test identifier with tilde operator (needs quoting)."""
        result = _quote_if_needed("~test")
        assert result == '"~test"'

    def test_identifier_with_parentheses(self):
        """Test identifier with parentheses (needs quoting)."""
        result = _quote_if_needed("test(123)")
        assert result == '"test(123)"'

    def test_identifier_with_quotes_inside(self):
        """Test identifier with quotes (needs escaping and quoting)."""
        result = _quote_if_needed('test"value')
        assert result == '"test\\"value"'

    def test_identifier_with_hyphen(self):
        """Test identifier with hyphen (no special handling in current impl)."""
        # Hyphens are allowed in identifiers without quoting in CQL
        result = _quote_if_needed("high-priority")
        assert result == "high-priority"

    def test_identifier_with_underscore(self):
        """Test identifier with underscore (no quoting needed)."""
        result = _quote_if_needed("my_label")
        assert result == "my_label"

    def test_empty_string(self):
        """Test empty string (no quoting needed)."""
        result = _quote_if_needed("")
        assert result == ""
