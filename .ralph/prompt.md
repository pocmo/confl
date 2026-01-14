# Ralph Agent Instructions

## IMPORTANT

- **WORK ON ONLY ONE TICKET PER ITERATION** - Pick one ticket from `tk ready`, finish it or note why you're blocked, then STOP. Do not work on multiple tickets in one iteration.
- **THIS APPLIES TO ALL TICKET TYPES** - Including discovery tickets, design tickets, implementation tickets. ONE ticket only, then stop.
- **YOU control the tickets** - Run `tk ready` to see available work, `tk start <id>`, `tk close <id>`
- **Write to the handoff log** - APPEND brief notes to `.ralph/handoff.log` about what you did and learned
- **Signal completion** - Write `COMPLETE` in the handoff log when all tickets are done

## Your Task

1. Run `tk ready` to see available tickets
2. Pick ONE ticket (prefer highest priority P0 > P1 > P2 etc.)
3. Run `tk show <id>` to read the full ticket description and context
4. Run `tk start <id>` to mark it in progress
5. Implement the work for that ticket
5. Add tests for your changes
6. **Consider documentation updates** - If your changes affect user-facing behavior (new commands, changed options, new features), update relevant documentation in README.md or docs/
7. Verify your work:
   - Run: `uv run pytest` (must pass)
   - Run confl commands to verify, e.g.:
     `uv run confl --help`
8. If tests pass and verification works:
   - Commit your changes with a descriptive message referencing the ticket
   - Run `tk close <id>` to close the ticket
   - Run `tk add-note <id> "Completed in commit <sha>"`
9. **APPEND a brief note to the handoff log** (`.ralph/handoff.log`):
   - What ticket you worked on
   - What you did
   - Any important learnings for the next iteration
10. If you discover follow-up work needed:
    - Create new tickets: `tk create "Title" -d "Description" -p <priority>`
11. If you cannot complete the ticket:
    - Add a note explaining why: `tk add-note <id> "Blocked because..."`
    - Do NOT close it
12. If no more tickets are ready, write `COMPLETE` in the handoff log

## Questions for the User

If you encounter a design decision or question you cannot resolve:
1. **First, try to resolve it yourself** using docs, code context, and best practices
2. If still blocked, append to `.ralph/questions.md` (don't overwrite existing questions)
3. Format:
   ```
   ## [ticket-id] Question title
   Context: ...
   Question: ...
   ```
4. Continue with other work if possible - don't block on questions

## For DECISION/DESIGN/DISCOVERY Tickets

When working on tickets prefixed with "DECISION:", "DESIGN:", or "Evaluate" (discovery tickets):
1. Research the options in the codebase and docs
2. Document your decision/findings in the ticket notes
3. If worthwhile, create follow-up implementation tickets with `tk create`
4. Close the ticket only after documenting findings and filing any needed implementation work
5. **STOP after completing this ONE ticket** - Do not work on the implementation tickets you just filed

## Verification Requirements

Before closing any implementation ticket:
1. **Format & lint**: `uv run ruff format . && uv run ruff check --fix .`
2. **Type check**: `uv run mypy src/`
3. **Tests must pass**: `uv run pytest`
4. **Manual verification**: Run confl commands to verify behavior
5. **No regressions**: Existing functionality still works

## Commit Messages

Format: `<type>(<scope>): <description> [<ticket-id>]`

Examples:
- `feat(cli): implement node resolve command [t-82b4]`
- `fix(parser): handle empty metadata.name [t-0ac2]`
- `docs(cli): document shell quoting for $ in IDs [t-2918]`

**Include ticket changes**: Always stage and commit any changes to `.tickets/` (ticket status, notes) along with your code changes.

## Filing Follow-up Tickets

When you discover additional work:
```bash
tk create "Title describing the work" \
  -d "Description with context. Reference source doc if applicable." \
  -p <priority 0-4>
```

Always include:
- Clear description of what needs to be done
- Reference to source document (e.g., "From cli-design.md")
- Appropriate priority (0=critical, 4=nice-to-have)

## Important Mindset

- Make small, incremental changes
- Commit frequently when green
- You will be run again - don't try to do everything at once
- The filesystem is your memory - update tickets and logs
- File follow-up tickets for anything you discover but don't implement
