import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request
import json
import psycopg2

# Load secure credentials from GitHub Actions
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DATABASE_URL = os.environ.get("DATABASE_URL")

# ==========================================
# OBJECT-ORIENTED STORE SCANNERS (API-DRIVEN)
# ==========================================

class BaseScanner:
    """Parent class establishing metadata and structural template for direct APIs."""
    def __init__(self, name, brand_color, border_color):
        self.name = name              
        self.brand_color = brand_color  
        self.border_color = border_color 

    def fetch_direct_deals(self):
        """Fallback method meant to be overridden by storefront child APIs."""
        return []


class SteamScanner(BaseScanner):
    """Child class hitting Steam's public storefront specials API directly."""
    def __init__(self):
        super().__init__(name="Steam", brand_color="#5c7e10", border_color="#2a475e")
        self.api_url = "https://store.steampowered.com/api/featuredcategories/?tab=specials"

    def fetch_direct_deals(self):
        deals = []
        try:
            req = urllib.request.Request(self.api_url, headers={'User-Agent': 'MultiStoreBot/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                specials = data.get('specials', {}).get('items', [])
                
                for item in specials:
                    # Filter for items that are currently 100% off or listed as 0 cost
                    if item.get('discount_percent') == 100 or item.get('final_price') == 0:
                        appid = item.get('id')
                        deals.append({
                            'title': item.get('name'),
                            'link': f"https://store.steampowered.com/app/{appid}/",
                            'store': self
                        })
        except Exception as e:
            print(f"Direct Steam API connection failed: {e}")
        return deals


class EpicGamesScanner(BaseScanner):
    """Child class fetching from Epic's static frontend API to bypass GraphQL edge blocks."""
    def __init__(self):
        super().__init__(name="Epic Games", brand_color="#0074e4", border_color="#333333")
        # Pivoting to the static promotional backend endpoint
        self.api_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"

    def fetch_direct_deals(self):
        deals = []
        try:
            # Standard browser user-agent is enough for this static endpoint
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            req = urllib.request.Request(self.api_url, headers=headers)

            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                elements = res_data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])

                for game in elements:
                    promotions = game.get('promotions')
                    # Verify the game has an active promotional offer running right now
                    if promotions and promotions.get('promotionalOffers'):
                        if len(promotions['promotionalOffers']) > 0:
                            offers = promotions['promotionalOffers'][0].get('promotionalOffers', [])
                            for offer in offers:
                                # A discount percentage of 0 means the cost has been fully subsidized (100% off)
                                discount = offer.get('discountSetting', {}).get('discountPercentage')
                                if discount == 0:
                                    
                                    # Epic stores the URL string in different keys depending on the game
                                    slug = game.get('productSlug')
                                    if not slug and game.get('catalogNs', {}).get('mappings'):
                                        slug = game['catalogNs']['mappings'][0].get('pageSlug')
                                    if not slug:
                                        slug = game.get('urlSlug')

                                    if slug:
                                        clean_slug = slug.replace('/home', '') # Clean up messy Epic database entries
                                        deals.append({
                                            'title': game.get('title'),
                                            'link': f"https://store.epicgames.com/en-US/p/{clean_slug}",
                                            'store': self
                                        })
        except Exception as e:
            print(f"Direct Epic Games API connection failed: {e}")
        return deals

# ==========================================
# NOTIFICATION ENGINE
# ==========================================

def send_combined_alerts(games_list):
    """Generates unified, platform-branded multi-channel alert formats."""
    game_cards_html = ""
    discord_embeds = []

    for game in games_list:
        clean_title = game['title'].replace("&amp;", "&")
        store = game['store']
        
        # Construct Dynamic HTML card
        game_cards_html += f"""
        <div style="background-color: #1b2838; border: 1px solid {store.border_color}; border-radius: 4px; padding: 15px; margin-bottom: 15px; font-family: Arial, sans-serif;">
            <span style="background-color: {store.brand_color}; color: #ffffff; padding: 2px 8px; font-size: 11px; font-weight: bold; border-radius: 2px; text-transform: uppercase;">{store.name}</span>
            <h3 style="color: #66c0f4; margin-top: 8px; margin-bottom: 10px; font-size: 18px;">🎮 {clean_title}</h3>
            <a href="{game['link']}" style="display: inline-block; background-color: {store.brand_color}; color: #ffffff; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 2px; font-size: 14px;">Claim on {store.name}</a>
        </div>
        """

        # Construct Discord embed profile
        hex_color_int = int(store.brand_color.lstrip('#'), 16)
        discord_embeds.append({
            "title": f"🎁 [{store.name}] Freebie: {clean_title}",
            "url": game['link'],
            "color": hex_color_int,
            "footer": {"text": "Official API Freebie Engine"}
        })

    # Assemble HTML document structure
    html_layout = f"""
    <html>
        <body style="background-color: #101822; padding: 20px; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #171a21; padding: 20px; border-radius: 8px; border: 1px solid #1b2838;">
                <h1 style="color: #ffffff; text-align: center; font-size: 22px; margin-bottom: 25px; border-bottom: 2px solid #2a475e; padding-bottom: 10px;">🔥 Direct API Storefront Alert</h1>
                {game_cards_html}
                <p style="color: #8f98a0; font-size: 11px; text-align: center; margin-top: 30px;">Automated Storefront Engine • GitHub Actions</p>
            </div>
        </body>
    </html>
    """

    subject = f"🎁 OFFICIAL STORE API ALERT: {len(games_list)} Games Found!"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.attach(MIMEText(html_layout, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Successfully dispatched official API HTML email notification.")
    except Exception as e:
        print(f"SMTP Transmission failure: {e}")

    if DISCORD_WEBHOOK_URL:
        payload = {"content": "🔔 **Official API Store Scrapes Complete!**", "embeds": discord_embeds}
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
# MAIN ROUTING ENGINE
# ==========================================

def check_deals():
    """Orchestrates connections, polls APIs, filters logs, and commits results."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        return

    # List of active store scanner APIs
    scanners = [SteamScanner(), EpicGamesScanner()]
    found_new_games = []

    for store in scanners:
        print(f"Querying active {store.name} storefront APIs...")
        active_deals = store.fetch_direct_deals()
        print(f"Fetched {len(active_deals)} total candidate deals from {store.name}.")
        
        for game in active_deals:
            link = game['link']
            
            # Parametric index verification check
            cursor.execute("SELECT id FROM tracked_games WHERE game_url = %s;", (link,))
            if cursor.fetchone() is not None:
                continue  # Already notified, skip
                
            found_new_games.append(game)
            
            # SQL write transaction
            cursor.execute(
                "INSERT INTO tracked_games (game_title, game_url, store_platform) VALUES (%s, %s, %s);",
                (game['title'], link, store.name)
            )

    if found_new_games:
        send_combined_alerts(found_new_games)
        conn.commit()  # Push database mutations to cluster live
        print(f"Operation complete. {len(found_new_games)} entries written to Postgres.")
    else:
        print("No new direct storefront promotions located during this cycle.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_deals()
