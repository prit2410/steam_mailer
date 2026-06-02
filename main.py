import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser
import urllib.request
import json

# Load secure credentials from GitHub Actions
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")  # New Optional Secret

RSS_FEED_URL = "https://www.reddit.com/r/FreeGameFindings/search.rss?q=site:steampowered.com+OR+site:steamcommunity.com&sort=new&restrict_sr=on"

def send_combined_email(games_list):
    """Sends exactly ONE visually stunning HTML email with all free games."""
    
    # 1. Generate the dynamic HTML game cards
    game_cards_html = ""
    for game in games_list:
        clean_title = game['title'].replace("&amp;", "&")
        game_cards_html += f"""
        <div style="background-color: #1b2838; border: 1px solid #2a475e; border-radius: 4px; padding: 15px; margin-bottom: 15px; font-family: Arial, sans-serif;">
            <h3 style="color: #66c0f4; margin-top: 0; font-size: 18px;">🎮 {clean_title}</h3>
            <p style="color: #c7d5df; font-size: 14px;">A new 100% off deal was detected on the Steam platform.</p>
            <a href="{game['link']}" style="display: inline-block; background-color: #5c7e10; color: #ffffff; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 2px; font-size: 14px; margin-top: 5px;">Claim Game</a>
        </div>
        """

    # 2. Complete HTML Document Layout
    html_body = f"""
    <html>
        <body style="background-color: #101822; margin: 0; padding: 20px; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #171a21; padding: 20px; border-radius: 8px; border: 1px solid #1b2838;">
                <h1 style="color: #ffffff; text-align: center; font-size: 24px; margin-bottom: 25px; border-bottom: 2px solid #2a475e; padding-bottom: 10px;">🎁 Steam Freebie Alert</h1>
                <p style="color: #acb2b8; font-size: 15px; margin-bottom: 20px;">The cloud scanner has located the following free titles available to claim permanently:</p>
                
                {game_cards_html}
                
                <p style="color: #8f98a0; font-size: 12px; text-align: center; margin-top: 30px;">Automated via Steam Freebie Bot • GitHub Actions</p>
            </div>
        </body>
    </html>
    """

    # 3. Create Multipart Email Payload
    if len(games_list) == 1:
        subject = f"🎁 FREE STEAM GAME: {games_list[0]['title'].replace('&amp;', '&')}"
    else:
        subject = f"🎁 MULTIPLE FREE STEAM GAMES FOUND ({len(games_list)} Games)"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"Successfully sent HTML email containing {len(games_list)} games.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_discord_webhook(games_list):
    """Pushes a sleek embedded message to Discord channel via native Webhook."""
    if not DISCORD_WEBHOOK_URL:
        return  # Silently skip if the user hasn't configured Discord

    embeds = []
    for game in games_list:
        clean_title = game['title'].replace("&amp;", "&")
        embeds.append({
            "title": f"🎁 Free Game: {clean_title}",
            "url": game['link'],
            "description": "Click the title to go directly to Steam and add it to your library!",
            "color": 6061584,  # Green accent color code
            "footer": {"text": "Steam Freebie Bot Scanner"}
        })

    payload = {
        "content": "🔥 **New Free Steam Games Detected!**",
        "embeds": embeds
    }

    try:
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/utf-8', 'User-Agent': 'SteamFreebieBot/1.0'}
        )
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 204]:
                print(f"Successfully pushed Discord alert for {len(games_list)} games.")
    except Exception as e:
        print(f"Discord Webhook notification failed: {e}")


def check_deals():
    """Parses the feed, bundles entries, and fires cross-platform alerts."""
    feed = feedparser.parse(RSS_FEED_URL, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) SteamFreebieBot/1.0')
    
    if not feed.entries:
        print("No new games found in the feed during this hour.")
        return

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
        if "steampowered.com" in link or "steamcommunity.com" in link:
            if link not in sent_games:
                found_new_games.append({'title': entry.title, 'link': link})
                new_links_to_log.append(link)

    if found_new_games:
        # Dispatch both notification mechanisms natively
        send_combined_email(found_new_games)
        send_discord_webhook(found_new_games)
        
        with open(history_file, "a") as f:
            for link in new_links_to_log:
                f.write(link + "\n")
    else:
        print("No brand new free games detected since the last check.")

if __name__ == "__main__":
    check_deals()
