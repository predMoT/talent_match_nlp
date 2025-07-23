# TalentMatch NLP

Yapay zeka ve NLP tabanlı CV & İş İlanı Eşleştirme Sistemi

## Özellikler
- CV parsing ve analiz (PDF, DOCX)
- İş ilanı yönetimi
- NLP tabanlı eşleştirme (BERT, TF-IDF, cosine similarity)
- FAISS ile hızlı vektör arama
- MongoDB ile veri saklama
- FastAPI backend, modern frontend

## Kurulum

### 1. Gerekli Araçlar
- Docker & Docker Compose
- Python 3.10+ (geliştirme için)

### 2. Çalıştırma (Docker ile)
```bash
docker-compose up --build
```

### 3. Geliştirici Modu (Manuel)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Frontend
- Frontend şablonları `frontend/templates` altında.
- Statik dosyalar için `frontend/static` dizini oluşturabilirsiniz.

## API Dokümantasyonu
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Ortam Değişkenleri
- `.env` dosyası ile MongoDB ve model ayarlarını özelleştirebilirsiniz.

## Testler
```bash
pytest --cov=app
```

## Katkı
Pull request ve issue açabilirsiniz.