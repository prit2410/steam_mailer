import os
import smtplib
from email.mime.text import MIMEText

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def send_test():
    print(f"Attempting to send email from {EMAIL_SENDER} to {EMAIL_RECEIVER}...")
    msg = MIMEText("If you are reading this, your GitHub secrets and email settings are 100% correct!")
    msg['Subject'] = "🚨 STEAM BOT: SYSTEM TEST SUCCESSFUL"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("✅ SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"❌ ERROR: Failed to send email. Reason: {e}")

if __name__ == "__main__":
    send_test()
