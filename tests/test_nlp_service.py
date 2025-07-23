import pytest
import numpy as np
import torch
from unittest.mock import Mock, patch
from app.services.nlp_service import NLPService

class TestNLPService:
    """
    NLP servisinin testleri - vektörleştirme ve benzerlik hesaplamaları
    """
    
    @pytest.fixture
    def nlp_service(self):
        return NLPService()
    
    def test_text_preprocessing(self, nlp_service):
        """Test text preprocessing pipeline"""
        text = "This is a SAMPLE text with Python and Machine Learning!"
        processed = nlp_service.preprocess_text(text)
        
        assert isinstance(processed, list)
        assert 'python' in processed
        assert 'machine' in processed or 'machin' in processed  # stemmed
        assert 'sample' in processed or 'sampl' in processed
    
    def test_vectorization_tfidf(self, nlp_service):
        """Test TF-IDF vectorization"""
        documents = [
            "Python developer with Django experience",
            "Java programmer with Spring framework",
            "Machine learning engineer with Python"
        ]
        
        vectors = nlp_service.vectorize_documents(documents, method='tfidf')
        
        assert vectors.shape[0] == 3  # 3 documents
        assert vectors.shape[1] > 0   # Non-zero features
        assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0, rtol=1e-10)  # Normalized
    
    def test_cosine_similarity_calculation(self, nlp_service):
        """Test cosine similarity - bu matematik konusu!"""
        # İki özdeş vektör
        vec1 = np.array([1, 0, 1, 0])
        vec2 = np.array([1, 0, 1, 0])
        similarity = nlp_service.calculate_cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0, rel=1e-10)
        
        # Dik vektörler
        vec1 = np.array([1, 0, 0, 0])
        vec2 = np.array([0, 1, 0, 0])
        similarity = nlp_service.calculate_cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0, abs=1e-10)
        
        # Zıt vektörler
        vec1 = np.array([1, 0])
        vec2 = np.array([-1, 0])
        similarity = nlp_service.calculate_cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(-1.0, rel=1e-10)
    
    @pytest.mark.asyncio
    async def test_bert_embeddings(self, nlp_service):
        """Test BERT embeddings (mocked because of model size)"""
        with patch('transformers.AutoTokenizer') as mock_tokenizer, \
             patch('transformers.AutoModel') as mock_model:
            
            # Mock BERT output
            mock_output = Mock()
            mock_output.last_hidden_state = torch.tensor([[[0.1, 0.2, 0.3]]])
            mock_model.return_value.return_value = mock_output
            
            text = "Sample text for BERT embedding"
            embedding = await nlp_service.get_bert_embedding(text)
            
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape[-1] > 0  # Has dimensions
    
    def test_similarity_threshold_filtering(self, nlp_service):
        """Test similarity score filtering"""
        similarities = [0.9, 0.7, 0.5, 0.3, 0.1]
        threshold = 0.6
        
        filtered = nlp_service.filter_by_threshold(similarities, threshold)
        expected = [0.9, 0.7]
        
        assert filtered == expected
    
    def test_batch_similarity_calculation(self, nlp_service):
        """Test batch similarity calculation efficiency"""
        # CV vektörü (1 x n)
        cv_vector = np.random.rand(1, 100)
        # İş ilanları vektörleri (m x n)
        job_vectors = np.random.rand(50, 100)
        
        similarities = nlp_service.calculate_batch_similarity(cv_vector, job_vectors)
        
        assert similarities.shape == (50,)  # 50 iş ilanı için 50 benzerlik skoru
        assert all(0 <= sim <= 1 for sim in similarities)  # Cosine similarity [0,1] aralığında
    
    def test_keyword_extraction(self, nlp_service):
        """Test keyword extraction using TF-IDF"""
        text = """
        Senior Python Developer with 5 years experience in Django and Flask.
        Strong background in machine learning, TensorFlow, and data analysis.
        Experience with PostgreSQL, Docker, and AWS cloud services.
        """
        
        keywords = nlp_service.extract_keywords(text, top_k=5)
        
        assert len(keywords) <= 5
        assert all(isinstance(kw, str) for kw in keywords)
        # Teknik terimler çıkarılmalı
        technical_terms = {'python', 'django', 'flask', 'tensorflow', 'postgresql', 'docker', 'aws'}
        found_terms = {kw.lower() for kw in keywords}
        assert len(technical_terms.intersection(found_terms)) >= 2