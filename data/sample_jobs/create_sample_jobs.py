def create_sample_jobs():
    """
    Örnek iş ilanı verilerini oluşturur
    """
    sample_jobs = [
        {
            "id": "job_001",
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "location": "İstanbul",
            "description": "E-ticaret platformumuz için deneyimli Python geliştiricisi arıyoruz. Django ve Flask deneyimi şart.",
            "requirements": [
                "5+ yıl Python deneyimi",
                "Django ve Flask framework bilgisi",
                "PostgreSQL veya MySQL deneyimi",
                "Docker ve Kubernetes bilgisi",
                "Git kullanımı"
            ],
            "skills_required": ["Python", "Django", "Flask", "PostgreSQL", "Docker", "Git"],
            "salary_range": "15000-25000 TL",
            "employment_type": "full-time",
            "experience_level": "senior",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "job_002",
            "title": "Frontend Developer (React)",
            "company": "Digital Agency",
            "location": "Ankara",
            "description": "Modern web uygulamaları geliştiren ekibimize React uzmanı frontend developer arıyoruz.",
            "requirements": [
                "3+ yıl React deneyimi",
                "JavaScript ES6+ bilgisi",
                "HTML5, CSS3, SASS/SCSS",
                "Redux veya Context API deneyimi",
                "Responsive design prensipleri"
            ],
            "skills_required": ["React", "JavaScript", "HTML5", "CSS3", "Redux", "SASS"],
            "salary_range": "12000-18000 TL",
            "employment_type": "full-time", 
            "experience_level": "mid",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "job_003",
            "title": "Machine Learning Engineer",
            "company": "AI Startup",
            "location": "İzmir",
            "description": "Makine öğrenmesi modellerini production ortamına taşıyacak ML Engineer arıyoruz.",
            "requirements": [
                "ML/DL algoritmaları deneyimi",
                "Python, TensorFlow/PyTorch",
                "Model deployment deneyimi",
                "Cloud platformları (AWS/Azure)",
                "Docker ve MLOps bilgisi"
            ],
            "skills_required": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AWS", "Docker"],
            "salary_range": "18000-30000 TL",
            "employment_type": "full-time",
            "experience_level": "senior",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return sample_jobs