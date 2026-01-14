# UAE University Web Scraping Tool

A fast, comprehensive web scraping solution to collect, structure, and organize UAE university and course data from multiple public sources. Features Pydantic validation, API-ready JSON output, and Docker support.

## ⚡ Performance

- **Fast Mode**: ~3 seconds (CAA + UniversityLiving)
- **Full Mode**: ~2 minutes (includes BachelorsPortal with Selenium)

## Overview

This tool scrapes data from three mandatory sources:
1. **CAA (Commission for Academic Accreditation)** - Official UAE government portal for accredited institutions
2. **BachelorsPortal** - University rankings, ratings, and course listings (optional, requires Selenium)
3. **UniversityLiving** - Cost of living reference data for Dubai

## Tech Stack

- **Python 3.11+**
- **Pydantic** - Data validation and API-ready responses
- **BeautifulSoup4** - HTML parsing
- **Selenium** - Dynamic content handling (optional)
- **Requests** - HTTP requests

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run fast scraper (recommended)
python main.py

# Run with BachelorsPortal (slower, requires Selenium)
python main.py --selenium
```

## Project Structure

```
marketing_grad/
├── main.py                      # Main entry point
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose setup
├── scrapers/
│   ├── base_scraper.py         # Base class with HTTP handling
│   ├── caa_scraper.py          # CAA government portal (FAST)
│   ├── bachelorsportal_scraper.py  # University rankings
│   └── universityliving_scraper.py # Cost of living
├── models/
│   └── schemas.py              # Pydantic models for API responses
├── database/
│   └── schema.sql              # PostgreSQL database schema
├── utils/
│   ├── data_cleaner.py         # Data normalization
│   └── exporter.py             # JSON export
└── output/
    └── uae_education_data.json  # API-ready JSON output
```

## Output Format

Single JSON file with Pydantic-validated structure:

```json
{
  "country": {
    "name": "United Arab Emirates",
    "code": "UAE",
    "currency": "AED",
    "cost_of_living": {
      "accommodation_min": 3500.0,
      "accommodation_max": 6000.0,
      "food_min": 500.0,
      "food_max": 1200.0,
      "total_min": 4500.0,
      "total_max": 6500.0
    },
    "tuition_range": {
      "undergraduate_min": 25000.0,
      "undergraduate_max": 75000.0
    },
    "total_universities": 156
  },
  "universities": [...],
  "courses": [...],
  "metadata": {...}
}
```

## Docker Setup

### Build and Run
```bash
# Build and run scraper
docker-compose up scraper

# Run with PostgreSQL database
docker-compose up -d postgres
docker-compose up scraper
```

### Access Database
- **PostgreSQL**: `localhost:5432`
- **pgAdmin**: `localhost:5050` (admin@gradpilots.com / admin)

## Database Schema

PostgreSQL schema available in `database/schema.sql`:

- `countries` - Country information
- `universities` - Institution data with accreditation status
- `courses` - Course/programme listings
- `cost_of_living` - Monthly expense estimates
- `tuition_ranges` - Annual tuition fees
- `scraping_logs` - Job tracking

## Pydantic Models

API-ready response models in `models/schemas.py`:

```python
from models import UniversityResponse, CountryResponse

# Validated university data
university = UniversityResponse(
    id="abc123",
    name="Abu Dhabi University",
    accreditation_status="Licensed",
    emirate="Abu Dhabi"
)

# Access as dict for API response
university.model_dump()
```

## CLI Options

```bash
python main.py                # Fast mode (default)
python main.py --selenium     # Enable BachelorsPortal scraping
python main.py --debug        # Enable debug logging
```

## Data Summary

| Metric | Value |
|--------|-------|
| Total Universities | 156 |
| Licensed | 133 (85%) |
| Licensure Revoked | 22 (14%) |
| Monthly Cost (AED) | 4,500 - 6,500 |
| Annual Tuition (AED) | 25,000 - 75,000 |

## Known Limitations

1. **BachelorsPortal**: Cloudflare anti-bot protection limits data collection
2. **CAA Course Data**: Government portal is an accreditation directory, not a course catalog
3. **Rate Limiting**: Built-in delays to respect server limits

## Deliverables

✅ **Scraped Dataset**: API-ready JSON in `/output`  
✅ **Source Code**: Clean Python with Pydantic models  
✅ **README**: Complete documentation  
✅ **Database Schema**: PostgreSQL-ready SQL  
✅ **Docker Setup**: Containerized deployment  

---

*Developed for GradPilots Web Scraping Assignment*
