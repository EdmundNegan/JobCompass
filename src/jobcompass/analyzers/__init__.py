"""AI-powered job-user matching analyzer."""

import os
from typing import List, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from ..models import (
    JobDescription, UserProfile, SearchCriteria, MatchResult,
    FeatureScore, WorkMode, JobType
)


class JobMatchAnalyzer:
    """Analyzes job-user compatibility using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the analyzer.
        
        Args:
            api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            if not OPENAI_AVAILABLE:
                print("Warning: OpenAI package not installed. AI analysis will be limited.")
            else:
                print("Warning: No OpenAI API key provided. AI analysis will be limited.")
        
        # Feature weights for scoring
        self.feature_weights = {
            'skills_match': 0.35,
            'experience_match': 0.20,
            'salary_match': 0.15,
            'location_work_mode': 0.15,
            'culture_fit': 0.10,
            'growth_potential': 0.05
        }
    
    def analyze_match(
        self,
        job: JobDescription,
        user: UserProfile,
        criteria: SearchCriteria
    ) -> MatchResult:
        """
        Analyze the match between a job and a user.
        
        Args:
            job: Job description
            user: User profile
            criteria: Search criteria
            
        Returns:
            MatchResult with detailed analysis
        """
        # First check dealbreakers
        is_filtered, filter_reasons = self._check_dealbreakers(job, criteria)
        
        if is_filtered:
            return MatchResult(
                job_id=job.id,
                job_title=job.title,
                company=job.company,
                overall_score=0.0,
                is_filtered=True,
                filter_reasons=filter_reasons
            )
        
        # Calculate feature scores
        feature_scores = self._calculate_feature_scores(job, user, criteria)
        
        # Calculate overall score
        overall_score = sum(fs.contribution for fs in feature_scores)
        
        # Generate AI analysis if available
        if self.client:
            job_to_user_fit, user_to_job_fit, strengths, concerns, recommendation = \
                self._generate_ai_analysis(job, user, criteria, feature_scores, overall_score)
        else:
            job_to_user_fit, user_to_job_fit, strengths, concerns, recommendation = \
                self._generate_basic_analysis(job, user, criteria, feature_scores, overall_score)
        
        return MatchResult(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            overall_score=overall_score,
            is_filtered=False,
            filter_reasons=[],
            feature_scores=feature_scores,
            job_to_user_fit=job_to_user_fit,
            user_to_job_fit=user_to_job_fit,
            strengths=strengths,
            concerns=concerns,
            recommendation=recommendation
        )
    
    def _check_dealbreakers(
        self,
        job: JobDescription,
        criteria: SearchCriteria
    ) -> tuple[bool, List[str]]:
        """Check if job violates any dealbreakers."""
        reasons = []
        
        # Check required work mode
        if criteria.required_work_mode and job.work_mode:
            if job.work_mode != criteria.required_work_mode:
                reasons.append(
                    f"Work mode is {job.work_mode.value}, but you require {criteria.required_work_mode.value}"
                )
        
        # Check minimum salary
        if criteria.min_salary and job.salary_max:
            if job.salary_max < criteria.min_salary:
                reasons.append(
                    f"Maximum salary ${job.salary_max:,.0f} is below your minimum ${criteria.min_salary:,.0f}"
                )
        
        # Check custom dealbreakers
        for dealbreaker in criteria.dealbreakers:
            dealbreaker_lower = dealbreaker.lower()
            
            # Check in description
            if job.description and dealbreaker_lower in job.description.lower():
                reasons.append(f"Contains dealbreaker keyword: '{dealbreaker}'")
            
            # Check in location
            if job.location and dealbreaker_lower in job.location.lower():
                reasons.append(f"Location contains dealbreaker: '{dealbreaker}'")
        
        return len(reasons) > 0, reasons
    
    def _calculate_feature_scores(
        self,
        job: JobDescription,
        user: UserProfile,
        criteria: SearchCriteria
    ) -> List[FeatureScore]:
        """Calculate individual feature scores."""
        scores = []
        
        # Skills match
        skills_score, skills_explanation = self._score_skills_match(job, user, criteria)
        scores.append(FeatureScore(
            feature_name="Skills Match",
            score=skills_score,
            weight=self.feature_weights['skills_match'],
            contribution=skills_score * self.feature_weights['skills_match'],
            explanation=skills_explanation
        ))
        
        # Experience match
        exp_score, exp_explanation = self._score_experience_match(job, user)
        scores.append(FeatureScore(
            feature_name="Experience Match",
            score=exp_score,
            weight=self.feature_weights['experience_match'],
            contribution=exp_score * self.feature_weights['experience_match'],
            explanation=exp_explanation
        ))
        
        # Salary match
        salary_score, salary_explanation = self._score_salary_match(job, criteria)
        scores.append(FeatureScore(
            feature_name="Salary Match",
            score=salary_score,
            weight=self.feature_weights['salary_match'],
            contribution=salary_score * self.feature_weights['salary_match'],
            explanation=salary_explanation
        ))
        
        # Location/Work mode match
        location_score, location_explanation = self._score_location_work_mode(job, criteria)
        scores.append(FeatureScore(
            feature_name="Location & Work Mode",
            score=location_score,
            weight=self.feature_weights['location_work_mode'],
            contribution=location_score * self.feature_weights['location_work_mode'],
            explanation=location_explanation
        ))
        
        # Culture fit (estimated)
        culture_score = 70.0  # Default moderate score
        scores.append(FeatureScore(
            feature_name="Culture Fit",
            score=culture_score,
            weight=self.feature_weights['culture_fit'],
            contribution=culture_score * self.feature_weights['culture_fit'],
            explanation="Estimated based on company description and benefits"
        ))
        
        # Growth potential (estimated)
        growth_score = 75.0  # Default moderate-high score
        scores.append(FeatureScore(
            feature_name="Growth Potential",
            score=growth_score,
            weight=self.feature_weights['growth_potential'],
            contribution=growth_score * self.feature_weights['growth_potential'],
            explanation="Estimated based on role level and company size"
        ))
        
        return scores
    
    def _score_skills_match(
        self,
        job: JobDescription,
        user: UserProfile,
        criteria: SearchCriteria
    ) -> tuple[float, str]:
        """Score skills match between job and user."""
        user_skills_lower = {s.lower() for s in user.skills}
        required_skills_lower = {s.lower() for s in job.required_skills}
        preferred_skills_lower = {s.lower() for s in job.preferred_skills}
        
        # Check required skills
        if required_skills_lower:
            matched_required = required_skills_lower.intersection(user_skills_lower)
            required_match_rate = len(matched_required) / len(required_skills_lower)
        else:
            required_match_rate = 1.0
        
        # Check preferred skills
        if preferred_skills_lower:
            matched_preferred = preferred_skills_lower.intersection(user_skills_lower)
            preferred_match_rate = len(matched_preferred) / len(preferred_skills_lower)
        else:
            preferred_match_rate = 1.0
        
        # Calculate score (required skills weighted more heavily)
        score = (required_match_rate * 0.7 + preferred_match_rate * 0.3) * 100
        
        explanation = f"Matched {len(user_skills_lower.intersection(required_skills_lower))}/{len(required_skills_lower)} required skills"
        if preferred_skills_lower:
            explanation += f" and {len(user_skills_lower.intersection(preferred_skills_lower))}/{len(preferred_skills_lower)} preferred skills"
        
        return score, explanation
    
    def _score_experience_match(
        self,
        job: JobDescription,
        user: UserProfile
    ) -> tuple[float, str]:
        """Score experience level match."""
        if not job.experience_level or user.years_of_experience is None:
            return 70.0, "Experience level not specified, assuming moderate fit"
        
        # Experience level ranges (in years)
        exp_ranges = {
            "Entry Level": (0, 2),
            "Junior": (1, 3),
            "Mid Level": (3, 6),
            "Senior": (5, 10),
            "Lead": (8, 15),
            "Principal": (10, 20)
        }
        
        level_range = exp_ranges.get(job.experience_level.value, (0, 100))
        user_exp = user.years_of_experience
        
        # Calculate score based on how well user's experience fits the range
        if level_range[0] <= user_exp <= level_range[1]:
            score = 100.0
            explanation = f"Your {user_exp} years of experience fits {job.experience_level.value} perfectly"
        elif user_exp < level_range[0]:
            gap = level_range[0] - user_exp
            score = max(50, 100 - (gap * 15))
            explanation = f"You have {user_exp} years, {gap:.1f} years below typical {job.experience_level.value}"
        else:
            excess = user_exp - level_range[1]
            score = max(60, 100 - (excess * 10))
            explanation = f"You have {user_exp} years, {excess:.1f} years above typical {job.experience_level.value}"
        
        return score, explanation
    
    def _score_salary_match(
        self,
        job: JobDescription,
        criteria: SearchCriteria
    ) -> tuple[float, str]:
        """Score salary match."""
        if not criteria.min_salary:
            return 70.0, "No minimum salary specified"
        
        if not job.salary_max and not job.salary_min:
            return 50.0, "Salary range not provided by employer"
        
        job_max = job.salary_max or job.salary_min or 0
        
        if job_max >= criteria.min_salary * 1.2:
            return 100.0, f"Salary range exceeds your minimum by 20%+"
        elif job_max >= criteria.min_salary:
            ratio = (job_max / criteria.min_salary - 1) * 100
            # Scale from 80-100 based on how much above minimum
            score = min(80.0 + ratio, 100.0)
            return score, f"Salary meets your minimum requirement"
        else:
            # Already filtered by dealbreaker
            return 0.0, "Below minimum salary"
    
    def _score_location_work_mode(
        self,
        job: JobDescription,
        criteria: SearchCriteria
    ) -> tuple[float, str]:
        """Score location and work mode match."""
        score = 0.0
        explanations = []
        
        # Work mode match (60 points max)
        if job.work_mode:
            if criteria.required_work_mode and job.work_mode == criteria.required_work_mode:
                score += 60.0
                explanations.append(f"Perfect work mode match: {job.work_mode.value}")
            elif job.work_mode in criteria.preferred_work_modes:
                score += 60.0
                explanations.append(f"Preferred work mode: {job.work_mode.value}")
            elif job.work_mode == WorkMode.HYBRID:
                score += 50.0
                explanations.append("Hybrid offers flexibility")
            elif job.work_mode == WorkMode.REMOTE:
                score += 55.0
                explanations.append("Remote provides maximum flexibility")
            else:
                score += 30.0
                explanations.append(f"Work mode is {job.work_mode.value}")
        else:
            score += 35.0
            explanations.append("Work mode not specified")
        
        # Location match (40 points max)
        if job.location and criteria.preferred_locations:
            location_lower = job.location.lower()
            matched = any(loc.lower() in location_lower for loc in criteria.preferred_locations)
            if matched:
                score += 40.0
                explanations.append("Location matches your preferences")
            else:
                score += 15.0
                explanations.append("Location not in preferred list")
        else:
            score += 20.0
        
        # Ensure score doesn't exceed 100
        score = min(score, 100.0)
        
        return score, "; ".join(explanations)
    
    def _generate_ai_analysis(
        self,
        job: JobDescription,
        user: UserProfile,
        criteria: SearchCriteria,
        feature_scores: List[FeatureScore],
        overall_score: float
    ) -> tuple[str, str, List[str], List[str], str]:
        """Generate AI-powered analysis using OpenAI."""
        try:
            # Prepare context
            context = self._prepare_analysis_context(job, user, criteria, feature_scores, overall_score)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career advisor and job matching specialist. Analyze job-candidate fits with detailed, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            
            # Parse the response (simplified - you might want structured output)
            return self._parse_ai_response(analysis)
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_basic_analysis(job, user, criteria, feature_scores, overall_score)
    
    def _prepare_analysis_context(
        self,
        job: JobDescription,
        user: UserProfile,
        criteria: SearchCriteria,
        feature_scores: List[FeatureScore],
        overall_score: float
    ) -> str:
        """Prepare context for AI analysis."""
        context = f"""Analyze this job-candidate match:

