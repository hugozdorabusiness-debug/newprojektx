import modal
from modal.volume import Volume
import sys
import os
import json
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# --- Configuration ---
APP_NAME = "ai-news-dashboard"
VOLUME_NAME = "ai-news-data"

# --- Modal Setup ---
app = modal.App(APP_NAME)
volume = Volume.from_name(VOLUME_NAME, create_if_missing=True)

# Image with dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("flask", "flask-cors", "requests", "beautifulsoup4")
    # Add local tools directory
    .add_local_dir("tools", remote_path="/root/tools")
    # Add static files (HTML, CSS, JS)
    .add_local_file("dashboard.html", remote_path="/root/dashboard.html")
    .add_local_file("dashboard.css", remote_path="/root/dashboard.css")
    .add_local_file("dashboard.js", remote_path="/root/dashboard.js")
    .add_local_file("date-picker.css", remote_path="/root/date-picker.css")
    .add_local_file("date-picker.js", remote_path="/root/date-picker.js")
)

# --- Flask Attributes ---
web_app = Flask(__name__, static_folder='/root')
CORS(web_app)

# In-memory database (populated from volume on request)
# We use methods to interact with volume data

def get_data_path():
    return "/data/articles_cache.json"

def get_saved_path():
    return "/data/saved_articles.json"

def get_details_dir():
    return "/data/details"

def ensure_dirs():
    os.makedirs("/data/details", exist_ok=True)

# --- Helper Functions ---
def load_articles():
    path = get_data_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def load_saved_ids():
    path = get_saved_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return set(data.get('saved_ids', []))
        except:
            pass
    return set()

def save_saved_ids(saved_set):
    ensure_dirs()
    path = get_saved_path()
    data = {
        'saved_ids': list(saved_set),
        'last_updated': datetime.now().isoformat()
    }
    with open(path, 'w') as f:
        json.dump(data, f)
    volume.commit()

# --- Routes ---
@web_app.route('/')
def index():
    return send_from_directory('/root', 'dashboard.html')

@web_app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('/root', filename)

@web_app.route('/api/articles')
def get_articles_api():
    articles = load_articles()
    saved_ids = load_saved_ids()
    
    # Enrich with is_saved status
    result = []
    for art in articles:
        art_copy = art.copy()
        art_id = art.get('id', art.get('url'))
        art_copy['is_saved'] = art_id in saved_ids
        result.append(art_copy)
        
    return jsonify({
        'articles': result,
        'total': len(result),
        'source': 'modal_volume'
    })

@web_app.route('/api/saved')
def get_saved_api():
    articles = load_articles()
    saved_ids = load_saved_ids()
    
    saved_articles = []
    for art in articles:
        if art.get('id', art.get('url')) in saved_ids:
            art_copy = art.copy()
            art_copy['is_saved'] = True
            saved_articles.append(art_copy)
            
    return jsonify({
        'articles': saved_articles,
        'total': len(saved_articles)
    })

@web_app.route('/api/save/<article_id>', methods=['POST'])
def save_article(article_id):
    saved_ids = load_saved_ids()
    saved_ids.add(article_id)
    save_saved_ids(saved_ids)
    return jsonify({'status': 'success', 'saved': True})

@web_app.route('/api/unsave/<article_id>', methods=['POST'])
def unsave_article(article_id):
    saved_ids = load_saved_ids()
    if article_id in saved_ids:
        saved_ids.remove(article_id)
        save_saved_ids(saved_ids)
    return jsonify({'status': 'success', 'saved': False})

@web_app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    # Trigger the modal function asynchronously
    manual_scrape.spawn()
    return jsonify({'status': 'started', 'message': 'Scraping started in background'})

# --- Scraper Logic ---
def run_scraper_logic():
    print("Running scraper logic...")
    sys.path.append("/root/tools")
    
    # Import locally
    try:
        from scraper_bens_bites import scrape_bens_bites
        from scraper_ai_rundown import scrape_ai_rundown
        from scraper_reddit import scrape_reddit
    except ImportError as e:
        print(f"Import error: {e}")
        return

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
            for i, article in enumerate(articles):
                article['id'] = f"{result['source']}_{i}_{hash(article['url'])}"
                article['source'] = result['source']
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error: {e}")

    # Dedup
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)

    # Save
    ensure_dirs()
    with open(get_data_path(), 'w') as f:
        json.dump(unique_articles, f, indent=2)
    volume.commit()
    print(f"Saved {len(unique_articles)} articles.")

# --- Modal Functions ---

@app.function(image=image, schedule=modal.Period(hours=24), volumes={"/data": volume})
def scheduled_scrape():
    run_scraper_logic()

@app.function(image=image, volumes={"/data": volume})
def manual_scrape():
    run_scraper_logic()

@app.function(image=image, volumes={"/data": volume})
@modal.wsgi_app()
def flask_app():
    return web_app
