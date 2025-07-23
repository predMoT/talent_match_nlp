from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

class Match(BaseModel):
    id: Optional[str] = Field(alias="_id")
    cv_id: str
    job_id: str
    similarity_score: float
    skill_match_score: float
    experience_match_score: float
    overall_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    match_details: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class MatchCreate(BaseModel):
    cv_id: str
    job_id: str
    similarity_score: float
    skill_match_score: float
    experience_match_score: float
    overall_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    match_details: Optional[Dict] = None

class MatchResponse(BaseModel):
    id: str
    cv_id: str
    job_id: str
    similarity_score: float
    skill_match_score: float
    experience_match_score: float
    overall_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    created_at: datetime

class CVJobMatch(BaseModel):
    cv: Dict
    job: Dict
    match: MatchResponse

class MatchFilters(BaseModel):
    min_score: Optional[float] = 0.0
    max_results: Optional[int] = 10
    job_id: Optional[str] = None
    cv_id: Optional[str] = None