"""Data models for JobCompass application."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    ENTRY = "Entry Level"
    JUNIOR = "Junior"
    MID = "Mid Level"
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"


class JobType(str, Enum):
    """Job type enumeration."""
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    TEMPORARY = "Temporary"


class WorkMode(str, Enum):
    """Work mode enumeration."""
    REMOTE = "Remote"
    ONSITE = "On-site"
    HYBRID = "Hybrid"


class JobDescription(BaseModel):
    """Model for job description."""
    id: Optional[str] = None
    title: str
    company: str
    location: Optional[str] = None
    work_mode: Optional[WorkMode] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """Model for user profile/resume."""
    name: str
    email: Optional[str] = None
    current_title: Optional[str] = None
    years_of_experience: Optional[float] = None
    skills: List[str] = Field(default_factory=list)
    experience: Optional[str] = None
    education: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)
    resume_text: str = ""


class SearchCriteria(BaseModel):
    """Model for user search criteria."""
    preferred_locations: List[str] = Field(default_factory=list)
    required_work_mode: Optional[WorkMode] = None
    preferred_work_modes: List[WorkMode] = Field(default_factory=list)
    min_salary: Optional[float] = None
    preferred_job_types: List[JobType] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: Optional[ExperienceLevel] = None
    dealbreakers: List[str] = Field(default_factory=list)
    custom_criteria: Dict[str, Any] = Field(default_factory=dict)


class FeatureScore(BaseModel):
    """Score for individual matching feature."""
    feature_name: str
    score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=1)
    contribution: float = Field(ge=0, le=100)  # weighted score
    explanation: str


class MatchResult(BaseModel):
    """Result of job-user matching analysis."""
    job_id: Optional[str]
    job_title: str
    company: str
    overall_score: float = Field(ge=0, le=100)
    is_filtered: bool = False
    filter_reasons: List[str] = Field(default_factory=list)
    feature_scores: List[FeatureScore] = Field(default_factory=list)
    job_to_user_fit: str = ""  # Why this job is good for the user
    user_to_job_fit: str = ""  # Why the user is good for this job
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    recommendation: str = ""
