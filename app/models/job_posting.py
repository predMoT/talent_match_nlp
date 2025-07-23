from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class JobPosting(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: str
    company: str
    description: str
    requirements: List[str] = []
    skills_required: List[str] = []
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = "Full-time"  # Full-time, Part-time, Contract
    experience_level: Optional[str] = None  # Entry, Mid, Senior
    raw_text: str
    embedding: Optional[List[float]] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    requirements: List[str] = []
    skills_required: List[str] = []
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = "Full-time"
    experience_level: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    skills_required: Optional[List[str]] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    is_active: Optional[bool] = None

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    description: str
    skills_required: List[str]
    location: Optional[str]
    employment_type: str
    created_at: datetime