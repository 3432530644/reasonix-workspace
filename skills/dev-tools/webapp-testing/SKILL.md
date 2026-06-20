---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, viewing browser logs, and automating end-to-end workflows. Trigger keywords: test, testing, playwright, e2e, end-to-end, browser test, UI test, automation, integration test, headless, selenium, webdriver, screenshot, local webapp.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation

## Error Handling

- **Server startup failure**: If `with_server.py` exits non-zero or the port is occupied, report the error output to the user and suggest checking port conflicts, missing dependencies (e.g., Node.js, Python), or malformed startup commands. Do not proceed with testing until the server is confirmed healthy.
- **Timeout / hang**: If `page.wait_for_load_state('networkidle')` or `page.wait_for_selector()` times out, capture a screenshot (`page.screenshot()`) and inspect `page.content()` to understand the actual page state. The app may have client-side errors that prevent rendering.
- **Selector not found**: When a locator fails to match, inspect the DOM with `page.content()` and use broader or role-based selectors (`role=button`, `text=Submit`). Avoid brittle selectors tied to dynamic class names.
- **Browser launch failure**: Ensure Chromium is installed (`playwright install chromium`). Fall back to `channel="chrome"` or `channel="msedge"` if system browsers are available.
- **Static HTML loading issues**: Use `file://` absolute paths for local HTML files. Verify the file exists at the path before writing the script.

## NEVER

- NEVER skip writing tests for critical user flows (login, checkout, data submission, error states) — these are the highest-value tests and must be covered.
- NEVER write tests that depend on other tests — each test must be independently runnable and must not share mutable state with other tests.
- NEVER hardcode dynamic values (session tokens, timestamps, auto-generated IDs) into assertions. Use stable attributes (`data-testid`, `role`, `text`) or capture them at runtime.
- NEVER read the source code of helper scripts (`scripts/with_server.py` etc.) before running them with `--help` first — they are large and pollute the context window.
- NEVER inspect the DOM or take screenshots before waiting for `networkidle` on dynamic applications — the page may not be fully rendered.
- NEVER leave the browser open after the test completes — always call `browser.close()` in a `finally` block or use context managers.
- NEVER use `sleep()` for synchronization — always use explicit waits (`wait_for_selector`, `wait_for_load_state`, `wait_for_timeout`) that react to actual page state.