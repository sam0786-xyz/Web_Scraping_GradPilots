-- UAE University Database Schema
-- PostgreSQL compatible

-- ============================================
-- COUNTRY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    currency VARCHAR(10) DEFAULT 'AED',
    currency_symbol VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- COST OF LIVING TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS cost_of_living (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
    accommodation_min DECIMAL(10, 2),
    accommodation_max DECIMAL(10, 2),
    food_min DECIMAL(10, 2),
    food_max DECIMAL(10, 2),
    transport_min DECIMAL(10, 2),
    transport_max DECIMAL(10, 2),
    utilities_min DECIMAL(10, 2),
    utilities_max DECIMAL(10, 2),
    total_min DECIMAL(10, 2),
    total_max DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'AED',
    period VARCHAR(20) DEFAULT 'monthly',
    year INTEGER DEFAULT 2025,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_id, year)
);

-- ============================================
-- TUITION RANGES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tuition_ranges (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
    undergraduate_min DECIMAL(12, 2),
    undergraduate_max DECIMAL(12, 2),
    postgraduate_min DECIMAL(12, 2),
    postgraduate_max DECIMAL(12, 2),
    currency VARCHAR(10) DEFAULT 'AED',
    period VARCHAR(20) DEFAULT 'annual',
    year INTEGER DEFAULT 2025,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_id, year)
);

-- ============================================
-- UNIVERSITIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS universities (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_arabic VARCHAR(255),
    country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    emirate VARCHAR(50),
    city VARCHAR(100),
    institution_type VARCHAR(20) CHECK (institution_type IN ('Public', 'Private', 'Unknown')),
    accreditation_status VARCHAR(30) CHECK (accreditation_status IN ('Licensed', 'Licensure Revoked', 'Unknown')),
    ranking VARCHAR(50),
    ranking_tier VARCHAR(20),
    rating DECIMAL(2, 1) CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0,
    website TEXT,
    caa_guid VARCHAR(20),
    total_programs INTEGER DEFAULT 0,
    bachelor_programs INTEGER DEFAULT 0,
    master_programs INTEGER DEFAULT 0,
    scholarships_available INTEGER DEFAULT 0,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- COURSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS courses (
    id VARCHAR(20) PRIMARY KEY,
    university_id VARCHAR(20) REFERENCES universities(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    degree_level VARCHAR(20) CHECK (degree_level IN ('Bachelor', 'Master', 'PhD', 'Diploma', 'Associate')),
    field_of_study VARCHAR(200),
    duration VARCHAR(50),
    duration_months INTEGER,
    study_mode VARCHAR(20) CHECK (study_mode IN ('Full-time', 'Part-time', 'Online', 'Blended')),
    delivery_format VARCHAR(30),
    tuition_fee VARCHAR(100),
    tuition_fee_value DECIMAL(12, 2),
    tuition_currency VARCHAR(10) DEFAULT 'AED',
    tuition_period VARCHAR(20),
    language VARCHAR(50) DEFAULT 'English',
    accredited BOOLEAN DEFAULT TRUE,
    start_dates TEXT,
    application_deadline TEXT,
    source VARCHAR(100),
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SCRAPING LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS scraping_logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    universities_scraped INTEGER DEFAULT 0,
    courses_scraped INTEGER DEFAULT 0,
    errors TEXT[],
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_universities_country ON universities(country_id);
CREATE INDEX IF NOT EXISTS idx_universities_emirate ON universities(emirate);
CREATE INDEX IF NOT EXISTS idx_universities_status ON universities(accreditation_status);
CREATE INDEX IF NOT EXISTS idx_universities_caa_guid ON universities(caa_guid);
CREATE INDEX IF NOT EXISTS idx_universities_name ON universities(name);

CREATE INDEX IF NOT EXISTS idx_courses_university ON courses(university_id);
CREATE INDEX IF NOT EXISTS idx_courses_degree ON courses(degree_level);
CREATE INDEX IF NOT EXISTS idx_courses_field ON courses(field_of_study);
CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(name);

-- ============================================
-- INITIAL DATA
-- ============================================
INSERT INTO countries (code, name, region, currency, currency_symbol)
VALUES ('UAE', 'United Arab Emirates', 'Middle East', 'AED', 'د.إ')
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- VIEWS
-- ============================================

-- University summary view
CREATE OR REPLACE VIEW university_summary AS
SELECT 
    u.id,
    u.name,
    u.emirate,
    u.accreditation_status,
    u.institution_type,
    u.total_programs,
    u.website,
    c.name as country_name
FROM universities u
LEFT JOIN countries c ON u.country_id = c.id;

-- Accreditation statistics view
CREATE OR REPLACE VIEW accreditation_stats AS
SELECT 
    accreditation_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM universities
GROUP BY accreditation_status;

-- Emirates distribution view
CREATE OR REPLACE VIEW emirates_distribution AS
SELECT 
    COALESCE(emirate, 'Unknown') as emirate,
    COUNT(*) as university_count
FROM universities
GROUP BY emirate
ORDER BY university_count DESC;
