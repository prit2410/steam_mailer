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
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Clean community feed tracking free game findings across all platforms
RSS_FEED_URL = "https://www.reddit.com/r/FreeGameFindings/new.rss"

# ==========================================
# OBJECT-ORIENTED STORE SCANNERS (OOP)
# ==========================================

class BaseScanner:
    """Parent class establishing the structural template for all storefronts."""
    def __init__(self, name, brand_color, border_color):
        self.name = name              # e.g., "Steam"
        self.brand_color = brand_color  # Hex code for HTML button backgrounds
        self.border_color = border_color # Hex code for HTML card borders

    def matches(self, title, link):
        """Fallback rule template; must be overridden by child classes."""
        return False


class SteamScanner(BaseScanner):
    """Child class specialized in isolating Steam deals."""
    def __init__(self):
        super().__init__(name="Steam", brand_color="#5c7e10", border_color="#2a475e")

    def matches(self, title, link):
        # Strict validation: Title must mention steam and the link must point to steam domains
        is_steam_url = "steampowered.com" in link or "steamcommunity.com" in link
        return is_steam_url and ("100%" in title or "free" in title)


class EpicGamesScanner(BaseScanner):
    """Child class specialized in isolating Epic Games Store deals."""
    def __init__(self):
        super().__init__(name="Epic Games", brand_color="#0074e4", border_color="#333333")

    def matches(self, title, link):
        # Captures titles tagged with [Epic Games] or links going to epicgames.com
        return "epicgames.com" in link or "[epic" in title or "epic games" in title


class GogScanner(BaseScanner):
    """Child class specialized in isolating GOG (Good Old Games) deals."""
    def __init__(self):
        super().__init__(name="GOG", brand_color="#bf00b1", border_color="#4c0046")

    def matches(self, title, link):
        # Captures titles tagged with [GOG] or linking to gog.com
        return "gog.com" in link or "[gog]" in title


# ==========================================
# NOTIFICATION ENGINE
# ==========================================

def send_combined_alerts(games_list):
    """Dispatches beautiful HTML emails and Discord posts for all platforms."""
    
    # 1. Build Dynamic HTML Cards based on the specific storefront design
    game_cards_html = ""
    discord_embeds = []

    for game in games_list:
        clean_title = game['title'].replace("&amp;", "&")
        store = game['store'] # This is the object template (SteamScanner, EpicScanner, etc.)
        
        # Append HTML Card string
        game_cards_html += f"""
        <div style="background-color: #1b2838; border: 1px solid {store.border_color}; border-radius: 4px; padding: 15px; margin-bottom: 15px; font-family: Arial, sans-serif;">
            <span style="background-color: {store.brand_color}; color: #ffffff; padding: 2px 8px; font-size: 11px; font-weight: bold; border-radius: 2px; text-transform: uppercase;">{store.name}</span>
            <h3 style="color: #66c0f4; margin-top: 8px; margin-bottom: 10px; font-size: 18px;">🎮 {clean_title}</h3>
            <a href="{game['link']}" style="display: inline-block; background-color: {store.brand_color}; color: #ffffff; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 2px; font-size: 14px;">Claim on {store.name}</a>
        </div>
        """

        # Append Discord Structure
        # Converts hex string to an integer decimal for Discord's API color fields
        hex_color_int = int(store.brand_color.lstrip('#'), 16)
        discord_embeds.append({
            "title": f"🎁 [{store.name}] Freebie: {clean_title}",
            "url": game['link'],
            "color": hex_color_int,
            "footer": {"text": "Multi-Store Freebie Bot"}
        })

    # 2. Email Transmission Processing
    html_layout = f"""
    <html>
        <body style="background-color: #101822; padding: 20px; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #171a21; padding: 20px; border-radius: 8px; border: 1px solid #1b2838;">
                <h1 style="color: #ffffff; text-align: center; font-size: 22px; margin-bottom: 25px; border-bottom: 2px solid #2a475e; padding-bottom: 10px;">🔥 Multi-Platform Freebie Alert</h1>
                {game_cards_html}
                <p style="color: #8f98a0; font-size: 11px; text-align: center; margin-top: 30px;">Automated Cross-Store Engine • GitHub Actions</p>
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

    # 3. Discord Webhook Processing
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
    """Fetches the master feed and evaluates titles across active store objects."""
    feed = feedparser.parse(RSS_FEED_URL, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) MultiStoreBot/1.0')
    
    if not feed.entries:
        print("Target RSS data source stream is empty this hour.")
        return

    history_file = "sent_games.txt"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            sent_games = f.read().splitlines()
    else:
        sent_games = []

    # Initialize our class scanner roster
    scanners = [SteamScanner(), EpicGamesScanner(), GogScanner()]
    
    found_new_games = []
    new_links_to_log = []

    for entry in feed.entries:
        title_lower = entry.title.lower()
        link = entry.link

        if link in sent_games:
            continue

        # Run polymorphic checks across all initialized storefront rules
        for store in scanners:
            if store.matches(title_lower, link):
                found_new_games.append({
                    'title': entry.title,
                    'link': link,
                    'store': store  # Storing the entire class instance preserves custom brand assets!
                })
                new_links_to_log.append(link)
                break # Match confirmed for this item; skip evaluating remaining scanners

    if found_new_games:
        send_combined_alerts(found_new_games)
        with open(history_file, "a") as f:
            for link in new_links_to_log:
                f.write(link + "\n")
    else:
        print("No new verified cross-platform freebies detected this cycle.")

if __name__ == "__main__":
    check_deals()