JOB:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location or 'Not specified'}
- Work Mode: {job.work_mode.value if job.work_mode else 'Not specified'}
- Experience Level: {job.experience_level.value if job.experience_level else 'Not specified'}
- Salary: ${job.salary_min or 0:,.0f} - ${job.salary_max or 0:,.0f}
- Required Skills: {', '.join(job.required_skills) or 'Not specified'}
- Description: {job.description[:500]}...

CANDIDATE:
- Name: {user.name}
- Current Title: {user.current_title or 'Not specified'}
- Experience: {user.years_of_experience or 0} years
- Skills: {', '.join(user.skills)}
- Background: {user.experience[:300] if user.experience else 'Not specified'}

MATCH SCORES (Overall: {overall_score:.1f}/100):
"""
        for fs in feature_scores:
            context += f"\n- {fs.feature_name}: {fs.score:.1f}/100 ({fs.explanation})"
        
        context += """

Please provide:
1. JOB_TO_USER_FIT: Why this job is good for the candidate (2-3 sentences)
2. USER_TO_JOB_FIT: Why the candidate is good for this job (2-3 sentences)
3. STRENGTHS: 3 key strengths of this match (bullet points)
4. CONCERNS: 2-3 potential concerns or gaps (bullet points)
5. RECOMMENDATION: Final recommendation (1-2 sentences)

