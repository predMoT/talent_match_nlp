def save_sample_data():
    """
    Örnek verileri dosyalara kaydeder
    """
    # Klasörleri oluştur
    os.makedirs("data/sample_cvs", exist_ok=True)
    os.makedirs("data/sample_jobs", exist_ok=True)
    
    # CV'leri kaydet
    cvs = create_sample_cvs()
    with open("data/sample_cvs/sample_cvs.json", "w", encoding="utf-8") as f:
        json.dump(cvs, f, ensure_ascii=False, indent=2)
    
    # İş ilanlarını kaydet  
    jobs = create_sample_jobs()
    with open("data/sample_jobs/sample_jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    print("✅ Örnek veriler oluşturuldu!")
    print(f"📄 {len(cvs)} CV kaydedildi")
    print(f"💼 {len(jobs)} İş ilanı kaydedildi")