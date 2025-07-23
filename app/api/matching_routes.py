from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from ..services.matching_service import MatchingService
from ..models.match import MatchResult

router = APIRouter(prefix="/api/matching", tags=["matching"])

# Request/Response modelleri
class MatchRequest(BaseModel):
    cv_id: str
    job_ids: Optional[List[str]] = None  # Boşsa tüm iş ilanlarında ara
    threshold: Optional[float] = 0.7     # Minimum benzerlik skoru
    max_results: Optional[int] = 10      # Maksimum sonuç sayısı

class JobMatchRequest(BaseModel):
    job_id: str
    cv_ids: Optional[List[str]] = None
    threshold: Optional[float] = 0.7
    max_results: Optional[int] = 10

# Dependency injection için
def get_matching_service():
    return MatchingService()

@router.post("/cv-to-jobs", response_model=List[MatchResult])
async def match_cv_to_jobs(
    request: MatchRequest,
    matching_service: MatchingService = Depends(get_matching_service)
):
    """
    Belirli bir CV için en uygun iş ilanlarını bulur
    
    Algoritma:
    1. CV'yi vektörleştirir (TF-IDF veya BERT embeddings)
    2. İş ilanları ile cosine similarity hesaplar
    3. Threshold'u geçen sonuçları döner
    """
    try:
        matches = await matching_service.find_matching_jobs(
            cv_id=request.cv_id,
            job_ids=request.job_ids,
            threshold=request.threshold,
            max_results=request.max_results
        )
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/job-to-cvs", response_model=List[MatchResult])
async def match_job_to_cvs(
    request: JobMatchRequest,
    matching_service: MatchingService = Depends(get_matching_service)
):
    """
    Belirli bir iş ilanı için en uygun CV'leri bulur
    """
    try:
        matches = await matching_service.find_matching_cvs(
            job_id=request.job_id,
            cv_ids=request.cv_ids,
            threshold=request.threshold,
            max_results=request.max_results
        )
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch-process")
async def batch_process_all():
    """
    Tüm CV'ler ve iş ilanları için toplu eşleştirme yapar
    Büyük veri setleri için optimize edilmiş
    """
    try:
        matching_service = MatchingService()
        result = await matching_service.batch_process_all_matches()
        return {"message": "Batch processing completed", "processed": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_matching_statistics():
    """
    Eşleştirme istatistiklerini döner
    """
    try:
        matching_service = MatchingService()
        stats = await matching_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))