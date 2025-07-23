import json
import os
from datetime import datetime

def create_sample_cvs():
    """
    Örnek CV verilerini oluşturur
    """
    sample_cvs = [
        {
            "id": "cv_001",
            "name": "Ahmet Yılmaz",
            "email": "ahmet.yilmaz@email.com",
            "phone": "+90 555 123 4567",
            "summary": "5 yıl deneyimli Python geliştiricisi. Machine Learning ve web development alanlarında uzman.",
            "skills": ["Python", "Django", "Flask", "Machine Learning", "TensorFlow", "PostgreSQL", "Docker"],
            "experience": [
                {
                    "company": "Tech Solutions",
                    "position": "Senior Python Developer",
                    "duration": "2021-2024",
                    "description": "Responsive web siteleri ve mobil uygulamalar geliştirdim."
                }
            ],
            "education": [
                {
                    "school": "Boğaziçi Üniversitesi",
                    "degree": "Grafik Tasarım",
                    "year": "2022"
                }
            ],
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "cv_003",
            "name": "Mehmet Öz",
            "email": "mehmet.oz@email.com", 
            "phone": "+90 555 456 7890",
            "summary": "Data Scientist ve Machine Learning uzmanı. 3 yıl deneyimli.",
            "skills": ["Python", "R", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "SQL"],
            "experience": [
                {
                    "company": "Data Analytics Corp",
                    "position": "Data Scientist",
                    "duration": "2021-2024",
                    "description": "Müşteri segmentasyonu ve tahminleme modelleri geliştirdim."
                }
            ],
            "education": [
                {
                    "school": "ODTÜ",
                    "degree": "Matematik",
                    "year": "2021"
                }
            ],
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return sample_cvs