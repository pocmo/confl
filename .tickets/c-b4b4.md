---
id: c-b4b4
status: closed
deps: []
links: []
created: 2026-01-15T08:05:44Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Add MIT License file and mention in README

Fetch the MIT License text and add it to the repository with proper attribution.

## Tasks
- Fetch MIT License text from authoritative source (e.g., opensource.org or choosealicense.com)
- Create LICENSE file in repository root
- Update copyright year to current year (2026)
- Update copyright holder to appropriate entity/person (check with existing repo attribution)
- Add license mention to README.md:
  - Add "## License" section (typically at bottom)
  - State: "This project is licensed under the MIT License - see the LICENSE file for details."
- Verify LICENSE file is plain text and properly formatted

## Acceptance Criteria
- LICENSE file exists in repository root
- Contains standard MIT License text
- Copyright year and holder are correct
- README.md mentions MIT License with link to LICENSE file
- File is committed to repository

## References
- https://opensource.org/licenses/MIT — MIT License text
- https://choosealicense.com/licenses/mit/ — Alternative source
- README.md — add license section

## Notes
- Use standard MIT License text, don't modify the template
- Keep LICENSE file name uppercase (convention)
- Check pyproject.toml if it has license field that should match


**2026-01-15T08:10:40Z**

Completed: Added MIT License file with 2026 copyright to Sebastian Kaspari, updated README.md with proper license section and link, added license field to pyproject.toml. All verification checks pass.
