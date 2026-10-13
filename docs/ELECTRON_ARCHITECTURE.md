# GAVIX Desktop Browser — Electron Architecture & Migration Plan (Phase 0)

**Company:** ZORVAK Studios LLP  
**Product:** GAVIX Desktop Browser  
**Framework:** Electron (Chromium + Node.js Main) + TypeScript + React / Vanilla Web Components  
**Date:** October 13, 2026  

---

## 1. Executive Summary & Strategic Reset

1. **Desktop Priority Realignment:** Development is redirected to **GAVIX Desktop Browser via Electron**. The previously contemplated native Chromium Android C++ compilation is decoupled from the desktop roadmap.
2. **Prototype Preservation:** The existing Python/PySide6 prototype under `browser/` is preserved untouched as the visual, design, and UX gold standard (23/23 tests passing).
3. **Independent Search Engine Track:** GAVIX Search is decoupled into an independent engineering track communicating strictly through the versioned HTTP contract documented in [`docs/GAVIX_SEARCH_API.md`](file:///c:/Users/sanju/Desktop/Gavix/docs/GAVIX_SEARCH_API.md).

---

## 2. Process & Process Isolation Architecture

Electron provides Chromium's native rendering engine while allowing modular process isolation:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   MAIN PROCESS (Node.js Environment)                  │
│  - Window Management (BrowserWindow)                                   │
│  - Tab Management via WebContentsView / BaseWindow                     │
│  - Session Management (Default Partition + Ephemeral Incognito)        │
│  - GAVIX Shield (session.webRequest.onBeforeRequest Interceptor)       │
│  - GAVIX Performance Engine (Tab lifecycle & memory monitor)          │
│  - Downloads Manager & Local SQLite Storage                            │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │ IPC (contextBridge / ipcRenderer.invoke)
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      PRELOAD SCRIPT (Isolated Bridge)                  │
│  - contextIsolation: true                                              │
│  - sandbox: true                                                       │
│  - Exposes typed window.gavixAPI (no direct Node.js access)            │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │ Strictly Typed Events
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     CHROME RENDERER (GAVIX UI Frame)                  │
│  - Top Tab Bar (Tabs, Add Button, Tab switching)                       │
│  - Omnibox Toolbar (Navigation, URL input, Shield/Settings buttons)    │
│  - 78px Left Navigation Rail (Vector SVG Icons, Active Home state)     │
│  - New Tab Portal (Cinematic background, 62x62px glass shortcuts)      │
│  - Internal Pages (gavix://bookmarks, history, downloads, settings)   │
└────────────────────────────────────────────────────────────────────────┘
                                  │ Controls
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                GUEST WEB CONTENTS (WebContentsView)                   │
│  - Arbitrary External Websites (youtube.com, github.com, etc.)         │
│  - 100% Sandbox, nodeIntegration: false, contextIsolation: true        │
│  - Runs isolated inside Chromium renderer processes                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Technical Subsystems

### 3.1. Tab Architecture (`WebContentsView`)
- Do **NOT** use legacy `<webview>` tags (deprecated, slower, security issues).
- Use Electron's modern **`WebContentsView`** attached to the `BaseWindow` / `BrowserWindow`.
- The Chrome UI (Tabs, Toolbar, Sidebar) occupies a persistent top/left frame, while the active `WebContentsView` dynamically fits the remaining content bounds.
- Inactive tabs remain preserved in memory or transition to `FROZEN` / `DISCARDED` based on memory pressure.

### 3.2. GAVIX Shield Engine (`electron/shield/`)
- Utilizes Electron's native `session.webRequest.onBeforeRequest` filter.
- Evaluates URLs against compact, pre-compiled ad/tracker rule lists (EasyList format).
- Intercepts and blocks tracking telemetry, cryptominers, and intrusive ad scripts before network dispatch.
- **Real Counters:** Increments `trackersBlocked` and `requestsBlocked` on actual interception events only.

### 3.3. GAVIX Search Integration (`electron/search/`)
- Implements `SearchProvider` interface with versioned endpoints matching `docs/GAVIX_SEARCH_API.md`:
  - `search(query, page, limit, lang, region)`
  - `suggest(query, lang)`
  - `images(query)`, `videos(query)`, `news(query)`, `maps(query)`
- **Development Mock Fixture:** A local fixture provider (`MockSearchProvider`) allows testing UI states, pagination, and error scenarios without blocking on the backend team.
- **Resilience:** Unreachable search endpoint gracefully displays `"Search temporarily unavailable"` with a retry button; general URL navigation is never interrupted.

### 3.4. Local-First Privacy & Ephemeral Incognito Profile
- **Persistent Profile:** Normal browsing persists cookies, cache, local bookmarks, and history in `%LOCALAPPDATA%/GavixBrowser/`.
- **Private Browsing Session:** Spawns an in-memory session partition (`session.fromPartition('persist:gavix-private', { cache: false })` or dynamic UUID partition).
  - Isolated cookies, zero history storage, zero cloud telemetry.

### 3.5. Performance Engine (`GavixPerformanceEngine`)
- Progressive tab lifecycle:
  `ACTIVE` (foreground) → `RECENT` (<5 min) → `IDLE` (background) → `FROZEN` (DOM timer throttling) → `DISCARDED` (webContents destroyed, restored on click).
- Excludes tabs with active audio/video playback, live downloads, or pending form submissions.

---

## 4. Prototype Design Migration Matrix

The visual system from the PySide6 prototype is mapped 1:1 to Electron CSS:

| Prototype Component | Current PySide6 Metric / Asset | Electron Implementation |
| :--- | :--- | :--- |
| **Top Tab Bar** | Dark charcoal `#080D13`, tabs 140–220px, icon + label + close button | Flexbox row `#080D13`, CSS glass tabs, active emerald border |
| **Omnibox Bar** | 12px radius, translucent `#141D28` (75%), emerald focus ring | CSS glass input, autocomplete dropdown, HTTPS security badge |
| **Left Sidebar** | 78px width, `#0A1118`, 22px SVG icons, active emerald pill | CSS flex column, 78px fixed, SVG icons with `color: #00E599` active pill |
| **New Tab Background** | `browser/assets/bg_image.png` (Cinematic Aurora & Mountain lake) | Copied to assets, responsive WebP/PNG background |
| **Shortcut Tiles** | 62×62px glass tiles, 16px radius, SVG brand logos | Pure CSS glassmorphic tiles with hover tilt and backdrop blur |
| **Weather Badge** | Top-right translucent pill (`24°C Bengaluru`) | Real-time / graceful fallback widget |
| **Bottom Cards** | `🛡 Privacy First` & `⚡ Faster Internet` floating cards | Bottom fixed glass cards with SVG icons |

---

## 5. Development Roadmap (Phases 0–15)

- **PHASE 0 (CURRENT):** Architecture reset, environment inspection, search API contract, Electron roadmap (Complete).
- **PHASE 1:** Initialize `electron-browser/` package, TypeScript configs, secure Main/Preload/Renderer scaffolding.
- **PHASE 2:** Multi-tab manager via `WebContentsView`, omnibox navigation, and back/forward/reload controls.
- **PHASE 3:** Persistent local SQLite storage (Bookmarks, History, Downloads Manager).
- **PHASE 4:** Isolated Incognito / Private Browsing session profiles.
- **PHASE 5:** GAVIX visual migration (78px sidebar, top tab bar, omnibox styling from prototype).
- **PHASE 6:** Cinematic New Tab portal (Shortcuts, weather, bottom cards).
- **PHASE 7:** GAVIX Search API integration (`docs/GAVIX_SEARCH_API.md` + fallback fixture).
- **PHASE 8:** Real GAVIX Shield network request interceptor and telemetry counters.
- **PHASE 9:** GAVIX Performance Engine (Tab lifecycle and memory throttling).
- **PHASE 10:** Multi-language localization (English, Hindi, Kannada).
- **PHASE 11:** Security hardening (CSP, contextBridge validation, permission gatekeeper).
- **PHASE 12:** Performance benchmarking against Chrome, Edge, and Brave.
- **PHASE 13:** Windows desktop packaging (`electron-builder` / NSIS installer).
- **PHASE 14:** Closed Beta distribution.
- **PHASE 15:** Production v1.0 Release.
