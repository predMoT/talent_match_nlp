import re
import string
from typing import List, Set
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk

# NLTK verilerini indir (ilk çalıştırmada)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class TextProcessor:
    """
    NLP için metin ön işleme sınıfı
    Matematik geçmişinizi düşünürsek, bu adımlar vektörleştirme öncesi önemli
    """
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        # Türkçe stop words (basit liste)
        self.turkish_stop_words = {
            'bir', 've', 'bu', 'da', 'de', 'den', 'için', 'ile', 'olan',
            'var', 'yok', 'gibi', 'kadar', 'daha', 'çok', 'az', 'tüm',
            'her', 'hiç', 'bazı', 'ancak', 'fakat', 'ama', 'veya'
        }
        self.stop_words.update(self.turkish_stop_words)
        
        # Teknik terimler (korunacak)
        self.technical_terms = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'mongodb', 'postgresql', 'mysql', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'machine learning', 'deep learning',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        }
    
    def clean_text(self, text: str) -> str:
        """
        Metni temizler - HTML, özel karakterler vb.
        """
        if not text:
            return ""
        
        # HTML etiketlerini kaldır
        text = re.sub(r'<[^>]+>', '', text)
        
        # E-mail ve URL'leri kaldır
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize_and_normalize(self, text: str) -> List[str]:
        """
        Metni tokenize eder ve normalize eder
        
        Adımlar:
        1. Küçük harfe çevir
        2. Tokenize et
        3. Stop words'leri kaldır
        4. Punctuation kaldır
        5. Stemming uygula (teknik terimler hariç)
        """
        if not text:
            return []
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # İşlenmiş tokenlar
        processed_tokens = []
        
        for token in tokens:
            # Punctuation kontrolü
            if token in string.punctuation:
                continue
                
            # Sadece harf içeren tokenları al
            if not re.match(r'^[a-zA-ZğüşıöçĞÜŞİÖÇ]+$', token):
                continue
                
            # Stop words kontrolü
            if token in self.stop_words:
                continue
                
            # Çok kısa tokenları atla
            if len(token) < 2:
                continue
            
            # Teknik terimse stemming yapma
            if token in self.technical_terms:
                processed_tokens.append(token)
            else:
                # Stemming uygula
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
        
        return processed_tokens
    
    def extract_skills(self, text: str) -> Set[str]:
        """
        Metinden beceri/yetenek kelimelerini çıkarır
        Basit pattern matching ile
        """
        skills = set()
        text_lower = text.lower()
        
        # Yaygın beceri patterns
        skill_patterns = [
            r'\b(python|java|javascript|c\+\+|c#|php|ruby|go|rust)\b',
            r'\b(react|angular|vue|node\.?js|express)\b',
            r'\b(mongodb|postgresql|mysql|sqlite|redis)\b',
            r'\b(docker|kubernetes|jenkins|git|github)\b',
            r'\b(aws|azure|gcp|cloud|devops)\b',
            r'\b(machine learning|deep learning|ai|data science)\b',
            r'\b(tensorflow|pytorch|scikit-learn|keras)\b',
            r'\b(html|css|sass|less|bootstrap|tailwind)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            skills.update(matches)
        
        return skills
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        İki metin arası basit Jaccard similarity hesaplar
        Bu, daha karmaşık algoritmalara alternatif hızlı bir yöntem
        
        Jaccard Index = |A ∩ B| / |A ∪ B|
        """
        tokens1 = set(self.tokenize_and_normalize(text1))
        tokens2 = set(self.tokenize_and_normalize(text2))
        
        if not tokens1 and not tokens2:
            return 1.0
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)
    
    def extract_years_of_experience(self, text: str) -> int:
        """
        Metinden deneyim yılını çıkarır
        """
        patterns = [
            r'(\d+)\s*(?:year|yıl|sene)s?\s*(?:of\s*)?(?:experience|deneyim)',
            r'(\d+)\+?\s*(?:year|yıl)',
            r'(?:experience|deneyim).*?(\d+)\s*(?:year|yıl)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return int(matches[0])
        
        return 0

# Kullanım örneği ve test fonksiyonu
def test_text_processor():
    processor = TextProcessor()
    
    sample_text = """
    Experienced Python developer with 5 years of experience in 
    machine learning and web development. Skilled in React, MongoDB, 
    and AWS cloud services. <p>HTML tags should be removed.</p>
    """
    
    print("Original:", sample_text)
    print("Cleaned:", processor.clean_text(sample_text))
    print("Tokens:", processor.tokenize_and_normalize(sample_text))
    print("Skills:", processor.extract_skills(sample_text))
    print("Experience:", processor.extract_years_of_experience(sample_text))

if __name__ == "__main__":
    test_text_processor()