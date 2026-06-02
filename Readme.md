# 🎮 Multi-Store Freebie Bot (Database Edition)

An automated, cloud-hosted Python application that monitors live community deal trackers and automatically sends cross-platform alerts the exact second a PC game becomes **100% off (Free to Keep)**.

By integrating a dedicated cloud database, this application runs entirely **stateless**—eliminating repository file modifications and utilizing cloud relational mapping for instant tracking data memory.

---

## ✨ Features

* **Zero Cost Hosting:** Uses GitHub Actions to execute entirely in the cloud for $0.
* **Hourly Scans:** Automatically wakes up every hour to check for new freebies.
* **Relational Storage Persistence:** Migrated from flat-text storage (`sent_games.txt`) to a hosted **PostgreSQL** cluster for secure tracking memory.
* **Multi-Store Polymorphism:** Seamlessly filters and identifies deals across **Steam**, **Epic Games Store**, and **GOG** via an object-oriented code framework.
* **Smart Bundling:** Combines multiple free games into a single, clean summary rather than spamming your channels.
* **Dynamic HTML Emails:** Delivers dark-themed, sleek HTML notification cards with buttons custom-branded to the game's storefront platform.
* **Discord Integration:** Uses native Discord Webhooks to instantly push beautifully formatted embeds matching platform brand colors.

---

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **Database Backend:** PostgreSQL (Hosted on Neon.tech)
* **Libraries:**

  * `feedparser` (for parsing community RSS feeds)
  * `psycopg2-binary` (PostgreSQL adapter for Python)
  * `smtplib` (for secure SSL email transport)
* **Architecture:** Object-Oriented Programming (Polymorphic Inheritance) & Relational Storage Persistence
* **Automation:** GitHub Actions (Cron Scheduler)

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── run_bot.yml      # GitHub Actions automation workflow (Stateless execution)
├── CODE_OF_CONDUCT.md   # Community standards guidelines
├── CONTRIBUTING.md      # Instructions for open-source contributors
├── LICENSE.md           # Legal MIT Open-Source License
├── main.py              # Main OOP Python logic (SQL verification & alert dispatch)
├── requirements.txt     # Python dependencies (including database drivers)
└── README.md            # Project documentation
```

---

## ⚙️ How It Works Under the Hood

### 1. The Trigger

GitHub Actions runs a cron job scheduled at:

```cron
0 * * * *
```

*(every hour)*

---

### 2. The Scanner

The script fetches a live, community-curated RSS feed tracking verified freebie platform findings.

---

### 3. The SQL Verification Step

The program opens a secure TLS connection to the PostgreSQL database and executes a parameterized lookup query for each game:

```sql
SELECT id FROM tracked_games WHERE game_url = %s;
```

* If a record exists → the game is skipped (prevents duplicate alerts)
* If no record exists → the game is processed further

---

### 4. The Object-Oriented Filter & Dispatcher

New items are passed through specialized storefront classes:

* `SteamScanner`
* `EpicGamesScanner`
* `GogScanner`

Each extracts platform-specific branding and constructs:

* Styled **HTML email notifications**
* Rich **Discord webhook embeds**

---

### 5. Database Commit

Newly discovered freebies are stored in a single transaction:

```sql
INSERT INTO tracked_games (game_title, game_url, store_platform)
VALUES (%s, %s, %s);
```

This keeps the system fully stateless and independent of repository storage.

---

## 🔒 Configuration & GitHub Secrets

This project uses **GitHub Encrypted Secrets** to securely store credentials and connection strings. All secrets are injected at runtime via environment variables (`os.environ`).

---

### Required Secrets (Core Functionality)

* `DATABASE_URL` → PostgreSQL connection string (from Neon dashboard)
* `EMAIL_SENDER` → Sender email (e.g., bot Gmail)
* `EMAIL_PASSWORD` → 16-character Google App Password
* `EMAIL_RECEIVER` → Destination inbox

---

### Optional Secrets (Discord)

* `DISCORD_WEBHOOK_URL` → Discord channel webhook URL

> If not configured, Discord notifications are skipped gracefully.

---

## 🚀 Manual Maintenance & Testing

To trigger the bot manually:

1. Go to the **Actions** tab in your repository
2. Select the workflow (e.g., *Multi-Store Freebie Bot*)
3. Click **Run workflow**
4. Confirm execution

---

## ⚖️ License

Distributed under the **MIT License**.
See `LICENSE.md` for more information.
