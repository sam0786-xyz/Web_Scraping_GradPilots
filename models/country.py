"""
Country data model for UAE education data
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json


@dataclass
class CostOfLiving:
    """Monthly cost of living estimates in AED"""
    accommodation_min: float = 3500.0
    accommodation_max: float = 6000.0
    food_min: float = 500.0
    food_max: float = 1200.0
    transport_min: float = 350.0
    transport_max: float = 500.0
    utilities_min: float = 300.0
    utilities_max: float = 600.0
    total_min: float = 4500.0
    total_max: float = 6500.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TuitionRange:
    """Annual tuition fee ranges in AED"""
    undergraduate_min: float = 25000.0
    undergraduate_max: float = 75000.0
    postgraduate_min: float = 30000.0
    postgraduate_max: float = 120000.0
    currency: str = "AED"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Country:
    """Country-level data model for UAE"""
    name: str = "United Arab Emirates"
    code: str = "UAE"
    region: str = "Middle East"
    currency: str = "AED"
    currency_symbol: str = "د.إ"
    cost_of_living: CostOfLiving = field(default_factory=CostOfLiving)
    tuition_range: TuitionRange = field(default_factory=TuitionRange)
    total_universities: int = 0
    total_courses: int = 0
    universities: List = field(default_factory=list)
    data_sources: List[str] = field(default_factory=lambda: [
        "https://www.caa.ae/Pages/Institutes/All.aspx",
        "https://www.bachelorsportal.com/search/universities/bachelor/united-arab-emirates",
        "https://www.universityliving.com/blog/student-finances/cost-of-living-in-dubai/"
    ])
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "code": self.code,
            "region": self.region,
            "currency": self.currency,
            "currency_symbol": self.currency_symbol,
            "cost_of_living": self.cost_of_living.to_dict(),
            "tuition_range": self.tuition_range.to_dict(),
            "total_universities": self.total_universities,
            "total_courses": self.total_courses,
            "data_sources": self.data_sources,
            "scraped_at": self.scraped_at,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def update_counts(self, universities: List, courses: List):
        """Update university and course counts"""
        self.total_universities = len(universities)
        self.total_courses = len(courses)
