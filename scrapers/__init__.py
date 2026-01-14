"""
Scrapers package for UAE University data collection
"""

from .base_scraper import BaseScraper
from .caa_scraper import CAAScraper
from .bachelorsportal_scraper import BachelorsPortalScraper
from .universityliving_scraper import UniversityLivingScraper

__all__ = [
    "BaseScraper",
    "CAAScraper", 
    "BachelorsPortalScraper",
    "UniversityLivingScraper",
]
