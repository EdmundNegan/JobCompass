"""Unit tests for job match analyzer."""

import pytest
from src.jobcompass.analyzers import JobMatchAnalyzer
from src.jobcompass.models import (
    JobDescription, UserProfile, SearchCriteria,
    WorkMode, JobType, ExperienceLevel
)


@pytest.fixture
def sample_job():
    """Create a sample job description."""
    return JobDescription(
        id="test_1",
        title="Senior Software Engineer",
        company="TechCorp",
        location="San Francisco, CA",
        work_mode=WorkMode.HYBRID,
        job_type=JobType.FULL_TIME,
        experience_level=ExperienceLevel.SENIOR,
        salary_min=130000,
        salary_max=180000,
        description="Build scalable applications",
        required_skills=["Python", "JavaScript", "AWS"],
        preferred_skills=["React", "Docker"]
    )


@pytest.fixture
def sample_user():
    """Create a sample user profile."""
    return UserProfile(
        name="Jane Doe",
        years_of_experience=6.0,
        skills=["Python", "JavaScript", "React", "AWS", "Docker"],
        resume_text="Experienced software engineer"
    )


@pytest.fixture
def sample_criteria():
    """Create sample search criteria."""
    return SearchCriteria(
        preferred_locations=["San Francisco", "Remote"],
        preferred_work_modes=[WorkMode.REMOTE, WorkMode.HYBRID],
        min_salary=120000,
        required_skills=["Python"],
        dealbreakers=[]
    )


def test_analyzer_initialization():
    """Test JobMatchAnalyzer initialization."""
    analyzer = JobMatchAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'feature_weights')


def test_analyze_match(sample_job, sample_user, sample_criteria):
    """Test basic job match analysis."""
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, sample_user, sample_criteria)
    
    assert result is not None
    assert result.job_id == "test_1"
    assert result.job_title == "Senior Software Engineer"
    assert result.company == "TechCorp"
    assert result.overall_score >= 0
    assert result.overall_score <= 100
    assert not result.is_filtered


def test_dealbreaker_salary(sample_job, sample_user, sample_criteria):
    """Test dealbreaker filtering for salary."""
    sample_criteria.min_salary = 200000  # Higher than job offers
    
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, sample_user, sample_criteria)
    
    assert result.is_filtered
    assert len(result.filter_reasons) > 0
    assert any("salary" in reason.lower() for reason in result.filter_reasons)


def test_dealbreaker_work_mode(sample_job, sample_user, sample_criteria):
    """Test dealbreaker filtering for work mode."""
    sample_criteria.required_work_mode = WorkMode.REMOTE
    sample_job.work_mode = WorkMode.ONSITE
    
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, sample_user, sample_criteria)
    
    assert result.is_filtered
    assert len(result.filter_reasons) > 0
    assert any("work mode" in reason.lower() for reason in result.filter_reasons)


def test_dealbreaker_keyword(sample_job, sample_user, sample_criteria):
    """Test dealbreaker filtering for keywords."""
    sample_criteria.dealbreakers = ["on-call"]
    sample_job.description = "Build apps. On-call rotation required."
    
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, sample_user, sample_criteria)
    
    assert result.is_filtered
    assert len(result.filter_reasons) > 0


def test_skills_match_scoring(sample_job, sample_user, sample_criteria):
    """Test skills matching score."""
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, sample_user, sample_criteria)
    
    # Should have feature scores
    assert len(result.feature_scores) > 0
    
    # Find skills score
    skills_score = next(fs for fs in result.feature_scores if "skills" in fs.feature_name.lower())
    assert skills_score is not None
    assert skills_score.score >= 0
    assert skills_score.score <= 100
    assert skills_score.weight == 0.35


def test_experience_match_scoring(sample_job, sample_user, sample_criteria):
    """Test experience matching score."""
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, sample_user, sample_criteria)
    
    # Find experience score
    exp_score = next(fs for fs in result.feature_scores if "experience" in fs.feature_name.lower())
    assert exp_score is not None
    assert exp_score.score >= 0
    assert exp_score.score <= 100
    assert exp_score.weight == 0.20


def test_overall_score_calculation(sample_job, sample_user, sample_criteria):
    """Test overall score is weighted sum of features."""
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, sample_user, sample_criteria)
    
    # Calculate expected score
    calculated_score = sum(fs.contribution for fs in result.feature_scores)
    
    # Should match overall score
    assert abs(result.overall_score - calculated_score) < 0.1


def test_feature_weights_sum_to_one():
    """Test that feature weights sum to 1.0."""
    analyzer = JobMatchAnalyzer()
    total_weight = sum(analyzer.feature_weights.values())
    assert abs(total_weight - 1.0) < 0.001


def test_parse_skills_empty_user_skills(sample_job, sample_criteria):
    """Test scoring with empty user skills."""
    user = UserProfile(
        name="Test User",
        years_of_experience=5.0,
        skills=[],  # No skills
        resume_text="Test"
    )
    
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(sample_job, user, sample_criteria)
    
    # Should still complete without error
    assert result is not None
    # Skills score should be low
    skills_score = next(fs for fs in result.feature_scores if "skills" in fs.feature_name.lower())
    assert skills_score.score < 50


def test_missing_salary_info(sample_user, sample_criteria):
    """Test handling of missing salary information."""
    job = JobDescription(
        id="test_2",
        title="Software Engineer",
        company="TestCo",
        description="Test job",
        salary_min=None,
        salary_max=None
    )
    
    analyzer = JobMatchAnalyzer()
    result = analyzer.analyze_match(job, sample_user, sample_criteria)
    
    # Should not filter out
    assert not result.is_filtered
    
    # Salary score should be moderate
    salary_score = next(fs for fs in result.feature_scores if "salary" in fs.feature_name.lower())
    assert 40 <= salary_score.score <= 60
