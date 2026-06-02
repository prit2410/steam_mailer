import os
import smtplib
from email.mime.text import MIMEText
import feedparser

# Load your secure credentials from GitHub Actions
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# The clean Reddit RSS feed that looks specifically for free Steam games
RSS_FEED_URL = "https://www.reddit.com/r/FreeGameFindings/search.rss?q=site:steampowered.com+OR+site:steamcommunity.com&sort=new&restrict_sr=on"

def send_combined_email(games_list):
    """Sends exactly ONE email containing all the newly found free games."""
    
    # Build a clean text body by looping through our bundle
    body_elements = ["🔥 New free Steam games have been detected!\n", "---"]
    for game in games_list:
        clean_title = game['title'].replace("&amp;", "&")
        body_elements.append(f"🎮 Game: {clean_title}")
        body_elements.append(f"🌐 Direct Link: {game['link']}\n---")
    
    body_elements.append("\nOpen the links, log in, and add them to your library permanently.")
    body = "\n".join(body_elements)
    
    # Determine subject line based on how many games were found
    if len(games_list) == 1:
        subject = f"🎁 FREE STEAM GAME: {games_list[0]['title'].replace('&amp;', '&')}"
    else:
        subject = f"🎁 MULTIPLE FREE STEAM GAMES FOUND ({len(games_list)} Games)"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"Successfully sent a bundled email containing {len(games_list)} games.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_deals():
    """Parses the feed and bundles new entries together to prevent duplicate alerts."""
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

    found_new_games = []
    new_links_to_log = []

    for entry in feed.entries:
        link = entry.link
        
        # Ensure it's a valid Steam store link
        if "steampowered.com" in link or "steamcommunity.com" in link:
            if link not in sent_games:
                # Instead of sending an email here, add it to our bundle list
                found_new_games.append({'title': entry.title, 'link': link})
                new_links_to_log.append(link)

    # If our bundle list isn't empty, send exactly ONE email
    if found_new_games:
        send_combined_email(found_new_games)
        
        # Save newly emailed games to history so you don't get them next hour
        with open(history_file, "a") as f:
            for link in new_links_to_log:
                f.write(link + "\n")
    else:
        print("No brand new free games detected since the last check.")

if __name__ == "__main__":
    check_deals()
