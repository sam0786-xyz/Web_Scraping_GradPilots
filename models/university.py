"""
University data model
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json
import hashlib


@dataclass
class University:
    """University-level data model"""
    name: str
    id: str = ""
    name_arabic: Optional[str] = None
    emirate: Optional[str] = None
    city: Optional[str] = None
    country: str = "United Arab Emirates"
    institution_type: Optional[str] = None  # Public/Private
    accreditation_status: Optional[str] = None  # Licensed/Licensure Revoked
    ranking: Optional[str] = None
    ranking_tier: Optional[str] = None  # e.g., "Top 5%"
    rating: Optional[float] = None
    review_count: Optional[int] = None
    website: Optional[str] = None
    caa_guid: Optional[str] = None  # CAA reference ID
    total_programs: int = 0
    bachelor_programs: int = 0
    master_programs: int = 0
    scholarships_available: int = 0
    attendance_options: List[str] = field(default_factory=list)  # On-campus, Online, Blended
    source: str = ""  # Which scraper found this
    courses: List = field(default_factory=list)
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate a unique ID based on university name"""
        name_clean = self.name.lower().strip()
        return hashlib.md5(name_clean.encode()).hexdigest()[:12]
    
    def to_dict(self, include_courses: bool = False) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = {
            "id": self.id,
            "name": self.name,
            "name_arabic": self.name_arabic,
            "emirate": self.emirate,
            "city": self.city,
            "country": self.country,
            "institution_type": self.institution_type,
            "accreditation_status": self.accreditation_status,
            "ranking": self.ranking,
            "ranking_tier": self.ranking_tier,
            "rating": self.rating,
            "review_count": self.review_count,
            "website": self.website,
            "caa_guid": self.caa_guid,
            "total_programs": self.total_programs,
            "bachelor_programs": self.bachelor_programs,
            "master_programs": self.master_programs,
            "scholarships_available": self.scholarships_available,
            "attendance_options": self.attendance_options,
            "source": self.source,
        }
        if include_courses:
            data["courses"] = [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.courses]
        return data
    
    def to_flat_dict(self) -> Dict:
        """Convert to flat dictionary for CSV export"""
        return {
            "id": self.id,
            "name": self.name,
            "name_arabic": self.name_arabic or "",
            "emirate": self.emirate or "",
            "city": self.city or "",
            "country": self.country,
            "institution_type": self.institution_type or "",
            "accreditation_status": self.accreditation_status or "",
            "ranking": self.ranking or "",
            "ranking_tier": self.ranking_tier or "",
            "rating": self.rating if self.rating else "",
            "review_count": self.review_count if self.review_count else "",
            "website": self.website or "",
            "caa_guid": self.caa_guid or "",
            "total_programs": self.total_programs,
            "bachelor_programs": self.bachelor_programs,
            "master_programs": self.master_programs,
            "scholarships_available": self.scholarships_available,
            "attendance_options": ", ".join(self.attendance_options) if self.attendance_options else "",
            "source": self.source,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def merge_with(self, other: 'University'):
        """Merge data from another University object (fill missing fields)"""
        if not self.name_arabic and other.name_arabic:
            self.name_arabic = other.name_arabic
        if not self.emirate and other.emirate:
            self.emirate = other.emirate
        if not self.city and other.city:
            self.city = other.city
        if not self.institution_type and other.institution_type:
            self.institution_type = other.institution_type
        if not self.accreditation_status and other.accreditation_status:
            self.accreditation_status = other.accreditation_status
        if not self.ranking and other.ranking:
            self.ranking = other.ranking
        if not self.ranking_tier and other.ranking_tier:
            self.ranking_tier = other.ranking_tier
        if not self.rating and other.rating:
            self.rating = other.rating
        if not self.review_count and other.review_count:
            self.review_count = other.review_count
        if not self.website and other.website:
            self.website = other.website
        if not self.caa_guid and other.caa_guid:
            self.caa_guid = other.caa_guid
        if other.total_programs > self.total_programs:
            self.total_programs = other.total_programs
        if other.bachelor_programs > self.bachelor_programs:
            self.bachelor_programs = other.bachelor_programs
        if other.scholarships_available > self.scholarships_available:
            self.scholarships_available = other.scholarships_available
        if other.attendance_options:
            self.attendance_options = list(set(self.attendance_options + other.attendance_options))
        if other.source and other.source not in self.source:
            self.source = f"{self.source}, {other.source}" if self.source else other.source
