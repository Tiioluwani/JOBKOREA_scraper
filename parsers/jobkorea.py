import re
import json
from typing import List
from bs4 import BeautifulSoup
from schemas import Job

def parse_nextjs_data(html: str) -> List[Job]:
    """
    Attempts to extract job data from Next.js client-side hydration scripts.
    """
    jobs = []
    
    # We look for the JSON structure we identified:
    # {"id":"...","title":"...","postingCompanyName":"..."...}
    # Since this is inside a string inside a script, we can use regex to find the objects.
    
    # Regex to find individual job objects. 
    # This assumes the keys are somewhat stable.
    # We look for "id": "...", "title": "..." which are standard.
    
    # Pattern: "id":"123","title":"Something", ... "postingCompanyName":"Corp"
    # We use a non-greedy matching.
    
    # Note: The data in the HTML is often double-escaped or just stringified JSON.
    # Let's try to find the full array first? No, regex finding objects is safer if array logic is complex.
    
    pattern = r'\\"id\\":\\"(?P<id>\d+)\\",\\"title\\":\\"(?P<title>.*?)\\",\\"postingCompanyName\\":\\"(?P<company>.*?)\\"'
    
    # If the HTML has normal quotes inside the script string (not escaped quote)
    # The debug logs showed: \"id\":\"113652775\" (escaped quotes)
    
    matches = re.finditer(pattern, html)
    
    for match in matches:
        job_id = match.group('id')
        title = match.group('title')
        company = match.group('company')
        
        # Unescape unicode entities if any (raw string might have them)
        # But simple replacement is usually enough for basic scrape
        title = title.replace('\\"', '"').replace('\\\\', '\\')
        company = company.replace('\\"', '"').replace('\\\\', '\\')
        
        # Link construction
        link = f"https://www.jobkorea.co.kr/Recruit/GI_Read/{job_id}"
        
        # Note: Previous encode/decode hack caused Mojibake if the string was already proper unicode.
        # Removing it. matched groups from re.finditer on a unicode string should be unicode.

        jobs.append(Job(
            title=title,
            company=company,
            link=link,
            location="See Link", # hard to regex strictly
            date="See Link"
        ))
        
    return jobs

def parse_job_list(html: str) -> List[Job]:
    """
    Parses JOBKOREA search result HTML and returns a list of Job objects.
    Attempts to handle different listing layouts.
    """
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []

    # Strategy 1: Static HTML Parsing
    job_lists = soup.find_all('div', class_='list-default')
    if not job_lists:
        job_lists = soup.find_all('ul', class_='clear')

    for container in job_lists:
        items = container.find_all('li')
        for item in items:
            try:
                title_elem = item.find('a', class_='title')
                if not title_elem:
                    title_elem = item.find('a', title=True)
                
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get('href')
                if link and not link.startswith('http'):
                    link = 'https://www.jobkorea.co.kr' + link

                company_elem = item.find('div', class_='post-list-corp')
                if not company_elem:
                    company_elem = item.find('a', class_='name')
                
                company = company_elem.get_text(strip=True) if company_elem else "Unknown"

                info_elem = item.find('div', class_='post-list-info')
                location = None
                date = None
                
                if info_elem:
                    spans = info_elem.find_all('span')
                    texts = [s.get_text(strip=True) for s in spans]
                    if texts:
                        location = texts[0]
                    
                    date_elem = info_elem.find('span', class_='date')
                    if date_elem:
                        date = date_elem.get_text(strip=True)
                    elif len(texts) > 1:
                        date = texts[-1]

                job = Job(
                    title=title,
                    company=company,
                    location=location,
                    date=date,
                    link=link
                )
                jobs.append(job)
            except Exception:
                continue
                
    # Strategy 2: Next.js Client-Side Data Extraction (Fallback)
    if not jobs:
        # print("Debug: No static jobs found. Attempting Next.js data extraction...")
        nextjs_jobs = parse_nextjs_data(html)
        if nextjs_jobs:
            jobs = nextjs_jobs
                
    return jobs
