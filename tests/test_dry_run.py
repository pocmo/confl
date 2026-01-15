"""Tests for dry-run mode across all mutating commands."""

import json

from typer.testing import CliRunner

from confl.cli import app

runner = CliRunner()


class TestDryRunMode:
    """Test dry-run mode for all mutating commands."""

    def test_page_delete_dry_run(self):
        """Test dry-run mode for page delete."""
        result = runner.invoke(app, ["page", "delete", "12345", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would delete page 12345" in result.stdout

    def test_page_delete_dry_run_json(self):
        """Test dry-run mode for page delete with JSON output."""
        result = runner.invoke(app, ["page", "delete", "12345", "--dry-run", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "delete"
        assert output["page_id"] == "12345"

    def test_page_create_dry_run(self):
        """Test dry-run mode for page create."""
        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "TEST",
                "--title",
                "Test Page",
                "--body",
                "# Content",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would create page" in result.stdout
        assert "Test Page" in result.stdout
        assert "TEST" in result.stdout

    def test_page_create_dry_run_json(self):
        """Test dry-run mode for page create with JSON output."""
        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "TEST",
                "--title",
                "Test",
                "--body",
                "Content",
                "--dry-run",
                "--json",
            ],
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "create"
        assert output["space"] == "TEST"
        assert output["title"] == "Test"

    def test_page_update_dry_run(self):
        """Test dry-run mode for page update."""
        result = runner.invoke(
            app, ["page", "update", "12345", "--title", "New Title", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would update page 12345" in result.stdout
        assert "New Title" in result.stdout

    def test_page_update_dry_run_json(self):
        """Test dry-run mode for page update with JSON output."""
        result = runner.invoke(
            app, ["page", "update", "12345", "--title", "New", "--dry-run", "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "update"
        assert output["page_id"] == "12345"
        assert output["title"] == "New"

    def test_attachment_delete_dry_run(self):
        """Test dry-run mode for attachment delete."""
        result = runner.invoke(app, ["attachment", "delete", "att123", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would delete attachment att123" in result.stdout

    def test_attachment_delete_dry_run_json(self):
        """Test dry-run mode for attachment delete with JSON output."""
        result = runner.invoke(app, ["attachment", "delete", "att123", "--dry-run", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "delete"
        assert output["attachment_id"] == "att123"

    def test_label_add_dry_run(self):
        """Test dry-run mode for label add."""
        result = runner.invoke(app, ["label", "add", "--page", "12345", "test-label", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would add 1 label(s) to page 12345" in result.stdout
        assert "test-label" in result.stdout

    def test_label_add_dry_run_json(self):
        """Test dry-run mode for label add with JSON output."""
        result = runner.invoke(
            app, ["label", "add", "--page", "12345", "test", "--dry-run", "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "add_labels"
        assert output["page_id"] == "12345"
        assert "test" in output["labels"]

    def test_label_remove_dry_run(self):
        """Test dry-run mode for label remove."""
        result = runner.invoke(
            app, ["label", "remove", "--page", "12345", "old-label", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would remove label 'old-label' from page 12345" in result.stdout

    def test_label_remove_dry_run_json(self):
        """Test dry-run mode for label remove with JSON output."""
        result = runner.invoke(
            app, ["label", "remove", "--page", "12345", "old", "--dry-run", "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "remove_label"
        assert output["page_id"] == "12345"
        assert output["label"] == "old"

    def test_comment_add_dry_run(self):
        """Test dry-run mode for comment add."""
        result = runner.invoke(
            app, ["comment", "add", "--page", "12345", "--body", "Test comment", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would add comment" in result.stdout
        assert "12345" in result.stdout

    def test_comment_add_dry_run_json(self):
        """Test dry-run mode for comment add with JSON output."""
        result = runner.invoke(
            app,
            ["comment", "add", "--page", "12345", "--body", "Test", "--dry-run", "--json"],
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "add_comment"
        assert output["page_id"] == "12345"

    def test_comment_update_dry_run(self):
        """Test dry-run mode for comment update."""
        result = runner.invoke(
            app, ["comment", "update", "67890", "--body", "Updated", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would update comment 67890" in result.stdout

    def test_comment_update_dry_run_json(self):
        """Test dry-run mode for comment update with JSON output."""
        result = runner.invoke(
            app, ["comment", "update", "67890", "--body", "New", "--dry-run", "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "update_comment"
        assert output["comment_id"] == "67890"

    def test_comment_delete_dry_run(self):
        """Test dry-run mode for comment delete."""
        result = runner.invoke(app, ["comment", "delete", "67890", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would delete comment 67890" in result.stdout

    def test_comment_delete_dry_run_json(self):
        """Test dry-run mode for comment delete with JSON output."""
        result = runner.invoke(app, ["comment", "delete", "67890", "--dry-run", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "delete_comment"
        assert output["comment_id"] == "67890"

    def test_space_update_dry_run(self):
        """Test dry-run mode for space update."""
        result = runner.invoke(app, ["space", "update", "TEST", "--name", "New Name", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would update space TEST" in result.stdout
        assert "New Name" in result.stdout

    def test_space_update_dry_run_json(self):
        """Test dry-run mode for space update with JSON output."""
        result = runner.invoke(
            app, ["space", "update", "TEST", "--name", "New", "--dry-run", "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "update_space"
        assert output["space"] == "TEST"
        assert output["name"] == "New"

    def test_space_delete_dry_run(self):
        """Test dry-run mode for space delete."""
        result = runner.invoke(app, ["space", "delete", "TEST", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would delete space TEST" in result.stdout

    def test_space_delete_dry_run_json(self):
        """Test dry-run mode for space delete with JSON output."""
        result = runner.invoke(app, ["space", "delete", "TEST", "--dry-run", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "delete_space"
        assert output["space"] == "TEST"

    def test_blogpost_delete_dry_run(self):
        """Test dry-run mode for blogpost delete."""
        result = runner.invoke(app, ["blogpost", "delete", "12345", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would delete blog post 12345" in result.stdout

    def test_blogpost_delete_dry_run_json(self):
        """Test dry-run mode for blogpost delete with JSON output."""
        result = runner.invoke(app, ["blogpost", "delete", "12345", "--dry-run", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "delete_blogpost"
        assert output["blogpost_id"] == "12345"

    def test_blogpost_create_dry_run(self):
        """Test dry-run mode for blogpost create."""
        result = runner.invoke(
            app,
            [
                "blogpost",
                "create",
                "--space",
                "TEST",
                "--title",
                "Test Post",
                "--body",
                "# Content",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would create blog post" in result.stdout
        assert "Test Post" in result.stdout

    def test_blogpost_create_dry_run_json(self):
        """Test dry-run mode for blogpost create with JSON output."""
        result = runner.invoke(
            app,
            [
                "blogpost",
                "create",
                "--space",
                "TEST",
                "--title",
                "Test",
                "--body",
                "Content",
                "--dry-run",
                "--json",
            ],
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "create_blogpost"
        assert output["space"] == "TEST"
        assert output["title"] == "Test"

    def test_blogpost_update_dry_run(self):
        """Test dry-run mode for blogpost update."""
        result = runner.invoke(
            app, ["blogpost", "update", "12345", "--title", "New Title", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would update blog post 12345" in result.stdout
        assert "New Title" in result.stdout

    def test_blogpost_update_dry_run_json(self):
        """Test dry-run mode for blogpost update with JSON output."""
        result = runner.invoke(
            app, ["blogpost", "update", "12345", "--title", "New", "--dry-run", "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
        assert output["action"] == "update_blogpost"
        assert output["blogpost_id"] == "12345"
        assert output["title"] == "New"
