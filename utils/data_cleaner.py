"""
Data cleaning utilities
"""

import re
from typing import List, Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.university import University
from models.course import Course


class DataCleaner:
    """Utilities for cleaning and normalizing scraped data"""
    
    # Emirates in UAE
    EMIRATES = [
        "Abu Dhabi",
        "Dubai", 
        "Sharjah",
        "Ajman",
        "Fujairah",
        "Ras Al Khaimah",
        "Umm Al Quwain",
    ]
    
    # Common university name variations to normalize
    NAME_NORMALIZATIONS = {
        "uae university": "United Arab Emirates University",
        "aud": "American University in Dubai",
        "aus": "American University of Sharjah",
        "nyu abu dhabi": "New York University, Abu Dhabi",
        "bits pilani": "Birla Institute of Technology & Science, Pilani, Dubai",
    }
    
    @classmethod
    def clean_university_name(cls, name: str) -> str:
        """Clean and normalize university name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        cleaned = " ".join(name.split())
        
        # Remove common suffixes that clutter the name
        patterns_to_remove = [
            r'\s*\(formerly:.*?\)',
            r'\s*\(licensure revoked\)',
            r'\s*\(.*campus\)',
        ]
        
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.I)
        
        # Check for known normalizations
        name_lower = cleaned.lower()
        if name_lower in cls.NAME_NORMALIZATIONS:
            return cls.NAME_NORMALIZATIONS[name_lower]
        
        return cleaned.strip()
    
    @classmethod
    def extract_emirate(cls, text: str) -> Optional[str]:
        """Extract emirate name from text"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        for emirate in cls.EMIRATES:
            if emirate.lower() in text_lower:
                return emirate
        
        # Handle abbreviations
        if "rak" in text_lower or "r.a.k" in text_lower:
            return "Ras Al Khaimah"
        if "uaq" in text_lower:
            return "Umm Al Quwain"
        
        return None
    
    @classmethod
    def normalize_fee(cls, fee_str: str) -> Dict[str, Any]:
        """Normalize fee string to structured data"""
        result = {
            "value": None,
            "currency": "AED",
            "period": None,
            "original": fee_str,
        }
        
        if not fee_str:
            return result
        
        # Detect currency
        if "USD" in fee_str.upper() or "$" in fee_str:
            result["currency"] = "USD"
        elif "EUR" in fee_str.upper() or "€" in fee_str:
            result["currency"] = "EUR"
        
        # Extract numeric value
        numbers = re.findall(r'[\d,]+\.?\d*', fee_str.replace(',', ''))
        if numbers:
            try:
                result["value"] = float(numbers[0])
            except ValueError:
                pass
        
        # Detect period
        fee_lower = fee_str.lower()
        if "year" in fee_lower or "annual" in fee_lower:
            result["period"] = "per year"
        elif "month" in fee_lower:
            result["period"] = "per month"
        elif "semester" in fee_lower:
            result["period"] = "per semester"
        elif "total" in fee_lower:
            result["period"] = "total"
        
        return result
    
    @classmethod
    def merge_universities(cls, uni_lists: List[List[University]]) -> List[University]:
        """Merge university lists from multiple sources, combining duplicates"""
        # Create a lookup by normalized name
        merged = {}
        
        for uni_list in uni_lists:
            for uni in uni_list:
                # Create a key for matching
                key = cls._create_university_key(uni.name)
                
                if key in merged:
                    # Merge with existing
                    merged[key].merge_with(uni)
                else:
                    # Add new
                    merged[key] = uni
        
        return list(merged.values())
    
    @classmethod
    def _create_university_key(cls, name: str) -> str:
        """Create a normalized key for university matching"""
        if not name:
            return ""
        
        # Lowercase and remove common words
        key = name.lower()
        
        # Remove common words that don't help with matching
        stop_words = ["university", "college", "institute", "of", "the", "in", "for", "and", "&"]
        words = key.split()
        words = [w for w in words if w not in stop_words]
        
        # Remove non-alphanumeric characters
        key = "".join(w for w in "".join(words) if w.isalnum())
        
        return key
    
    @classmethod
    def deduplicate_courses(cls, courses: List[Course]) -> List[Course]:
        """Remove duplicate courses"""
        seen = set()
        unique = []
        
        for course in courses:
            # Create a key for matching
            key = (
                course.name.lower().strip(),
                course.university_id,
                course.degree_level,
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(course)
        
        return unique
    
    @classmethod
    def validate_university(cls, uni: University) -> List[str]:
        """Validate university data and return list of issues"""
        issues = []
        
        if not uni.name:
            issues.append("Missing university name")
        
        if uni.rating and (uni.rating < 0 or uni.rating > 5):
            issues.append(f"Invalid rating: {uni.rating}")
        
        if uni.accreditation_status and "revoked" in uni.accreditation_status.lower():
            issues.append("Licensure revoked")
        
        return issues
    
    @classmethod
    def validate_course(cls, course: Course) -> List[str]:
        """Validate course data and return list of issues"""
        issues = []
        
        if not course.name:
            issues.append("Missing course name")
        
        if not course.university_id:
            issues.append("Missing university reference")
        
        if course.tuition_fee_value and course.tuition_fee_value < 0:
            issues.append(f"Invalid tuition fee: {course.tuition_fee_value}")
        
        return issues
