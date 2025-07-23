class TestIntegration:
    """
    Servislerin entegrasyon testleri
    """
    
    @pytest.mark.asyncio
    async def test_full_cv_processing_pipeline(self):
        """Test complete CV processing workflow"""
        with patch('app.services.cv_parser.CVParser') as mock_parser, \
             patch('app.services.nlp_service.NLPService') as mock_nlp, \
             patch('app.services.matching_algorithm.CVJobMatcher') as mock_matcher:
            
            # Mock CV parsing
            mock_parser.return_value.parse_pdf.return_value = "Sample CV content"
            mock_parser.return_value.extract_skills.return_value = ['Python', 'Django']
            
            # Mock NLP processing
            mock_nlp.return_value.vectorize_documents.return_value = np.array([[0.1, 0.2, 0.3]])
            
            # Mock matching
            mock_matcher.return_value.rank_jobs.return_value = [
                {'job_id': 1, 'score': 0.9},
                {'job_id': 2, 'score': 0.8}
            ]
            
            # Test the full pipeline
            from app.services.cv_processor import CVProcessor
            processor = CVProcessor()
            
            result = await processor.process_cv_and_match(
                cv_file=b"fake_pdf_content",
                user_preferences={'location': 'Istanbul'}
            )
            
            assert 'matched_jobs' in result
            assert len(result['matched_jobs']) > 0
            assert 'cv_analysis' in result


if __name__ == '__main__':
    # Test çalıştırma komutları
    pytest.main([
        '-v',                    # Verbose output
        '--tb=short',           # Short traceback format
        '--cov=app',            # Coverage report
        '--cov-report=html',    # HTML coverage report
        'tests/'                # Test directory
    ])
