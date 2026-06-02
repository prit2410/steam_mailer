import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser
import urllib.request
import json
import psycopg2  # Core relational database driver

# Load secure credentials from GitHub Actions
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DATABASE_URL = os.environ.get("DATABASE_URL")  # Your new PostgreSQL string

RSS_FEED_URL = "https://www.reddit.com/r/FreeGameFindings/new.rss"

# ==========================================
# OBJECT-ORIENTED STORE SCANNERS (OOP)
# ==========================================
class BaseScanner:
    def __init__(self, name, brand_color, border_color):
        self.name = name
        self.brand_color = brand_color
        self.border_color = border_color
    def matches(self, title, link):
        return False

class SteamScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="Steam", brand_color="#5c7e10", border_color="#2a475e")
    def matches(self, title, link):
        return ("steampowered.com" in link or "steamcommunity.com" in link) and ("100%" in title or "free" in title)

class EpicGamesScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="Epic Games", brand_color="#0074e4", border_color="#333333")
    def matches(self, title, link):
        return "epicgames.com" in link or "[epic" in title or "epic games" in title

class GogScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="GOG", brand_color="#bf00b1", border_color="#4c0046")
    def matches(self, title, link):
        return "gog.com" in link or "[gog]" in title

# ==========================================
# NOTIFICATION ENGINE
# ==========================================
def send_combined_alerts(games_list):
    game_cards_html = ""
    discord_embeds = []

    for game in games_list:
        clean_title = game['title'].replace("&amp;", "&")
        store = game['store']
        
        game_cards_html += f"""
        <div style="background-color: #1b2838; border: 1px solid {store.border_color}; border-radius: 4px; padding: 15px; margin-bottom: 15px; font-family: Arial, sans-serif;">
            <span style="background-color: {store.brand_color}; color: #ffffff; padding: 2px 8px; font-size: 11px; font-weight: bold; border-radius: 2px; text-transform: uppercase;">{store.name}</span>
            <h3 style="color: #66c0f4; margin-top: 8px; margin-bottom: 10px; font-size: 18px;">🎮 {clean_title}</h3>
            <a href="{game['link']}" style="display: inline-block; background-color: {store.brand_color}; color: #ffffff; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 2px; font-size: 14px;">Claim on {store.name}</a>
        </div>
        """

        hex_color_int = int(store.brand_color.lstrip('#'), 16)
        discord_embeds.append({
            "title": f"🎁 [{store.name}] Freebie: {clean_title}",
            "url": game['link'],
            "color": hex_color_int,
            "footer": {"text": "Multi-Store Freebie Bot"}
        })

    html_layout = f"""
    <html>
        <body style="background-color: #101822; padding: 20px; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #171a21; padding: 20px; border-radius: 8px; border: 1px solid #1b2838;">
                <h1 style="color: #ffffff; text-align: center; font-size: 22px; margin-bottom: 25px; border-bottom: 2px solid #2a475e; padding-bottom: 10px;">🔥 Multi-Platform Freebie Alert</h1>
                {game_cards_html}
                <p style="color: #8f98a0; font-size: 11px; text-align: center; margin-top: 30px;">Automated Database Engine • GitHub Actions</p>
            </div>
        </body>
    </html>
    """

    subject = f"🎁 MULTI-STORE FREEBIE ALERT: {len(games_list)} Games Found!"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.attach(MIMEText(html_layout, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Successfully dispatched multi-store HTML email notification.")
    except Exception as e:
        print(f"SMTP Transmission failure: {e}")

    if DISCORD_WEBHOOK_URL:
        payload = {"content": "🔔 **New Free Games Spotted Across Stores!**", "embeds": discord_embeds}
        try:
            req = urllib.request.Request(
                DISCORD_WEBHOOK_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'MultiStoreBot/1.0'}
            )
            with urllib.request.urlopen(req) as response:
                if response.status in [200, 204]:
                    print("Successfully pushed alerts to Discord channel.")
        except Exception as e:
            print(f"Discord Hook delivery failed: {e}")

# ==========================================
# MAIN EXECUTION ROUTINE
# ==========================================
def check_deals():
    feed = feedparser.parse(RSS_FEED_URL, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) MultiStoreBot/1.0')
    if not feed.entries:
        print("Target RSS data source stream is empty this hour.")
        return

    # Connect to the cloud relational database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        return

    scanners = [SteamScanner(), EpicGamesScanner(), GogScanner()]
    found_new_games = []

    for entry in feed.entries:
        title_lower = entry.title.lower()
        link = entry.link

        # Use SQL parameterized query to check if link already exists
        cursor.execute("SELECT id FROM tracked_games WHERE game_url = %s;", (link,))
        if cursor.fetchone() is not None:
            continue  # Already processed this game, skip it

        for store in scanners:
            if store.matches(title_lower, link):
                found_new_games.append({
                    'title': entry.title,
                    'link': link,
                    'store': store
                })
                
                # Write newly discovered game straight into your database architecture
                cursor.execute(
                    "INSERT INTO tracked_games (game_title, game_url, store_platform) VALUES (%s, %s, %s);",
                    (entry.title, link, store.name)
                )
                break

    if found_new_games:
        send_combined_alerts(found_new_games)
        conn.commit()  # Save changes to the live cloud database permanently
    else:
        print("No new verified cross-platform freebies detected this cycle.")

    # Clean up server resources
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_deals()
