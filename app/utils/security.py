import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

# Konfigürasyon
SECRET_KEY = "your-secret-key-here"  # Prod'da environment variable olmalı
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class SecurityHelper:
    """
    Güvenlik işlemleri için yardımcı sınıf
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Şifreyi hash'ler (bcrypt kullanarak)
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Şifreyi doğrular
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """
        JWT access token oluşturur
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, credentials_exception) -> TokenData:
        """
        JWT token'ı doğrular
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        return token_data
    
    @staticmethod
    def generate_api_key() -> str:
        """
        API key oluşturur
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_file_content(content: bytes) -> str:
        """
        Dosya içeriğinin hash'ini hesaplar (duplicate detection için)
        """
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Dosya adını güvenli hale getirir
        """
        # Tehlikeli karakterleri kaldır
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Maksimum uzunluk sınırı
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename
    
    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: set) -> bool:
        """
        Dosya tipini doğrular
        """
        if '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in allowed_extensions
    
    @staticmethod
    def rate_limit_key(user_id: str, endpoint: str) -> str:
        """
        Rate limiting için anahtar oluşturur
        """
        return f"rate_limit:{user_id}:{endpoint}"

class FileSecurityValidator:
    """
    Dosya güvenliği için validator
    """
    
    ALLOWED_CV_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def validate_cv_file(cls, filename: str, file_size: int) -> tuple[bool, str]:
        """
        CV dosyasını doğrular
        
        Returns:
            (is_valid, error_message)
        """
        # Dosya boyutu kontrolü
        if file_size > cls.MAX_FILE_SIZE:
            return False, "Dosya boyutu çok büyük (max 10MB)"
        
        # Dosya tipi kontrolü
        if not SecurityHelper.validate_file_type(filename, cls.ALLOWED_CV_EXTENSIONS):
            return False, f"Desteklenmeyen dosya tipi. İzin verilenler: {cls.ALLOWED_CV_EXTENSIONS}"
        
        return True, ""
    
    @staticmethod
    def scan_for_malicious_content(content: str) -> bool:
        """
        Basit malicious content tarama
        """
        malicious_patterns = [
            'javascript:', 'vbscript:', 'onload=', 'onerror=',
            '<script', '</script>', 'eval(', 'document.cookie'
        ]
        
        content_lower = content.lower()
        for pattern in malicious_patterns:
            if pattern in content_lower:
                return True
        
        return False

# Authentication dependency
def get_current_user_dependency():
    """
    FastAPI dependency for authentication
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    def get_current_user(token: str):
        return SecurityHelper.verify_token(token, credentials_exception)
    
    return get_current_user

# Örnek kullanım
def demo_security():
    """
    Güvenlik özelliklerinin demo'su
    """
    security = SecurityHelper()
    
    # Şifre hash'leme
    password = "mypassword123"
    hashed = security.hash_password(password)
    print(f"Hashed password: {hashed}")
    print(f"Password verified: {security.verify_password(password, hashed)}")
    
    # JWT token
    token = security.create_access_token({"sub": "user123"})
    print(f"JWT Token: {token}")
    
    # API key
    api_key = security.generate_api_key()
    print(f"API Key: {api_key}")
    
    # Dosya güvenliği
    validator = FileSecurityValidator()
    is_valid, error = validator.validate_cv_file("resume.pdf", 1024*1024)
    print(f"File validation: {is_valid}, Error: {error}")

if __name__ == "__main__":
    demo_security()