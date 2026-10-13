# GAVIX Search API — Version 1 Contract (`/v1/`)

**Author:** ZORVAK Studios LLP / GAVIX Browser Engineering  
**Version:** 1.0.0  
**Specification Status:** Production Baseline Contract  
**Consumer:** GAVIX Desktop & Mobile Browsers  
**Producer:** Independent GAVIX Search Engine Backend  

---

## 1. Principles & Independence

1. **Decoupled Architecture:** The browser has zero dependency on the implementation language, crawler architecture, indexing database, or ranking pipeline of GAVIX Search.
2. **Strict Versioning:** All endpoints are strictly prefixed with `/v1/`. Breaking changes must be released under `/v2/`.
3. **Graceful Degradation:** If the search endpoint returns an error (5xx, 429) or is unreachable, the browser **must never crash**. General web navigation continues unimpeded with an inline user notice.
4. **Zero Telemetry Leakage:** Search queries contain query text, pagination, language, and region only. No user IDs, browser history, or advertising cookies may be transmitted.

---

## 2. API Endpoints

### 2.1. Web Search
`GET /v1/search`

#### Request Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `q` | `string` | **Yes** | — | Clean search query string (URL-encoded). |
| `page` | `integer` | No | `1` | 1-based page index. |
| `limit` | `integer` | No | `10` | Results per page (maximum 50). |
| `language` | `string` | No | `"en"` | BCP 47 language code (`en`, `hi`, `kn`, etc.). |
| `region` | `string` | No | `"IN"` | ISO 3166-1 alpha-2 region code. |

#### Response Schema (`200 OK`)
```json
{
  "query": "karnataka scholarships",
  "page": 1,
  "limit": 10,
  "totalResults": 1420,
  "hasNextPage": true,
  "executionTimeMs": 42,
  "results": [
    {
      "id": "res_001",
      "title": "State Scholarship Portal (SSP) - Post Matric",
      "url": "https://ssp.postmatric.karnataka.gov.in",
      "displayUrl": "ssp.postmatric.karnataka.gov.in",
      "snippet": "Official Karnataka state portal for post-matric and technical education scholarships for 2026-2027.",
      "faviconUrl": "https://ssp.postmatric.karnataka.gov.in/favicon.ico",
      "source": "gavix_index",
      "publishedDate": "2026-10-10"
    }
  ],
  "relatedQueries": [
    "ssp scholarship status 2026",
    "karnataka technical education scholarship login"
  ],
  "indexStatus": {
    "coverageNote": "Indexed by GAVIX India Search Engine."
  }
}
```

---

### 2.2. Query Autocomplete / Suggestions
`GET /v1/suggest`

#### Request Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `q` | `string` | **Yes** | Current prefix typed in the omnibox. |
| `language` | `string` | No | Preferred language (`en`, `hi`, `kn`). |

#### Response Schema (`200 OK`)
```json
{
  "query": "karnat",
  "suggestions": [
    "karnataka one",
    "karnataka rto",
    "karnataka tourism",
    "karnataka scholarship ssp"
  ]
}
```

---

### 2.3. Specialized Vertical Searches
- `GET /v1/images?q=...&page=...`
- `GET /v1/videos?q=...&page=...`
- `GET /v1/news?q=...&page=...`
- `GET /v1/maps?q=...&page=...`

#### Shared Result Item Extensions
- **Image Items:** `{ "thumbnailUrl": "...", "originalUrl": "...", "width": 1920, "height": 1080 }`
- **Video Items:** `{ "thumbnailUrl": "...", "duration": "14:20", "creator": "..." }`
- **News Items:** `{ "publisher": "...", "publishedAt": "2026-10-13T06:00:00Z" }`

---

## 3. Standard HTTP Error Codes

| Status | Code | Meaning | Browser Fallback Action |
| :--- | :--- | :--- | :--- |
| `400` | `INVALID_QUERY` | Empty or malformed query string. | Render empty query prompt. |
| `429` | `RATE_LIMITED` | Too many requests from client IP. | Display cooldown retry indicator. |
| `500` | `INTERNAL_ERROR` | Search backend failure. | Display friendly retry screen ("Search is temporarily unavailable"). |
| `503` | `MAINTENANCE` | Service under maintenance. | General web navigation remains 100% active. |
