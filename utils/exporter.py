"""
Data export utilities - JSON only for API-ready output
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OUTPUT_DIR


class DataExporter:
    """Export data to JSON format only (API-ready)"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_all(self, country_data: dict, universities: List[dict], 
                   courses: List[dict]) -> Dict[str, str]:
        """Export all data to JSON format"""
        return self.export_to_json(country_data, universities, courses)
    
    def export_to_json(self, country_data: dict, universities: List[dict],
                       courses: List[dict]) -> Dict[str, str]:
        """Export data to JSON files"""
        files = {}
        timestamp = datetime.now().isoformat()
        
        # Prepare complete API-ready response
        complete_data = {
            "country": country_data,
            "universities": universities,
            "courses": courses,
            "metadata": {
                "total_universities": len(universities),
                "total_courses": len(courses),
                "scraped_at": timestamp,
                "version": "1.0",
                "api_ready": True,
                "sources": [
                    "https://www.caa.ae/Pages/Institutes/All.aspx",
                    "https://www.bachelorsportal.com",
                    "https://www.universityliving.com"
                ]
            }
        }
        
        # Export complete data
        complete_path = os.path.join(self.output_dir, "uae_education_data.json")
        with open(complete_path, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False, default=str)
        files["complete"] = complete_path
        
        return files
    
    def generate_summary(self, universities: List[dict], courses: List[dict]) -> dict:
        """Generate summary statistics"""
        # Count by accreditation status
        licensed = sum(1 for u in universities if u.get("accreditation_status") == "Licensed")
        revoked = sum(1 for u in universities if u.get("accreditation_status") == "Licensure Revoked")
        
        # Count by emirate
        emirates = {}
        for u in universities:
            em = u.get("emirate") or "Unknown"
            emirates[em] = emirates.get(em, 0) + 1
        
        return {
            "total_universities": len(universities),
            "total_courses": len(courses),
            "accreditation": {
                "licensed": licensed,
                "revoked": revoked
            },
            "by_emirate": emirates,
            "generated_at": datetime.now().isoformat()
        }
