import os
import smtplib
from email.mime.text import MIMEText
import feedparser

# Load your secure credentials from GitHub Actions
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# The RSS feed that updates when games go 100% off
RSS_FEED_URL = "https://isthereanydeal.com/rss/specials/"

def send_email(game_title, game_url):
    """Sends an email notification when a free game is found."""
    body = f"Good news! '{game_title}' is currently free (100% off) on Steam.\n\nClaim it here: {game_url}"
    msg = MIMEText(body)
    msg['Subject'] = f"🔥 FREE STEAM GAME: {game_title}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"Successfully sent email for: {game_title}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_deals():
    """Parses the RSS feed and checks for 100% off Steam games."""
    feed = feedparser.parse(RSS_FEED_URL)
    
    # Track games we've already emailed about to prevent spam
    history_file = "sent_games.txt"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            sent_games = f.read().splitlines()
    else:
        sent_games = []

    new_sent_games = []

    for entry in feed.entries:
        title = entry.title.lower()
        # Look for indicators of a 100% discount or 'free' on Steam
        if "steam" in title:
            if entry.link not in sent_games:
                send_email(entry.title, entry.link)
                new_sent_games.append(entry.link)

    # Save newly emailed games to history
    if new_sent_games:
        with open(history_file, "a") as f:
            for link in new_sent_games:
                f.write(link + "\n")

if __name__ == "__main__":
    check_deals()
