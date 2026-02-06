"""Markdown to Confluence storage format conversion."""

import html
import logging
from typing import Any
from urllib.parse import quote

import mistune
from bs4 import Tag
from markdownify import MarkdownConverter

logger = logging.getLogger(__name__)


class ConfluenceStorageRenderer(mistune.HTMLRenderer):
    """Custom Mistune renderer that outputs Confluence storage format XHTML."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with HTML escaping enabled by default."""
        # Always escape HTML for security
        super().__init__(escape=True, **kwargs)

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        """Render heading as Confluence storage format."""
        return f"<h{level}>{text}</h{level}>\n"

    def paragraph(self, text: str) -> str:
        """Render paragraph as Confluence storage format."""
        return f"<p>{text}</p>\n"

    def strong(self, text: str) -> str:
        """Render bold text."""
        return f"<strong>{text}</strong>"

    def emphasis(self, text: str) -> str:
        """Render italic text."""
        return f"<em>{text}</em>"

    def codespan(self, text: str) -> str:
        """Render inline code."""
        escaped_text = html.escape(text)
        return f"<code>{escaped_text}</code>"

    def block_code(self, code: str, info: str | None = None) -> str:
        """Render code block as Confluence code macro."""
        language = info.split()[0] if info else ""
        # Don't escape code in CDATA - it's already protected
        clean_code = code.rstrip()

        # Use Confluence code macro for syntax highlighting
        macro = '<ac:structured-macro ac:name="code"'
        if language:
            macro += (
                f' ac:schema-version="1"><ac:parameter ac:name="language">{language}</ac:parameter>'
            )
        else:
            macro += ' ac:schema-version="1">'

        macro += f"<ac:plain-text-body><![CDATA[{clean_code}]]></ac:plain-text-body>"
        macro += "</ac:structured-macro>\n"
        return macro

    def linebreak(self) -> str:
        """Render line break."""
        return "<br />"

    def softbreak(self) -> str:
        """Render soft line break (space)."""
        return " "

    def link(self, text: str, url: str, title: str | None = None) -> str:
        """Render link."""
        link_text = text if text else url
        safe_url = self.safe_url(url)
        return f'<a href="{safe_url}">{link_text}</a>'

    def image(self, text: str, url: str, title: str | None = None) -> str:
        """Render image as Confluence image tag."""
        alt = text
        safe_url = self.safe_url(url)
        # For external images, use ri:url
        if url.startswith(("http://", "https://")):
            img = f'<ac:image><ri:url ri:value="{safe_url}" />'
            if alt:
                img += f"<ac:caption><p>{html.escape(alt)}</p></ac:caption>"
            img += "</ac:image>"
            return img
        else:
            # For attachments, use ri:attachment
            img = f'<ac:image><ri:attachment ri:filename="{html.escape(url)}" />'
            if alt:
                img += f"<ac:caption><p>{html.escape(alt)}</p></ac:caption>"
            img += "</ac:image>"
            return img

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        """Render list (ordered or unordered)."""
        tag = "ol" if ordered else "ul"
        return f"<{tag}>\n{text}</{tag}>\n"

    def list_item(self, text: str) -> str:
        """Render list item."""
        return f"<li>{text}</li>\n"

    def block_quote(self, text: str) -> str:
        """
        Render block quote.

        Supports special syntax for Confluence panels:
        > **INFO**: Content → info panel
        > **WARNING**: Content → warning panel
        > **NOTE**: Content → note panel
        > **TIP**: Content → tip panel
        """
        stripped = text.strip()

        # Strip surrounding <p></p> tags if present (added by paragraph renderer)
        if stripped.startswith("<p>") and stripped.endswith("</p>"):
            stripped = stripped[3:-4].strip()

        # Check for panel syntax: **LABEL**: content
        for panel_type in ["INFO", "WARNING", "NOTE", "TIP"]:
            prefix = f"<strong>{panel_type}</strong>:"
            if stripped.startswith(prefix):
                content = stripped[len(prefix) :].strip()
                macro_name = panel_type.lower()
                return (
                    f'<ac:structured-macro ac:name="{macro_name}" ac:schema-version="1">'
                    f"<ac:rich-text-body><p>{content}</p></ac:rich-text-body>"
                    f"</ac:structured-macro>\n"
                )

        # Regular blockquote - restore paragraph tag if we removed it
        return f"<blockquote><p>{stripped}</p></blockquote>\n"

    def thematic_break(self) -> str:
        """Render horizontal rule."""
        return "<hr />\n"

    def text(self, text: str) -> str:
        """Render plain text - escape HTML entities."""
        return html.escape(text)

    def table(self, text: str) -> str:
        """Render table."""
        return f"<table>\n{text}</table>\n"

    def table_head(self, text: str) -> str:
        """Render table head."""
        return f"<thead>\n<tr>\n{text}</tr>\n</thead>\n"

    def table_body(self, text: str) -> str:
        """Render table body."""
        return f"<tbody>\n{text}</tbody>\n"

    def table_row(self, text: str) -> str:
        """Render table row."""
        return f"<tr>\n{text}</tr>\n"

    def table_cell(self, text: str, align: str | None = None, head: bool = False) -> str:
        """Render table cell."""
        tag = "th" if head else "td"
        attrs = f' style="text-align:{align}"' if align else ""
        return f"<{tag}{attrs}>{text}</{tag}>\n"


