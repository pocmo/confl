---
id: c-0a8c
status: closed
deps: []
links: []
created: 2026-01-15T08:13:05Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Update CONTRIBUTING.md with Ralph agent development info

Add prominent section at top of CONTRIBUTING.md explaining that this project is developed by Ralph, an autonomous loop agent.

## Tasks
- Add a prominent section at the very top of CONTRIBUTING.md (before other content)
- Title it something like "🤖 Development by Ralph" or "About This Project's Development"
- Explain:
  - This project is completely 'vibe coded' by Ralph, an autonomous coding agent
  - Brief explanation of what that means (agent works in iterations, files tickets, implements them)
  - How Ralph works at high level (reads tickets, implements, commits, repeats)
  - Point to .ralph/ directory for the implementation
  - Link to: https://dev.to/alexandergekov/2026-the-year-of-the-ralph-loop-agent-1gkj for detailed explanation
- Keep it engaging and concise (4-8 sentences)
- Make it clear this is a unique development approach
- Still welcome human contributions (if that's the case)

## Example tone/structure:
```markdown
## 🤖 Developed by Ralph

This project is **completely vibe coded by Ralph**, an autonomous loop agent. Ralph works in iterations: it reads tickets from our issue tracker (`tk`), implements one feature at a time, runs tests, commits changes, and moves to the next ticket. The entire codebase you see here was written autonomously by AI agents following architecture docs and best practices.

Want to understand how this works? Check out the [`.ralph/`](.ralph/) directory for the implementation, or read [The Year of the Ralph Loop Agent](https://dev.to/alexandergekov/2026-the-year-of-the-ralph-loop-agent-1gkj) for a deep dive into this development approach.

```

## Acceptance Criteria
- CONTRIBUTING.md has prominent Ralph section at the top
- Explains 'vibe coding' concept clearly
- Links to the dev.to article
- Points to .ralph/ directory
- Tone is informative and engaging
- Doesn't overwhelm with too much detail

## References
- CONTRIBUTING.md — file to update
- .ralph/ — Ralph implementation directory
- https://dev.to/alexandergekov/2026-the-year-of-the-ralph-loop-agent-1gkj — article link

## Notes
- This is a unique selling point of the project - make it prominent
- Keep it concise - don't explain every detail
- Link out for those who want more info


**2026-01-15T08:21:11Z**

Completed: Added prominent Ralph section at top of CONTRIBUTING.md explaining autonomous development approach. Includes links to .ralph/ directory and dev.to article. Section is concise, engaging, and welcoming to human contributors.
