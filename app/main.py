from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from contextlib import asynccontextmanager

# API routes import
from .api.cv_routes import router as cv_router
from .api.job_routes import router as job_router
from .api.matching_routes import router as matching_router

# Database connection
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

# Global değişkenler
database = None
client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama başlangıç ve kapanış event'leri
    """
    # Startup
    global database, client
    
    # MongoDB bağlantısı
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Database'i app state'e ekle
    app.state.database = database
    
    print("🚀 TalentMatch NLP API başlatıldı!")
    print(f"📊 Database: {settings.DATABASE_NAME}")
    print(f"🌐 Docs: http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    if client:
        client.close()
    print("👋 Uygulama kapatıldı")

# FastAPI uygulaması oluştur
app = FastAPI(
    title="TalentMatch NLP API",
    description="""
    CV ve İş İlanı Eşleştirme Sistemi
    
    ## Özellikler
    * 📄 CV parsing ve analizi
    * 💼 İş ilanı yönetimi  
    * 🤖 NLP tabanlı eşleştirme
    * 📊 Benzerlik skoru hesaplama
    * 🔔 Bildirim sistemi
    
    ## Algoritma
    Sistem, TF-IDF ve BERT embeddings kullanarak
    cosine similarity hesaplar ve eşleştirme yapar.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Frontend bağlantısı için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (frontend için)
try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
except:
    pass  # Frontend yoksa devam et

# API route'larını ekle
app.include_router(cv_router)
app.include_router(job_router)
app.include_router(matching_router)

# Ana sayfa
@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Ana sayfa - API bilgileri
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TalentMatch NLP API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }
            .feature { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }
            .link { display: inline-block; margin: 10px 10px 10px 0; padding: 10px 20px; background: #007acc; color: white; text-decoration: none; border-radius: 5px; }
            .link:hover { background: #005fa3; }
            .status { color: #28a745; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 TalentMatch NLP API</h1>
            <p class="status">✅ Sistem Aktif</p>
            
            <div class="feature">
                <h3>📄 CV İşleme</h3>
                <p>PDF, DOC, DOCX formatlarında CV'leri parse eder ve analiz eder</p>
            </div>
            
            <div class="feature">
                <h3>💼 İş İlanı Yönetimi</h3>
                <p>İş ilanlarını kategorize eder ve gereksinimlerini analiz eder</p>
            </div>
            
            <div class="feature">
                <h3>🤖 Akıllı Eşleştirme</h3>
                <p>NLP algoritmaları ile CV-İş İlanı uyumluluğunu hesaplar</p>
            </div>
            
            <div class="feature">
                <h3>📊 Analitik</h3>
                <p>Detaylı eşleştirme raporları ve istatistikler</p>
            </div>
            
            <h3>🔗 Bağlantılar</h3>
            <a href="/docs" class="link">📚 API Dokümantasyonu</a>
            <a href="/redoc" class="link">📖 ReDoc</a>
            <a href="/api/cv" class="link">📄 CV API</a>
            <a href="/api/jobs" class="link">💼 İş İlanları</a>
            <a href="/api/matching" class="link">🎯 Eşleştirme</a>
            
            <hr style="margin: 30px 0;">
            <p style="text-align: center; color: #666;">
                <small>TalentMatch NLP v1.0.0 - Matematik & AI Powered</small>
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Sistem sağlık kontrolü
    """
    try:
        # Database bağlantısını test et
        await database.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0",
        "message": "TalentMatch NLP API is running!"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global hata yakalayıcı
    """
    return HTTPException(
        status_code=500,
        detail=f"Bir hata oluştu: {str(exc)}"
    )

# Development server için
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development için
        log_level="info"
    )