def markdown_to_storage(markdown: str) -> str:
    """
    Convert Markdown to Confluence storage format.

    Args:
        markdown: Markdown text to convert

    Returns:
        Confluence storage format XHTML string

    Supported features:
        - Headings (h1-h6)
        - Bold (**text**) and italic (*text*)
        - Lists (ordered and unordered)
        - Code blocks (with syntax highlighting)
        - Inline code
        - Links
        - Images (external URLs and attachments)
        - Tables
        - Block quotes
        - Confluence panels (info/warning/note/tip) via special blockquote syntax
        - Horizontal rules

    Example:
        >>> md = "# Hello\\n\\nThis is **bold** text."
        >>> storage = markdown_to_storage(md)
        >>> print(storage)
        <h1>Hello</h1>
        <p>This is <strong>bold</strong> text.</p>
    """
    renderer = ConfluenceStorageRenderer()
    md = mistune.create_markdown(renderer=renderer, plugins=["table"])
    result = md(markdown)
    # With a renderer, mistune always returns a string
    assert isinstance(result, str)
    return result.rstrip() + "\n"


class ConfluenceMarkdownConverter(MarkdownConverter):
    """Custom markdownify converter that handles Confluence storage format tags."""

    def __init__(
        self, base_url: str | None = None, space_key: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize converter with optional base URL for internal links.

        Args:
            base_url: Confluence base URL (e.g., 'https://company.atlassian.net/wiki')
                     Used to construct clickable URLs for internal page links.
            space_key: Current page's space key, used as fallback for links without explicit space.
            **kwargs: Additional arguments passed to MarkdownConverter.
        """
        super().__init__(**kwargs)
        self.base_url = base_url.rstrip("/") if base_url else None
        self.space_key = space_key

    def convert_ac_structured_macro(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence structured macro to Markdown."""
        macro_name_attr = el.get("ac:name", "")
        # el.get() can return a list in some edge cases, ensure it's a string
        macro_name = macro_name_attr if isinstance(macro_name_attr, str) else ""

        # Handle code macro
        if macro_name == "code":
            # Extract language parameter
            language = ""
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "language":
                    language = param.get_text().strip()
                    break

            # Extract code content from plain-text-body
            code_body = el.find("ac:plain-text-body")
            if code_body is not None:
                code_text = code_body.get_text().strip()
                return f"```{language}\n{code_text}\n```\n\n"
            else:
                # Empty code block - still render as code fence
                return f"```{language}\n```\n\n"

        # Handle info/warning/note panels
        if macro_name in ("info", "warning", "note", "tip"):
            # Extract rich-text-body content
            rich_body = el.find("ac:rich-text-body")
            if rich_body is not None:
                # Convert the content inside recursively
                inner_md = self.process_tag(rich_body, **options)  # type: ignore[attr-defined]
                return f"> **{macro_name.upper()}**: {inner_md.strip()}\n\n"

        # Handle status macro
        if macro_name == "status":
            # Extract title and color parameters
            title = ""
            color = ""
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "title":
                    title = param.get_text().strip()
                elif param_name == "colour":
                    color = param.get_text().strip()

            # Convert to badge-like Markdown (use bold with emoji indicators)
            color_emoji = {
                "Green": "✅",
                "Yellow": "⚠️",
                "Red": "❌",
                "Blue": "ℹ️",
                "Grey": "⚪",
            }.get(color, "▪️")

            return f"{color_emoji} **{title}** "

        # Handle expand macro (collapsible content)
        if macro_name == "expand":
            # Extract title parameter
            expand_title: str | None = None
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "title":
                    expand_title = param.get_text().strip()
                    break

            # Extract rich-text-body content
            rich_body = el.find("ac:rich-text-body")
            if rich_body is not None:
                # If no explicit title, try to extract from first paragraph
                if expand_title is None:
                    first_p = rich_body.find("p")
                    if first_p is not None:
                        # Use first paragraph as title
                        expand_title = first_p.get_text().strip()
                        # Remove the first paragraph from the body
                        first_p.decompose()
                    else:
                        expand_title = "Details"

                inner_md = self.process_tag(rich_body, **options)  # type: ignore[attr-defined]
                # Convert to details/summary HTML (supported in many Markdown renderers)
                return (
                    f"<details>\n<summary>{expand_title}</summary>\n\n"
                    f"{inner_md.strip()}\n</details>\n\n"
                )

        # Handle table of contents macro
        if macro_name == "toc":
            return "_Table of Contents_\n\n"

        # Handle jira macro (Jira issue integration)
        if macro_name == "jira":
            # Extract parameters - can be single key, multiple keys, or JQL query
            jql_query = ""
            keys = []

            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                param_value = param.get_text().strip()

                if param_name == "key":
                    # Single issue key or comma-separated keys
                    if param_value:
                        keys.extend([k.strip() for k in param_value.split(",")])
                elif param_name == "jqlQuery":
                    jql_query = param_value

            # Format output based on what we found
            if jql_query:
                return f"[Jira query: {jql_query}]\n\n"
            elif keys:
                keys_str = ", ".join(keys)
                return f"[Jira: {keys_str}]\n\n"
            else:
                # Macro present but no recognizable parameters
                return "[Jira]\n\n"

        # Handle excerpt macro (reusable content blocks)
        if macro_name == "excerpt":
            # Extract rich-text-body content
            rich_body = el.find("ac:rich-text-body")
            if rich_body is not None:
                # Convert the content inside recursively
                inner_md = self.process_tag(rich_body, **options)  # type: ignore[attr-defined]
                return f"[Excerpt]\n\n{inner_md.strip()}\n\n"
            # If no rich-text-body, just show the label
            return "[Excerpt]\n\n"

        # Handle children macro (lists child pages)
        if macro_name == "children":
            # Extract parameters to provide context
            params = {}
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                param_value = param.get_text().strip()
                if param_name and param_value:
                    params[param_name] = param_value

            # Build descriptive placeholder based on parameters
            if params:
                # Common parameters: sort, depth, all, page, excerpt, etc.
                param_parts = []
                if "sort" in params:
                    param_parts.append(f"sorted by {params['sort']}")
                if "depth" in params:
                    param_parts.append(f"depth {params['depth']}")
                if "all" in params and params["all"].lower() == "true":
                    param_parts.append("include all descendants")

                if param_parts:
                    param_desc = ", ".join(param_parts)
                    return f"[Child pages: {param_desc}]\n\n"

            # Default placeholder
            return "[Child pages]\n\n"

        # Handle attachments macro (lists files on page)
        if macro_name == "attachments":
            # Extract parameters to provide context
            params = {}
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                param_value = param.get_text().strip()
                if param_name and param_value:
                    params[param_name] = param_value

            # Build descriptive placeholder based on parameters
            if params:
                # Common parameters: old (show old versions), upload (allow upload), etc.
                param_parts = []
                if "old" in params and params["old"].lower() == "true":
                    param_parts.append("include old versions")
                if "upload" in params and params["upload"].lower() == "true":
                    param_parts.append("upload enabled")
                if "patterns" in params:
                    param_parts.append(f"pattern: {params['patterns']}")

                if param_parts:
                    param_desc = ", ".join(param_parts)
                    return f"[Page attachments: {param_desc}]\n\n"

            # Default placeholder
            return "[Page attachments]\n\n"

        # Handle pagetree macro (hierarchical page navigation)
        if macro_name == "pagetree":
            return "[Page tree]\n\n"

        # Handle recently-updated macro (shows recently modified pages)
        if macro_name == "recently-updated":
            return "[Recently updated pages]\n\n"

        # Handle content-report-table macro (table of pages matching criteria)
        if macro_name == "content-report-table":
            return "[Content report]\n\n"

        # Handle livesearch macro (search interface)
        if macro_name == "livesearch":
            return "[Live search]\n\n"

        # Handle page-properties and page-properties-report macros
        if macro_name in ("page-properties", "page-properties-report"):
            return "[Page properties]\n\n"

        # Handle include macro (includes content from another page)
        if macro_name == "include":
            # Try to show which page is being included
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "page":
                    page_title = param.get_text().strip()
                    if page_title:
                        return f"[Include: {page_title}]\n\n"
            return "[Include page]\n\n"

        # Handle excerpt-include macro (includes excerpt from another page)
        if macro_name == "excerpt-include":
            # Try to show which page's excerpt is being included
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "page":
                    page_title = param.get_text().strip()
                    if page_title:
                        return f"[Excerpt from: {page_title}]\n\n"
            return "[Excerpt include]\n\n"

        # For unknown macros, handle gracefully
        return self._handle_unknown_macro(el, macro_name, text, **options)

    def _handle_unknown_macro(self, el: Tag, macro_name: str, text: str, **options: Any) -> str:
        """Handle unknown Confluence macros gracefully.

        Uses a simplified format [Macro: name] to indicate unsupported macros
        without cluttering output with parameters. Content from rich-text-body
        or plain-text-body is still preserved when present.

        Args:
            el: The macro element
            macro_name: Name of the macro
            text: Extracted text content
            **options: Additional options

        Returns:
            Markdown representation of the macro
        """
        logger.debug(f"Converting unknown macro: {macro_name}")

        # Try to extract content from rich-text-body
        rich_body = el.find("ac:rich-text-body")
        if rich_body is not None:
            inner_md = self.process_tag(rich_body, **options)  # type: ignore[attr-defined]
            if inner_md.strip():
                # For macros with rich content, show a placeholder with content
                logger.debug(f"Extracted rich-text-body from {macro_name} macro")
                return f"[Macro: {macro_name}]\n\n{inner_md.strip()}\n\n"

        # Try to extract from plain-text-body
        plain_body = el.find("ac:plain-text-body")
        if plain_body is not None:
            plain_text = plain_body.get_text().strip()
            if plain_text:
                logger.debug(f"Extracted plain-text-body from {macro_name} macro")
                return f"[Macro: {macro_name}]\n\n{plain_text}\n\n"

        # For macros without rich-text or plain-text bodies, use simplified placeholder
        # Don't show parameter values as they're configuration details, not content
        logger.debug(f"No content body found for {macro_name} macro, using placeholder")
        return f"[Macro: {macro_name}]\n\n"

    def convert_ac_link(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence link to Markdown.

        Handles <ac:link> tags with <ri:page> or <ri:user> references.

        For user mentions: delegates to convert_ri_user() to show @username
        For page links: creates clickable markdown links when base_url is available,
                       otherwise shows link text in brackets: [Page Title]

        Example Confluence formats:
            <ac:link ac:card-appearance="inline">
                <ri:page ri:space-key="PM" ri:content-title="Page Title" />
                <ac:link-body>Page Title</ac:link-body>
            </ac:link>

            <ac:link>
                <ri:user ri:username="jsmith" />
                <ac:link-body>John Smith</ac:link-body>
            </ac:link>

        Result: [Page Title](url) or @jsmith
        """
        # Check if this is a user mention wrapped in ac:link
        ri_user = el.find("ri:user")
        if ri_user is not None:
            # Extract display name from link-body if present
            link_body = el.find("ac:link-body")
            display_name = link_body.get_text().strip() if link_body is not None else ""
            # Delegate to convert_ri_user, passing display name as fallback
            return self.convert_ri_user(ri_user, text, display_name=display_name, **options)

        # Check for ri:page to build internal link
        ri_page = el.find("ri:page")
        if ri_page is not None:
            # Extract page title and optional space key
            content_title_attr = ri_page.get("ri:content-title", "")
            content_title = content_title_attr if isinstance(content_title_attr, str) else ""
            space_key_attr = ri_page.get("ri:space-key", "")
            space_key = space_key_attr if isinstance(space_key_attr, str) else ""

            # Get link text (prefer ac:link-body over title)
            link_body = el.find("ac:link-body")
            link_text = link_body.get_text().strip() if link_body is not None else content_title

            if not link_text:
                link_text = "Page Link"

            # Build URL if we have base_url and enough info
            # Use space from link, or fall back to current page's space
            effective_space = space_key or self.space_key
            if self.base_url and effective_space and content_title:
                # URL format: /display/{SPACE}/{TITLE} - Confluence's title-based navigation
                encoded_title = quote(content_title, safe="")
                url = f"{self.base_url}/display/{effective_space}/{encoded_title}"
                return f"[{link_text}]({url})"

            # No base_url or missing space, return bracketed text
            return f"[{link_text}]"

        # Extract link text from ac:link-body (non-page links)
        link_body = el.find("ac:link-body")
        if link_body is not None:
            link_text = link_body.get_text().strip()
            if link_text:
                return f"[{link_text}]"

        # Last resort: return any text content
        if text.strip():
            return f"[{text.strip()}]"

        return "[Page Link]"

    def convert_ac_image(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence image tag to Markdown."""
        # Try to find ri:url (external image)
        url_elem = el.find("ri:url")
        if url_elem is not None:
            url = url_elem.get("ri:value", "")
        else:
            # Try to find ri:attachment (attached image)
            attachment = el.find("ri:attachment")
            if attachment is not None:
                url = attachment.get("ri:filename", "")
            else:
                return ""

        # Try to find caption
        caption_elem = el.find("ac:caption")
        alt_text = ""
        if caption_elem is not None:
            alt_text = caption_elem.get_text().strip()

        return f"![{alt_text}]({url})"

    def convert_ac_task_list(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence task list to Markdown checkboxes.

        Handles <ac:task-list> containers with <ac:task> items.
        Each task has <ac:task-status> (complete/incomplete) and <ac:task-body>.

        Example Confluence format:
            <ac:task-list>
                <ac:task>
                    <ac:task-status>incomplete</ac:task-status>
                    <ac:task-body>Task description</ac:task-body>
                </ac:task>
                <ac:task>
                    <ac:task-status>complete</ac:task-status>
                    <ac:task-body>Completed task</ac:task-body>
                </ac:task>
            </ac:task-list>

        Result:
            - [ ] Task description
            - [x] Completed task
        """
        result = []

        # Find all task elements
        tasks = el.find_all("ac:task", recursive=False)
        for task in tasks:
            # Extract status (default to incomplete)
            status_elem = task.find("ac:task-status")
            is_complete = False
            if status_elem is not None:
                status_text = status_elem.get_text().strip().lower()
                is_complete = status_text == "complete"

            # Extract task body text
            body_elem = task.find("ac:task-body")
            if body_elem is not None:
                # Process the body content recursively for any nested formatting
                task_text = self.process_tag(body_elem, **options).strip()  # type: ignore[attr-defined]
                if task_text:
                    checkbox = "[x]" if is_complete else "[ ]"
                    result.append(f"- {checkbox} {task_text}")

        if result:
            return "\n".join(result) + "\n\n"

        return ""

    def convert_ri_user(self, el: Tag, text: str, display_name: str = "", **options: Any) -> str:
        """Convert Confluence user mention to @username format.

        Handles <ri:user> tags with username or account-id attributes.
        Prefers ri:username for readability, falls back to ri:userkey,
        display_name, or ri:account-id.

        Args:
            el: The ri:user tag element
            text: Inner text content (usually empty for user tags)
            display_name: Display name from ac:link-body if available
            **options: Additional options passed through

        Example Confluence formats:
            <ri:user ri:username="jsmith" />
            <ri:user ri:account-id="abc123" ri:userkey="~jsmith" />
            <ac:link>
              <ri:user ri:account-id="5e9c86..." />
              <ac:link-body>John Smith</ac:link-body>
            </ac:link>

        Result: @jsmith, @John Smith, or @abc123
        """
        # Try to extract username (most readable)
        username_attr = el.get("ri:username", "")
        # el.get() can return a list in some edge cases, ensure it's a string
        username = username_attr if isinstance(username_attr, str) else ""
        if username:
            return f"@{username}"

        # Fall back to userkey (often contains username with ~ prefix)
        userkey_attr = el.get("ri:userkey", "")
        userkey = userkey_attr if isinstance(userkey_attr, str) else ""
        if userkey:
            # Strip ~ prefix if present
            clean_userkey = userkey.lstrip("~")
            return f"@{clean_userkey}"

        # Use display name if available (from ac:link-body)
        if display_name:
            return f"@{display_name}"

        # Last resort: use account-id
        account_id_attr = el.get("ri:account-id", "")
        account_id = account_id_attr if isinstance(account_id_attr, str) else ""
        if account_id:
            return f"@{account_id}"

        # If no identifier found, return placeholder
        return "@user"

    def convert_time(self, el: Tag, text: str, **options: Any) -> str:
        """Convert HTML time element with datetime attribute to formatted date.

        Handles <time> tags with datetime attributes used for date display.

        Example Confluence format:
            <time datetime="2026-02-15" local-id="..." />

        Result: 2026-02-15
        """
        # Extract datetime attribute
        datetime_attr = el.get("datetime", "")
        # el.get() can return a list in some edge cases, ensure it's a string
        datetime_value = datetime_attr if isinstance(datetime_attr, str) else ""

        if datetime_value:
            return datetime_value

        # Fallback to any text content if no datetime attribute
        if text.strip():
            return text.strip()

        # Last resort: return placeholder
        return "[date]"


def storage_to_markdown(
    storage: str, *, base_url: str | None = None, space_key: str | None = None
) -> str:
    """
    Convert Confluence storage format to Markdown.

    This is a best-effort conversion. Some Confluence-specific features
    may not have direct Markdown equivalents and will be converted to
    the closest approximation or omitted.

    Args:
        storage: Confluence storage format XHTML string
        base_url: Optional Confluence base URL (e.g., 'https://company.atlassian.net/wiki').
                 When provided, internal page links will be converted to clickable markdown links.
        space_key: Optional space key for the current page. Used as fallback for internal links
                  that don't specify a space key.

    Returns:
        Markdown text

    Supported conversions:
        - Headings (h1-h6)
        - Bold and italic
        - Lists (ordered and unordered)
        - Task lists → markdown checkboxes (- [ ] / - [x])
        - Code blocks (including code macro with syntax)
        - Inline code
        - Links (standard HTML and Confluence page links)
        - Images (both external URLs and attachments)
        - Tables
        - Block quotes
        - Horizontal rules
        - Info/warning/note/tip panels → block quotes with label
        - Status macros → emoji badges
        - Expand macros → HTML details/summary
        - TOC macro → italic text placeholder
        - Jira macro → bracketed Jira issue keys or query
        - Excerpt macro → labeled content block
        - Children macro → placeholder
        - Attachments macro → placeholder with parameters
        - Page tree macro → placeholder
        - Recently updated macro → placeholder
        - Content report macro → placeholder
        - Live search macro → placeholder
        - Page properties macros → placeholder
        - Include/excerpt-include macros → placeholder with page reference
        - Page links (ac:link with ri:page) → clickable links when base_url provided
        - User mentions (ri:user) → @username format

    Partial support:
        - Unknown macros → clean placeholder [Macro: name]

    Limitations:
        - Complex Confluence macros may not convert cleanly
        - Nested macros may lose formatting
        - Navigation and dynamic content macros show placeholders only

    Example:
        >>> storage = "<h1>Hello</h1><p>This is <strong>bold</strong>.</p>"
        >>> md = storage_to_markdown(storage)
        >>> print(md)
        # Hello

        This is **bold**.
    """
    converter = ConfluenceMarkdownConverter(
        base_url=base_url,
        space_key=space_key,
        heading_style="ATX",  # Use # for headings
    )

    result = converter.convert(storage)
    return result.strip() + "\n"
