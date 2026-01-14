"""
BachelorsPortal Scraper
Scrapes university rankings, ratings, and course listings from BachelorsPortal
"""

import re
import time
import random
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from tqdm import tqdm

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from models.university import University
from models.course import Course
from config import URLS, DELAYS, SELENIUM_HEADLESS, SELENIUM_PAGE_LOAD_TIMEOUT


class BachelorsPortalScraper(BaseScraper):
    """Scraper for BachelorsPortal website"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__(name="BachelorsPortalScraper", delay=DELAYS["bachelorsportal"])
        self.universities_url = URLS["bachelorsportal_universities"]
        self.programmes_url = URLS["bachelorsportal_programmes"]
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        
        if self.use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Set up Selenium WebDriver"""
        try:
            options = Options()
            if SELENIUM_HEADLESS:
                options.add_argument("--headless=new")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(f"user-agent={self._get_random_user_agent()}")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(SELENIUM_PAGE_LOAD_TIMEOUT)
            
            # Execute script to remove webdriver property
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            self.logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
    
    def _selenium_get(self, url: str) -> Optional[str]:
        """Fetch page using Selenium and return HTML"""
        if not self.driver:
            return None
        
        try:
            self._wait()
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(random.uniform(2, 4))
            
            # Scroll to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Selenium fetch failed for {url}: {e}")
            return None
    
    def scrape(self) -> Dict[str, Any]:
        """Main scraping method"""
        self.logger.info("Starting BachelorsPortal scraper...")
        
        # Scrape universities
        universities = self._scrape_universities()
        self.logger.info(f"Found {len(universities)} universities")
        
        # Scrape programmes/courses
        courses = self._scrape_programmes()
        self.logger.info(f"Found {len(courses)} courses")
        
        # Link courses to universities
        self._link_courses_to_universities(universities, courses)
        
        return {
            "universities": universities,
            "courses": courses,
        }
    
    def _scrape_universities(self) -> List[University]:
        """Scrape university listings"""
        universities = []
        page = 1
        max_pages = 5  # Limit to avoid excessive scraping
        
        while page <= max_pages:
            url = f"{self.universities_url}?page={page}" if page > 1 else self.universities_url
            self.logger.info(f"Scraping universities page {page}...")
            
            # Try Selenium first, fall back to requests
            html = None
            if self.use_selenium:
                html = self._selenium_get(url)
            
            if html:
                soup = BeautifulSoup(html, "lxml")
            else:
                soup = self.get_soup(url)
            
            if not soup:
                self.logger.warning(f"Failed to fetch page {page}")
                break
            
            page_universities = self._parse_university_cards(soup)
            
            if not page_universities:
                self.logger.info(f"No more universities found on page {page}")
                break
            
            universities.extend(page_universities)
            
            # Check for next page
            if not self._has_next_page(soup):
                break
            
            page += 1
        
        return universities
    
    def _parse_university_cards(self, soup: BeautifulSoup) -> List[University]:
        """Parse university cards from search results"""
        universities = []
        
        # Find university card elements
        # Look for common card patterns
        cards = soup.find_all("div", class_=re.compile(r"card|result|item", re.I))
        
        if not cards:
            # Try alternative selectors
            cards = soup.find_all("article")
        
        if not cards:
            # Try finding by link patterns
            links = soup.find_all("a", href=re.compile(r"/universities/"))
            for link in links:
                name = self.clean_text(link.get_text())
                if name and len(name) > 3:
                    uni = University(
                        name=name,
                        source="BachelorsPortal",
                    )
                    universities.append(uni)
            return universities
        
        for card in cards:
            try:
                uni = self._parse_single_university_card(card)
                if uni:
                    universities.append(uni)
            except Exception as e:
                self.logger.debug(f"Error parsing card: {e}")
                continue
        
        return universities
    
    def _parse_single_university_card(self, card) -> Optional[University]:
        """Parse a single university card"""
        # Find university name
        name_elem = card.find(["h2", "h3", "h4", "a"], class_=re.compile(r"title|name", re.I))
        if not name_elem:
            name_elem = card.find("a", href=re.compile(r"/universities/"))
        
        if not name_elem:
            return None
        
        name = self.clean_text(name_elem.get_text())
        if not name or len(name) < 3:
            return None
        
        # Find location
        location = None
        city = None
        location_elem = card.find(class_=re.compile(r"location|city", re.I))
        if location_elem:
            location = self.clean_text(location_elem.get_text())
            # Extract city/emirate
            if location:
                parts = location.split(",")
                if parts:
                    city = parts[0].strip()
        
        # Find institution type
        inst_type = None
        type_elem = card.find(text=re.compile(r"public|private", re.I))
        if type_elem:
            if "public" in str(type_elem).lower():
                inst_type = "Public"
            elif "private" in str(type_elem).lower():
                inst_type = "Private"
        
        # Find rating
        rating = None
        rating_elem = card.find(class_=re.compile(r"rating|score|star", re.I))
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating = self.extract_number(rating_text)
        
        # Find ranking
        ranking = None
        ranking_tier = None
        ranking_elem = card.find(text=re.compile(r"top\s*\d+%|rank", re.I))
        if ranking_elem:
            ranking_text = str(ranking_elem)
            if "%" in ranking_text:
                ranking_tier = self.clean_text(ranking_text)
        
        # Find program counts
        bachelor_count = 0
        program_elem = card.find(text=re.compile(r"\d+\s*bachelor", re.I))
        if program_elem:
            numbers = re.findall(r"(\d+)", str(program_elem))
            if numbers:
                bachelor_count = int(numbers[0])
        
        # Find scholarships
        scholarships = 0
        scholarship_elem = card.find(text=re.compile(r"\d+\s*scholarship", re.I))
        if scholarship_elem:
            numbers = re.findall(r"(\d+)", str(scholarship_elem))
            if numbers:
                scholarships = int(numbers[0])
        
        # Find attendance options
        attendance = []
        if card.find(text=re.compile(r"on.?campus", re.I)):
            attendance.append("On-campus")
        if card.find(text=re.compile(r"online", re.I)):
            attendance.append("Online")
        if card.find(text=re.compile(r"blended|hybrid", re.I)):
            attendance.append("Blended")
        
        return University(
            name=name,
            city=city,
            emirate=city,  # Often the same for UAE
            institution_type=inst_type,
            rating=rating,
            ranking_tier=ranking_tier,
            bachelor_programs=bachelor_count,
            scholarships_available=scholarships,
            attendance_options=attendance,
            source="BachelorsPortal",
        )
    
    def _scrape_programmes(self) -> List[Course]:
        """Scrape programme/course listings"""
        courses = []
        page = 1
        max_pages = 10  # Limit to avoid excessive scraping
        
        while page <= max_pages:
            url = f"{self.programmes_url}?page={page}" if page > 1 else self.programmes_url
            self.logger.info(f"Scraping programmes page {page}...")
            
            # Try Selenium first
            html = None
            if self.use_selenium:
                html = self._selenium_get(url)
            
            if html:
                soup = BeautifulSoup(html, "lxml")
            else:
                soup = self.get_soup(url)
            
            if not soup:
                self.logger.warning(f"Failed to fetch programmes page {page}")
                break
            
            page_courses = self._parse_programme_cards(soup)
            
            if not page_courses:
                self.logger.info(f"No more programmes found on page {page}")
                break
            
            courses.extend(page_courses)
            
            if not self._has_next_page(soup):
                break
            
            page += 1
        
        return courses
    
    def _parse_programme_cards(self, soup: BeautifulSoup) -> List[Course]:
        """Parse programme cards from search results"""
        courses = []
        
        # Find programme card elements
        cards = soup.find_all("div", class_=re.compile(r"card|result|item|programme", re.I))
        
        if not cards:
            cards = soup.find_all("article")
        
        for card in cards:
            try:
                course = self._parse_single_programme_card(card)
                if course:
                    courses.append(course)
            except Exception as e:
                self.logger.debug(f"Error parsing programme card: {e}")
                continue
        
        return courses
    
    def _parse_single_programme_card(self, card) -> Optional[Course]:
        """Parse a single programme card"""
        # Find course name
        name_elem = card.find(["h2", "h3", "h4", "a"], class_=re.compile(r"title|name", re.I))
        if not name_elem:
            name_elem = card.find("a", href=re.compile(r"/studies/"))
        
        if not name_elem:
            return None
        
        name = self.clean_text(name_elem.get_text())
        if not name or len(name) < 3:
            return None
        
        # Find university name
        uni_name = ""
        uni_elem = card.find(class_=re.compile(r"university|institution|provider", re.I))
        if uni_elem:
            uni_name = self.clean_text(uni_elem.get_text())
        
        # Find duration
        duration = None
        duration_months = None
        duration_elem = card.find(text=re.compile(r"\d+\s*(year|month)", re.I))
        if duration_elem:
            duration = self.clean_text(str(duration_elem))
            # Extract months
            years_match = re.search(r"(\d+)\s*year", str(duration_elem), re.I)
            months_match = re.search(r"(\d+)\s*month", str(duration_elem), re.I)
            if years_match:
                duration_months = int(years_match.group(1)) * 12
            if months_match:
                duration_months = (duration_months or 0) + int(months_match.group(1))
        
        # Find study mode
        study_mode = None
        if card.find(text=re.compile(r"full.?time", re.I)):
            study_mode = "Full-time"
        elif card.find(text=re.compile(r"part.?time", re.I)):
            study_mode = "Part-time"
        
        # Find delivery format
        delivery = None
        if card.find(text=re.compile(r"on.?campus", re.I)):
            delivery = "On-campus"
        elif card.find(text=re.compile(r"online", re.I)):
            delivery = "Online"
        elif card.find(text=re.compile(r"blended|hybrid", re.I)):
            delivery = "Blended"
        
        # Find tuition fee
        tuition = None
        tuition_value = None
        fee_elem = card.find(text=re.compile(r"(AED|USD|EUR|\$|€)\s*[\d,]+", re.I))
        if fee_elem:
            tuition = self.clean_text(str(fee_elem))
            tuition_value = self.extract_number(str(fee_elem))
        
        # Determine degree level from name
        degree_level = "Bachelor"
        if any(term in name.lower() for term in ["master", "mba", "msc"]):
            degree_level = "Master"
        elif any(term in name.lower() for term in ["phd", "doctorate"]):
            degree_level = "PhD"
        
        # Generate a temporary university ID (will be linked later)
        temp_uni_id = ""
        if uni_name:
            import hashlib
            temp_uni_id = hashlib.md5(uni_name.lower().encode()).hexdigest()[:12]
        
        return Course(
            name=name,
            university_id=temp_uni_id,
            university_name=uni_name,
            degree_level=degree_level,
            duration=duration,
            duration_months=duration_months,
            study_mode=study_mode,
            delivery_format=delivery,
            tuition_fee=tuition,
            tuition_fee_value=tuition_value,
            source="BachelorsPortal",
        )
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if there's a next page"""
        next_btn = soup.find("a", text=re.compile(r"next|→|›", re.I))
        if next_btn:
            return True
        
        # Check pagination
        pagination = soup.find(class_=re.compile(r"pagination", re.I))
        if pagination:
            current = pagination.find(class_=re.compile(r"active|current", re.I))
            if current:
                next_sibling = current.find_next_sibling("a")
                return next_sibling is not None
        
        return False
    
    def _link_courses_to_universities(self, universities: List[University], 
                                       courses: List[Course]):
        """Link courses to their universities"""
        # Create university lookup by name
        uni_lookup = {}
        for uni in universities:
            # Normalize name for matching
            name_key = uni.name.lower().strip()
            uni_lookup[name_key] = uni
            
            # Also add partial matches
            words = name_key.split()
            if len(words) > 1:
                uni_lookup[" ".join(words[:2])] = uni
        
        # Update courses with correct university IDs
        for course in courses:
            if course.university_name:
                name_key = course.university_name.lower().strip()
                
                # Try exact match
                if name_key in uni_lookup:
                    course.university_id = uni_lookup[name_key].id
                    continue
                
                # Try partial match
                for key, uni in uni_lookup.items():
                    if key in name_key or name_key in key:
                        course.university_id = uni.id
                        break
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        super().__exit__(exc_type, exc_val, exc_tb)
