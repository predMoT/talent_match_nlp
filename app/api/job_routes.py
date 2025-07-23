from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.models.job_posting import JobPosting, JobCreate, JobUpdate, JobResponse
from app.services.nlp_service import nlp_service
from app.utils.database import get_database

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("/", response_model=dict)
async def create_job(
    job_data: JobCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Yeni iş ilanı oluşturur"""
    try:
        # Raw text oluştur
        raw_text = f"{job_data.title} {job_data.company} {job_data.description} " + \
                  f"{' '.join(job_data.requirements)} {' '.join(job_data.skills_required)}"
        
        # Embedding oluştur
        embedding = nlp_service.create_embedding(raw_text)
        
        # Job modelini oluştur
        job_dict = {
            **job_data.dict(),
            'raw_text': raw_text,
            'embedding': embedding,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # MongoDB'ye kaydet
        result = await db.jobs.insert_one(job_dict)
        job_id = str(result.inserted_id)
        
        # FAISS index'e ekle
        nlp_service.add_job_to_index(job_id, embedding)
        
        return {
            "message": "Job created successfully",
            "job_id": job_id,
            "title": job_data.title,
            "company": job_data.company
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job creation error: {str(e)}")

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    company: Optional[str] = None,
    location: Optional[str] = None,
    employment_type: Optional[str] = None,
    is_active: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """İş ilanlarını listeler"""
    try:
        # Filter query oluştur
        filter_query = {"is_active": is_active}
        
        if company:
            filter_query["company"] = {"$regex": company, "$options": "i"}
        if location:
            filter_query["location"] = {"$regex": location, "$options": "i"}
        if employment_type:
            filter_query["employment_type"] = employment_type
        
        # MongoDB'den çek
        cursor = db.jobs.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
        jobs = await cursor.to_list(length=limit)
        
        # Response formatına çevir
        job_responses = []
        for job in jobs:
            job_responses.append(JobResponse(
                id=str(job['_id']),
                title=job.get('title', ''),
                company=job.get('company', ''),
                description=job.get('description', '')[:200] + "...",  # İlk 200 karakter
                skills_required=job.get('skills_required', []),
                location=job.get('location'),
                employment_type=job.get('employment_type', 'Full-time'),
                created_at=job.get('created_at')
            ))
        
        return job_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job listing error: {str(e)}")

@router.get("/{job_id}", response_model=JobPosting)
async def get_job(
    job_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Tek bir iş ilanını getirir"""
    try:
        if not ObjectId.is_valid(job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID")
        
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # ID'yi string'e çevir
        job['_id'] = str(job['_id'])
        
        return JobPosting(**job)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job retrieval error: {str(e)}")

@router.put("/{job_id}", response_model=dict)
async def update_job(
    job_id: str,
    job_update: JobUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """İş ilanını günceller"""
    try:
        if not ObjectId.is_valid(job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID")
        
        # Mevcut job'ı kontrol et
        existing_job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not existing_job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Sadece değişen alanları al
        update_data = {k: v for k, v in job_update.dict().items() if v is not None}
        
        if update_data:
            # Eğer içerik değişti ise embedding güncelle
            content_fields = ['title', 'description', 'requirements', 'skills_required']
            if any(field in update_data for field in content_fields):
                # Güncellenmiş verilerle raw text oluştur
                updated_job = {**existing_job, **update_data}
                raw_text = f"{updated_job.get('title', '')} {updated_job.get('company', '')} " + \
                          f"{updated_job.get('description', '')} " + \
                          f"{' '.join(updated_job.get('requirements', []))} " + \
                          f"{' '.join(updated_job.get('skills_required', []))}"
                
                # Yeni embedding oluştur
                new_embedding = nlp_service.create_embedding(raw_text)
                update_data['raw_text'] = raw_text
                update_data['embedding'] = new_embedding
                
                # FAISS index'i güncelle
                nlp_service.update_job_in_index(job_id, new_embedding)
            
            # updated_at alanını güncelle
            update_data['updated_at'] = datetime.utcnow()
            
            # MongoDB'de güncelle
            result = await db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Job not found")
            
            return {
                "message": "Job updated successfully",
                "job_id": job_id,
                "modified_count": result.modified_count
            }
        else:
            return {
                "message": "No changes detected",
                "job_id": job_id,
                "modified_count": 0
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job update error: {str(e)}")

@router.delete("/{job_id}", response_model=dict)
async def delete_job(
    job_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """İş ilanını siler (soft delete)"""
    try:
        if not ObjectId.is_valid(job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID")
        
        # Job'ı deaktif et (soft delete)
        result = await db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # FAISS index'den kaldır
        nlp_service.remove_job_from_index(job_id)
        
        return {
            "message": "Job deleted successfully",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job deletion error: {str(e)}")

@router.post("/search", response_model=List[JobResponse])
async def search_jobs(
    query: str = Query(..., description="Arama sorgusu"),
    limit: int = Query(10, ge=1, le=50, description="Maksimum sonuç sayısı"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Benzerlik eşiği"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Doğal dil işleme ile iş ilanlarını arar"""
    try:
        # Query için embedding oluştur
        query_embedding = nlp_service.create_embedding(query)
        
        # FAISS ile benzer job'ları bul
        similar_job_ids, similarities = nlp_service.search_similar_jobs(
            query_embedding, 
            k=limit * 2  # Filtre sonrası yeterli sonuç olması için
        )
        
        # Threshold'u geçenleri filtrele
        filtered_results = [
            (job_id, similarity) for job_id, similarity in zip(similar_job_ids, similarities)
            if similarity >= threshold
        ]
        
        if not filtered_results:
            return []
        
        # Job ID'leri al
        job_ids = [ObjectId(job_id) for job_id, _ in filtered_results[:limit]]
        
        # MongoDB'den job'ları çek
        jobs = await db.jobs.find({
            "_id": {"$in": job_ids},
            "is_active": True
        }).to_list(length=limit)
        
        # Sonuçları similarity skoruna göre sırala
        job_dict = {str(job['_id']): job for job in jobs}
        sorted_jobs = []
        
        for job_id, similarity in filtered_results[:limit]:
            if job_id in job_dict:
                job = job_dict[job_id]
                job_response = JobResponse(
                    id=str(job['_id']),
                    title=job.get('title', ''),
                    company=job.get('company', ''),
                    description=job.get('description', '')[:200] + "...",
                    skills_required=job.get('skills_required', []),
                    location=job.get('location'),
                    employment_type=job.get('employment_type', 'Full-time'),
                    created_at=job.get('created_at'),
                    similarity_score=float(similarity)  # Benzerlik skorunu ekle
                )
                sorted_jobs.append(job_response)
        
        return sorted_jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search error: {str(e)}")

@router.get("/stats/summary", response_model=dict)
async def get_job_stats(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """İş ilanı istatistiklerini getirir"""
    try:
        # Toplam iş sayısı
        total_jobs = await db.jobs.count_documents({"is_active": True})
        
        # Şirket bazında gruplandırma
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": "$company",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_companies = await db.jobs.aggregate(pipeline).to_list(length=10)
        
        # Lokasyon bazında gruplandırma
        pipeline[1]["$group"]["_id"] = "$location"
        top_locations = await db.jobs.aggregate(pipeline).to_list(length=10)
        
        # İstihdam türü bazında gruplandırma
        pipeline[1]["$group"]["_id"] = "$employment_type"
        employment_types = await db.jobs.aggregate(pipeline).to_list(length=None)
        
        return {
            "total_active_jobs": total_jobs,
            "top_companies": [{"company": item["_id"], "job_count": item["count"]} for item in top_companies],
            "top_locations": [{"location": item["_id"], "job_count": item["count"]} for item in top_locations],
            "employment_types": [{"type": item["_id"], "job_count": item["count"]} for item in employment_types]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval error: {str(e)}")