import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.services.matching_algorithm import CVJobMatcher

class TestCVJobMatcher:
    """
    CV-İş eşleştirme algoritmasının testleri
    Matematik optimizasyon ve skorlama algoritmaları
    """
    
    @pytest.fixture
    def matcher(self):
        return CVJobMatcher()
    
    @pytest.fixture
    def sample_cv_data(self):
        return {
            'skills': ['Python', 'Django', 'Machine Learning', 'PostgreSQL'],
            'experience_years': 5,
            'education_level': 'Bachelor',
            'certifications': ['AWS Certified'],
            'location': 'Istanbul',
            'salary_expectation': 15000
        }
    
    @pytest.fixture
    def sample_job_data(self):
        return {
            'required_skills': ['Python', 'Django', 'REST API'],
            'nice_to_have_skills': ['Machine Learning', 'Docker'],
            'min_experience': 3,
            'education_requirement': 'Bachelor',
            'location': 'Istanbul',
            'salary_range': (12000, 18000),
            'job_type': 'Full-time'
        }
    
    def test_skill_matching_score(self, matcher, sample_cv_data, sample_job_data):
        """Test skill matching with weighted scoring"""
        score = matcher.calculate_skill_match_score(
            sample_cv_data['skills'], 
            sample_job_data['required_skills'],
            sample_job_data['nice_to_have_skills']
        )
        
        # Python ve Django eşleşmesi var (2/3 required skills)
        # Machine Learning nice-to-have eşleşmesi var
        expected_base_score = (2/3) * 0.8  # Required skills weight: 0.8
        expected_bonus_score = (1/2) * 0.2  # Nice-to-have weight: 0.2
        expected_total = expected_base_score + expected_bonus_score
        
        assert score == pytest.approx(expected_total, rel=0.1)
    
    def test_experience_matching_score(self, matcher, sample_cv_data, sample_job_data):
        """Test experience level matching"""
        score = matcher.calculate_experience_score(
            sample_cv_data['experience_years'],
            sample_job_data['min_experience']
        )
        
        # 5 yıl deneyim, minimum 3 yıl gerekli
        # Over-qualification penalty uygulanmamalı (reasonable range)
        assert score > 0.8  # Yüksek skor beklenir
    
    def test_location_matching_score(self, matcher, sample_cv_data, sample_job_data):
        """Test location compatibility scoring"""
        score = matcher.calculate_location_score(
            sample_cv_data['location'],
            sample_job_data['location']
        )
        
        assert score == 1.0  # Exact match
        
        # Different cities
        score_diff = matcher.calculate_location_score('Ankara', 'Istanbul')
        assert 0 <= score_diff < 1.0
    
    def test_salary_compatibility_score(self, matcher, sample_cv_data, sample_job_data):
        """Test salary expectation vs offer compatibility"""
        score = matcher.calculate_salary_compatibility(
            sample_cv_data['salary_expectation'],
            sample_job_data['salary_range']
        )
        
        # 15000 expectation, 12000-18000 range
        # Within range, should be high score
        assert score > 0.8
    
    def test_overall_matching_score(self, matcher, sample_cv_data, sample_job_data):
        """Test weighted overall matching score calculation"""
        overall_score = matcher.calculate_overall_match_score(
            sample_cv_data, 
            sample_job_data
        )
        
        assert 0 <= overall_score <= 1.0
        assert isinstance(overall_score, float)
    
    def test_ranking_algorithm(self, matcher):
        """Test job ranking based on match scores"""
        cv_data = {
            'skills': ['Python', 'Django'],
            'experience_years': 3,
            'location': 'Istanbul'
        }
        
        jobs_data = [
            {
                'id': 1,
                'required_skills': ['Python', 'Django'],
                'min_experience': 2,
                'location': 'Istanbul'
            },
            {
                'id': 2,
                'required_skills': ['Java', 'Spring'],
                'min_experience': 5,
                'location': 'Ankara'
            },
            {
                'id': 3,
                'required_skills': ['Python', 'Flask'],
                'min_experience': 1,
                'location': 'Istanbul'
            }
        ]
        
        ranked_jobs = matcher.rank_jobs(cv_data, jobs_data)
        
        assert len(ranked_jobs) == 3
        assert ranked_jobs[0]['id'] == 1  # En yüksek eşleşme
        assert all(ranked_jobs[i]['score'] >= ranked_jobs[i+1]['score'] 
                  for i in range(len(ranked_jobs)-1))  # Descending order
    
    def test_confidence_interval_calculation(self, matcher):
        """Test confidence interval for match scores"""
        scores = [0.85, 0.78, 0.92, 0.67, 0.89]
        
        mean_score, confidence_interval = matcher.calculate_confidence_interval(
            scores, confidence_level=0.95
        )
        
        assert isinstance(mean_score, float)
        assert isinstance(confidence_interval, tuple)
        assert confidence_interval[0] < confidence_interval[1]
        assert confidence_interval[0] <= mean_score <= confidence_interval[1]
    
    def test_outlier_detection(self, matcher):
        """Test outlier detection in matching scores"""
        scores = [0.1, 0.2, 0.15, 0.9, 0.18, 0.12, 0.95, 0.11]  # 0.9 and 0.95 are outliers
        
        outliers = matcher.detect_outliers(scores, method='iqr')
        
        assert len(outliers) > 0
        assert 0.9 in outliers or 0.95 in outliers
    
    @pytest.mark.parametrize("experience,min_required,expected_range", [
        (2, 2, (0.8, 1.0)),    # Exactly meets requirement
        (5, 3, (0.9, 1.0)),    # Exceeds requirement
        (1, 3, (0.0, 0.5)),    # Below requirement
        (10, 2, (0.7, 0.9)),   # Over-qualified
    ])
    def test_experience_scoring_edge_cases(self, matcher, experience, min_required, expected_range):
        """Test experience scoring with various scenarios"""
        score = matcher.calculate_experience_score(experience, min_required)
        assert expected_range[0] <= score <= expected_range[1]