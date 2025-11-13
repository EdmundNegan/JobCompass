"""Job description extractor from Excel files."""

import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from ..models import JobDescription, ExperienceLevel, JobType, WorkMode


class ExcelJobExtractor:
    """Extracts job descriptions from Excel files."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.column_mappings = {
            'title': ['title', 'job_title', 'position', 'role'],
            'company': ['company', 'company_name', 'employer', 'organization'],
            'location': ['location', 'city', 'office_location', 'job_location'],
            'work_mode': ['work_mode', 'remote', 'location_type', 'work_type'],
            'job_type': ['job_type', 'employment_type', 'type'],
            'experience_level': ['experience_level', 'level', 'seniority', 'experience'],
            'salary_min': ['salary_min', 'min_salary', 'salary_from'],
            'salary_max': ['salary_max', 'max_salary', 'salary_to'],
            'description': ['description', 'job_description', 'desc', 'details'],
            'required_skills': ['required_skills', 'skills', 'requirements', 'must_have'],
            'preferred_skills': ['preferred_skills', 'nice_to_have', 'optional_skills'],
            'responsibilities': ['responsibilities', 'duties', 'what_you_will_do'],
            'benefits': ['benefits', 'perks', 'what_we_offer'],
        }
    
    def _find_column(self, df: pd.DataFrame, field_name: str) -> str | None:
        """Find the actual column name in the dataframe."""
        possible_names = self.column_mappings.get(field_name, [field_name])
        df_columns_lower = {col.lower(): col for col in df.columns}
        
        for name in possible_names:
            if name.lower() in df_columns_lower:
                return df_columns_lower[name.lower()]
        return None
    
    def _parse_skills(self, skills_str: Any) -> List[str]:
        """Parse skills from string to list."""
        if pd.isna(skills_str) or not skills_str:
            return []
        
        if isinstance(skills_str, list):
            return skills_str
        
        # Try comma-separated
        if ',' in str(skills_str):
            return [s.strip() for s in str(skills_str).split(',') if s.strip()]
        
        # Try semicolon-separated
        if ';' in str(skills_str):
            return [s.strip() for s in str(skills_str).split(';') if s.strip()]
        
        # Try pipe-separated
        if '|' in str(skills_str):
            return [s.strip() for s in str(skills_str).split('|') if s.strip()]
        
        # Single skill
        return [str(skills_str).strip()]
    
    def _parse_enum(self, value: Any, enum_class):
        """Parse enum value from string."""
        if pd.isna(value) or not value:
            return None
        
        value_str = str(value).strip()
        
        # Try exact match first
        for enum_val in enum_class:
            if enum_val.value.lower() == value_str.lower():
                return enum_val
        
        # Try partial match
        for enum_val in enum_class:
            if value_str.lower() in enum_val.value.lower() or enum_val.value.lower() in value_str.lower():
                return enum_val
        
        return None
    
    def extract_from_excel(self, file_path: str | Path) -> List[JobDescription]:
        """
        Extract job descriptions from an Excel file.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            List of JobDescription objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        jobs = []
        for idx, row in df.iterrows():
            try:
                job_data = self._extract_job_from_row(row, df, idx)
                jobs.append(job_data)
            except Exception as e:
                print(f"Warning: Failed to extract job at row {idx}: {e}")
                continue
        
        return jobs
    
    def _extract_job_from_row(self, row: pd.Series, df: pd.DataFrame, idx: int) -> JobDescription:
        """Extract a single job description from a row."""
        # Find column mappings
        title_col = self._find_column(df, 'title')
        company_col = self._find_column(df, 'company')
        description_col = self._find_column(df, 'description')
        
        if not title_col or not company_col:
            raise ValueError("Missing required columns: title and company")
        
        # Extract required fields
        title = str(row[title_col]) if pd.notna(row[title_col]) else ""
        company = str(row[company_col]) if pd.notna(row[company_col]) else ""
        
        # Extract description
        description = ""
        if description_col and pd.notna(row[description_col]):
            description = str(row[description_col])
        
        # Extract optional fields
        location_col = self._find_column(df, 'location')
        location = str(row[location_col]) if location_col and pd.notna(row[location_col]) else None
        
        work_mode_col = self._find_column(df, 'work_mode')
        work_mode = self._parse_enum(row[work_mode_col] if work_mode_col else None, WorkMode)
        
        job_type_col = self._find_column(df, 'job_type')
        job_type = self._parse_enum(row[job_type_col] if job_type_col else None, JobType)
        
        exp_level_col = self._find_column(df, 'experience_level')
        experience_level = self._parse_enum(row[exp_level_col] if exp_level_col else None, ExperienceLevel)
        
        # Extract salary
        salary_min_col = self._find_column(df, 'salary_min')
        salary_min = float(row[salary_min_col]) if salary_min_col and pd.notna(row[salary_min_col]) else None
        
        salary_max_col = self._find_column(df, 'salary_max')
        salary_max = float(row[salary_max_col]) if salary_max_col and pd.notna(row[salary_max_col]) else None
        
        # Extract skills
        req_skills_col = self._find_column(df, 'required_skills')
        required_skills = self._parse_skills(row[req_skills_col] if req_skills_col else None)
        
        pref_skills_col = self._find_column(df, 'preferred_skills')
        preferred_skills = self._parse_skills(row[pref_skills_col] if pref_skills_col else None)
        
        # Extract other fields
        resp_col = self._find_column(df, 'responsibilities')
        responsibilities = str(row[resp_col]) if resp_col and pd.notna(row[resp_col]) else None
        
        benefits_col = self._find_column(df, 'benefits')
        benefits = str(row[benefits_col]) if benefits_col and pd.notna(row[benefits_col]) else None
        
        return JobDescription(
            id=f"job_{idx}",
            title=title,
            company=company,
            location=location,
            work_mode=work_mode,
            job_type=job_type,
            experience_level=experience_level,
            salary_min=salary_min,
            salary_max=salary_max,
            description=description,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            responsibilities=responsibilities,
            benefits=benefits,
            raw_data=row.to_dict()
        )
