import os
import smtplib
from email.mime.text import MIMEText
import feedparser

# Load your secure credentials from GitHub Actions
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# NEW CLEAN FEED: Explicitly filters Reddit for free Steam games only
RSS_FEED_URL = "https://www.reddit.com/r/FreeGameFindings/search.rss?q=site:steampowered.com+OR+site:steamcommunity.com&sort=new&restrict_sr=on"

def send_email(game_title, game_url):
    """Sends an email notification with the clean game name and direct link."""
    
    # Cleans up the title formatting slightly for readability
    clean_title = game_title.replace("&amp;", "&")
    
    body = (
        f"🔥 A free Steam game is available to claim!\n\n"
        f"🎮 Game: {clean_title}\n"
        f"🌐 Direct Link: {game_url}\n\n"
        f"Open the link, log in, and add it to your library permanently."
    )
    
    msg = MIMEText(body)
    msg['Subject'] = f"🎁 FREE STEAM GAME: {clean_title}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"Successfully sent email for: {clean_title}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_deals():
    """Parses the Reddit RSS feed for raw Steam links."""
    # Reddit feeds require a User-Agent header so they don't block the request
    feed = feedparser.parse(RSS_FEED_URL, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) SteamFreebieBot/1.0')
    
    if not feed.entries:
        print("No new games found in the feed during this hour.")
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
        link = entry.link
        
        # Double check to make sure it's a direct Steam store link
        if "steampowered.com" in link or "steamcommunity.com" in link:
            if link not in sent_games:
                send_email(entry.title, link)
                new_sent_games.append(link)

    # Save newly emailed games to history so you don't get duplicate emails next hour
    if new_sent_games:
        with open(history_file, "a") as f:
            for link in new_sent_games:
                f.write(link + "\n")

if __name__ == "__main__":
    check_deals()