Format your response with clear section headers."""
        
        return context
    
    def _parse_ai_response(self, response: str) -> tuple[str, str, List[str], List[str], str]:
        """Parse AI response into structured components."""
        # Simplified parsing - you might want to use structured output instead
        job_to_user = ""
        user_to_job = ""
        strengths = []
        concerns = []
        recommendation = ""
        
        sections = response.split('\n')
        current_section = None
        
        for line in sections:
            line = line.strip()
            if not line:
                continue
            
            if 'JOB_TO_USER' in line.upper() or 'JOB TO USER' in line.upper():
                current_section = 'job_to_user'
            elif 'USER_TO_JOB' in line.upper() or 'USER TO JOB' in line.upper():
                current_section = 'user_to_job'
            elif 'STRENGTH' in line.upper():
                current_section = 'strengths'
            elif 'CONCERN' in line.upper():
                current_section = 'concerns'
            elif 'RECOMMENDATION' in line.upper():
                current_section = 'recommendation'
            elif current_section == 'job_to_user' and not line.startswith('#'):
                job_to_user += line + ' '
            elif current_section == 'user_to_job' and not line.startswith('#'):
                user_to_job += line + ' '
            elif current_section == 'strengths' and (line.startswith('-') or line.startswith('•')):
                strengths.append(line.lstrip('-•').strip())
            elif current_section == 'concerns' and (line.startswith('-') or line.startswith('•')):
                concerns.append(line.lstrip('-•').strip())
            elif current_section == 'recommendation' and not line.startswith('#'):
                recommendation += line + ' '
        
        return (
            job_to_user.strip() or "This position aligns with your background.",
            user_to_job.strip() or "Your skills match the job requirements.",
            strengths or ["Good overall fit"],
            concerns or ["None identified"],
            recommendation.strip() or "Worth considering."
        )
    
    def _generate_basic_analysis(
        self,
        job: JobDescription,
        user: UserProfile,
        criteria: SearchCriteria,
        feature_scores: List[FeatureScore],
        overall_score: float
    ) -> tuple[str, str, List[str], List[str], str]:
        """Generate basic analysis without AI."""
        # Job to user fit
        job_to_user = f"This {job.title} role at {job.company} offers "
        if job.work_mode:
            job_to_user += f"{job.work_mode.value.lower()} work, "
        if job.salary_max:
            job_to_user += f"competitive compensation up to ${job.salary_max:,.0f}, "
        job_to_user += "and opportunities to leverage your technical skills."
        
        # User to job fit
        user_to_job = f"With {user.years_of_experience or 0} years of experience and skills in {', '.join(user.skills[:3])}, "
        user_to_job += f"you meet the core requirements for this {job.experience_level.value if job.experience_level else ''} position."
        
        # Strengths
        strengths = []
        for fs in sorted(feature_scores, key=lambda x: x.score, reverse=True)[:3]:
            if fs.score >= 70:
                strengths.append(f"{fs.feature_name}: {fs.explanation}")
        
        # Concerns
        concerns = []
        for fs in sorted(feature_scores, key=lambda x: x.score)[:2]:
            if fs.score < 60:
                concerns.append(f"{fs.feature_name} could be stronger: {fs.explanation}")
        
        if not concerns:
            concerns = ["No major concerns identified"]
        
        # Recommendation
        if overall_score >= 80:
            recommendation = "Highly recommended - strong match across most criteria."
        elif overall_score >= 65:
            recommendation = "Good fit - worth pursuing with some areas to address in interview."
        elif overall_score >= 50:
            recommendation = "Moderate fit - consider if other options are limited."
        else:
            recommendation = "Weak fit - may want to focus on better-matching opportunities."
        
        return job_to_user, user_to_job, strengths, concerns, recommendation
