"""
Reddit Scraper
Scrapes latest AI news from Reddit
"""
import requests
from datetime import datetime
import json
import time

def scrape_reddit():
    """Scrape articles from Reddit AI subreddits"""
    articles = []
    subreddits = ['artificial', 'MachineLearning', 'OpenAI']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for subreddit in subreddits:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=5"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for post in data['data']['children']:
                try:
                    post_data = post['data']
                    
                    # Skip stickied posts
                    if post_data.get('stickied', False):
                        continue
                    
                    title = post_data.get('title', '')
                    post_url = post_data.get('url', '')
                    
                    # Use Reddit post URL if no external URL
                    if not post_url or 'reddit.com' in post_url:
                        post_url = f"https://www.reddit.com{post_data.get('permalink', '')}"
                    
                    summary = post_data.get('selftext', '')[:300] or title
                    upvotes = post_data.get('ups', 0)
                    created_utc = post_data.get('created_utc', time.time())
                    published_at = datetime.fromtimestamp(created_utc).isoformat()
                    
                    articles.append({
                        'title': title,
                        'url': post_url,
                        'summary': summary,
                        'published_at': published_at,
                        'metadata': {
                            'author': post_data.get('author', 'Unknown'),
                            'tags': ['AI', 'Reddit'],
                            'upvotes': upvotes,
                            'subreddit': f"r/{subreddit}"
                        }
                    })
                    
                except Exception as e:
                    print(f"Error parsing Reddit post: {e}")
                    continue
            
            # Rate limiting between subreddits
            time.sleep(2)
            
        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
            continue
    
    return {
        'source': 'reddit',
        'scraped_at': datetime.now().isoformat(),
        'articles': articles
    }

if __name__ == '__main__':
    result = scrape_reddit()
    print(json.dumps(result, indent=2))
