import sys
import json
import asyncio
import os
import re
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from schemas import Job

# Load environment variables from .env file
load_dotenv()

# Check for API Token
BRIGHT_DATA_API_TOKEN = os.environ.get("BRIGHT_DATA_API_TOKEN")

def parse_markdown_jobs(markdown: str) -> list[Job]:
    """
    Parses job listings from the markdown output of scrape_as_markdown.
    Pattern observed:
    [Job Title](link)
    [Company Name](link)
    Location
    Tags
    ...
    Date
    """
    jobs = []
    lines = markdown.split('\n')
    
    # Regex for a markdown link: [text](url)
    link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line is a Job Title Link
        match = link_pattern.match(line)
        if match:
            text = match.group(1)
            url = match.group(2)
            
            # Filter: Is this a job link?
            # Looking for links containing Recruit/GI_Read
            if "Recruit/GI_Read" in url:
                # Found a potential job title
                title = text
                link = url
                if not link.startswith('http'):
                     link = 'https://www.jobkorea.co.kr' + link
                
                # Default values
                company = "Unknown"
                location = "Unknown"
                date = "Unknown"
                
                # Look ahead for Company (next link)
                # Usually there is an empty line between title and company
                offset = 1
                while i + offset < len(lines) and offset < 6:
                    next_line = lines[i+offset].strip()
                    if not next_line:
                        offset += 1
                        continue
                        
                    # Is this the company link?
                    company_match = link_pattern.match(next_line)
                    if company_match:
                        company = company_match.group(1)
                        
                        # Location usually follows shortly after company
                        loc_offset = offset + 1
                        while i + loc_offset < len(lines) and loc_offset < offset + 5:
                            loc_line = lines[i+loc_offset].strip()
                            # Location is usually a simple string like "서울 강남구"
                            # It shouldn't be a link or empty
                            if loc_line and not loc_line.startswith('['):
                                location = loc_line
                                break
                            loc_offset += 1
                        
                        # Date usually follows location or tags
                        date_offset = loc_offset + 1
                        while i + date_offset < len(lines) and date_offset < offset + 10:
                            date_line = lines[i+date_offset].strip()
                            if "등록" in date_line or "마감" in date_line:
                                date = date_line
                                break
                            date_offset += 1
                            
                        # Advance iterator past this block
                        i += offset 
                        break
                    
                    # If we hit another job title link (unlikely this close) or something else
                    if "Recruit/GI_Read" in next_line:
                        break 
                    
                    offset += 1

                jobs.append(Job(
                    title=title,
                    company=company,
                    location=location,
                    date=date,
                    link=link
                ))
        
        i += 1
        
    return jobs

async def scrape_mcp(url: str):
    if not BRIGHT_DATA_API_TOKEN or BRIGHT_DATA_API_TOKEN == "your_token_here":
        print("Error: BRIGHT_DATA_API_TOKEN is not set in .env or environment variables.")
        print("Please update the .env file with your actual Bright Data API Token.")
        return

    # Server parameters
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@brightdata/mcp"],
        env={"API_TOKEN": BRIGHT_DATA_API_TOKEN, **os.environ}
    )

    print(f"Connecting to Bright Data MCP server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print(f"Connected. Fetching {url} via scrape_as_markdown tool...")

                try:
                    result = await session.call_tool(
                        "scrape_as_markdown",
                        arguments={"url": url}
                    )
                    
                    content_text = ""
                    if result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                content_text += content.text
                                
                    if not content_text:
                        print("Warning: No content returned from tool.")
                        return

                    # Save raw markdown
                    output_file_md = 'scraped_data.md'
                    with open(output_file_md, 'w', encoding='utf-8') as f:
                        f.write(content_text)
                    print(f"Saved raw markdown to {output_file_md}")

                    # Parse Markdown to JSON
                    print("Parsing markdown jobs...")
                    jobs = parse_markdown_jobs(content_text)
                    
                    output_file_json = 'jobs_mcp.json'
                    with open(output_file_json, 'w', encoding='utf-8') as f:
                        json.dump([job.model_dump() for job in jobs], f, ensure_ascii=False, indent=2)
                        
                    print(f"Successfully scraped {len(jobs)} jobs. Saved to {output_file_json}")

                except Exception as e:
                    print(f"Error calling tool: {e}")

    except Exception as e:
        print(f"Error connecting to MCP server (make sure you have npx installed): {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_scraper.py <url>")
        sys.exit(1)
        
    target_url = sys.argv[1]
    asyncio.run(scrape_mcp(target_url))
