"""
Course data model
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import hashlib


@dataclass
class Course:
    """Course/Programme data model"""
    name: str
    university_id: str
    university_name: str = ""
    id: str = ""
    degree_level: str = "Bachelor"  # Bachelor, Master, PhD, etc.
    field_of_study: Optional[str] = None
    duration: Optional[str] = None  # e.g., "3 years", "4 years"
    duration_months: Optional[int] = None
    study_mode: Optional[str] = None  # Full-time, Part-time
    delivery_format: Optional[str] = None  # On-campus, Online, Blended
    tuition_fee: Optional[str] = None  # e.g., "50,000 AED"
    tuition_fee_value: Optional[float] = None
    tuition_currency: str = "AED"
    tuition_period: Optional[str] = None  # Per year, Total
    language: str = "English"
    accredited: bool = True
    start_dates: Optional[str] = None
    application_deadline: Optional[str] = None
    source: str = ""
    url: Optional[str] = None
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate a unique ID based on course name and university"""
        combined = f"{self.name.lower().strip()}_{self.university_id}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "university_id": self.university_id,
            "university_name": self.university_name,
            "degree_level": self.degree_level,
            "field_of_study": self.field_of_study,
            "duration": self.duration,
            "duration_months": self.duration_months,
            "study_mode": self.study_mode,
            "delivery_format": self.delivery_format,
            "tuition_fee": self.tuition_fee,
            "tuition_fee_value": self.tuition_fee_value,
            "tuition_currency": self.tuition_currency,
            "tuition_period": self.tuition_period,
            "language": self.language,
            "accredited": self.accredited,
            "start_dates": self.start_dates,
            "application_deadline": self.application_deadline,
            "source": self.source,
            "url": self.url,
        }
    
    def to_flat_dict(self) -> Dict:
        """Convert to flat dictionary for CSV export"""
        return {
            "id": self.id,
            "name": self.name,
            "university_id": self.university_id,
            "university_name": self.university_name,
            "degree_level": self.degree_level,
            "field_of_study": self.field_of_study or "",
            "duration": self.duration or "",
            "duration_months": self.duration_months if self.duration_months else "",
            "study_mode": self.study_mode or "",
            "delivery_format": self.delivery_format or "",
            "tuition_fee": self.tuition_fee or "",
            "tuition_fee_value": self.tuition_fee_value if self.tuition_fee_value else "",
            "tuition_currency": self.tuition_currency,
            "tuition_period": self.tuition_period or "",
            "language": self.language,
            "accredited": "Yes" if self.accredited else "No",
            "start_dates": self.start_dates or "",
            "application_deadline": self.application_deadline or "",
            "source": self.source,
            "url": self.url or "",
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
