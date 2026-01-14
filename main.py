#!/usr/bin/env python3
"""
UAE University Web Scraping Tool
FAST version with Pydantic models and JSON-only output

Developed for GradPilots Web Scraping Assignment
"""

import argparse
import logging
import sys
import json
from datetime import datetime
from typing import List

from config import LOG_LEVEL, LOG_FORMAT, OUTPUT_DIR
from scrapers.caa_scraper import CAAScraper
from scrapers.bachelorsportal_scraper import BachelorsPortalScraper
from scrapers.universityliving_scraper import UniversityLivingScraper
from utils.exporter import DataExporter

# Import Pydantic models for validation
from models.schemas import (
    CountryResponse, 
    UniversityResponse, 
    CourseResponse,
    CostOfLivingResponse,
    TuitionRangeResponse,
    FullDataResponse,
    AccreditationStatus
)


def setup_logging(level: str = LOG_LEVEL):
    """Configure logging"""
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def scrape_caa(fast_mode: bool = True) -> dict:
    """Run CAA scraper"""
    logger = logging.getLogger("main")
    logger.info("Starting CAA Scraper (fast mode)...")
    
    try:
        with CAAScraper(fast_mode=fast_mode) as scraper:
            return scraper.scrape()
    except Exception as e:
        logger.error(f"CAA scraper failed: {e}")
        return {"universities": [], "courses": []}


def scrape_bachelorsportal(use_selenium: bool = False) -> dict:
    """Run BachelorsPortal scraper - skipped by default for speed"""
    logger = logging.getLogger("main")
    
    if not use_selenium:
        logger.info("Skipping BachelorsPortal (use --selenium to enable)")
        return {"universities": [], "courses": []}
    
    logger.info("Starting BachelorsPortal Scraper...")
    
    try:
        scraper = BachelorsPortalScraper(use_selenium=use_selenium)
        result = scraper.scrape()
        scraper.close()
        return result
    except Exception as e:
        logger.error(f"BachelorsPortal scraper failed: {e}")
        return {"universities": [], "courses": []}


def scrape_universityliving() -> dict:
    """Run University Living scraper"""
    logger = logging.getLogger("main")
    logger.info("Starting University Living Scraper...")
    
    try:
        with UniversityLivingScraper() as scraper:
            return scraper.scrape()
    except Exception as e:
        logger.error(f"University Living scraper failed: {e}")
        return {"cost_of_living": {}, "tuition_range": {}}


