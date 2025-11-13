"""Main JobCompass application."""

from typing import List, Optional
from pathlib import Path
import json

from .models import JobDescription, UserProfile, SearchCriteria, MatchResult
from .extractors import ExcelJobExtractor
from .analyzers import JobMatchAnalyzer


class JobCompass:
    """Main application class for job matching."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize JobCompass application.
        
        Args:
            api_key: OpenAI API key for AI analysis
        """
        self.extractor = ExcelJobExtractor()
        self.analyzer = JobMatchAnalyzer(api_key=api_key)
        self.jobs: List[JobDescription] = []
        self.results: List[MatchResult] = []
    
    def load_jobs_from_excel(self, file_path: str | Path) -> int:
        """
        Load job descriptions from Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Number of jobs loaded
        """
        self.jobs = self.extractor.extract_from_excel(file_path)
        return len(self.jobs)
    
    def analyze_jobs(
        self,
        user_profile: UserProfile,
        search_criteria: SearchCriteria
    ) -> List[MatchResult]:
        """
        Analyze all loaded jobs against user profile and criteria.
        
        Args:
            user_profile: User's profile and resume
            search_criteria: User's search criteria
            
        Returns:
            List of match results sorted by score
        """
        self.results = []
        
        for job in self.jobs:
            result = self.analyzer.analyze_match(job, user_profile, search_criteria)
            self.results.append(result)
        
        # Sort by overall score (descending)
        self.results.sort(key=lambda x: x.overall_score, reverse=True)
        
        return self.results
    
    def get_filtered_jobs(self) -> List[MatchResult]:
        """Get list of jobs that were filtered out."""
        return [r for r in self.results if r.is_filtered]
    
    def get_matched_jobs(self, min_score: float = 0) -> List[MatchResult]:
        """
        Get list of jobs that passed filters.
        
        Args:
            min_score: Minimum compatibility score threshold
            
        Returns:
            List of matched jobs above threshold
        """
        return [r for r in self.results if not r.is_filtered and r.overall_score >= min_score]
    
    def export_results(self, output_path: str | Path, format: str = 'json'):
        """
        Export results to file.
        
        Args:
            output_path: Output file path
            format: Output format ('json', 'text')
        """
        output_path = Path(output_path)
        
        if format == 'json':
            self._export_json(output_path)
        elif format == 'text':
            self._export_text(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, output_path: Path):
        """Export results as JSON."""
        data = {
            'total_jobs': len(self.jobs),
            'matched_jobs': len(self.get_matched_jobs()),
            'filtered_jobs': len(self.get_filtered_jobs()),
            'results': [result.model_dump() for result in self.results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _export_text(self, output_path: Path):
        """Export results as human-readable text."""
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("JobCompass Analysis Results\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write(f"Total Jobs Analyzed: {len(self.jobs)}\n")
            f.write(f"Jobs Matching Criteria: {len(self.get_matched_jobs())}\n")
            f.write(f"Jobs Filtered Out: {len(self.get_filtered_jobs())}\n\n")
            
            # Filtered jobs
            if self.get_filtered_jobs():
                f.write("-" * 80 + "\n")
                f.write("FILTERED OUT JOBS (Dealbreakers)\n")
                f.write("-" * 80 + "\n\n")
                
                for result in self.get_filtered_jobs():
                    f.write(f"{result.job_title} at {result.company}\n")
                    f.write(f"Reasons:\n")
                    for reason in result.filter_reasons:
                        f.write(f"  • {reason}\n")
                    f.write("\n")
            
            # Matched jobs
            f.write("-" * 80 + "\n")
            f.write("MATCHED JOBS (Ranked by Compatibility)\n")
            f.write("-" * 80 + "\n\n")
            
            for i, result in enumerate(self.get_matched_jobs(), 1):
                f.write(f"\n{'=' * 80}\n")
                f.write(f"#{i} - {result.job_title} at {result.company}\n")
                f.write(f"Overall Compatibility Score: {result.overall_score:.1f}/100\n")
                f.write(f"{'=' * 80}\n\n")
                
                # Feature scores
                f.write("SCORE BREAKDOWN:\n")
                for fs in result.feature_scores:
                    f.write(f"  • {fs.feature_name}: {fs.score:.1f}/100 "
                           f"(Weight: {fs.weight:.0%}, Contribution: {fs.contribution:.1f})\n")
                    f.write(f"    {fs.explanation}\n")
                
                # Analysis
                f.write(f"\nWHY THIS JOB FITS YOU:\n{result.job_to_user_fit}\n")
                f.write(f"\nWHY YOU FIT THIS JOB:\n{result.user_to_job_fit}\n")
                
                if result.strengths:
                    f.write(f"\nSTRENGTHS:\n")
                    for strength in result.strengths:
                        f.write(f"  • {strength}\n")
                
                if result.concerns:
                    f.write(f"\nPOTENTIAL CONCERNS:\n")
                    for concern in result.concerns:
                        f.write(f"  • {concern}\n")
                
                f.write(f"\nRECOMMENDATION:\n{result.recommendation}\n")
                f.write("\n")
