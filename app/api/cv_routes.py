from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.models.cv import CVModel, CVCreate, CVResponse
from app.services.cv_parser import CVParser
from app.services.nlp_service import nlp_service
from app.utils.database import get_database

router = APIRouter(prefix="/api/cv", tags=["CV"])
cv_parser = CVParser()

@router.post("/upload", response_model=dict)
async def upload_cv(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """CV dosyası yükler ve parse eder"""
    try:
        # Dosya tipi kontrolü
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        # Dosya boyutu kontrolü (10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
        
        # CV'yi parse et
        parsed_data = cv_parser.parse_cv(file_content, file.filename)
        
        # Embedding oluştur
        full_text = f"{parsed_data['summary'] or ''} {' '.join(parsed_data['skills'])} {parsed_data['raw_text']}"
        embedding = nlp_service.create_embedding(full_text)
        
        # CV modelini oluştur
        cv_data = {
            **parsed_data,
            'embedding': embedding,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # MongoDB'ye kaydet
        result = await db.cvs.insert_one(cv_data)
        cv_id = str(result.inserted_id)
        
        # FAISS index'e ekle
        nlp_service.add_cv_to_index(cv_id, embedding)
        
        return {
            "message": "CV uploaded and processed successfully",
            "cv_id": cv_id,
            "extracted_data": {
                "name": parsed_data['full_name'],
                "email": parsed_data['email'],
                "skills": parsed_data['skills'][:10],  # İlk 10 skill
                "skills_count": len(parsed_data['skills'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV processing error: {str(e)}")

@router.get("/", response_model=List[CVResponse])
async def list_cvs(
    skip: int = 0,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """CV'leri listeler"""
    try:
        cursor = db.cvs.find().skip(skip).limit(limit).sort("created_at", -1)
        cvs = await cursor.to_list(length=limit)
        
        # Response formatına çevir
        cv_responses = []
        for cv in cvs:
            cv_responses.append(CVResponse(
                id=str(cv['_id']),
                full_name=cv.get('full_name', ''),
                email=cv.get('email', ''),
                skills=cv.get('skills', []),
                summary=cv.get('summary'),
                created_at=cv.get('created_at')
            ))
        
        return cv_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV listing error: {str(e)}")

@router.get("/{cv_id}", response_model=CVModel)
async def get_cv(
    cv_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Tek bir CV'yi getirir"""
    try:
        if not ObjectId.is_valid(cv_id):
            raise HTTPException(status_code=400, detail="Invalid CV ID")
        
        cv = await db.cvs.find_one({"_id": ObjectId(cv_id)})
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # ID'yi string'e çevir
        cv['_id'] = str(cv['_id'])
        
        return CVModel(**cv)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV retrieval error: {str(e)}")

@router.put("/{cv_id}", response_model=dict)
async def update_cv(
    cv_id: str,
    cv_update: CVCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """CV'yi günceller"""
    try:
        if not ObjectId.is_valid(cv_id):
            raise HTTPException(status_code=400, detail="Invalid CV ID")
        
        # Mevcut CV'yi kontrol et
        existing_cv = await db.cvs.find_one({"_id": ObjectId(cv_id)})
        if not existing_cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Embedding güncelle
        full_text = f"{cv_update.summary or ''} {' '.join(cv_update.skills)} {cv_update.raw_text}"
        embedding = nlp_service.create_embedding(full_text)
        
        # Güncelleme verisi
        update_data = {
            **cv_update.dict(),
            'embedding': embedding,
            'updated_at': datetime.utcnow()
        }
        
        # MongoDB'yi güncelle
        await db.cvs.update_one(
            {"_id": ObjectId(cv_id)},
            {"$set": update_data}
        )
        
        return {"message": "CV updated successfully", "cv_id": cv_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV update error: {str(e)}")

@router.delete("/{cv_id}", response_model=dict)
async def delete_cv(
    cv_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """CV'yi siler"""
    try:
        if not ObjectId.is_valid(cv_id):
            raise HTTPException(status_code=400, detail="Invalid CV ID")
        
        # CV'yi kontrol et
        cv = await db.cvs.find_one({"_id": ObjectId(cv_id)})
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # MongoDB'den sil
        await db.cvs.delete_one({"_id": ObjectId(cv_id)})
        
        # İlgili match'leri de sil
        await db.matches.delete_many({"cv_id": cv_id})
        
        return {"message": "CV deleted successfully", "cv_id": cv_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV deletion error: {str(e)}")

@router.get("/{cv_id}/skills", response_model=dict)
async def get_cv_skills(
    cv_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """CV'nin becerilerini detaylı şekilde getirir"""
    try:
        if not ObjectId.is_valid(cv_id):
            raise HTTPException(status_code=400, detail="Invalid CV ID")
        
        cv = await db.cvs.find_one({"_id": ObjectId(cv_id)})
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        skills = cv.get('skills', [])
        
        # Skill kategorilerine ayır (basit)
        technical_skills = []
        soft_skills = []
        
        technical_keywords = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'nodejs']
        soft_keywords = ['communication', 'leadership', 'teamwork', 'problem solving']
        
        for skill in skills:
            skill_lower = skill.lower()
            if any(tech in skill_lower for tech in technical_keywords):
                technical_skills.append(skill)
            elif any(soft in skill_lower for soft in soft_keywords):
                soft_skills.append(skill)
            else:
                technical_skills.append(skill)  # Default olarak technical
        
        return {
            "cv_id": cv_id,
            "total_skills": len(skills),
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "all_skills": skills
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skills retrieval error: {str(e)}")