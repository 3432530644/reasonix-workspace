---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Use at end of session, when switching context, or when the user says 'handoff', 'write handoff', 'save my progress'.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the user OS temp directory (not the current workspace).

## Handoff Document Structure

```
# Handoff: {session title}

## Context
- What was being worked on
- Current state (how far along, what's done vs pending)
- Key decisions made so far

## Completed
- [x] Item 1 (with key results)
- [x] Item 2

## Next Steps
- [ ] Next action item 1
- [ ] Next action item 2
- Dependencies blocking progress (if any)

## Key Files / Artifacts
- path/to/file1 — what it contains
- path/to/PRD.md — reference only, see that doc for details

## Suggested Skills
- skill-name-1: why the next agent should invoke it
- skill-name-2: why

## Decisions & Rationale
- Decision 1: why chosen, what alternatives were considered
- Decision 2: why chosen

## Sensitive Data Redacted
List what was redacted (API keys, passwords, PII) — note presence without revealing values.

---
Generated: {timestamp}
```

## Rules

1. Include a "Suggested Skills" section — list skills the next agent should invoke and why
2. Do NOT duplicate content already captured in other artifacts (PRDs, plans, ADRs, commits, diffs). Reference them by path/URL instead
3. Redact sensitive information: API keys, passwords, PII (replace with `[REDACTED: {type}]`)
4. If user passed arguments, treat them as a description of what the next session focuses on and tailor the doc accordingly
5. Use clear Markdown formatting — the next agent reads this as its first context

## NEVER

- NEVER include raw API keys, passwords, tokens, or secrets
- NEVER copy-paste full artifact content — reference by path
- NEVER write to the current workspace — use OS temp directory
- NEVER omit the Suggested Skills section
