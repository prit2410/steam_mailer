import os
import smtplib
from email.mime.text import MIMEText
import feedparser

# Load your secure credentials from GitHub Actions
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# FIXED URL: A reliable, highly-active freebie and deal RSS feed
RSS_FEED_URL = "https://gg.deals/news/feed/"

def send_email(game_title, game_url):
    """Sends an email notification when a game is found."""
    body = f"Good news! The tracker found an active update:\n\n'{game_title}'\n\nLink: {game_url}"
    msg = MIMEText(body)
    msg['Subject'] = f"🔥 STEAM TEST DEAL: {game_title}"
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
    """Parses the active feed and prints out games found."""
    feed = feedparser.parse(RSS_FEED_URL)
    
    # Check if feed is returning empty to prevent silent failures
    if not feed.entries:
        print("Warning: The RSS feed is empty or blocked. Forcing a direct test email instead...")
        send_email("Fallback System Test", "https://store.steampowered.com")
        return

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
        
        # TEST RULE: Triggers for literally ANY article or deal to guarantee an email
        if entry.link not in sent_games:
            send_email(entry.title, entry.link)
            new_sent_games.append(entry.link)
            break  # Break immediately after 1 game so you don't get spammed with 30 emails at once!

    # Save newly emailed games to history
    if new_sent_games:
        with open(history_file, "a") as f:
            for link in new_sent_games:
                f.write(link + "\n")

if __name__ == "__main__":
    check_deals()
