import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from app.config import settings

class NLPService:
    def __init__(self):
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        self.cv_index = None
        self.job_index = None
        self.cv_embeddings = []
        self.job_embeddings = []
        self.cv_ids = []
        self.job_ids = []
        
        # FAISS index dosyalarını yükle
        self._load_indexes()
    
    def _load_indexes(self):
        """FAISS index dosyalarını yükler"""
        try:
            cv_index_path = os.path.join(settings.FAISS_INDEX_PATH, "cv_index.faiss")
            job_index_path = os.path.join(settings.FAISS_INDEX_PATH, "job_index.faiss")
            
            if os.path.exists(cv_index_path):
                self.cv_index = faiss.read_index(cv_index_path)
            if os.path.exists(job_index_path):
                self.job_index = faiss.read_index(job_index_path)
                
        except Exception as e:
            print(f"Index loading error: {e}")
            self._create_empty_indexes()
    
    def _create_empty_indexes(self):
        """Boş FAISS index'leri oluşturur"""
        dimension = 384  # all-MiniLM-L6-v2 embedding dimension
        self.cv_index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
        self.job_index = faiss.IndexFlatIP(dimension)
    
    def create_embedding(self, text: str) -> List[float]:
        """Text'i embedding'e çevirir"""
        try:
            # Text'i temizle
            clean_text = self._clean_text(text)
            # Embedding oluştur
            embedding = self.model.encode(clean_text)
            # Normalize et (cosine similarity için)
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding creation error: {e}")
            return [0.0] * 384  # Default embedding
    
    def _clean_text(self, text: str) -> str:
        """Text'i temizler"""
        import re
        # Gereksiz karakterleri temizle
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        # Çok uzun text'leri kısalt
        if len(text) > 5000:
            text = text[:5000]
        return text
    
    def add_cv_to_index(self, cv_id: str, embedding: List[float]):
        """CV embedding'ini index'e ekler"""
        try:
            if self.cv_index is None:
                self._create_empty_indexes()
            
            embedding_array = np.array([embedding], dtype=np.float32)
            self.cv_index.add(embedding_array)
            self.cv_ids.append(cv_id)
            self.cv_embeddings.append(embedding)
            
            # Index'i kaydet
            self._save_cv_index()
            
        except Exception as e:
            print(f"CV index addition error: {e}")
    
    def add_job_to_index(self, job_id: str, embedding: List[float]):
        """Job embedding'ini index'e ekler"""
        try:
            if self.job_index is None:
                self._create_empty_indexes()
            
            embedding_array = np.array([embedding], dtype=np.float32)
            self.job_index.add(embedding_array)
            self.job_ids.append(job_id)
            self.job_embeddings.append(embedding)
            
            # Index'i kaydet
            self._save_job_index()
            
        except Exception as e:
            print(f"Job index addition error: {e}")
    
    def search_similar_jobs(self, cv_embedding: List[float], k: int = 10) -> List[Dict]:
        """CV embedding'ine benzer işleri bulur"""
        try:
            if self.job_index is None or self.job_index.ntotal == 0:
                return []
            
            query_vector = np.array([cv_embedding], dtype=np.float32)
            scores, indices = self.job_index.search(query_vector, min(k, self.job_index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.job_ids):
                    results.append({
                        'job_id': self.job_ids[idx],
                        'similarity_score': float(score)
                    })
            
            return results
        except Exception as e:
            print(f"Job search error: {e}")
            return []
    
    def search_similar_cvs(self, job_embedding: List[float], k: int = 10) -> List[Dict]:
        """Job embedding'ine benzer CV'leri bulur"""
        try:
            if self.cv_index is None or self.cv_index.ntotal == 0:
                return []
            
            query_vector = np.array([job_embedding], dtype=np.float32)
            scores, indices = self.cv_index.search(query_vector, min(k, self.cv_index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.cv_ids):
                    results.append({
                        'cv_id': self.cv_ids[idx],
                        'similarity_score': float(score)
                    })
            
            return results
        except Exception as e:
            print(f"CV search error: {e}")
            return []
    
    def calculate_skill_similarity(self, cv_skills: List[str], job_skills: List[str]) -> Dict:
        """Beceri benzerliğini hesaplar"""
        cv_skills_lower = [skill.lower() for skill in cv_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matched_skills = []
        missing_skills = []
        
        for job_skill in job_skills_lower:
            if job_skill in cv_skills_lower:
                matched_skills.append(job_skill)
            else:
                missing_skills.append(job_skill)
        
        # Skill match score hesapla
        if len(job_skills_lower) > 0:
            skill_match_score = len(matched_skills) / len(job_skills_lower)
        else:
            skill_match_score = 0.0
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'skill_match_score': skill_match_score
        }
    
    def _save_cv_index(self):
        """CV index'ini dosyaya kaydeder"""
        try:
            os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
            cv_index_path = os.path.join(settings.FAISS_INDEX_PATH, "cv_index.faiss")
            faiss.write_index(self.cv_index, cv_index_path)
        except Exception as e:
            print(f"CV index save error: {e}")
    
    def _save_job_index(self):
        """Job index'ini dosyaya kaydeder"""
        try:
            os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
            job_index_path = os.path.join(settings.FAISS_INDEX_PATH, "job_index.faiss")
            faiss.write_index(self.job_index, job_index_path)
        except Exception as e:
            print(f"Job index save error: {e}")

# Global instance
nlp_service = NLPService()