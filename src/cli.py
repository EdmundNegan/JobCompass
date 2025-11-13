"""Command-line interface for JobCompass."""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

from jobcompass import JobCompass
from jobcompass.models import UserProfile, SearchCriteria, WorkMode, JobType, ExperienceLevel


def load_default_user_profile() -> UserProfile:
    """Load a default user profile for demonstration."""
    return UserProfile(
        name="Jane Doe",
        email="jane.doe@example.com",
        current_title="Senior Software Engineer",
        years_of_experience=6.5,
        skills=[
            "Python", "JavaScript", "React", "Node.js", "AWS",
            "Docker", "Kubernetes", "PostgreSQL", "REST APIs",
            "Git", "Agile", "CI/CD"
        ],
        experience="""
        Senior Software Engineer with 6+ years of experience building scalable web applications.
        Strong background in full-stack development with expertise in Python, JavaScript, and cloud technologies.
        Led multiple projects from conception to deployment, working with cross-functional teams.
        """,
        education="B.S. Computer Science, State University",
        certifications=["AWS Certified Developer", "Certified Scrum Master"],
        resume_text="Experienced software engineer with strong technical and leadership skills."
    )


def load_default_search_criteria() -> SearchCriteria:
    """Load default search criteria for demonstration."""
    return SearchCriteria(
        preferred_locations=["San Francisco", "New York", "Remote"],
        required_work_mode=None,
        preferred_work_modes=[WorkMode.REMOTE, WorkMode.HYBRID],
        min_salary=120000,
        preferred_job_types=[JobType.FULL_TIME],
        required_skills=["Python"],
        preferred_skills=["React", "AWS", "Docker"],
        experience_level=ExperienceLevel.SENIOR,
        dealbreakers=["on-call 24/7", "no remote", "unpaid overtime"],
        custom_criteria={}
    )


def main():
    """Main CLI entry point."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="JobCompass - AI-powered job matching tool"
    )
    parser.add_argument(
        "jobs_file",
        type=str,
        help="Path to Excel file containing job descriptions"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="results.txt",
        help="Output file path (default: results.txt)"
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0,
        help="Minimum compatibility score to include (0-100, default: 0)"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI analysis (use rule-based analysis only)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    jobs_file = Path(args.jobs_file)
    if not jobs_file.exists():
        print(f"Error: Jobs file not found: {jobs_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("JobCompass - AI-Powered Job Matching")
    print("=" * 80)
    print()
    
    # Initialize application
    api_key = None if args.no_ai else None  # Will use env var OPENAI_API_KEY
    app = JobCompass(api_key=api_key)
    
    # Load jobs
    print(f"Loading jobs from {jobs_file}...")
    try:
        num_jobs = app.load_jobs_from_excel(jobs_file)
        print(f"✓ Loaded {num_jobs} job descriptions")
    except Exception as e:
        print(f"Error loading jobs: {e}")
        sys.exit(1)
    
    print()
    
    # Load user profile and criteria (using defaults for now)
    print("Loading user profile and search criteria...")
    user_profile = load_default_user_profile()
    search_criteria = load_default_search_criteria()
    print(f"✓ Profile: {user_profile.name} - {user_profile.current_title}")
    print(f"✓ {user_profile.years_of_experience} years experience")
    print(f"✓ Skills: {', '.join(user_profile.skills[:5])}...")
    print(f"✓ Min Salary: ${search_criteria.min_salary:,.0f}")
    print(f"✓ Preferred Work Modes: {', '.join([wm.value for wm in search_criteria.preferred_work_modes])}")
    print()
    
    # Analyze jobs
    print("Analyzing job matches...")
    try:
        results = app.analyze_jobs(user_profile, search_criteria)
        matched = app.get_matched_jobs(min_score=args.min_score)
        filtered = app.get_filtered_jobs()
        
        print(f"✓ Analysis complete!")
        print(f"  - {len(matched)} jobs match your criteria (score >= {args.min_score})")
        print(f"  - {len(filtered)} jobs filtered out (dealbreakers)")
    except Exception as e:
        print(f"Error analyzing jobs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    
    # Export results
    output_path = Path(args.output)
    print(f"Exporting results to {output_path}...")
    try:
        app.export_results(output_path, format=args.format)
        print(f"✓ Results saved to {output_path}")
    except Exception as e:
        print(f"Error exporting results: {e}")
        sys.exit(1)
    
    print()
    
    # Show top matches
    if matched:
        print("=" * 80)
        print("TOP MATCHES")
        print("=" * 80)
        for i, result in enumerate(matched[:5], 1):
            print(f"\n{i}. {result.job_title} at {result.company}")
            print(f"   Score: {result.overall_score:.1f}/100")
            print(f"   {result.recommendation}")
    
    print()
    print("=" * 80)
    print(f"Analysis complete! Check {output_path} for full details.")
    print("=" * 80)


if __name__ == "__main__":
    main()
