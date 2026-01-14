"""
Configuration settings for the UAE University Web Scraper
Optimized for speed
"""

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Data source URLs
URLS = {
    "caa_institutions": "https://www.caa.ae/Pages/Institutes/All.aspx",
    "caa_institution_detail": "https://www.caa.ae/Pages/Institutes/Details.aspx?GUID={}",
    "bachelorsportal_universities": "https://www.bachelorsportal.com/search/universities/bachelor/united-arab-emirates",
    "bachelorsportal_programmes": "https://www.bachelorsportal.com/search/bachelor/united-arab-emirates",
    "universityliving_cost": "https://www.universityliving.com/blog/student-finances/cost-of-living-in-dubai/",
}

# Rate limiting - delays between requests (in seconds)
# FAST mode for quicker execution
DELAYS = {
    "caa": 0.3,              # Reduced delay for government site
    "bachelorsportal": 1.5,  # Still needs some delay for anti-bot
    "universityliving": 0.2, # Blog - very low delay
}

# Slow mode delays (more polite)
DELAYS_SLOW = {
    "caa": 1.0,
    "bachelorsportal": 3.0,
    "universityliving": 0.5,
}

# Request settings
REQUEST_TIMEOUT = 15  # Reduced timeout for faster failure
MAX_RETRIES = 2      # Reduced retries for speed

# User-Agent rotation for avoiding blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

# Selenium settings
SELENIUM_HEADLESS = True
SELENIUM_PAGE_LOAD_TIMEOUT = 30  # Reduced from 60

# CAA scraping settings
CAA_SCRAPE_DETAILS = False  # Set to False for faster scraping (list only)
CAA_MAX_INSTITUTIONS = None  # Set to a number to limit for testing

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Country data
COUNTRY_INFO = {
    "name": "United Arab Emirates",
    "code": "UAE",
    "region": "Middle East",
    "currency": "AED",
    "currency_symbol": "د.إ",
}

# Output format (JSON only for API-ready output)
OUTPUT_FORMAT = "json"
