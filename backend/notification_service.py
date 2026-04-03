import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

EMAIL_SENDER = "vishaljoshi9694@gmail.com"
EMAIL_PASSWORD = "stbg nqhs gmif mgml"
TELEGRAM_BOT_TOKEN = "8468673237:AAGGkS35bhN1NhMzD7mX_Ff8UEJT3ee8vH8"

class NotificationService:
    @staticmethod
    def send_email(receiver_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = f"Alpha Engine <{EMAIL_SENDER}>"
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP Error: {e}")
            return False

    @staticmethod
    def send_telegram(chat_id, message):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            resp = requests.post(url, json=payload)
            return resp.status_code == 200
        except Exception as e:
            print(f"Telegram Error: {e}")
            return False

    @staticmethod
    def send_welcome(email, telegram_id=None):
        # Email Welcome
        html = f"""
        <div style="font-family: sans-serif; background: #020617; color: white; padding: 40px; border-radius: 20px;">
            <h1 style="color: #3b82f6;">Alpha Engine Initialized</h1>
            <p>Your notifications are now linked successfully.</p>
            <p><b>Enabled Channels:</b> Email & Telegram</p>
            <hr style="border: 1px solid #1e293b; margin: 20px 0;">
            <p style="font-size: 12px; color: #64748b;">This is an automated system report.</p>
        </div>
        """
        NotificationService.send_email(email, "Alpha Engine: Notification Link Success", html)
        
        # Telegram Welcome
        if telegram_id:
            msg = "🚀 <b>ALPHA ENGINE LINK SUCCESS</b>\n\nYour Telegram ID has been verified. You will now receive trade logs and daily AI research reports directly here."
            NotificationService.send_telegram(telegram_id, msg)
