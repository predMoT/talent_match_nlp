from typing import List, Dict
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging

class NotificationService:
    def __init__(self):
        # Email konfigürasyonu (gerçek projede environment'tan al)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "your-email@gmail.com"
        self.email_password = "your-app-password"
        
        self.logger = logging.getLogger(__name__)
    
    def send_match_notification(self, candidate_email: str, matches: List[Dict]) -> bool:
        """Aday için iş eşleştirme bildirimi gönderir"""
        try:
            if not matches:
                return False
            
            subject = f"🎯 {len(matches)} New Job Match{'es' if len(matches) > 1 else ''} Found!"
            
            # Email içeriği oluştur
            html_content = self._create_job_match_email(matches)
            
            return self._send_email(candidate_email, subject, html_content)
            
        except Exception as e:
            self.logger.error(f"Match notification error: {e}")
            return False
    
    def send_cv_notification(self, company_email: str, matches: List[Dict]) -> bool:
        """Şirket için CV eşleştirme bildirimi gönderir"""
        try:
            if not matches:
                return False
            
            subject = f"🎯 {len(matches)} New Candidate Match{'es' if len(matches) > 1 else ''} Found!"
            
            # Email içeriği oluştur
            html_content = self._create_cv_match_email(matches)
            
            return self._send_email(company_email, subject, html_content)
            
        except Exception as e:
            self.logger.error(f"CV notification error: {e}")
            return False
    
    def _create_job_match_email(self, matches: List[Dict]) -> str:
        """İş eşleştirme email içeriği oluşturur"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">🎯 New Job Matches Found!</h2>
                <p>Great news! We found {len(matches)} job{'s' if len(matches) > 1 else ''} that match your profile:</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
        """
        
        for i, match in enumerate(matches[:3], 1):  # İlk 3 match'i göster
            html += f"""
                    <div style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px;">
                        <h4 style="margin: 0 0 5px 0; color: #3498db;">Match #{i}</h4>
                        <p style="margin: 5px 0;"><strong>Job:</strong> {match.get('job_title', 'N/A')}</p>
                        <p style="margin: 5px 0;"><strong>Company:</strong> {match.get('company', 'N/A')}</p>
                        <p style="margin: 5px 0;"><strong>Match Score:</strong> {match.get('overall_score', 0):.1%}</p>
                        <p style="margin: 5px 0;"><strong>Matched Skills:</strong> {', '.join(match.get('matched_skills', [])[:5])}</p>
                    </div>
            """
        
        html += """
                </div>
                
                <p>Login to your account to view all matches and apply to jobs.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" style="background: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px;">View All Matches</a>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from TalentMatch. 
                    You received this because you have an active profile with us.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_cv_match_email(self, matches: List[Dict]) -> str:
        """CV eşleştirme email içeriği oluşturur"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">🎯 New Candidate Matches Found!</h2>
                <p>Great news! We found {len(matches)} candidate{'s' if len(matches) > 1 else ''} that match your job posting:</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
        """
        
        for i, match in enumerate(matches[:3], 1):  # İlk 3 match'i göster
            html += f"""
                    <div style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px;">
                        <h4 style="margin: 0 0 5px 0; color: #e74c3c;">Candidate #{i}</h4>
                        <p style="margin: 5px 0;"><strong>Name:</strong> {match.get('candidate_name', 'N/A')}</p>
                        <p style="margin: 5px 0;"><strong>Match Score:</strong> {match.get('overall_score', 0):.1%}</p>
                        <p style="margin: 5px 0;"><strong>Key Skills:</strong> {', '.join(match.get('matched_skills', [])[:5])}</p>
                        <p style="margin: 5px 0;"><strong>Experience:</strong> {match.get('experience_level', 'N/A')}</p>
                    </div>
            """
        
        html += """
                </div>
                
                <p>Login to your company account to view full candidate profiles and contact them.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="#" style="background: #e74c3c; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px;">View All Candidates</a>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from TalentMatch. 
                    You received this because you have an active job posting with us.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Email gönderir"""
        try:
            # SMTP sunucusuna bağlan
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            # Email mesajını oluştur
            msg = MimeMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML içeriği ekle
            html_part = MimeText(html_content, 'html')
            msg.attach(html_part)
            
            # Email gönder
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Email sending error: {e}")
            return False
    
    def send_bulk_notifications(self, notifications: List[Dict]) -> Dict[str, int]:
        """Toplu bildirim gönderir"""
        results = {"success": 0, "failed": 0}
        
        for notification in notifications:
            try:
                email = notification.get('email')
                notification_type = notification.get('type')  # 'job_match' or 'cv_match'
                matches = notification.get('matches', [])
                
                if notification_type == 'job_match':
                    success = self.send_match_notification(email, matches)
                elif notification_type == 'cv_match':
                    success = self.send_cv_notification(email, matches)
                else:
                    success = False
                
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                self.logger.error(f"Bulk notification error: {e}")
                results["failed"] += 1
        
        return results

# Global instance
notification_service = NotificationService()