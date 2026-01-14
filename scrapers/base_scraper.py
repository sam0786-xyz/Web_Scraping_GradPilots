"""
Base scraper class with common functionality
"""

import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import USER_AGENTS, REQUEST_TIMEOUT, MAX_RETRIES


class BaseScraper(ABC):
    """Base class for all scrapers with common utilities"""
    
    def __init__(self, name: str, delay: float = 1.0):
        self.name = name
        self.delay = delay
        self.session = requests.Session()
        self.logger = logging.getLogger(name)
        self._setup_session()
    
    def _setup_session(self):
        """Configure session with headers"""
        self.session.headers.update({
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        return random.choice(USER_AGENTS)
    
    def _rotate_user_agent(self):
        """Rotate to a new user agent"""
        self.session.headers["User-Agent"] = self._get_random_user_agent()
    
    def _wait(self, extra_delay: float = 0):
        """Wait between requests to respect rate limits"""
        wait_time = self.delay + random.uniform(0, 1) + extra_delay
        time.sleep(wait_time)
    
    def _make_request(self, url: str, method: str = "GET", 
                      params: Dict = None, data: Dict = None,
                      retry_count: int = 0) -> Optional[requests.Response]:
        """Make an HTTP request with retry logic"""
        try:
            self._wait()
            
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(url, params=params, data=data, timeout=REQUEST_TIMEOUT)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Request failed for {url}: {e}")
            
            if retry_count < MAX_RETRIES:
                self.logger.info(f"Retrying... ({retry_count + 1}/{MAX_RETRIES})")
                self._rotate_user_agent()
                self._wait(extra_delay=2)
                return self._make_request(url, method, params, data, retry_count + 1)
            
            self.logger.error(f"Max retries exceeded for {url}")
            return None
    
    def get_soup(self, url: str, params: Dict = None) -> Optional[BeautifulSoup]:
        """Fetch URL and return BeautifulSoup object"""
        response = self._make_request(url, params=params)
        if response:
            return BeautifulSoup(response.content, "lxml")
        return None
    
    @staticmethod
    def clean_text(text: Optional[str], default: str = "") -> str:
        """Clean and normalize text"""
        if text is None:
            return default
        # Remove extra whitespace and normalize
        cleaned = " ".join(text.split())
        return cleaned.strip() if cleaned else default
    
    @staticmethod
    def extract_number(text: str) -> Optional[float]:
        """Extract numeric value from text"""
        if not text:
            return None
        # Remove currency symbols, commas, and non-numeric characters
        import re
        numbers = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
        return None
    
    @abstractmethod
    def scrape(self) -> Dict[str, Any]:
        """Main scraping method - must be implemented by subclasses"""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
