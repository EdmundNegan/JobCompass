#!/usr/bin/env python3
"""
Example usage of JobCompass library.

This script demonstrates how to use JobCompass programmatically
instead of through the CLI.
"""

from pathlib import Path
from dotenv import load_dotenv

from src.jobcompass import JobCompass
from src.jobcompass.models import (
    UserProfile, SearchCriteria, WorkMode, JobType, ExperienceLevel
)


def main():
    """Run example analysis."""
    # Load environment variables
    load_dotenv()
    
    print("JobCompass API Example")
    print("=" * 80)
    print()
    
    # Initialize JobCompass
    app = JobCompass()
    
    # Load jobs from Excel
    jobs_file = Path("sample_data/sample_jobs.xlsx")
    print(f"Loading jobs from {jobs_file}...")
    num_jobs = app.load_jobs_from_excel(jobs_file)
    print(f"✓ Loaded {num_jobs} jobs")
    print()
    
    # Create user profile
    user = UserProfile(
        name="John Smith",
        current_title="Mid-Level Developer",
        years_of_experience=4.0,
        skills=[
            "Python", "JavaScript", "React", "Node.js", "AWS",
            "Docker", "PostgreSQL", "Git"
        ],
        experience="Mid-level developer with 4 years of experience in web development.",
        education="B.S. Computer Science",
        resume_text="Passionate developer with strong technical skills."
    )
    print(f"User Profile: {user.name}")
    print(f"  Experience: {user.years_of_experience} years")
    print(f"  Skills: {', '.join(user.skills[:5])}...")
    print()
    
    # Create search criteria
    criteria = SearchCriteria(
        preferred_locations=["San Francisco", "New York", "Remote"],
        preferred_work_modes=[WorkMode.REMOTE, WorkMode.HYBRID],
        min_salary=110000,
        preferred_job_types=[JobType.FULL_TIME],
        required_skills=["Python", "JavaScript"],
        preferred_skills=["React", "AWS"],
        experience_level=ExperienceLevel.MID,
        dealbreakers=["on-call 24/7", "no remote work"]
    )
    print("Search Criteria:")
    print(f"  Min Salary: ${criteria.min_salary:,}")
    print(f"  Work Modes: {', '.join([wm.value for wm in criteria.preferred_work_modes])}")
    print(f"  Required Skills: {', '.join(criteria.required_skills)}")
    print(f"  Dealbreakers: {', '.join(criteria.dealbreakers)}")
    print()
    
    # Analyze jobs
    print("Analyzing jobs...")
    results = app.analyze_jobs(user, criteria)
    
    matched_jobs = app.get_matched_jobs(min_score=50)
    filtered_jobs = app.get_filtered_jobs()
    
    print(f"✓ Found {len(matched_jobs)} matching jobs")
    print(f"✓ Filtered out {len(filtered_jobs)} jobs")
    print()
    
    # Show filtered jobs
    if filtered_jobs:
        print("-" * 80)
        print("FILTERED OUT JOBS:")
        print("-" * 80)
        for result in filtered_jobs:
            print(f"\n{result.job_title} at {result.company}")
            for reason in result.filter_reasons:
                print(f"  ✗ {reason}")
        print()
    
    # Show top 3 matches
    print("-" * 80)
    print("TOP 3 MATCHES:")
    print("-" * 80)
    
    for i, result in enumerate(matched_jobs[:3], 1):
        print(f"\n{i}. {result.job_title} at {result.company}")
        print(f"   Overall Score: {result.overall_score:.1f}/100")
        print(f"\n   Score Breakdown:")
        
        for fs in result.feature_scores:
            print(f"   • {fs.feature_name}: {fs.score:.1f}/100 "
                  f"(contribution: {fs.contribution:.1f})")
        
        print(f"\n   Why this job fits you:")
        print(f"   {result.job_to_user_fit}")
        
        print(f"\n   Why you fit this job:")
        print(f"   {result.user_to_job_fit}")
        
        print(f"\n   Recommendation: {result.recommendation}")
        print()
    
    # Export results
    output_file = Path("example_results.json")
    print(f"Exporting results to {output_file}...")
    app.export_results(output_file, format='json')
    print(f"✓ Results saved")
    print()
    
    print("=" * 80)
    print("Example complete!")


if __name__ == "__main__":
    main()
