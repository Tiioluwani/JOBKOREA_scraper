# JOBKOREA Scraper Walkthrough

This project implements three techniques to scrape JOBKOREA, demonstrating the progression from manual scraping to agentic/MCP-based scraping.

## 1. Manual Scraper (Requests + BeautifulSoup)
**File:** `manual_scraper.py`

Attempts to scrape the site using standard HTTP requests.
**Result:** **SUCCESS** (via Advanced Parsing).
- JOBKOREA uses Next.js Client-Side Rendering (CSR), meaning job data is hidden in JSON scripts, not static HTML.
- **Problem:** Standard `BeautifulSoup` fails to find list items.
- **Solution:** The script now uses **Regex** to extract the job data directly from the Next.js hydration scripts (`self.__next_f.push`).
- **Outcome:** Successfully scrapes jobs without needing a full browser, though it's more fragile than the MCP approach.

**Usage:**
```bash
python manual_scraper.py "https://www.jobkorea.co.kr/Search/?stext=python"
```

## 2. Bright Data MCP Scraper
**File:** `mcp_scraper.py`

Uses the `@brightdata/mcp` server to bypass blocking.
**Method:**
1. Connects to the local MCP server.
2. Calls `scrape_as_markdown` (since `scrape_as_html` was deprecated/unavailable).
3. Saves raw markdown to `scraped_data.md`.
4. Parses the markdown to extract structure data into `jobs_mcp.json`.

**Prerequisites:**
- Node.js & npx installed
- Bright Data API Token in `.env` file

**Usage:**
1. Open `.env` and paste your token: `BRIGHT_DATA_API_TOKEN=...`
2. Run the scraper:
```bash
python3 mcp_scraper.py "https://www.jobkorea.co.kr/Search/?stext=python"
```

## 3. AI No-Code Scraper
**File:** `ai_nocode_scraper.md`

A recipe for using an AI agent (like Claude Desktop or this one) with the Bright Data MCP to extract data without writing scraping code.

**Steps:**
1.  Connect LLM to `@brightdata/mcp`.
2.  Paste the prompt from `ai_nocode_scraper.md`.
3.  Receive `jobs.json` structure directly.

## Project Structure
- `parsers/jobkorea.py`: Shared parsing logic (BeautifulSoup). containing best-effort selectors.
- `schemas.py`: Pydantic model for data validation.
- `jobs.json`: Output from manual scraper.
- `jobs_mcp.json`: Output from MCP scraper.
