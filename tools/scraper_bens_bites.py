"""
Ben's Bites Scraper
Scrapes latest AI news from Ben's Bites
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time

def scrape_bens_bites():
    """Scrape articles from Ben's Bites"""
    articles = []
    
    try:
        # Ben's Bites main page
        url = "https://www.bensbites.co"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find article elements (adjust selectors based on actual site structure)
        article_elements = soup.find_all(['article', 'div'], class_=['post', 'article', 'card'], limit=10)
        
        for element in article_elements:
            try:
                # Extract title
                title_elem = element.find(['h1', 'h2', 'h3', 'a'])
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                # Extract URL
                link_elem = element.find('a', href=True)
                article_url = link_elem['href'] if link_elem else url
                if not article_url.startswith('http'):
                    article_url = f"{url}{article_url}"
                
                # Extract summary
                summary_elem = element.find(['p', 'div'], class_=['excerpt', 'summary', 'description'])
                summary = summary_elem.get_text(strip=True) if summary_elem else title
                
                # Use current time as published date (can be improved with actual date parsing)
                published_at = datetime.now().isoformat()
                
                articles.append({
                    'title': title,
                    'url': article_url,
                    'summary': summary[:300],  # Limit summary length
                    'published_at': published_at,
                    'metadata': {
                        'author': 'Ben\'s Bites',
                        'tags': ['AI', 'News']
                    }
                })
                
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
        
        # Rate limiting
        time.sleep(2)
        
    except Exception as e:
        print(f"Error scraping Ben's Bites: {e}")
    
    return {
        'source': 'bens_bites',
        'scraped_at': datetime.now().isoformat(),
        'articles': articles
    }

if __name__ == '__main__':
    result = scrape_bens_bites()
    print(json.dumps(result, indent=2))
