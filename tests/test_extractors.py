"""Unit tests for Excel job extractor."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
from src.jobcompass.extractors import ExcelJobExtractor
from src.jobcompass.models import WorkMode, JobType, ExperienceLevel


@pytest.fixture
def sample_excel_file():
    """Create a temporary Excel file with sample data."""
    data = {
        'title': ['Software Engineer', 'Data Scientist'],
        'company': ['TechCorp', 'DataCo'],
        'description': ['Build software', 'Analyze data'],
        'location': ['San Francisco', 'New York'],
        'work_mode': ['Remote', 'Hybrid'],
        'job_type': ['Full-time', 'Full-time'],
        'experience_level': ['Senior', 'Mid Level'],
        'salary_min': [120000, 100000],
        'salary_max': [180000, 150000],
        'required_skills': ['Python, JavaScript', 'Python, SQL'],
        'preferred_skills': ['React, AWS', 'Spark, Airflow']
    }
    
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.xlsx', delete=False) as f:
        df.to_excel(f.name, index=False)
        yield f.name
    
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


def test_extractor_initialization():
    """Test ExcelJobExtractor initialization."""
    extractor = ExcelJobExtractor()
    assert extractor is not None
    assert hasattr(extractor, 'column_mappings')


def test_extract_from_excel(sample_excel_file):
    """Test extracting jobs from Excel file."""
    extractor = ExcelJobExtractor()
    jobs = extractor.extract_from_excel(sample_excel_file)
    
    assert len(jobs) == 2
    assert jobs[0].title == 'Software Engineer'
    assert jobs[0].company == 'TechCorp'
    assert jobs[1].title == 'Data Scientist'
    assert jobs[1].company == 'DataCo'


def test_extract_skills_parsing(sample_excel_file):
    """Test skills parsing from Excel."""
    extractor = ExcelJobExtractor()
    jobs = extractor.extract_from_excel(sample_excel_file)
    
    job = jobs[0]
    assert 'Python' in job.required_skills
    assert 'JavaScript' in job.required_skills
    assert 'React' in job.preferred_skills
    assert 'AWS' in job.preferred_skills


def test_extract_enums(sample_excel_file):
    """Test enum parsing from Excel."""
    extractor = ExcelJobExtractor()
    jobs = extractor.extract_from_excel(sample_excel_file)
    
    job1 = jobs[0]
    assert job1.work_mode == WorkMode.REMOTE
    assert job1.job_type == JobType.FULL_TIME
    assert job1.experience_level == ExperienceLevel.SENIOR
    
    job2 = jobs[1]
    assert job2.work_mode == WorkMode.HYBRID
    assert job2.experience_level == ExperienceLevel.MID


def test_extract_salary(sample_excel_file):
    """Test salary extraction from Excel."""
    extractor = ExcelJobExtractor()
    jobs = extractor.extract_from_excel(sample_excel_file)
    
    assert jobs[0].salary_min == 120000
    assert jobs[0].salary_max == 180000
    assert jobs[1].salary_min == 100000
    assert jobs[1].salary_max == 150000


def test_file_not_found():
    """Test handling of missing file."""
    extractor = ExcelJobExtractor()
    
    with pytest.raises(FileNotFoundError):
        extractor.extract_from_excel("/nonexistent/file.xlsx")


def test_parse_skills_various_formats():
    """Test parsing skills in different formats."""
    extractor = ExcelJobExtractor()
    
    # Comma-separated
    assert extractor._parse_skills("Python, JavaScript, React") == ["Python", "JavaScript", "React"]
    
    # Semicolon-separated
    assert extractor._parse_skills("Python; JavaScript; React") == ["Python", "JavaScript", "React"]
    
    # Pipe-separated
    assert extractor._parse_skills("Python | JavaScript | React") == ["Python", "JavaScript", "React"]
    
    # Single skill
    assert extractor._parse_skills("Python") == ["Python"]
    
    # Empty/None
    assert extractor._parse_skills(None) == []
    assert extractor._parse_skills("") == []
