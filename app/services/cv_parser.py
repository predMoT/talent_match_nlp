import PyPDF2
import docx
import re
from typing import Dict, List, Optional
from io import BytesIO

class CVParser:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
        
    def parse_pdf(self, file_content: bytes) -> str:
        """PDF dosyasından text çıkarır"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"PDF parsing error: {str(e)}")
    
    def parse_docx(self, file_content: bytes) -> str:
        """DOCX dosyasından text çıkarır"""
        try:
            doc_file = BytesIO(file_content)
            doc = docx.Document(doc_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"DOCX parsing error: {str(e)}")
    
    def extract_email(self, text: str) -> Optional[str]:
        """Text'ten email adresi çıkarır"""
        emails = re.findall(self.email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Text'ten telefon numarası çıkarır"""
        phones = re.findall(self.phone_pattern, text)
        return phones[0] if phones else None
    
    def extract_name(self, text: str) -> Optional[str]:
        """Text'ten isim çıkarmaya çalışır (basit)"""
        lines = text.split('\n')
        for line in lines[:5]:  # İlk 5 satırda ara
            line = line.strip()
            if len(line) > 2 and len(line) < 50 and ' ' in line:
                # Basit isim kontrolü
                words = line.split()
                if len(words) >= 2 and all(word.replace('.', '').isalpha() for word in words):
                    return line
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """Text'ten yetenekleri çıkarır"""
        common_skills = [
            'python', 'java', 'javascript', 'react', 'nodejs', 'html', 'css',
            'sql', 'mongodb', 'postgresql', 'docker', 'kubernetes', 'aws',
            'git', 'linux', 'machine learning', 'data analysis', 'excel',
            'project management', 'agile', 'scrum', 'leadership', 'communication'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))  # Duplicate'leri kaldır
    
    def parse_cv(self, file_content: bytes, filename: str) -> Dict:
        """CV dosyasını parse eder ve structured data döner"""
        # Dosya tipine göre text çıkar
        if filename.lower().endswith('.pdf'):
            raw_text = self.parse_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            raw_text = self.parse_docx(file_content)
        else:
            raise Exception(f"Unsupported file type: {filename}")
        
        # Structured data çıkar
        cv_data = {
            'raw_text': raw_text,
            'full_name': self.extract_name(raw_text) or "Unknown",
            'email': self.extract_email(raw_text) or "",
            'phone': self.extract_phone(raw_text),
            'skills': self.extract_skills(raw_text),
            'summary': self._extract_summary(raw_text),
            'experience': self._extract_experience(raw_text),
            'education': self._extract_education(raw_text)
        }
        
        return cv_data
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Özet bölümünü çıkarır"""
        lines = text.split('\n')
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in summary_keywords):
                # Sonraki birkaç satırı al
                summary_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                    else:
                        break
                return ' '.join(summary_lines) if summary_lines else None
        return None
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Deneyim bilgilerini çıkarır (basit)"""
        # Bu gerçek projede daha gelişmiş olmalı
        experience_keywords = ['experience', 'work', 'employment', 'career']
        lines = text.split('\n')
        
        experiences = []
        in_experience_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in experience_keywords):
                in_experience_section = True
                continue
            
            if in_experience_section and line.strip():
                # Basit company detection
                if len(line.strip()) > 5:
                    experiences.append({
                        'company': line.strip(),
                        'position': 'Unknown',
                        'description': line.strip()
                    })
                if len(experiences) >= 3:  # Max 3 experience
                    break
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Eğitim bilgilerini çıkarır (basit)"""
        education_keywords = ['education', 'university', 'college', 'degree']
        lines = text.split('\n')
        
        education = []
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in education_keywords):
                if len(line.strip()) > 5:
                    education.append({
                        'institution': line.strip(),
                        'degree': 'Unknown',
                        'field_of_study': None
                    })
                if len(education) >= 2:  # Max 2 education
                    break
        
        return education