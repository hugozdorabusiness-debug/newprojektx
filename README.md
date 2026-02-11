# AI News Dashboard

A beautiful, self-healing AI news aggregator dashboard that automatically scrapes the latest AI news from Ben's Bites, The AI Rundown, and Reddit.

## Features

- 🔥 **Multi-Source Scraping**: Aggregates news from Ben's Bites, The AI Rundown, and Reddit
- 💎 **Beautiful UI**: Modern, premium design with neon-green brand colors
- ⭐ **Persistent Saved Articles**: Save articles that survive server restarts and refresh operations
- 💾 **Separate Storage**: Saved articles stored in dedicated folder with full details
- 🎯 **Smart Filtering**: Filter by source or view saved articles only
- 📊 **Live Statistics**: Real-time stats for each news source
- 🔄 **One-Click Refresh**: Scrape latest news with a single click

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python server.py
```

### 3. Open Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Refresh News**: Click the "Refresh News" button to scrape the latest articles
2. **Filter Sources**: Use the filter tabs to view articles from specific sources
3. **Save Articles**: Click the star icon to save/unsave articles
4. **View Saved**: Click "Saved Only" tab to see your saved articles

## Project Structure

```
├── server.py              # Flask server with API endpoints
├── dashboard.html         # Main dashboard interface
├── dashboard.css          # Styling with modern design
├── dashboard.js           # Interactive functionality
├── requirements.txt       # Python dependencies
├── tools/
│   ├── scraper_bens_bites.py    # Ben's Bites scraper
│   ├── scraper_ai_rundown.py    # AI Rundown scraper
│   └── scraper_reddit.py        # Reddit scraper
├── saved_articles/        # Persistent saved articles storage
│   ├── saved_articles.json      # List of saved article IDs
│   └── details/                 # Individual article details
└── .tmp/                  # Temporary cache files
```

## Deployment (Automated Scraping) 🚀

This project uses [Modal](https://modal.com) to run the scraper automatically every 24 hours in the cloud.

### 1. Setup Modal

```bash
pip install modal
python -m modal setup
```

### 2. Deploy Scraper

```bash
python -m modal deploy modal_scraper.py
```

This will:
- Deploy the scraper to the cloud ☁️
- Schedule it to run every 24 hours ⏰
- Create a persistent volume for data 💾
- Provide a web endpoint to access the scraped data 🌐

### 3. View Logs & Manage

You can view logs, run history, and manage the deployment at [modal.com](https://modal.com/apps).

## API Endpoints

- `GET /` - Serve dashboard
- `GET /api/articles` - Get all articles
- `POST /api/scrape` - Trigger scraping
- `POST /api/save/<id>` - Save article
- `POST /api/unsave/<id>` - Unsave article
- `GET /api/saved` - Get saved articles

## Technologies

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Scraping**: BeautifulSoup4, Requests
- **Design**: Modern CSS with gradients, glassmorphism, animations

## Features in Detail

### Web Scrapers
- Rate-limited requests (2 seconds between requests)
- Error handling and retry logic
- Realistic browser user agents
- JSON output format

### Dashboard
- Responsive design (mobile, tablet, desktop)
- Dark mode with vibrant gradients
- Smooth animations and transitions
- Toast notifications for user feedback
- Real-time statistics

### Data Management
- In-memory storage with file caching
- **Persistent saved articles** in `saved_articles/` folder
- **Individual article files** with full details in `saved_articles/details/`
- Automatic deduplication by URL
- Save/unsave functionality survives server restarts
- Filter by source or saved status

## Troubleshooting

**Server won't start:**
- Make sure port 5000 is not in use
- Check that all dependencies are installed

**No articles showing:**
- Click "Refresh News" to scrape articles
- Check your internet connection
- Some sites may block scraping - this is normal

**Scraping errors:**
- Website structures may change over time
- Rate limiting may be in effect
- Check console logs for specific errors

## Future Enhancements

- [ ] Supabase integration for persistent storage
- [ ] User authentication
- [x] Scheduled automatic scraping (via Modal)
- [ ] Email notifications for new articles
- [ ] Advanced search and filtering
- [ ] Export to PDF/CSV

## License

MIT License - Feel free to use and modify!

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