def validate_and_convert(caa_data: dict, bp_data: dict, ul_data: dict) -> FullDataResponse:
    """Validate data using Pydantic models and create API response"""
    logger = logging.getLogger("main")
    logger.info("Validating data with Pydantic models...")
    
    # Merge universities (CAA is primary)
    all_universities = caa_data.get("universities", []) + bp_data.get("universities", [])
    
    # Convert to Pydantic models for validation
    validated_universities = []
    for uni_data in all_universities:
        try:
            # Map accreditation status
            status = uni_data.get("accreditation_status", "Unknown")
            if status == "Licensed":
                acc_status = AccreditationStatus.LICENSED
            elif "Revoked" in status:
                acc_status = AccreditationStatus.REVOKED
            else:
                acc_status = AccreditationStatus.UNKNOWN
            
            uni = UniversityResponse(
                id=uni_data.get("id", ""),
                name=uni_data.get("name", ""),
                name_arabic=uni_data.get("name_arabic"),
                emirate=uni_data.get("emirate"),
                city=uni_data.get("city"),
                country=uni_data.get("country", "United Arab Emirates"),
                accreditation_status=acc_status,
                caa_guid=uni_data.get("caa_guid"),
                total_programs=uni_data.get("total_programs", 0),
                source=uni_data.get("source", ""),
            )
            validated_universities.append(uni.model_dump())
        except Exception as e:
            logger.warning(f"Validation failed for university: {e}")
    
    # Validate courses
    all_courses = caa_data.get("courses", []) + bp_data.get("courses", [])
    validated_courses = []
    for course_data in all_courses:
        try:
            course = CourseResponse(
                id=course_data.get("id", ""),
                name=course_data.get("name", ""),
                university_id=course_data.get("university_id", ""),
                university_name=course_data.get("university_name", ""),
                source=course_data.get("source", ""),
            )
            validated_courses.append(course.model_dump())
        except Exception as e:
            logger.warning(f"Validation failed for course: {e}")
    
    # Get cost of living data
    cost_data = ul_data.get("cost_of_living", {})
    tuition_data = ul_data.get("tuition_range", {})
    
    # Create cost of living response
    cost_of_living = CostOfLivingResponse(
        accommodation_min=getattr(cost_data, 'accommodation_min', 3500.0) if hasattr(cost_data, 'accommodation_min') else 3500.0,
        accommodation_max=getattr(cost_data, 'accommodation_max', 6000.0) if hasattr(cost_data, 'accommodation_max') else 6000.0,
        food_min=getattr(cost_data, 'food_min', 500.0) if hasattr(cost_data, 'food_min') else 500.0,
        food_max=getattr(cost_data, 'food_max', 1200.0) if hasattr(cost_data, 'food_max') else 1200.0,
        transport_min=getattr(cost_data, 'transport_min', 350.0) if hasattr(cost_data, 'transport_min') else 350.0,
        transport_max=getattr(cost_data, 'transport_max', 500.0) if hasattr(cost_data, 'transport_max') else 500.0,
        utilities_min=getattr(cost_data, 'utilities_min', 300.0) if hasattr(cost_data, 'utilities_min') else 300.0,
        utilities_max=getattr(cost_data, 'utilities_max', 600.0) if hasattr(cost_data, 'utilities_max') else 600.0,
        total_min=getattr(cost_data, 'total_min', 4500.0) if hasattr(cost_data, 'total_min') else 4500.0,
        total_max=getattr(cost_data, 'total_max', 6500.0) if hasattr(cost_data, 'total_max') else 6500.0,
    )
    
    tuition_range = TuitionRangeResponse(
        undergraduate_min=getattr(tuition_data, 'undergraduate_min', 25000.0) if hasattr(tuition_data, 'undergraduate_min') else 25000.0,
        undergraduate_max=getattr(tuition_data, 'undergraduate_max', 75000.0) if hasattr(tuition_data, 'undergraduate_max') else 75000.0,
        postgraduate_min=getattr(tuition_data, 'postgraduate_min', 30000.0) if hasattr(tuition_data, 'postgraduate_min') else 30000.0,
        postgraduate_max=getattr(tuition_data, 'postgraduate_max', 120000.0) if hasattr(tuition_data, 'postgraduate_max') else 120000.0,
    )
    
    # Create country response
    country = CountryResponse(
        cost_of_living=cost_of_living,
        tuition_range=tuition_range,
        total_universities=len(validated_universities),
        total_courses=len(validated_courses),
        data_sources=[
            "https://www.caa.ae/Pages/Institutes/All.aspx",
            "https://www.bachelorsportal.com",
            "https://www.universityliving.com"
        ],
        scraped_at=datetime.now(),
    )
    
    # Create full response
    return FullDataResponse(
        country=country,
        universities=[UniversityResponse(**u) for u in validated_universities],
        courses=[CourseResponse(**c) for c in validated_courses],
        metadata={
            "scraped_at": datetime.now().isoformat(),
            "total_universities": len(validated_universities),
            "total_courses": len(validated_courses),
            "api_version": "1.0",
        }
    )


def run_full_pipeline(use_selenium: bool = False) -> dict:
    """Run the complete scraping pipeline - FAST by default"""
    logger = logging.getLogger("main")
    
    start_time = datetime.now()
    
    logger.info("=" * 50)
    logger.info("UAE UNIVERSITY WEB SCRAPING TOOL (FAST)")
    logger.info("=" * 50)
    
    # Run scrapers
    caa_data = scrape_caa(fast_mode=True)
    bp_data = scrape_bachelorsportal(use_selenium=use_selenium)
    ul_data = scrape_universityliving()
    
    # Validate and convert to Pydantic models
    full_response = validate_and_convert(caa_data, bp_data, ul_data)
    
    # Export to JSON only
    logger.info("Exporting to JSON...")
    
    output_path = f"{OUTPUT_DIR}/uae_education_data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_response.model_dump(), f, indent=2, ensure_ascii=False, default=str)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=" * 50)
    logger.info("SCRAPING COMPLETE")
    logger.info("=" * 50)
    logger.info(f"Total Universities: {len(full_response.universities)}")
    logger.info(f"Total Courses: {len(full_response.courses)}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Output: {output_path}")
    
    return {
        "response": full_response,
        "output_path": output_path,
        "duration": duration,
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="UAE University Web Scraping Tool (FAST)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Fast mode (CAA + UniversityLiving only)
  python main.py --selenium   # Include BachelorsPortal with Selenium
  python main.py --debug      # Enable debug logging
        """
    )
    
    parser.add_argument(
        "--selenium",
        action="store_true",
        help="Enable Selenium for BachelorsPortal (slower but more data)"
    )
    
    parser.add_argument(
        "--fast", "-f",
        action="store_true",
        default=True,
        help="Fast mode (default)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else LOG_LEVEL
    setup_logging(log_level)
    
    try:
        results = run_full_pipeline(use_selenium=args.selenium)
        print(f"\n✅ Scraped {len(results['response'].universities)} universities in {results['duration']:.2f}s")
        print(f"📁 Output saved to: {results['output_path']}")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        return 1
    except Exception as e:
        logging.exception(f"❌ Scraping failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
