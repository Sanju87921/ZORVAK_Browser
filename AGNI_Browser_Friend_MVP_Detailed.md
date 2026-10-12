# AGNI Browser — Friend's Detailed MVP Build Specification

**Product:** AGNI Browser  
**Owner of this workstream:** Browser developer (Amar's friend)  
**Product vision:** An Indian-owned, privacy-first, AI-powered browser  
**Design reference:** `AGNI_Browser_UI_Reference.png` — use this image as the visual target  
**MVP version:** 0.1  
**Primary development environment:** Windows  
**Recommended implementation:** Python + PySide6 + Qt WebEngine, subject to validation  
**Budget:** ₹0 for local development; no paid search API or paid cloud service required  
**Integration dependency:** AGNI Search API, developed separately by Amar

---

## 0. Read This First — Non-Negotiable Requirements

The attached UI reference is the target appearance. Build the browser to resemble it as closely as practical, but treat it as a design reference rather than a screenshot to copy pixel-for-pixel. The final application must be functional, not a static mockup.

### The application must have these major surfaces

1. **Main browser window / AGNI home page**
   - Dark browser chrome.
   - Left vertical navigation rail.
   - Large AGNI logo and tagline.
   - Search field connected to AGNI Search.
   - Configurable shortcut tiles.
   - Three compact information cards near the bottom of the hero area.
   - Optional AGNI AI side panel.
2. **AGNI AI side panel**
   - Separate collapsible panel attached to the right of the browser window.
   - Suggested actions: summarize, explain simply, translate, find key points, compare sources, research help.
   - Input field and send button.
   - “Use page content” toggle, OFF by default until a real consent/data-flow implementation exists.
   - Model/provider status selector only if actual supported providers are implemented; do not show fake options.
3. **Settings**
   - Privacy & Security.
   - AI Assistant.
   - Appearance.
   - Search Engine.
   - Languages.
   - Downloads.
   - System.
   - About AGNI.
4. **Page summary view**
   - Demonstrates AI output beside or over a webpage.
   - Shows a concise summary and extracted key points.
   - Buttons such as “Explain in Kannada” and “Extract key dates” must work only when a real implementation is connected. Otherwise mark them as disabled or “Coming later”; never fabricate results.
5. **Mobile concept**
   - The supplied reference includes a phone mockup, but **mobile development is not part of this Windows desktop MVP**.
   - Do not build an Android app in this workstream. Preserve the visual direction so it can be reused later.

### Critical product rule

**AGNI Search is a separate application built by Amar.** Do not create a second crawler, search index, or search engine in the browser repository. Your job is to build the browser UI and call AGNI Search through a documented HTTP API.

### No fake functionality

Do not display made-up numbers such as “1,248 trackers blocked,” “100% data stays in India,” or “2.3x faster” as real metrics. The reference contains concept/demo figures. In the actual MVP:
- Hide the cards until real measurements exist, or label them explicitly as illustrative demo content.
- Do not claim all user data stays in India unless the full data flow has been verified.
- Do not claim a tracker is blocked unless the browser actually blocks it and can count the action reliably.
- Do not claim performance multipliers without reproducible benchmarks.
- Do not fabricate AI responses, search results, index counts, provider status, or privacy states.

---

## 1. Product Summary

AGNI Browser is a desktop browser application with a Chromium-based web rendering component, familiar navigation controls, tabs, local bookmarks/history, an AGNI-branded new-tab page, and a built-in connection to AGNI Search. The visual design uses a dark charcoal interface, deep navy surfaces, saffron/orange accents, rounded panels, and premium Indian heritage imagery on the new-tab page.

The MVP must be a usable browser, not just a UI prototype. A user must be able to open a website, navigate back and forward, open tabs, search through AGNI Search, save bookmarks, inspect and clear local history, download files, and change basic settings.

### MVP success definition

A Windows user can launch AGNI Browser, enter a URL or query, browse a real website, see search results from Amar's AGNI Search service, open a result, manage tabs, save a bookmark, view local history, and clear local browsing data.

## 2. Product Goals

1. Match the supplied AGNI UI reference's design language.
2. Deliver reliable core browsing behavior.
3. Use AGNI Search as the default search provider.
4. Keep browser history, bookmarks, and preferences on the device by default.
5. Make privacy controls honest, understandable, and testable.
6. Build the UI so the AI side panel can be connected later without rewriting the browser.
7. Keep the browser code in its own folder/repository area, separate from the search engine.
8. Run locally without a paid service.

## 3. Out of Scope for This MVP

Do **not** implement these as part of the first release:
- A new browser rendering engine.
- A crawler or search index.
- An account/login system.
- Cloud sync.
- A production AI assistant if no free/local inference integration has been selected and tested.
- A built-in VPN or proxy.
- A password manager.
- An extension store.
- Android or iOS application.
- A claim of complete anonymity.
- A claim that all internet traffic remains in India.
- Automated website tracking protection unless a real, tested implementation is included.
- Fake AI, fake performance, fake tracker-blocking, or fake data-residency metrics.

A UI placeholder may be used during development, but it must be visibly marked “Demo,” “Unavailable,” or “Coming later” and must not be mistaken for a working feature.

---

## 4. Recommended Technology Stack

### Preferred prototype stack
- **Language:** Python 3.x; pin and document the selected version.
- **Desktop UI:** PySide6.
- **Web rendering:** Qt WebEngine, which embeds a Chromium-based engine.
- **Local app data:** SQLite.
- **HTTP requests to AGNI Search:** HTTPX or Qt networking; choose one approach and use it consistently.
- **Tests:** pytest.
- **Version control:** Git.
- **Packaging:** Start from source on Windows; package later only after functionality is stable.

### Important framework validation before committing
Before building too much, verify on the target Windows machine:
- PySide6 and Qt WebEngine install correctly.
- A real HTTPS website opens.
- JavaScript-heavy websites work sufficiently for the intended prototype.
- Back/forward navigation and tabs work.
- Download handling is possible.
- Browser profile/cookie persistence works.
- Security sandbox and runtime constraints are understood.
- Qt/Chromium update and licensing requirements are documented.

Qt WebEngine is a practical prototype option, but it is not equivalent to shipping a complete custom Chromium distribution. Reassess the framework if it cannot meet required security updates or platform behavior.

---

## 5. Visual Design System

Use the supplied reference image as the primary design target. The UI should feel premium, dark, warm, and modern—not a generic white browser window.

### Suggested design tokens

Use these as starting values and tune them against the reference.

| Token | Suggested value | Usage |
|---|---|---|
| Main background | `#0B0D12` | Browser chrome and dark panels |
| Secondary surface | `#141720` | Sidebars and cards |
| Raised surface | `#1B202B` | Inputs, hover states, secondary panels |
| Border | `#2C3240` | Panel outlines and separators |
| Primary text | `#F5F7FA` | Main labels and headings |
| Secondary text | `#A8AFBD` | Supporting labels |
| AGNI orange | `#FF6A00` | Primary action, active nav, toggle |
| Saffron highlight | `#FF9F1C` | Flame/brand highlights |
| Error | `#F05252` | Errors |
| Success | `#2CB67D` | Verified positive state only |

### Shape and spacing
- Rounded panels and controls, approximately 10–18 px corner radius depending on size.
- Thin, low-contrast borders.
- Clear hover, pressed, selected, disabled, and keyboard-focus states.
- Avoid excessive glow, blur, and shadows that reduce text clarity.
- Use a consistent spacing scale, such as 4, 8, 12, 16, 24, 32 px.
- Prefer a readable UI font available on Windows; provide a fallback.
- Do not stretch or distort the AGNI logo.
- Keep icons visually consistent in stroke, size, and alignment.

### Layout behavior
- The main browser window should resize cleanly.
- The left rail should remain a stable width at normal desktop sizes.
- The webpage viewport should take most of the space.
- The AI panel should be collapsible and should not permanently cover important webpage content.
- At smaller window sizes, the UI should simplify instead of overlapping controls.

### Asset requirements
Create or source local assets for:
- AGNI flame mark and wordmark.
- Small monochrome sidebar icons.
- Shortcut tile icons or safe local placeholders.
- New-tab background image inspired by Hampi/Indian heritage at sunset.

Do not hotlink a random image from a website. Use an asset with suitable usage rights, or a locally created placeholder. Do not bundle third-party brand logos in a way that implies partnership or endorsement. Shortcuts can be user-configurable and their icons can be fetched or displayed only with appropriate safeguards.

---

## 6. Main Window Layout — Match the Reference

The reference's main desktop window has four visual zones.

### 6.1 Browser chrome at the top
Include:
- Window title/tab strip.
- New-tab button.
- Back button.
- Forward button.
- Reload/stop button.
- Address/search bar.
- Bookmark action.
- Downloads shortcut.
- Settings/menu button.

Expected behavior:
- Back and forward operate on the active tab.
- Reload becomes Stop while loading, then returns to Reload.
- Address bar shows the current URL in a readable, selectable format.
- Pressing Enter navigates to a valid URL or submits a search query.
- A bookmark icon toggles the current page's bookmark state.
- The menu opens real implemented commands only.

### 6.2 Left navigation rail
Match the reference with an AGNI mark at the top and these items:
- Home
- AI Assistant
- Bookmarks
- History
- Downloads
- Extensions
- Settings

MVP behavior:
- **Home:** Opens the AGNI new-tab/home page.
- **AI Assistant:** Opens the AI panel. If AI is not connected, show a clear “AI assistant is not configured yet” state and explain that no page content has been sent.
- **Bookmarks:** Opens a local bookmarks view.
- **History:** Opens local history.
- **Downloads:** Opens a local downloads view.
- **Extensions:** Show “Not available in this MVP” or omit the item. Do not imply extensions work if they do not.
- **Settings:** Opens settings.

The active navigation item must have an orange accent and readable text, like the reference.

### 6.3 Home/new-tab hero
The home page should contain:
- Large AGNI logo and wordmark.
- Tagline: **“Your Internet. Your Control.”**
- Central search field with placeholder such as “Search with AGNI…”
- Shortcut tiles, for example YouTube, Gmail, Wikipedia, and Add Shortcut.
- Heritage-inspired sunset background based on Indian architecture/landscape.
- Optional status cards at the bottom, but only if their values are genuine and measured.

**Search field integration:** Submit the query to AGNI Search. Do not send the query to Google, Brave, or DuckDuckGo as a fallback. If the local/remote AGNI Search API is unavailable, show an error panel with Retry and Settings actions.

### 6.4 Optional bottom information cards
The concept image shows:
- Tracking Blocked.
- Data Stays in India.
- Faster Browsing.

These must not be implemented as unverified claims.

Acceptable MVP choices:
1. Omit the cards.
2. Replace them with accurate states, such as “Search index connected,” “History stored locally,” and “AI not configured,” when the application can verify those states.
3. Label figures as “Illustrative demo” in development builds only.

Never display “100% data stays in India” unless every relevant data flow has been audited and the statement is supportable.

---

## 7. Address Bar: URL Detection and Search Routing

The address bar is the core connection between the browser and AGNI Search.

### Required behavior
1. Trim leading/trailing whitespace.
2. If the input is a supported explicit URL, navigate to it.
3. If it looks like a hostname/domain with optional path/port and no spaces, apply the documented URL policy and navigate.
4. Otherwise, treat it as a search query.
5. Send search requests only to the configured AGNI Search endpoint.
6. Do not send every keystroke to an external suggestion provider.
7. Do not silently fall back to another search provider.
8. Validate schemes; do not execute arbitrary shell commands or open unsafe protocols.
9. Encode query parameters correctly.
10. Show progress while navigating/searching and meaningful errors when it fails.

### Search routing example
- Input: `https://example.com` → open the website.
- Input: `example.com/about` → navigate according to the chosen HTTPS-first policy.
- Input: `Karnataka engineering scholarships` → query AGNI Search.
- Input: empty string → do nothing.
- Input: unsupported scheme → reject or show a safe error.

---

## 8. AGNI Search Integration Contract

Amar is developing AGNI Search separately. The browser must use the agreed API and must not access the search database directly.

### Configurable API base URL
Examples:
- Local development on the same computer: `http://127.0.0.1:8000`
- Testing from the Windows machine against Amar's Linux machine: `http://<AMAR_LINUX_LAN_IP>:8000`
- Production later: an HTTPS endpoint on an appropriately secured host.

Do not hardcode a developer's IP address in the code. Add a setting/environment variable such as `AGNI_SEARCH_BASE_URL`.

For LAN testing, the machines must be on a network that permits access; Amar's API must bind to an appropriate interface and the firewall must permit the chosen port. Do not expose the development API to the public internet. Use only a trusted local network and temporary test data.

### Endpoint
`GET /api/v1/search?q=<query>&page=1&limit=10`

### Expected JSON response
```json
{
  "query": "karnataka scholarships",
  "page": 1,
  "limit": 10,
  "total_estimate": 2,
  "results": [
    {
      "title": "Example Scholarship Information",
      "url": "https://example.in/scholarships",
      "snippet": "Information about available scholarships...",
      "source": "agni_index",
      "last_crawled": "2026-10-12"
    }
  ],
  "index_status": {
    "documents_indexed": 500,
    "coverage_note": "Results are limited to pages currently indexed by AGNI."
  }
}
```

The sample content is illustrative. Do not hardcode it as real results.

### Search results page requirements
- Display query at the top.
- Display result count only if the API returns a valid count/estimate.
- Each result should show title, URL/domain, and snippet.
- Clicking a result opens the original URL in the active tab by default; middle-click/new-tab behavior is desirable if supported.
- Display “Results are limited to pages currently indexed by AGNI” or the API-provided coverage note.
- Empty state: “No results found in the current AGNI index.”
- Loading state: visible spinner/progress indicator.
- Error state: “AGNI Search is unavailable” with Retry and Settings actions.
- Do not show fabricated results or claim full-web coverage.
- Escape/sanitize text before rendering in the app UI. Never interpret result snippets as executable HTML.

### API error handling
Handle:
- Connection refused / server unavailable.
- Timeout.
- HTTP 4xx/5xx.
- Invalid JSON.
- Missing result fields.
- Empty result list.
- Unexpected URL schemes in results.

Never crash the browser because a search request fails.

---

## 9. Tabs and Navigation

### Tabs
P0:
- Create a new tab.
- Switch between tabs.
- Close a tab.
- Keep each tab's current page and navigation state.
- Show a short title or hostname.
- Show loading state while navigation is in progress.
- Prevent closing the last tab from leaving the app in an unusable state; open a new tab or show the home page.

P1:
- Keyboard shortcuts.
- Duplicate tab.
- Reopen recently closed tab.

### Navigation controls
P0:
- Back.
- Forward.
- Reload.
- Stop loading.
- Home.
- Address bar.
- Bookmark toggle.

The controls must reflect the active tab's state. Disable back/forward when there is no history in that direction.

### Keyboard shortcuts to target
Use conventional shortcuts where they do not conflict with Qt:
- `Ctrl+L`: focus/select address bar.
- `Ctrl+T`: new tab.
- `Ctrl+W`: close current tab.
- `Ctrl+R` or `F5`: reload.
- `Alt+Left`: back.
- `Alt+Right`: forward.
- `Ctrl+D`: bookmark current page.
- `Ctrl+H`: history.
- `Ctrl+J`: downloads.
- `Ctrl+,` or another documented shortcut: settings.

Test every shortcut on Windows before documenting it.

---

## 10. Bookmarks, History, and Downloads

### Bookmarks
- Add/remove current page.
- Store URL, title, created timestamp, optional folder.
- Open a bookmark in the active tab.
- Delete a bookmark.
- Persist across application restarts.
- Avoid duplicates or update an existing bookmark instead.

Suggested SQLite table:
```sql
CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    folder TEXT
);
```

### History
- Record completed navigations with URL, title, and timestamp.
- Do not record failed requests as successful visits.
- Show most recent first.
- Search/filter local history if time permits.
- Clear history with an explicit confirmation.
- Provide a “clear browsing data” action with clearly defined scope.
- Avoid logging sensitive URL query strings to diagnostic logs.

Suggested SQLite table:
```sql
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    visited_at TEXT NOT NULL,
    status TEXT NOT NULL
);
```

### Downloads
- Handle the browser engine's download events.
- Show filename, progress, completion/failure state.
- Let the user choose or configure the download folder.
- Confirm overwrite when a file already exists.
- Sanitize filenames and prevent path traversal.
- Provide Open File / Show in Folder only when safe and supported.
- Never execute downloaded files automatically.
- Handle cancelled, failed, and interrupted downloads.

Do not implement a fake downloads page populated with sample files in production mode.

---

## 11. AGNI AI Side Panel — UI Now, Real AI Later

The reference shows an AGNI AI panel docked on the right. The panel should be designed now so it fits the visual target, but AI execution must not be faked.

### Panel layout
- AGNI flame mark and “AGNI AI” heading.
- Close/collapse button.
- Greeting or neutral heading.
- Action chips:
  - Summarize this page
  - Explain in simple language
  - Translate
  - Find key points
  - Compare sources
  - Help with research
- Large action area with icons:
  - Understand this page
  - Summarize content
  - Translate instantly
  - Answer your questions
- Prompt input: “Ask anything about this page…”
- Send button.
- “Use page content” toggle.
- Provider/model status, only if a real provider/model is configured.

### Default behavior
- AI panel can open without sending any page content.
- “Use page content” should be OFF by default until a real implementation has an explicit consent flow and clear data disclosure.
- If AI is not connected, clicking an action should show a clear “AI is not configured in this MVP” message.
- Do not simulate a response that looks real.
- Do not send the current page to an external model automatically.
- Do not save AI prompts or page contents to remote servers by default.

### Later integration options
A later version may use a local model, such as a model served by Ollama, or a remote model with explicit consent. That choice is outside this browser-only MVP unless both developers agree otherwise. Local inference has hardware requirements; remote inference introduces data-flow and privacy considerations.

### AI response UI (when a real model is connected)
- User message and assistant message visually distinct.
- Loading/cancel state.
- Error state.
- Copy response action.
- If answer relies on page content, label that context.
- Avoid presenting AI output as verified fact.
- Where practical, provide source links/section references.
- Never invent source citations.

---

## 12. Page Summary Overlay / Split View

The reference includes a webpage with a summary card beside it. Build the layout shell, but connect it only to a real AI result source.

### UI elements
- Page title “Page Summary.”
- Summary paragraph/card.
- Key-point bullet list.
- Action button “Explain in Kannada.”
- Action button “Extract key dates.”

### Behavior
- If AI is not implemented, show an explicit disabled state or “Coming later.”
- If AI is implemented, request page extraction only after the user initiates the action and receives clear disclosure about where the text will be processed.
- Limit the amount of page text sent to a model.
- Handle pages that cannot be extracted, PDFs, very long pages, and empty content.
- Do not show an invented government-scheme summary as if it came from the page currently open.

---

## 13. Settings Screen

The settings screen should closely follow the reference's dark layout and orange active selection.

### Sidebar categories
- Privacy & Security
- AI Assistant
- Appearance
- Search Engine
- Languages
- Downloads
- System
- About AGNI

### Privacy & Security
Possible controls:
- Clear browsing history.
- Clear cookies/site data where supported.
- Clear cache where supported.
- Manage supported website permissions.
- Explain local history storage.
- Explain that websites and network providers may still observe connection activity.
- Do not show a tracker-blocking toggle unless it is actually implemented and tested.

### AI Assistant
- Enable/disable AI panel.
- Local/remote processing disclosure when applicable.
- Page-content permission default.
- Clear local AI conversation history only if conversation history is actually stored.
- Provider/model status based on real configuration.

### Appearance
- Dark/light/system theme if implemented.
- Home background selection from bundled assets.
- Shortcut management.

### Search Engine
- Default endpoint: AGNI Search.
- API base URL configurable for development.
- “Test connection” button.
- Display API status and index coverage only after a real request.
- No automatic third-party fallback.

### Languages
- UI language setting if implemented.
- Language preference for AI output only when AI is connected.
- Do not claim full Indian-language support until tested.

### Downloads
- Default download directory.
- Ask where to save each file toggle if implemented.
- Show completed downloads list.

### System
- Browser profile location information.
- Version and runtime details.
- Safe diagnostics export, excluding sensitive browsing data by default.

### About AGNI
- Product name and version.
- Open-source/license notices for dependencies.
- Link to project repository if public.
- Security/reporting contact when established.

---

## 14. Data Storage and Local Privacy

Use SQLite for app-owned metadata, such as bookmarks, history, and settings. Let the embedded browser engine manage its own cookies and website storage through a persistent profile.

Suggested application database tables:
- `bookmarks`
- `history`
- `settings`

Do not put cookies, passwords, form contents, or entire page HTML into the application database.

### Local profile requirements
- Use a stable, documented profile directory.
- Make sure profile files are not committed to Git.
- Use OS file permissions.
- Offer clear-data controls that specify which data categories are removed.
- Test persistence after app restart.
- Do not claim AGNI encrypts every local file unless that has been implemented and verified.

### Data-flow rule
Browsing requests should normally go directly from the browser to the destination website. Search queries go to the configured AGNI Search API. Page text should not be sent to an AI service unless the user initiates an AI action and receives appropriate disclosure.

---

## 15. Security Requirements

- Never disable TLS certificate verification.
- Validate URL schemes.
- Do not expose privileged Python/native objects to arbitrary websites.
- Keep browser chrome/UI actions separate from untrusted webpage JavaScript.
- Do not execute downloaded files automatically.
- Sanitize filenames and avoid path traversal.
- Escape search result text in custom UI widgets.
- Do not render search snippets as trusted HTML.
- Do not log passwords, cookies, full sensitive URLs, or page content.
- Keep dependencies pinned and check for security updates.
- Understand and preserve supported browser-engine sandboxing.
- Handle certificate errors safely; do not offer a casual “ignore all errors” option.
- Do not store the AGNI Search API secret in the browser. The browser's search API endpoint is not a secret; any server credentials must stay on Amar's backend.
- For local development, do not expose the API to the public internet.

---

## 16. Error, Loading, and Empty States

Every network-dependent view needs these states:
- Idle.
- Loading.
- Success.
- Empty.
- Error.
- Retry.

Examples:
- AGNI Search is offline.
- Search returned no indexed matches.
- Website failed to load.
- Download failed.
- Bookmark could not be saved.
- History database unavailable.
- AI is not configured.
- Page text could not be extracted.

Use plain, actionable language. Do not show raw stack traces to users; write diagnostic details to local development logs with sensitive values removed.

---

## 17. Accessibility and UX Quality

- All main controls reachable by keyboard.
- Visible keyboard focus.
- Meaningful accessible labels for icon-only buttons.
- Adequate contrast for text and secondary labels.
- No important state indicated only by color.
- Search result titles and controls have sensible tab order.
- Tooltips for unfamiliar icons.
- The AI side panel can be closed without disrupting the active page.
- Window resizing must not cause controls to overlap.
- Respect the operating system's high-DPI scaling where possible.

---

## 18. Testing Plan

### Unit tests
- URL vs search-query detection.
- URL scheme validation.
- Search API request construction.
- Search JSON validation.
- Bookmark CRUD.
- History CRUD and clearing.
- Settings persistence.
- Download filename sanitization.

### Integration tests
1. Launch app.
2. Open a local test page and a public HTTPS page.
3. Navigate back and forward.
4. Open, switch, and close tabs.
5. Submit a query to a mock AGNI Search API.
6. Verify results are displayed from the API response.
7. Test empty results.
8. Stop the API and verify an error state appears without crashing.
9. Save a bookmark, restart app, and verify it persists.
10. Clear history and verify deletion.
11. Download a safe test file and verify progress/completion.
12. Verify the AI panel does not send content when disabled/unconfigured.
13. Verify the browser does not silently query Google/Brave/DuckDuckGo.

### Manual security tests
- Try an unsupported URL scheme.
- Try a malformed URL.
- Try a search result URL with an unsafe scheme.
- Try a download filename containing path traversal characters.
- Check that a website cannot access privileged application functions.
- Check invalid TLS certificates are not silently accepted.
- Check logs do not contain sensitive page content or full sensitive URLs.

---

## 19. Definition of Done

The Browser MVP is ready for integration review when:
- It launches on the documented Windows setup.
- It opens real websites.
- URL and search-query routing work.
- Tabs and navigation controls work.
- The new-tab page matches the visual reference's overall layout and color system.
- AGNI Search can be configured and queried through its API.
- Search results display title, URL, snippet, and honest coverage information.
- Bookmarks and history persist locally.
- Downloads work with safe filename handling.
- Clear-data controls work and describe their scope.
- AI panel UI exists but never fabricates output or silently transmits page content.
- Search/API failure states work.
- Core tests pass.
- Setup and run instructions are complete.
- No unsupported privacy, speed, tracker-blocking, AI, or index-coverage claims appear in production UI.

---

## 20. Suggested Repository Layout

```text
agni/
├── README.md
├── browser/
│   ├── README.md
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── src/
│   │   └── agni_browser/
│   │       ├── main.py
│   │       ├── app_shell.py
│   │       ├── theme.py
│   │       ├── navigation.py
│   │       ├── tabs.py
│   │       ├── web_view.py
│   │       ├── search_client.py
│   │       ├── search_results.py
│   │       ├── home_page.py
│   │       ├── ai_panel.py
│   │       ├── bookmarks.py
│   │       ├── history.py
│   │       ├── downloads.py
│   │       ├── settings.py
│   │       ├── storage.py
│   │       └── privacy.py
│   ├── assets/
│   │   ├── agni_logo.svg
│   │   ├── icons/
│   │   └── backgrounds/
│   └── tests/
│       ├── test_navigation.py
│       ├── test_search_client.py
│       ├── test_bookmarks.py
│       ├── test_history.py
│       └── test_settings.py
├── search/
│   └── (Amar's separate AGNI Search implementation)
└── docs/
    ├── AGNI_Browser_MVP.md
    └── api-contract.md
```

Do not create placeholder source files for every item before the architecture is understood. The layout is a guide; keep modules cohesive and avoid overengineering.

---

## 21. Development Sequence

### Milestone 1 — App shell
- Set up Python and PySide6/Qt WebEngine.
- Build the main window and theme.
- Open one real webpage.
- Implement the address bar and navigation actions.

### Milestone 2 — Tabs and home
- Add tabs and tab state.
- Build the AGNI new-tab page.
- Add shortcut tiles.
- Add search query detection.

### Milestone 3 — Search integration
- Agree API schema with Amar.
- Implement configurable `AGNI_SEARCH_BASE_URL`.
- Build result rendering and coverage note.
- Add loading, empty, error, and retry states.
- Use a mock API until Amar's service is ready.

### Milestone 4 — Local features
- Add bookmarks.
- Add history.
- Add downloads.
- Add settings and clear-data behavior.

### Milestone 5 — AI panel shell
- Implement the side-panel layout and action chips.
- Show explicit unavailable state until a real model is connected.
- Ensure page content is not transmitted automatically.

### Milestone 6 — QA and integration
- Run the complete test plan.
- Test with Amar's real API on a trusted local network.
- Fix bugs and update documentation.
- Verify all displayed claims are accurate.
- Prepare a demo build.

---

## 22. Daily Collaboration Protocol with Amar

- Agree on the API contract before integration.
- Work primarily in `browser/`; do not modify the search crawler or database.
- Use a separate feature branch such as `feature/browser-app`.
- Commit small, meaningful changes.
- Keep dependencies pinned and document setup.
- Use mock JSON matching the API contract while Amar builds the search engine.
- Do not hardcode Amar's local IP address.
- For local-network testing, use a configurable base URL and a trusted network only.
- Tell Amar when the browser client is ready for the real API.
- Report blockers with the exact error, environment, and reproduction steps.

### Daily status format
- Completed:
- In progress:
- Blocked by:
- Files changed:
- Tests run:
- Next task:

---

## 23. Final Build Principle

**Build a real browser with an AGNI visual identity and a clean integration to AGNI Search. Do not build a fake demo that merely resembles the reference.**

The first version should be visually close to the supplied image, but reliability, honest privacy behavior, and real search integration take priority over decorative details. Keep AI and advanced protections modular so they can be added after the core browser works.
