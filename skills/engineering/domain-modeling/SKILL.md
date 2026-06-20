---
name: domain-modeling
description: Build and sharpen a project's domain model — ubiquitous language, glossary, ADRs, bounded contexts. Invoke when user says "let's model this", "what should we call this term", "record an ADR", "write CONTEXT.md", or when another skill encounters a term conflict.
---

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise.

> Merely reading CONTEXT.md for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're **changing** the model, not just consuming it.

## File Structure

Most repos have a single context:

```
/
├── CONTEXT.md                    ← glossary of domain terms
├── docs/adr/                     ← architecture decision records
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

If `CONTEXT-MAP.md` exists at root, the repo has multiple bounded contexts:

```
/
├── CONTEXT-MAP.md                ← maps where each context lives
├── docs/adr/                     ← system-wide decisions
├── src/ordering/CONTEXT.md
├── src/ordering/docs/adr/        ← context-specific decisions
└── src/billing/CONTEXT.md
```

Create files **lazily** — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## Activities (perform throughout session)

### 1. Challenge Against Glossary
When user uses a term that conflicts with existing language in `CONTEXT.md`, call it out immediately:
> "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### 2. Sharpen Fuzzy Language
When user uses vague or overloaded terms, propose a precise canonical term:
> "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### 3. Discuss Concrete Scenarios
When domain relationships are being discussed, stress-test them with specific scenarios that probe edge cases. Force the user to be precise about boundaries between concepts.

### 4. Cross-Reference with Code
When user states how something works, check whether the code agrees. Surface contradictions:
> "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### 5. Update CONTEXT.md Inline
When a term is resolved, update `CONTEXT.md` immediately. Don't batch them up. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

> `CONTEXT.md` is a **glossary and nothing else** — no implementation details, no specs, no scratch pad.

### 6. Offer ADRs Sparingly
Only offer to create an ADR when **all three** are true:

1. **Hard to reverse** — meaningful cost to change mind later
2. **Surprising without context** — future reader will wonder "why did they do it this way?"
3. **Result of a real trade-off** — genuine alternatives existed, you picked one for specific reasons

If any is missing, skip the ADR. Use format in [ADR-FORMAT.md](./ADR-FORMAT.md).

## NEVER

- NEVER put implementation details, specs, or scratch content into CONTEXT.md
- NEVER let a term conflict pass unremarked — call it out every time
- NEVER batch term resolutions — update CONTEXT.md immediately as each term is resolved
- NEVER create an ADR for trivial, easily-reversed, or obvious decisions
- NEVER treat CONTEXT.md as a requirements document
