// AI News Dashboard JavaScript

// State
let allArticles = [];
let currentFilter = 'all';

// DOM Elements
const articlesGrid = document.getElementById('articlesGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const scrapeBtn = document.getElementById('scrapeBtn');
const savedBtn = document.getElementById('savedBtn');
const lastUpdated = document.getElementById('lastUpdated');
const toastContainer = document.getElementById('toastContainer');

// Stats elements
const totalArticles = document.getElementById('totalArticles');
const bensBitesCount = document.getElementById('bensBitesCount');
const aiRundownCount = document.getElementById('aiRundownCount');
const redditCount = document.getElementById('redditCount');
const savedCount = document.getElementById('savedCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    scrapeBtn.addEventListener('click', scrapeArticles);

    // Filter tabs - use currentTarget to get the button, not the clicked child element
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const button = e.currentTarget; // Get the button, not the span inside
            const filter = button.dataset.filter;

            if (!filter) {
                console.warn('No filter attribute found on button:', button);
                return;
            }

            // Update active tab
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            button.classList.add('active');

            // Apply filter
            await filterArticles(filter);
        });
    });
}

// Load articles from API
async function loadArticles() {
    try {
        showLoading(true);

        const response = await fetch('/api/articles');
        const data = await response.json();

        allArticles = data.articles || [];

        if (allArticles.length === 0) {
            showEmptyState(true);
        } else {
            showEmptyState(false);
            renderArticles(allArticles);
            updateStats();

            if (data.last_updated) {
                const date = new Date(data.last_updated);
                lastUpdated.textContent = `Last updated: ${formatDate(date)}`;
            }
        }

    } catch (error) {
        console.error('Error loading articles:', error);
        showToast('Failed to load articles', 'error');
    } finally {
        showLoading(false);
    }
}

// Scrape new articles
async function scrapeArticles() {
    try {
        scrapeBtn.disabled = true;
        scrapeBtn.innerHTML = '<span class="icon">⏳</span><span>Scraping...</span>';

        showToast('Scraping articles from all sources...', 'info');

        const response = await fetch('/api/scrape', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.status === 'success') {
            showToast(`Found ${data.articles_found} new articles!`, 'success');
            await loadArticles();
        } else {
            showToast('Scraping failed', 'error');
        }

    } catch (error) {
        console.error('Error scraping:', error);
        showToast('Failed to scrape articles', 'error');
    } finally {
        scrapeBtn.disabled = false;
        scrapeBtn.innerHTML = '<span class="icon">🔄</span><span>Refresh News</span>';
    }
}

// Filter articles
async function filterArticles(filter) {
    currentFilter = filter;

    // If filtering by saved, load from API
    if (filter === 'saved') {
        try {
            showLoading(true);
            const response = await fetch('/api/saved');
            const data = await response.json();

            const savedArticles = data.articles || [];

            if (savedArticles.length === 0) {
                showEmptyState(true);
                articlesGrid.innerHTML = '';
            } else {
                showEmptyState(false);
                renderArticles(savedArticles);
            }
            showLoading(false);
        } catch (error) {
            console.error('Error loading saved articles:', error);
            showToast('Failed to load saved articles', 'error');
            showLoading(false);
        }
        return;
    }

    // Filter from all articles for other filters
    let filtered = allArticles;

    if (filter !== 'all') {
        filtered = allArticles.filter(a => a.source === filter);
    }

    if (filtered.length === 0) {
        showEmptyState(true);
        articlesGrid.innerHTML = '';
    } else {
        showEmptyState(false);
        renderArticles(filtered);
    }
}

// Render articles
function renderArticles(articles) {
    articlesGrid.innerHTML = '';

    articles.forEach(article => {
        const card = createArticleCard(article);
        articlesGrid.appendChild(card);
    });
}

// Create article card
function createArticleCard(article) {
    const card = document.createElement('div');
    card.className = 'article-card';
    card.setAttribute('data-id', article.id);

    const sourceLabel = getSourceLabel(article.source);
    const sourceIcon = getSourceIcon(article.source);

    card.innerHTML = `
        <div class="article-header">
            <span class="article-source">
                ${sourceIcon} ${sourceLabel}
            </span>
            <button class="save-btn ${article.is_saved ? 'saved' : ''}" 
                    onclick="toggleSave('${article.id}')"
                    aria-label="Save article">
                ${article.is_saved ? '⭐' : '☆'}
            </button>
        </div>
        
        <h3 class="article-title">
            <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                ${escapeHtml(article.title)}
            </a>
        </h3>
        
        <p class="article-summary">
            ${escapeHtml(article.summary)}
        </p>
        
        <div class="article-footer">
            <span class="article-meta">
                ${formatDate(new Date(article.published_at))}
            </span>
            <a href="${article.url}" class="article-link" target="_blank" rel="noopener noreferrer">
                Read More →
            </a>
        </div>
    `;

    return card;
}

// Toggle save/unsave
async function toggleSave(articleId) {
    const article = allArticles.find(a => a.id === articleId);
    if (!article) return;

    try {
        const endpoint = article.is_saved ? `/api/unsave/${articleId}` : `/api/save/${articleId}`;

        const response = await fetch(endpoint, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.status === 'success') {
            article.is_saved = !article.is_saved;

            // Update the card
            const card = document.querySelector(`[data-id="${articleId}"]`);
            if (card) {
                const saveBtn = card.querySelector('.save-btn');
                saveBtn.textContent = article.is_saved ? '⭐' : '☆';
                saveBtn.classList.toggle('saved', article.is_saved);
            }

            updateStats();

            showToast(
                article.is_saved ? 'Article saved!' : 'Article unsaved',
                'success'
            );

            // If we're in the saved filter, refresh the view
            if (currentFilter === 'saved') {
                await filterArticles('saved');
            }
        }

    } catch (error) {
        console.error('Error toggling save:', error);
        showToast('Failed to save article', 'error');
    }
}

// Update statistics
function updateStats() {
    totalArticles.textContent = allArticles.length;

    bensBitesCount.textContent = allArticles.filter(a => a.source === 'bens_bites').length;
    aiRundownCount.textContent = allArticles.filter(a => a.source === 'ai_rundown').length;
    redditCount.textContent = allArticles.filter(a => a.source === 'reddit').length;
    savedCount.textContent = allArticles.filter(a => a.is_saved).length;
}

// Helper functions
function getSourceLabel(source) {
    const labels = {
        'bens_bites': "Ben's Bites",
        'ai_rundown': 'AI Rundown',
        'reddit': 'Reddit'
    };
    return labels[source] || source;
}

function getSourceIcon(source) {
    const icons = {
        'bens_bites': '🔥',
        'ai_rundown': '⚡',
        'reddit': '💬'
    };
    return icons[source] || '📰';
}

function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading(show) {
    loadingState.style.display = show ? 'block' : 'none';
}

function showEmptyState(show) {
    emptyState.style.display = show ? 'block' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Make toggleSave available globally
window.toggleSave = toggleSave;
