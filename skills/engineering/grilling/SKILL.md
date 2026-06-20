---
name: grilling
description: Interview the user relentlessly about a plan or design. Use when the user wants to stress-test a plan before building, or uses any 'grill me', 'stress test', 'push back', 'challenge me', 'review my plan', 'what am I missing' trigger phrases.
---

Interview the user relentlessly about every aspect of their plan until reaching shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

## Questioning Approach

Ask questions **one at a time** — wait for feedback on each question before continuing. Asking multiple questions at once is bewildering.

### Question Types (cycle through these)

| Type | Purpose | Example |
|------|---------|---------|
| **Assumption** | Challenge unstated beliefs | "What are you assuming about X that, if wrong, would break this?" |
| **Edge Case** | Probe boundary conditions | "What happens when Y occurs at the same time?" |
| **Trade-off** | Force explicit prioritization | "Between speed and correctness, which wins here?" |
| **Dependency** | Uncover hidden coupling | "Does Z need to be resolved before we can decide on W?" |
| **Cost** | Surface resource constraints | "What's the cost of being wrong about this?" |
| **Scope** | Test ambition vs capacity | "Is this essential for v1 or can it wait?" |

### Deep Dive Paths

1. **Why this approach?** — What alternatives were considered? Why were they rejected?
2. **What could go wrong?** — Visualize failure modes before they happen
3. **How will you know it works?** — Define the measurable success criteria
4. **Who needs to agree?** — Identify stakeholders not in the room
5. **What's the cheap test?** — What can you validate in an hour vs a week?

## If a question can be answered by exploring the codebase, explore instead.

When the user gives a vague answer, push deeper with "Concretely, what does that look like?"

## Convergence Criteria

Stop grilling when:
- User can articulate the full decision tree from start to finish
- Top 3 risks are identified with mitigation plans
- There's a clear "what to do next" step

## NEVER

- NEVER ask more than one question at a time
- NEVER move to a new topic before the current one is resolved
- NEVER make assumptions on the user's behalf — let them answer
- NEVER skip a branch because it seems obvious
