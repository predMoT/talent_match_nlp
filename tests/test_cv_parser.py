import pytest
import asyncio
from unittest.mock import Mock, patch
from app.services.cv_parser import CVParser

class TestCVParser:
    """
    CV Parser servisinin unit testleri
    Matematik geçmişinizi düşünerek, algoritmaları test ediyoruz
    """
    
    @pytest.fixture
    def cv_parser(self):
        return CVParser()
    
    @pytest.fixture
    def sample_text(self):
        return """
        John Doe
        Senior Python Developer
        Email: john.doe@email.com
        Phone: +1234567890
        
        Experience:
        - 5 years Python development
        - Django and Flask frameworks
        - Machine Learning with TensorFlow
        
        Skills: Python, Django, Flask, TensorFlow, PostgreSQL, Docker
        
        Education:
        Computer Science, MIT, 2018
        """
    
    def test_extract_contact_info(self, cv_parser, sample_text):
        """Test contact information extraction"""
        result = cv_parser.extract_contact_info(sample_text)
        
        assert result['email'] == 'john.doe@email.com'
        assert result['phone'] == '+1234567890'
        assert 'John Doe' in result['name'] or result['name'] == 'John Doe'
    
    def test_extract_skills(self, cv_parser, sample_text):
        """Test skill extraction using NLP"""
        skills = cv_parser.extract_skills(sample_text)
        
        expected_skills = {'python', 'django', 'flask', 'tensorflow', 'postgresql', 'docker'}
        found_skills = {skill.lower() for skill in skills}
        
        # En az yarısının bulunması beklenir
        assert len(expected_skills.intersection(found_skills)) >= len(expected_skills) // 2
    
    def test_extract_experience_years(self, cv_parser, sample_text):
        """Test experience years extraction"""
        years = cv_parser.extract_experience_years(sample_text)
        assert years == 5
    
    def test_calculate_experience_score(self, cv_parser):
        """Test experience scoring algorithm"""
        # Linear scoring: 0-2 years = 0.2-0.4, 3-5 = 0.5-0.7, 6+ = 0.8-1.0
        assert cv_parser.calculate_experience_score(1) == pytest.approx(0.3, rel=0.1)
        assert cv_parser.calculate_experience_score(5) == pytest.approx(0.7, rel=0.1)
        assert cv_parser.calculate_experience_score(10) >= 0.8
    
    @pytest.mark.asyncio
    async def test_parse_pdf_file(self, cv_parser):
        """Test PDF parsing (mocked)"""
        mock_content = "Sample CV content with Python and Django skills"
        
        with patch('PyPDF2.PdfReader') as mock_pdf:
            mock_pdf.return_value.pages[0].extract_text.return_value = mock_content
            
            result = await cv_parser.parse_pdf(b"fake_pdf_content")
            assert 'python' in result.lower()
            assert 'django' in result.lower()
    
    def test_empty_input_handling(self, cv_parser):
        """Test handling of empty or invalid inputs"""
        assert cv_parser.extract_skills("") == []
        assert cv_parser.extract_skills(None) == []
        assert cv_parser.extract_experience_years("") == 0