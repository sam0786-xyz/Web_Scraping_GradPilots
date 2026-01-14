"""
CAA (Commission for Academic Accreditation) Scraper
FAST version - scrapes main list only without detail pages
"""

import re
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import hashlib

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from config import URLS, DELAYS, CAA_SCRAPE_DETAILS, CAA_MAX_INSTITUTIONS


class CAAScraper(BaseScraper):
    """Fast scraper for CAA (Commission for Academic Accreditation) website"""
    
    def __init__(self, fast_mode: bool = True):
        super().__init__(name="CAAScraper", delay=DELAYS["caa"])
        self.base_url = "https://www.caa.ae"
        self.institutions_url = URLS["caa_institutions"]
        self.fast_mode = fast_mode
    
    def scrape(self) -> Dict[str, Any]:
        """Main scraping method - FAST mode by default"""
        self.logger.info("Starting CAA scraper (fast mode)...")
        
        # Get list of all institutions from main page
        universities = self._scrape_institutions_list()
        self.logger.info(f"Scraped {len(universities)} universities from CAA")
        
        return {
            "universities": universities,
            "courses": [],  # CAA doesn't expose course details in a scrapable format
        }
    
    def _scrape_institutions_list(self) -> List[Dict]:
        """Scrape the main institutions list page - FAST"""
        soup = self.get_soup(self.institutions_url)
        if not soup:
            self.logger.error("Failed to fetch institutions list")
            return []
        
        universities = []
        
        # Find all institution links
        links = soup.find_all("a", href=re.compile(r"/Pages/Institutes/Details\.aspx\?GUID="))
        
        for link in links:
            name = self.clean_text(link.get_text())
            href = link.get("href", "")
            
            if not name or not href:
                continue
            
            # Extract GUID from URL
            guid_match = re.search(r"GUID=(\d+)", href)
            guid = guid_match.group(1) if guid_match else None
            
            # Check if licensure is revoked
            is_revoked = "LICENSURE REVOKED" in name.upper()
            
            # Clean the name
            clean_name = re.sub(r'\s*\(LICENSURE REVOKED\)\s*', '', name, flags=re.IGNORECASE)
            
            # Detect emirate from name
            emirate = self._detect_emirate(name)
            
            # Generate ID
            uni_id = hashlib.md5(clean_name.lower().encode()).hexdigest()[:12]
            
            universities.append({
                "id": uni_id,
                "name": clean_name.strip(),
                "name_arabic": None,
                "emirate": emirate,
                "city": emirate,
                "country": "United Arab Emirates",
                "institution_type": None,
                "accreditation_status": "Licensure Revoked" if is_revoked else "Licensed",
                "ranking": None,
                "ranking_tier": None,
                "rating": None,
                "review_count": None,
                "website": None,
                "caa_guid": guid,
                "total_programs": 0,
                "source": "CAA",
            })
        
        # Remove duplicates based on GUID
        seen_guids = set()
        unique_universities = []
        for uni in universities:
            if uni["caa_guid"] and uni["caa_guid"] not in seen_guids:
                seen_guids.add(uni["caa_guid"])
                unique_universities.append(uni)
        
        # Apply limit if set
        if CAA_MAX_INSTITUTIONS:
            unique_universities = unique_universities[:CAA_MAX_INSTITUTIONS]
        
        return unique_universities
    
    def _detect_emirate(self, name: str) -> str:
        """Detect emirate from university name"""
        name_lower = name.lower()
        
        if "dubai" in name_lower:
            return "Dubai"
        elif "abu dhabi" in name_lower or "abu-dhabi" in name_lower:
            return "Abu Dhabi"
        elif "sharjah" in name_lower:
            return "Sharjah"
        elif "ajman" in name_lower:
            return "Ajman"
        elif "fujairah" in name_lower:
            return "Fujairah"
        elif "ras al khaimah" in name_lower or "rak" in name_lower:
            return "Ras Al Khaimah"
        elif "umm al quwain" in name_lower:
            return "Umm Al Quwain"
        elif "al ain" in name_lower:
            return "Abu Dhabi"  # Al Ain is in Abu Dhabi emirate
        else:
            return "Abu Dhabi"  # Default
