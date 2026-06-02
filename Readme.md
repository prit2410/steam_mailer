# 🎮 Multi-Store Freebie Bot (Official API Edition)

An automated, cloud-hosted Python application that queries official storefront production APIs and automatically sends cross-platform alerts the exact second a PC game becomes **100% off (Free to Keep)**.

By bypassing third-party scrapers and community feeds, this application interfaces directly with developer endpoints—running entirely **stateless** and utilizing cloud relational mapping for real-time memory tracking.

---

## ✨ Features

* **Zero Cost Hosting:** Uses GitHub Actions to execute entirely in the cloud for $0.
* **Hourly Scans:** Automatically wakes up every hour to check for new freebies.
* **Official Storefront APIs:** Interfaces directly with **Steam Storefront APIs** and **Epic Games GraphQL endpoints** for authoritative, real-time data.
* **Relational Storage Persistence:** Uses a hosted **PostgreSQL** cluster for secure tracking memory (no local files).
* **Smart Bundling:** Combines multiple free games into a single, clean summary instead of spamming notifications.
* **Dynamic HTML Emails:** Sends dark-themed, modern HTML notification cards with platform-specific branding.
* **Discord Integration:** Pushes rich embeds via Discord Webhooks with matching store colors.

---

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **Database Backend:** PostgreSQL (Hosted on Neon.tech)
* **Endpoints Integration:** REST (Steam) & GraphQL (Epic Games)
* **Libraries:**

  * `psycopg2-binary` (PostgreSQL adapter)
  * `smtplib` (secure email transport)
  * `urllib.request`, `json` (native networking & parsing)
* **Architecture:** Object-Oriented Programming (Polymorphic Inheritance) + Stateless Design
* **Automation:** GitHub Actions (Cron Scheduler)

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── run_bot.yml      # GitHub Actions workflow (stateless execution)
├── CODE_OF_CONDUCT.md   # Community guidelines
├── CONTRIBUTING.md      # Contribution instructions
├── LICENSE.md           # MIT License
├── main.py              # API polling + SQL verification logic
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ⚙️ How It Works Under the Hood

### 1. The Trigger

GitHub Actions runs on a cron schedule:

```cron
0 * * * *
```

*(every hour)*

---

### 2. The Direct API Scanner

The application uses specialized scanner classes:

* `SteamScanner` → Queries Steam storefront endpoints for pricing data
* `EpicGamesScanner` → Sends GraphQL queries to Epic’s backend to detect promotions

Each inherits from a common `BaseScanner` for consistent processing.

---

### 3. The SQL Verification Step

The bot connects securely to PostgreSQL and checks for duplicates:

```sql
SELECT id FROM tracked_games WHERE game_url = %s;
```

* If found → skipped (prevents duplicate alerts)
* If not found → processed further

---

### 4. The Dispatcher

New deals are transformed into:

* 📧 Styled **HTML email notifications**
* 💬 Rich **Discord webhook embeds**

Brand-specific colors and metadata are dynamically injected.

---

### 5. Database Commit

New entries are stored atomically:

```sql
INSERT INTO tracked_games (game_title, game_url, store_platform)
VALUES (%s, %s, %s);
```

This ensures persistent tracking without modifying repository files.

---

## 🔒 Configuration & GitHub Secrets

All sensitive data is stored using **GitHub Encrypted Secrets** and injected at runtime via environment variables (`os.environ`).

---

### Required Secrets

* `DATABASE_URL` → PostgreSQL connection string
* `EMAIL_SENDER` → Sender email
* `EMAIL_PASSWORD` → App password (Gmail recommended)
* `EMAIL_RECEIVER` → Destination inbox

---

### Optional Secrets

* `DISCORD_WEBHOOK_URL` → Discord webhook endpoint

> If omitted, Discord notifications are skipped gracefully.

---

## 🚀 Manual Maintenance & Testing

To run the bot manually:

1. Navigate to the **Actions** tab
2. Select the workflow (e.g., *Multi-Store Freebie Bot*)
3. Click **Run workflow**
4. Execute

---

## ⚖️ License

Distributed under the **MIT License**.
See `LICENSE.md` for more information.
