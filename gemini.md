# 📜 Project Constitution (gemini.md)

> **This is LAW.** All schemas, rules, and architectural invariants live here.
> Update only when schemas change, rules are added, or architecture is modified.

---

## 🎯 Project Overview

**Status:** Blueprint Phase (Protocol 0 Complete)  
**Created:** 2026-02-11  
**Last Updated:** 2026-02-11 10:10 CET  

### Mission Statement
Build a **beautiful, self-healing AI news aggregator dashboard** that automatically scrapes the latest AI news from Ben's Bites, The AI Rundown, and Reddit every 24 hours, stores it in Supabase, and displays it in a gorgeous interactive interface with save/unsave functionality.

---

## 📊 Data Schemas

### Scraper Output Schema (Intermediate)
**Location:** `.tmp/{source}_articles.json`

```json
{
  "source": "bens_bites | ai_rundown | reddit",
  "scraped_at": "2026-02-11T10:00:00Z",
  "articles": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "summary": "Brief description or excerpt",
      "published_at": "2026-02-11T08:30:00Z",
      "metadata": {
        "author": "Optional",
        "tags": ["AI", "ML"],
        "upvotes": 123,
        "subreddit": "r/artificial"
      }
    }
  ]
}
```

### Supabase Database Schema

**Table: `articles`**
```sql
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('bens_bites', 'ai_rundown', 'reddit')),
  summary TEXT,
  published_at TIMESTAMP NOT NULL,
  scraped_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_source ON articles(source);
```

**Table: `saved_articles`**
```sql
CREATE TABLE saved_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
  saved_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(article_id)
);
```

**Table: `scraper_runs`**
```sql
CREATE TABLE scraper_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'partial')),
  articles_found INTEGER DEFAULT 0,
  error_message TEXT,
  run_at TIMESTAMP DEFAULT NOW()
);
```

### Dashboard API Response Schema
**Endpoint:** Frontend fetches from Supabase

```json
{
  "articles": [
    {
      "id": "uuid",
      "title": "Article Title",
      "url": "https://example.com",
      "source": "bens_bites",
      "summary": "Brief description",
      "published_at": "2026-02-11T08:30:00Z",
      "is_saved": false
    }
  ],
  "last_updated": "2026-02-11T10:00:00Z"
}
```

---

## 🧭 Behavioral Rules

### Core Principles
1. **Data-First:** No coding until schemas are defined ✅
2. **Deterministic:** Business logic must be predictable and testable
3. **Self-Healing:** Errors update architecture docs to prevent recurrence
4. **Separation of Concerns:** Architecture → Navigation → Tools
5. **Design Excellence:** UI must be gorgeous, interactive, and premium

### Data Freshness Rules
- **24-Hour Window:** Only display articles published in the last 24 hours
- **Auto-Refresh:** Scrapers run every 24 hours (configurable)
- **Deduplication:** Never insert duplicate articles (enforce by URL uniqueness)
- **Stale Data Cleanup:** Optional - archive articles older than 7 days

### Scraping Behavior
- **Rate Limiting:** Minimum 2-second delay between requests to same domain
- **User Agent:** Always use realistic browser user agent
- **Error Handling:** If one scraper fails, continue with others
- **Retry Logic:** Retry failed requests up to 3 times with exponential backoff
- **Logging:** Log all scraper runs to `scraper_runs` table

### UI/UX Rules
- **Performance:** Dashboard must load in <2 seconds
- **Responsiveness:** Support mobile, tablet, desktop (breakpoints: 640px, 1024px)
- **Accessibility:** Proper ARIA labels, keyboard navigation
- **Feedback:** Show loading states, success/error messages
- **Animations:** Smooth transitions (max 300ms), no jarring effects

### "Do Not" Rules
- ❌ Do NOT scrape more frequently than every 12 hours (respect servers)
- ❌ Do NOT store user passwords (no authentication yet)
- ❌ Do NOT display articles without source attribution
- ❌ Do NOT use inline styles (keep CSS in separate file)
- ❌ Do NOT commit `.env` file to version control

---

## 🏗️ Architectural Invariants

### File Structure
```
├── gemini.md          # This file - Project Constitution
├── task_plan.md       # Phase tracking and checklists
├── findings.md        # Research and discoveries
├── progress.md        # Action log and results
├── .env               # API Keys/Secrets (git-ignored)
├── architecture/      # Layer 1: SOPs (Markdown)
├── tools/             # Layer 3: Python Scripts
└── .tmp/              # Temporary workbench
```

### Layer Responsibilities

**Layer 1: Architecture (`architecture/`)**
- Technical SOPs in Markdown
- Define goals, inputs, tool logic, edge cases
- **Golden Rule:** Update SOP before updating code

**Layer 2: Navigation (Decision Making)**
- Reasoning layer (this AI agent)
- Routes data between SOPs and Tools
- Does not perform complex tasks directly

**Layer 3: Tools (`tools/`)**
- Deterministic Python scripts
- Atomic and testable operations
- Environment variables from `.env`
- Intermediate files in `.tmp/`

---

## 🔗 Integration Points

### External Services

**Supabase (Database)**
- **Purpose:** Store articles, saved items, scraper logs
- **Required:** Project URL, Anon Key
- **Tables:** `articles`, `saved_articles`, `scraper_runs`

**Ben's Bites**
- **Type:** Newsletter/Website scraping
- **URL:** https://www.bensbites.co (or archive)
- **Method:** Web scraping (BeautifulSoup)
- **Rate Limit:** 1 request per 2 seconds

**The AI Rundown**
- **Type:** Newsletter/Website scraping
- **URL:** https://www.therundown.ai
- **Method:** Web scraping (BeautifulSoup)
- **Rate Limit:** 1 request per 2 seconds

**Reddit**
- **Type:** API or web scraping
- **Subreddits:** r/artificial, r/MachineLearning, r/OpenAI
- **Method:** PRAW (Python Reddit API Wrapper) or scraping
- **Rate Limit:** 60 requests per minute (API), 1 per 2 sec (scraping)

### API Endpoints
*To be documented during Link phase after testing*

### Authentication
- **Supabase:** API Key in `.env` (SUPABASE_KEY)
- **Reddit:** Optional - Client ID/Secret for API access
- **Scrapers:** User-Agent header (no auth needed)

---

## 🧪 Testing Strategy

### Test Requirements
*To be defined during Architecture phase*

### Success Criteria
*To be defined after Discovery Questions*

---

## 🚨 Maintenance Log

### Known Issues
- None yet

### Resolved Issues
- None yet

### Performance Optimizations
- None yet

---

## 📝 Change History

### 2026-02-11 10:10 CET
- **Action:** Protocol 0 Complete - Schemas Defined
- **Phase:** Blueprint (B.L.A.S.T.)
- **Changes:** 
  - Defined scraper output schema (JSON)
  - Defined Supabase database schema (3 tables)
  - Defined dashboard API response schema
  - Documented behavioral rules and constraints
  - Documented integration points (Supabase, Ben's Bites, AI Rundown, Reddit)
- **Reason:** Data-First Rule requires schemas before coding

### 2026-02-11 09:43 CET
- **Action:** Initial creation
- **Phase:** Protocol 0 - Initialization
- **Changes:** Established constitution structure
- **Reason:** B.L.A.S.T. protocol requires project constitution before coding
