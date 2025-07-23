def create_faiss_indexes():
    """
    FAISS indekslerini oluşturur (boş template)
    """
    import numpy as np
    try:
        import faiss
        
        # Örnek embedding boyutu (BERT base = 768)
        dimension = 768
        
        # CV'ler için index
        cv_index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity için)
        
        # Jobs için index
        job_index = faiss.IndexFlatIP(dimension)
        
        # Kaydet
        os.makedirs("data/faiss_indexes", exist_ok=True)
        faiss.write_index(cv_index, "data/faiss_indexes/cv_index.faiss")
        faiss.write_index(job_index, "data/faiss_indexes/job_index.faiss")
        
        print("✅ FAISS indeksleri oluşturuldu!")
        
    except ImportError:
        print("⚠️ FAISS kurulu değil. pip install faiss-cpu")
        # Boş dosyalar oluştur
        with open("data/faiss_indexes/cv_index.faiss", "w") as f:
            f.write("# FAISS index placeholder")
        with open("data/faiss_indexes/job_index.faiss", "w") as f:
            f.write("# FAISS index placeholder")

if __name__ == "__main__":
    save_sample_data()
    create_faiss_indexes()E-ticaret platformları geliştirdim. ML algoritmalarını production'a aldım."
                },
                {
                    "company": "StartupX",
                    "position": "Python Developer",
                    "duration": "2019-2021",
                    "description": "Web API'leri ve microservice'ler geliştirdim."
                }
            ],
            "education": [
                {
                    "school": "İstanbul Teknik Üniversitesi",
                    "degree": "Bilgisayar Mühendisliği",
                    "year": "2019"
                }
            ],
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "cv_002", 
            "name": "Ayşe Demir",
            "email": "ayse.demir@email.com",
            "phone": "+90 555 987 6543",
            "summary": "Frontend geliştirici ve UX/UI tasarımcısı. React ve Vue.js konularında deneyimli.",
            "skills": ["React", "Vue.js", "JavaScript", "HTML5", "CSS3", "Figma", "Adobe XD"],
            "experience": [
                {
                    "company": "Design Agency",
                    "position": "Frontend Developer",
                    "duration": "2022-2024",
                    "description": "