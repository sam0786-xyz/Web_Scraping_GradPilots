"""
Pydantic models for API-ready responses
Clean, validated data structures for UAE University data
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AccreditationStatus(str, Enum):
    """Accreditation status enum"""
    LICENSED = "Licensed"
    REVOKED = "Licensure Revoked"
    UNKNOWN = "Unknown"


class InstitutionType(str, Enum):
    """Institution type enum"""
    PUBLIC = "Public"
    PRIVATE = "Private"
    UNKNOWN = "Unknown"


class DegreeLevel(str, Enum):
    """Degree level enum"""
    BACHELOR = "Bachelor"
    MASTER = "Master"
    PHD = "PhD"
    DIPLOMA = "Diploma"
    ASSOCIATE = "Associate"


class StudyMode(str, Enum):
    """Study mode enum"""
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    ONLINE = "Online"
    BLENDED = "Blended"


# ============== Cost of Living Models ==============

class CostOfLivingResponse(BaseModel):
    """Monthly cost of living in AED"""
    accommodation_min: float = Field(3500.0, description="Minimum monthly accommodation cost in AED")
    accommodation_max: float = Field(6000.0, description="Maximum monthly accommodation cost in AED")
    food_min: float = Field(500.0, description="Minimum monthly food cost in AED")
    food_max: float = Field(1200.0, description="Maximum monthly food cost in AED")
    transport_min: float = Field(350.0, description="Minimum monthly transport cost in AED")
    transport_max: float = Field(500.0, description="Maximum monthly transport cost in AED")
    utilities_min: float = Field(300.0, description="Minimum monthly utilities cost in AED")
    utilities_max: float = Field(600.0, description="Maximum monthly utilities cost in AED")
    total_min: float = Field(4500.0, description="Minimum total monthly cost in AED")
    total_max: float = Field(6500.0, description="Maximum total monthly cost in AED")
    currency: str = Field("AED", description="Currency code")

    class Config:
        json_schema_extra = {
            "example": {
                "accommodation_min": 3500.0,
                "accommodation_max": 6000.0,
                "food_min": 500.0,
                "food_max": 1200.0,
                "transport_min": 350.0,
                "transport_max": 500.0,
                "utilities_min": 300.0,
                "utilities_max": 600.0,
                "total_min": 4500.0,
                "total_max": 6500.0,
                "currency": "AED"
            }
        }


class TuitionRangeResponse(BaseModel):
    """Annual tuition fee ranges in AED"""
    undergraduate_min: float = Field(25000.0, description="Minimum annual undergraduate tuition in AED")
    undergraduate_max: float = Field(75000.0, description="Maximum annual undergraduate tuition in AED")
    postgraduate_min: float = Field(30000.0, description="Minimum annual postgraduate tuition in AED")
    postgraduate_max: float = Field(120000.0, description="Maximum annual postgraduate tuition in AED")
    currency: str = Field("AED", description="Currency code")

    class Config:
        json_schema_extra = {
            "example": {
                "undergraduate_min": 25000.0,
                "undergraduate_max": 75000.0,
                "postgraduate_min": 30000.0,
                "postgraduate_max": 120000.0,
                "currency": "AED"
            }
        }


# ============== Course Model ==============

class CourseResponse(BaseModel):
    """Course/Programme data model"""
    id: str = Field(..., description="Unique course identifier")
    name: str = Field(..., description="Course name")
    university_id: str = Field(..., description="Parent university ID")
    university_name: str = Field("", description="Parent university name")
    degree_level: DegreeLevel = Field(DegreeLevel.BACHELOR, description="Degree level")
    field_of_study: Optional[str] = Field(None, description="Field of study")
    duration: Optional[str] = Field(None, description="Course duration (e.g., '4 years')")
    duration_months: Optional[int] = Field(None, description="Duration in months")
    study_mode: Optional[StudyMode] = Field(None, description="Study mode")
    tuition_fee: Optional[str] = Field(None, description="Tuition fee as string")
    tuition_fee_value: Optional[float] = Field(None, description="Tuition fee numeric value")
    tuition_currency: str = Field("AED", description="Tuition currency")
    language: str = Field("English", description="Medium of instruction")
    accredited: bool = Field(True, description="Whether the course is accredited")
    source: str = Field("", description="Data source")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "name": "Bachelor of Computer Science",
                "university_id": "uni456",
                "university_name": "Abu Dhabi University",
                "degree_level": "Bachelor",
                "duration": "4 years",
                "duration_months": 48,
                "study_mode": "Full-time",
                "tuition_fee": "50,000 AED/year",
                "tuition_fee_value": 50000.0,
                "tuition_currency": "AED",
                "language": "English",
                "accredited": True,
                "source": "BachelorsPortal"
            }
        }


# ============== University Model ==============

class UniversityResponse(BaseModel):
    """University/Institution data model"""
    id: str = Field(..., description="Unique university identifier")
    name: str = Field(..., description="University name")
    name_arabic: Optional[str] = Field(None, description="Arabic name")
    emirate: Optional[str] = Field(None, description="Emirate location")
    city: Optional[str] = Field(None, description="City location")
    country: str = Field("United Arab Emirates", description="Country")
    institution_type: Optional[InstitutionType] = Field(None, description="Public or Private")
    accreditation_status: AccreditationStatus = Field(AccreditationStatus.UNKNOWN, description="CAA accreditation status")
    ranking: Optional[str] = Field(None, description="University ranking")
    ranking_tier: Optional[str] = Field(None, description="Ranking tier (e.g., 'Top 5%')")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating out of 5")
    review_count: Optional[int] = Field(None, ge=0, description="Number of reviews")
    website: Optional[str] = Field(None, description="Official website URL")
    caa_guid: Optional[str] = Field(None, description="CAA reference ID")
    total_programs: int = Field(0, ge=0, description="Total number of programs")
    source: str = Field("", description="Data source")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "24bc1f387b8a",
                "name": "Abu Dhabi University",
                "emirate": "Abu Dhabi",
                "country": "United Arab Emirates",
                "institution_type": "Private",
                "accreditation_status": "Licensed",
                "caa_guid": "14",
                "total_programs": 50,
                "source": "CAA"
            }
        }


# ============== Country Model ==============

class CountryResponse(BaseModel):
    """Country-level data model"""
    name: str = Field("United Arab Emirates", description="Country name")
    code: str = Field("UAE", description="Country code")
    region: str = Field("Middle East", description="Geographic region")
    currency: str = Field("AED", description="Currency code")
    currency_symbol: str = Field("د.إ", description="Currency symbol")
    cost_of_living: CostOfLivingResponse = Field(default_factory=CostOfLivingResponse)
    tuition_range: TuitionRangeResponse = Field(default_factory=TuitionRangeResponse)
    total_universities: int = Field(0, ge=0, description="Total number of universities")
    total_courses: int = Field(0, ge=0, description="Total number of courses")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    scraped_at: Optional[datetime] = Field(None, description="Timestamp of data collection")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "United Arab Emirates",
                "code": "UAE",
                "region": "Middle East",
                "currency": "AED",
                "total_universities": 156,
                "total_courses": 0,
                "scraped_at": "2024-01-14T21:00:00"
            }
        }


# ============== API Response Models ==============

class UniversityListResponse(BaseModel):
    """Paginated university list response"""
    total: int = Field(..., description="Total number of universities")
    page: int = Field(1, ge=1, description="Current page")
    per_page: int = Field(50, ge=1, le=100, description="Items per page")
    universities: List[UniversityResponse] = Field(default_factory=list)


class CourseListResponse(BaseModel):
    """Paginated course list response"""
    total: int = Field(..., description="Total number of courses")
    page: int = Field(1, ge=1, description="Current page")
    per_page: int = Field(50, ge=1, le=100, description="Items per page")
    courses: List[CourseResponse] = Field(default_factory=list)


class FullDataResponse(BaseModel):
    """Complete scraped data response"""
    country: CountryResponse
    universities: List[UniversityResponse]
    courses: List[CourseResponse]
    metadata: dict = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "country": {"name": "United Arab Emirates", "code": "UAE"},
                "universities": [],
                "courses": [],
                "metadata": {
                    "scraped_at": "2024-01-14T21:00:00",
                    "total_universities": 156,
                    "total_courses": 0
                }
            }
        }


class ScrapingStatusResponse(BaseModel):
    """Scraping job status response"""
    status: str = Field(..., description="Job status: pending, running, completed, failed")
    progress: float = Field(0.0, ge=0, le=100, description="Progress percentage")
    message: str = Field("", description="Status message")
    universities_scraped: int = Field(0, ge=0)
    courses_scraped: int = Field(0, ge=0)
    errors: List[str] = Field(default_factory=list)
