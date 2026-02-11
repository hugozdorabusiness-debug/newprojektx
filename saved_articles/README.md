# Saved Articles

This folder contains your saved articles that persist across server restarts and refresh operations.

## Structure

```
saved_articles/
├── saved_articles.json      # List of saved article IDs
└── details/                 # Individual article details
    ├── article_1.json
    ├── article_2.json
    └── ...
```

## Files

### `saved_articles.json`
Contains the list of saved article IDs and metadata:
```json
{
  "saved_ids": ["article_id_1", "article_id_2"],
  "last_updated": "2026-02-11T12:30:00",
  "total_saved": 2
}
```

### `details/*.json`
Each file contains the full details of a saved article:
```json
{
  "id": "article_id",
  "title": "Article Title",
  "url": "https://example.com/article",
  "source": "bens_bites",
  "summary": "Article summary...",
  "published_at": "2026-02-11T10:00:00",
  "saved_at": "2026-02-11T12:30:00",
  "metadata": {
    "author": "Author Name",
    "tags": ["AI", "News"]
  }
}
```

## Features

- ✅ **Persistent Storage**: Saved articles survive server restarts
- ✅ **Refresh-Safe**: Articles remain saved even after refreshing news
- ✅ **Full Details**: Complete article information stored separately
- ✅ **Easy Backup**: Simply copy this folder to backup your saved articles

## Notes

- This folder is automatically created when you save your first article
- Unsaving an article removes it from both files
- You can manually edit `saved_articles.json` if needed
- Individual article files are named using sanitized article IDs
