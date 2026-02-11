import modal
from modal.volume import Volume
import sys
import os
import json
from datetime import datetime

# Define Modal App
app = modal.App("ai-news-scraper")

# Define volume for persistence
volume = Volume.from_name("ai-news-data", create_if_missing=True)

# Define image with dependencies AND local directory
image = (
    modal.Image.debian_slim()
    .pip_install("requests", "beautifulsoup4", "flask", "flask-cors", "fastapi[standard]")
    .add_local_dir("tools", remote_path="/root/tools")
)

@app.function(image=image, schedule=modal.Period(days=1), volumes={"/data": volume})
def scheduled_scrape():
    # Add tools to path
    sys.path.append("/root/tools")
    
    # Import scrapers locally inside function to utilize mounted code
    try:
        from scraper_bens_bites import scrape_bens_bites
        from scraper_ai_rundown import scrape_ai_rundown
        from scraper_reddit import scrape_reddit
    except ImportError as e:
        print(f"Error importing scrapers: {e}")
        return

    print("Starting scheduled scrape...")
    all_articles = []
    
    sources = [
        ('Ben\'s Bites', scrape_bens_bites),
        ('AI Rundown', scrape_ai_rundown),
        ('Reddit', scrape_reddit)
    ]
    
    for source_name, scraper_func in sources:
        try:
            print(f"Scraping {source_name}...")
            result = scraper_func()
            articles = result.get('articles', [])
            
            # Add unique IDs and source
            for i, article in enumerate(articles):
                article['id'] = f"{result['source']}_{i}_{hash(article['url'])}"
                article['source'] = result['source']
            
            all_articles.extend(articles)
            print(f"Found {len(articles)} articles from {source_name}")
        except Exception as e:
            print(f"Error scraping {source_name}: {e}")
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    # Save to volume
    DATA_PATH = "/data/articles_cache.json"
    try:
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, indent=2)
        volume.commit()
        print(f"Saved {len(unique_articles)} articles to persistent storage at {DATA_PATH}.")
    except Exception as e:
        print(f"Error saving data: {e}")

@app.function(image=image, volumes={"/data": volume})
@modal.web_endpoint()
def get_articles():
    DATA_PATH = "/data/articles_cache.json"
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'status': 'success',
                    'articles': data,
                    'total': len(data), 
                    'source': 'modal_volume'
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    return {'status': 'success', 'articles': [], 'total': 0, 'message': 'No data found'}

if __name__ == "__main__":
    # Setup runs immediately for verification
    with app.run():
        scheduled_scrape.remote()
