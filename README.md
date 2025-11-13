# JobCompass

AI-powered tool that navigates to the right job for you.

## Overview

JobCompass is an intelligent job matching system that analyzes job descriptions from Excel files and compares them against your resume and search criteria. It provides detailed compatibility scores, explains why jobs match (or don't match), and helps you focus on the best opportunities.

## Features

- 📊 **Excel Job Extraction**: Load job descriptions from Excel files with flexible column mapping
- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-4 for intelligent job-candidate matching (optional)
- 🎯 **Smart Filtering**: Automatically filters out jobs based on dealbreakers
- 💯 **Detailed Scoring**: 100-point compatibility score with breakdown by feature
- 📈 **Feature Contributions**: See exactly how each factor (skills, experience, salary, etc.) contributes to the match
- 🚫 **Dealbreaker Detection**: Shows why certain jobs were filtered out
- 📝 **Comprehensive Reports**: Get detailed insights on why you're a good fit (or not) for each position
- ⚙️ **Customizable Criteria**: Start with predefined criteria and add your own

## Installation

1. Clone the repository:
```bash
git clone https://github.com/EdmundNegan/JobCompass.git
cd JobCompass
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up OpenAI API key for AI analysis:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Quick Start

Run the tool with the sample data:

```bash
python src/cli.py sample_data/sample_jobs.xlsx
```

This will:
1. Load job descriptions from the Excel file
2. Analyze them against a default user profile
3. Generate a detailed report in `results.txt`

## Usage

### Basic Usage

```bash
python src/cli.py path/to/jobs.xlsx
```

### Advanced Options

```bash
# Save results as JSON
python src/cli.py jobs.xlsx -o results.json -f json

# Filter to only show jobs with score >= 70
python src/cli.py jobs.xlsx --min-score 70

# Use rule-based analysis only (no AI)
python src/cli.py jobs.xlsx --no-ai
```

### Excel File Format

Your Excel file should contain job descriptions with columns like:

| Column Name | Description | Required |
|------------|-------------|----------|
| title | Job title | Yes |
| company | Company name | Yes |
| description | Job description | Recommended |
| location | Job location | No |
| work_mode | Remote/Hybrid/On-site | No |
| job_type | Full-time/Part-time/Contract | No |
| experience_level | Entry/Junior/Mid/Senior/Lead | No |
| salary_min | Minimum salary | No |
| salary_max | Maximum salary | No |
| required_skills | Comma-separated skills | No |
| preferred_skills | Comma-separated skills | No |
| responsibilities | Job responsibilities | No |
| benefits | Benefits offered | No |

The system is flexible with column names and will try to match common variations (e.g., "job_title", "position", "role" all map to title).

See `sample_data/sample_jobs.xlsx` for an example.

## How It Works

### 1. Job Extraction
JobCompass reads your Excel file and extracts job information using intelligent column mapping.

### 2. Dealbreaker Filtering
Jobs are first filtered based on your dealbreakers:
- Required work mode (e.g., must be remote)
- Minimum salary requirements
- Custom dealbreaker keywords

Filtered jobs are listed separately with clear reasons.

### 3. Compatibility Scoring
Each job that passes filters is scored on multiple dimensions:

| Feature | Weight | Description |
|---------|--------|-------------|
| **Skills Match** | 35% | How well your skills match required/preferred skills |
| **Experience Match** | 20% | How your experience level aligns with the role |
| **Salary Match** | 15% | How the salary meets your requirements |
| **Location & Work Mode** | 15% | Match with preferred locations and work arrangements |
| **Culture Fit** | 10% | Estimated cultural compatibility |
| **Growth Potential** | 5% | Career growth opportunities |

### 4. AI Analysis (Optional)
When OpenAI API key is provided, the system generates:
- **Job-to-User Fit**: Why this job is good for you
- **User-to-Job Fit**: Why you're a good candidate for this job
- **Strengths**: Key advantages of this match
- **Concerns**: Potential gaps or issues
- **Recommendation**: Final hiring recommendation

### 5. Results Report
All results are compiled into a comprehensive report showing:
- Overall match scores
- Feature-by-feature breakdown
- Why jobs were filtered out
- Detailed analysis for each matched job

## Configuration

### User Profile
Currently uses a default profile defined in `src/cli.py`. To customize:
1. Edit the `load_default_user_profile()` function
2. Or extend the code to load from a file

### Search Criteria
Default criteria are defined in `load_default_search_criteria()`. You can customize:
- Preferred locations
- Work mode preferences (Remote, Hybrid, On-site)
- Minimum salary
- Required and preferred skills
- Experience level
- Dealbreakers (keywords that automatically filter out jobs)

## Example Output

```
================================================================================
JobCompass Analysis Results
================================================================================

Total Jobs Analyzed: 8
Jobs Matching Criteria: 6
Jobs Filtered Out: 2

--------------------------------------------------------------------------------
FILTERED OUT JOBS (Dealbreakers)
--------------------------------------------------------------------------------

Junior Python Developer at CodeFactory
Reasons:
  • Maximum salary $90,000 is below your minimum $120,000

--------------------------------------------------------------------------------
MATCHED JOBS (Ranked by Compatibility)
--------------------------------------------------------------------------------

================================================================================
#1 - Senior Software Engineer at TechCorp
Overall Compatibility Score: 82.5/100
================================================================================

SCORE BREAKDOWN:
  • Skills Match: 90.0/100 (Weight: 35%, Contribution: 31.5)
    Matched 5/5 required skills and 2/4 preferred skills
  • Experience Match: 95.0/100 (Weight: 20%, Contribution: 19.0)
    Your 6.5 years of experience fits Senior Level perfectly
  ...

WHY THIS JOB FITS YOU:
This Senior Software Engineer role at TechCorp offers hybrid work, competitive
compensation up to $180,000, and opportunities to leverage your technical skills.

WHY YOU FIT THIS JOB:
With 6.5 years of experience and skills in Python, JavaScript, React, you meet
the core requirements for this Senior position.

STRENGTHS:
  • Excellent skills alignment with required technologies
  • Experience level is a perfect match
  • Salary exceeds minimum by 50%

RECOMMENDATION:
Highly recommended - strong match across most criteria.
```

## Development

### Project Structure
```
JobCompass/
├── src/
│   ├── jobcompass/
│   │   ├── __init__.py          # Main application
│   │   ├── models/
│   │   │   └── __init__.py      # Data models
│   │   ├── extractors/
│   │   │   └── __init__.py      # Excel extraction
│   │   ├── analyzers/
│   │   │   └── __init__.py      # Job matching logic
│   │   └── utils/
│   └── cli.py                    # Command-line interface
├── sample_data/
│   └── sample_jobs.xlsx          # Sample job data
├── tests/                        # Unit tests
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Roadmap

- [x] Excel job extraction
- [x] Rule-based matching and scoring
- [x] AI-powered analysis with OpenAI
- [x] Dealbreaker filtering
- [x] Feature contribution breakdown
- [x] Text and JSON output formats
- [ ] Custom user profile loading from file
- [ ] User-definable criteria via config file
- [ ] Resume parsing (PDF, DOCX)
- [ ] Web interface
- [ ] Job application tracking
- [ ] Interview preparation suggestions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
