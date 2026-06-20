---
name: to-prd
description: Turn the current conversation into a PRD and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed. Trigger when the user says "write a PRD", "create product requirements", "document this feature", "generate a specification", "turn this into a spec", "formalize this feature", or has discussed a feature request and asks for formal documentation.
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the PRD, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Write the PRD using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>

## Error Handling

| Situation | Handling |
|-----------|----------|
| `/setup-matt-pocock-skills` not run (issue tracker unknown) | Run setup first or ask the user for issue tracker URL and triage labels |
| Repo exploration fails (no access, no README) | Ask the user for a summary of the codebase architecture |
| User disagrees with proposed test seams | Discuss alternatives until consensus is reached; do not publish without agreement |
| Issue tracker API returns 401/403 | Inform the user credentials are missing or expired |
| PRD template section feels empty (e.g. Out of Scope) | Still include the section with "TBD — to be determined during implementation" rather than omitting it |

## NEVER

- NEVER interview the user for information — synthesize only from the conversation and codebase you have already explored
- NEVER include specific file paths or inline code snippets in the PRD (they become outdated quickly)
- NEVER skip exploring the repo to understand current codebase state before writing
- NEVER apply triage labels other than `ready-for-agent` without explicit user instruction
- NEVER omit the "Out of Scope" section — it prevents scope creep and sets clear boundaries
- NEVER propose new test seams without first checking if existing seams can be reused
- NEVER publish the PRD without user confirmation on the testing decisions
