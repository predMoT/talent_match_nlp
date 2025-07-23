from typing import List, Dict, Optional
from app.services.nlp_service import nlp_service
from app.models.cv import CVModel
from app.models.job_posting import JobPosting
from app.models.match import MatchCreate
import numpy as np

class MatchingService:
    def __init__(self):
        self.nlp_service = nlp_service
        
        # Ağırlıklar
        self.weights = {
            'similarity_score': 0.4,
            'skill_match_score': 0.4,
            'experience_match_score': 0.2
        }
    
    def find_matching_jobs(self, cv: CVModel, limit: int = 10) -> List[Dict]:
        """CV için uygun işleri bulur"""
        if not cv.embedding:
            return []
        
        # Benzer işleri bul
        similar_jobs = self.nlp_service.search_similar_jobs(cv.embedding, limit)
        
        matches = []
        for job_match in similar_jobs:
            match_data = {
                'job_id': job_match['job_id'],
                'similarity_score': job_match['similarity_score'],
                'cv_id': str(cv.id)
            }
            matches.append(match_data)
        
        return matches
    
    def find_matching_cvs(self, job: JobPosting, limit: int = 10) -> List[Dict]:
        """İş için uygun CV'leri bulur"""
        if not job.embedding:
            return []
        
        # Benzer CV'leri bul
        similar_cvs = self.nlp_service.search_similar_cvs(job.embedding, limit)
        
        matches = []
        for cv_match in similar_cvs:
            match_data = {
                'cv_id': cv_match['cv_id'],
                'similarity_score': cv_match['similarity_score'],
                'job_id': str(job.id)
            }
            matches.append(match_data)
        
        return matches
    
    def calculate_detailed_match(self, cv: CVModel, job: JobPosting) -> MatchCreate:
        """CV ve iş arasında detaylı eşleştirme hesaplar"""
        
        # 1. Semantic similarity (embedding)
        similarity_score = self._calculate_cosine_similarity(cv.embedding, job.embedding)
        
        # 2. Skill matching
        skill_match_result = self.nlp_service.calculate_skill_similarity(
            cv.skills, job.skills_required
        )
        skill_match_score = skill_match_result['skill_match_score']
        matched_skills = skill_match_result['matched_skills']
        missing_skills = skill_match_result['missing_skills']
        
        # 3. Experience matching (basit)
        experience_match_score = self._calculate_experience_match(cv, job)
        
        # 4. Overall score hesapla
        overall_score = (
            self.weights['similarity_score'] * similarity_score +
            self.weights['skill_match_score'] * skill_match_score +
            self.weights['experience_match_score'] * experience_match_score
        )
        
        # Match details
        match_details = {
            'cv_skills_count': len(cv.skills),
            'job_skills_count': len(job.skills_required),
            'matched_skills_count': len(matched_skills),
            'cv_experience_count': len(cv.experience),
            'job_experience_level': job.experience_level
        }
        
        return MatchCreate(
            cv_id=str(cv.id),
            job_id=str(job.id),
            similarity_score=similarity_score,
            skill_match_score=skill_match_score,
            experience_match_score=experience_match_score,
            overall_score=overall_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            match_details=match_details
        )
    
    def _calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """İki embedding arasında cosine similarity hesaplar"""
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity = dot product / (norm1 * norm2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, float(similarity))  # Negatif değerleri 0 yap
            
        except Exception as e:
            print(f"Cosine similarity calculation error: {e}")
            return 0.0
    
    def _calculate_experience_match(self, cv: CVModel, job: JobPosting) -> float:
        """Deneyim uyumu hesaplar (basit)"""
        try:
            cv_experience_count = len(cv.experience)
            
            # İş deneyim seviyesine göre puan ver
            experience_level_map = {
                'Entry': 0,
                'Mid': 2,
                'Senior': 4
            }
            
            required_experience = experience_level_map.get(job.experience_level, 1)
            
            if cv_experience_count >= required_experience:
                return 1.0
            elif cv_experience_count == 0:
                return 0.0 if required_experience > 0 else 1.0
            else:
                return cv_experience_count / max(required_experience, 1)
                
        except Exception as e:
            print(f"Experience match calculation error: {e}")
            return 0.5  # Default moderate score
    
    def rank_matches(self, matches: List[Dict], score_field: str = 'overall_score') -> List[Dict]:
        """Match'leri puana göre sıralar"""
        try:
            return sorted(matches, key=lambda x: x.get(score_field, 0), reverse=True)
        except Exception as e:
            print(f"Ranking error: {e}")
            return matches
    
    def filter_matches(self, matches: List[Dict], min_score: float = 0.0, 
                      max_results: int = 10) -> List[Dict]:
        """Match'leri filtreler"""
        try:
            # Minimum skora göre filtrele
            filtered = [match for match in matches if match.get('overall_score', 0) >= min_score]
            
            # Maksimum sonuç sayısına göre kırp
            return filtered[:max_results]
            
        except Exception as e:
            print(f"Filtering error: {e}")
            return matches[:max_results]

# Global instance
matching_service = MatchingService()