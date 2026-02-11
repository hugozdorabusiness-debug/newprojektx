"""
The AI Rundown Scraper
Scrapes latest AI news from The AI Rundown
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import re

def scrape_ai_rundown():
    """Scrape articles from The AI Rundown"""
    articles = []
    
    try:
        url = "https://www.therundown.ai"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find article links - they follow pattern /p/article-slug
        article_links = soup.find_all('a', href=re.compile(r'^/p/'))
        
        seen_urls = set()
        
        for link in article_links[:10]:  # Limit to 10 articles
            try:
                article_url = link.get('href', '')
                if not article_url or article_url in seen_urls:
                    continue
                
                # Make full URL
                if article_url.startswith('/'):
                    article_url = f"{url}{article_url}"
                
                seen_urls.add(article_url)
                
                # Extract title from link text or nearby heading
                title = link.get_text(strip=True)
                
                # If title is too short or empty, try to find nearby h3
                if len(title) < 10:
                    parent = link.find_parent(['div', 'article', 'section'])
                    if parent:
                        heading = parent.find(['h3', 'h2', 'h1'])
                        if heading:
                            title = heading.get_text(strip=True)
                
                # Clean up title (remove author names like "Zach Mink, +4")
                title = re.sub(r',?\s*\+\d+$', '', title)
                title = re.sub(r'Zach Mink.*$', '', title).strip()
                
                if not title or len(title) < 5:
                    continue
                
                # Try to find summary/description
                summary = title  # Default to title
                parent = link.find_parent(['div', 'article', 'section'])
                if parent:
                    # Look for paragraph or description
                    desc = parent.find('p')
                    if desc:
                        summary_text = desc.get_text(strip=True)
                        if len(summary_text) > 20:
                            summary = summary_text
                
                published_at = datetime.now().isoformat()
                
                articles.append({
                    'title': title,
                    'url': article_url,
                    'summary': summary[:300],
                    'published_at': published_at,
                    'metadata': {
                        'author': 'The AI Rundown',
                        'tags': ['AI', 'News', 'Technology']
                    }
                })
                
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
        
        time.sleep(2)
        
    except Exception as e:
        print(f"Error scraping The AI Rundown: {e}")
    
    return {
        'source': 'ai_rundown',
        'scraped_at': datetime.now().isoformat(),
        'articles': articles
    }

if __name__ == '__main__':
    result = scrape_ai_rundown()
    print(json.dumps(result, indent=2))
