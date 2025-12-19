import sys
import json
import requests
from parsers.jobkorea import parse_job_list

def scrape_manual(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
        'Referer': 'https://www.jobkorea.co.kr/'
    }
    
    try:
        print(f"Fetching {url} with requests...")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Force UTF-8 as Korean sites sometimes don't send charset or requests guesses wrong
        response.encoding = 'utf-8'
        html = response.text
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Parsing jobs...")
        jobs = parse_job_list(html)
        
        output_file = 'jobs.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([job.model_dump() for job in jobs], f, ensure_ascii=False, indent=2)
            
        if not jobs:
            print("Successfully scraped 0 jobs.")
            print("Hint: The website structure might have changed, or it uses client-side rendering (Next.js/React) which BeautifulSoup cannot parse directly.")
            print("Technique 2 or 3 (using MCP) is recommended for this site.")
        else:
            print(f"Successfully scraped {len(jobs)} jobs. Saved to {output_file}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manual_scraper.py <url>")
        sys.exit(1)
        
    target_url = sys.argv[1]
    scrape_manual(target_url)
