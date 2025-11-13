"""Unit tests for JobCompass models."""

import pytest
from src.jobcompass.models import (
    JobDescription, UserProfile, SearchCriteria, MatchResult,
    FeatureScore, WorkMode, JobType, ExperienceLevel
)


def test_job_description_creation():
    """Test creating a JobDescription."""
    job = JobDescription(
        id="test_1",
        title="Software Engineer",
        company="TestCorp",
        description="Test job description",
        required_skills=["Python", "JavaScript"]
    )
    
    assert job.id == "test_1"
    assert job.title == "Software Engineer"
    assert job.company == "TestCorp"
    assert len(job.required_skills) == 2
    assert "Python" in job.required_skills


def test_user_profile_creation():
    """Test creating a UserProfile."""
    user = UserProfile(
        name="Test User",
        email="test@example.com",
        years_of_experience=5.0,
        skills=["Python", "React", "AWS"],
        resume_text="Test resume"
    )
    
    assert user.name == "Test User"
    assert user.years_of_experience == 5.0
    assert len(user.skills) == 3


def test_search_criteria_creation():
    """Test creating SearchCriteria."""
    criteria = SearchCriteria(
        preferred_locations=["San Francisco", "Remote"],
        min_salary=100000,
        preferred_work_modes=[WorkMode.REMOTE, WorkMode.HYBRID],
        required_skills=["Python"],
        dealbreakers=["on-call"]
    )
    
    assert len(criteria.preferred_locations) == 2
    assert criteria.min_salary == 100000
    assert WorkMode.REMOTE in criteria.preferred_work_modes
    assert "on-call" in criteria.dealbreakers


def test_feature_score_validation():
    """Test FeatureScore validation."""
    # Valid score
    score = FeatureScore(
        feature_name="Test",
        score=85.0,
        weight=0.35,
        contribution=29.75,
        explanation="Test explanation"
    )
    assert score.score == 85.0
    
    # Invalid score (> 100)
    with pytest.raises(Exception):
        FeatureScore(
            feature_name="Test",
            score=150.0,
            weight=0.35,
            contribution=52.5,
            explanation="Invalid"
        )


def test_match_result_creation():
    """Test creating a MatchResult."""
    result = MatchResult(
        job_id="test_1",
        job_title="Software Engineer",
        company="TestCorp",
        overall_score=85.5,
        is_filtered=False,
        recommendation="Great match"
    )
    
    assert result.job_id == "test_1"
    assert result.overall_score == 85.5
    assert not result.is_filtered


def test_work_mode_enum():
    """Test WorkMode enum."""
    assert WorkMode.REMOTE.value == "Remote"
    assert WorkMode.HYBRID.value == "Hybrid"
    assert WorkMode.ONSITE.value == "On-site"


def test_experience_level_enum():
    """Test ExperienceLevel enum."""
    assert ExperienceLevel.SENIOR.value == "Senior"
    assert ExperienceLevel.JUNIOR.value == "Junior"
    assert ExperienceLevel.MID.value == "Mid Level"
