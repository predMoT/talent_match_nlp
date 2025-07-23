import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.recommendation_engine import RecommendationEngine

class TestRecommendationEngine:
    """
    AI-powered recommendation engine testleri
    """
    
    @pytest.fixture
    def recommendation_engine(self):
        return RecommendationEngine()
    
    @pytest.fixture
    def user_profile(self):
        return {
            'user_id': 'user123',
            'skills': ['Python', 'Machine Learning', 'Django'],
            'experience_years': 4,
            'industry_preference': 'Technology',
            'location': 'Istanbul',
            'career_goals': 'Senior Developer',
            'previous_applications': [101, 102, 103],
            'job_views': [101, 104, 105, 106]
        }
    
    @pytest.mark.asyncio
    async def test_collaborative_filtering(self, recommendation_engine, user_profile):
        """Test collaborative filtering algorithm"""
        with patch.object(recommendation_engine, 'get_similar_users') as mock_similar:
            mock_similar.return_value = [
                {'user_id': 'user456', 'similarity': 0.85},
                {'user_id': 'user789', 'similarity': 0.72}
            ]
            
            recommendations = await recommendation_engine.collaborative_filtering(
                user_profile['user_id'], top_k=5
            )
            
            assert len(recommendations) <= 5
            assert all('job_id' in rec for rec in recommendations)
            assert all('score' in rec for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_content_based_filtering(self, recommendation_engine, user_profile):
        """Test content-based filtering using user skills and preferences"""
        recommendations = await recommendation_engine.content_based_filtering(
            user_profile, top_k=10
        )
        
        assert len(recommendations) <= 10
        assert all(isinstance(rec['job_id'], int) for rec in recommendations)
        assert all(0 <= rec['score'] <= 1 for rec in recommendations)
    
    def test_diversity_injection(self, recommendation_engine):
        """Test recommendation diversity to avoid filter bubbles"""
        similar_recommendations = [
            {'job_id': 1, 'score': 0.9, 'category': 'Backend Developer'},
            {'job_id': 2, 'score': 0.85, 'category': 'Backend Developer'},
            {'job_id': 3, 'score': 0.8, 'category': 'Backend Developer'},
            {'job_id': 4, 'score': 0.7, 'category': 'Frontend Developer'},
            {'job_id': 5, 'score': 0.6, 'category': 'Data Scientist'}
        ]
        
        diverse_recs = recommendation_engine.inject_diversity(
            similar_recommendations, diversity_factor=0.3
        )
        
        categories = [rec['category'] for rec in diverse_recs[:3]]
        unique_categories = set(categories)
        
        # Diversity injection should include different categories
        assert len(unique_categories) > 1
    
    def test_cold_start_problem_handling(self, recommendation_engine):
        """Test handling of new users with minimal data"""
        new_user_profile = {
            'user_id': 'newuser001',
            'skills': ['Python'],
            'experience_years': 0,
            'previous_applications': [],
            'job_views': []
        }
        
        recommendations = recommendation_engine.handle_cold_start(new_user_profile)
        
        assert len(recommendations) > 0
        # Should recommend popular/trending jobs for new users
        assert all('popularity_score' in rec for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_real_time_updates(self, recommendation_engine, user_profile):
        """Test real-time recommendation updates based on user actions"""
        # Simulate user applying to a job
        await recommendation_engine.update_user_action(
            user_profile['user_id'], 
            'application', 
            job_id=107
        )
        
        # Get updated recommendations
        updated_recs = await recommendation_engine.get_recommendations(
            user_profile['user_id']
        )
        
        # Recommendations should reflect the new application
        assert any(rec.get('reason') == 'similar_to_applied' for rec in updated_recs)
    
    def test_explanation_generation(self, recommendation_engine):
        """Test recommendation explanation generation"""
        recommendation = {
            'job_id': 123,
            'score': 0.87,
            'matched_skills': ['Python', 'Django'],
            'company': 'Tech Corp',
            'similarity_reason': 'skills_match'
        }
        
        explanation = recommendation_engine.generate_explanation(recommendation)
        
        assert isinstance(explanation, str)
        assert 'Python' in explanation or 'Django' in explanation
        assert len(explanation) > 0
    
    def test_a_b_testing_support(self, recommendation_engine):
        """Test A/B testing framework for different algorithms"""
        user_id = 'test_user'
        
        # Test assignment to A/B groups
        group_a = recommendation_engine.assign_ab_group(user_id, experiment='algo_test')
        group_b = recommendation_engine.assign_ab_group(user_id + '_2', experiment='algo_test')
        
        assert group_a in ['A', 'B']
        assert group_b in ['A', 'B']
        
        # Same user should get same group consistently
        group_a_again = recommendation_engine.assign_ab_group(user_id, experiment='algo_test')
        assert group_a == group_a_again