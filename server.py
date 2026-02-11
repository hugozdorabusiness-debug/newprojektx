"""
Flask Server for AI News Dashboard
Serves the dashboard and provides API endpoints
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import sys
import re

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from scraper_bens_bites import scrape_bens_bites
from scraper_ai_rundown import scrape_ai_rundown
from scraper_reddit import scrape_reddit

app = Flask(__name__, static_folder='.')
CORS(app)

# In-memory storage for articles and saved items
articles_db = []
saved_articles = set()

def load_cached_articles():
    """Load articles from cache file if exists"""
    global articles_db
    cache_file = '.tmp/articles_cache.json'
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                articles_db = json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")

def save_articles_cache():
    """Save articles to cache file"""
    os.makedirs('.tmp', exist_ok=True)
    cache_file = '.tmp/articles_cache.json'
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(articles_db, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")

def load_saved_articles():
    """Load saved articles from persistent storage"""
    global saved_articles
    saved_file = 'saved_articles/saved_articles.json'
    if os.path.exists(saved_file):
        try:
            with open(saved_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                saved_articles = set(data.get('saved_ids', []))
                print(f"Loaded {len(saved_articles)} saved articles")
        except Exception as e:
            print(f"Error loading saved articles: {e}")

def save_saved_articles():
    """Save saved articles to persistent storage"""
    os.makedirs('saved_articles', exist_ok=True)
    saved_file = 'saved_articles/saved_articles.json'
    try:
        data = {
            'saved_ids': list(saved_articles),
            'last_updated': datetime.now().isoformat(),
            'total_saved': len(saved_articles)
        }
        with open(saved_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(saved_articles)} articles to persistent storage")
    except Exception as e:
        print(f"Error saving saved articles: {e}")

def save_article_details(article_id):
    """Save full article details to individual file"""
    # Find the article in the database
    article = next((a for a in articles_db if a.get('id', a.get('url')) == article_id), None)
    if not article:
        return
    
    os.makedirs('saved_articles/details', exist_ok=True)
    # Create safe filename from article ID
    safe_filename = re.sub(r'[^\w\-_]', '_', article_id)
    article_file = f'saved_articles/details/{safe_filename}.json'
    
    try:
        article_data = article.copy()
        article_data['saved_at'] = datetime.now().isoformat()
        
        with open(article_file, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, indent=2, ensure_ascii=False)
        print(f"Saved article details: {article.get('title', 'Unknown')}")
    except Exception as e:
        print(f"Error saving article details: {e}")

def delete_article_details(article_id):
    """Delete article details file when unsaved"""
    safe_filename = re.sub(r'[^\w\-_]', '_', article_id)
    article_file = f'saved_articles/details/{safe_filename}.json'
    
    try:
        if os.path.exists(article_file):
            os.remove(article_file)
            print(f"Deleted article details file")
    except Exception as e:
        print(f"Error deleting article details: {e}")

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/dashboard.css')
def serve_css():
    """Serve the CSS file"""
    return send_from_directory('.', 'dashboard.css')

@app.route('/dashboard.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory('.', 'dashboard.js')

@app.route('/date-picker.css')
def serve_date_picker_css():
    """Serve the date picker CSS file"""
    return send_from_directory('.', 'date-picker.css')

@app.route('/date-picker.js')
def serve_date_picker_js():
    """Serve the date picker JavaScript file"""
    return send_from_directory('.', 'date-picker.js')

@app.route('/api/articles')
def get_articles():
    """Get all articles with saved status"""
    articles_with_saved = []
    for article in articles_db:
        article_copy = article.copy()
        article_copy['is_saved'] = article.get('id', article.get('url')) in saved_articles
        articles_with_saved.append(article_copy)
    
    return jsonify({
        'articles': articles_with_saved,
        'last_updated': datetime.now().isoformat(),
        'total': len(articles_with_saved)
    })

@app.route('/api/scrape', methods=['POST'])
def scrape_all():
    """Trigger scraping from all sources"""
    global articles_db
    
    print("Starting scrape...")
    all_articles = []
    
    # Scrape from all sources
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
    
    articles_db = unique_articles
    save_articles_cache()
    
    return jsonify({
        'status': 'success',
        'articles_found': len(unique_articles),
        'scraped_at': datetime.now().isoformat()
    })

@app.route('/api/save/<article_id>', methods=['POST'])
def save_article(article_id):
    """Save an article"""
    saved_articles.add(article_id)
    save_saved_articles()  # Persist to file
    save_article_details(article_id)  # Save full article details
    return jsonify({'status': 'success', 'saved': True})

@app.route('/api/unsave/<article_id>', methods=['POST'])
def unsave_article(article_id):
    """Unsave an article"""
    saved_articles.discard(article_id)
    save_saved_articles()  # Persist to file
    delete_article_details(article_id)  # Delete article details file
    return jsonify({'status': 'success', 'saved': False})

@app.route('/api/saved')
def get_saved_articles():
    """Get all saved articles"""
    saved = []
    for article in articles_db:
        article_id = article.get('id', article.get('url'))
        if article_id in saved_articles:
            # Make a copy and ensure is_saved is True
            article_copy = article.copy()
            article_copy['is_saved'] = True
            saved.append(article_copy)
    
    return jsonify({
        'articles': saved,
        'total': len(saved)
    })

if __name__ == '__main__':
    # Load cached articles on startup
    load_cached_articles()
    # Load saved articles from persistent storage
    load_saved_articles()
    
    print("=" * 60)
    print("🚀 AI News Dashboard Server Starting...")
    print("=" * 60)
    print("📍 Dashboard URL: http://localhost:5000")
    print("📡 API Endpoints:")
    print("   - GET  /api/articles     - Get all articles")
    print("   - POST /api/scrape       - Trigger scraping")
    print("   - POST /api/save/<id>    - Save article")
    print("   - POST /api/unsave/<id>  - Unsave article")
    print("   - GET  /api/saved        - Get saved articles")
    print("=" * 60)
    print("\n💡 Open http://localhost:5000 in your browser\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
