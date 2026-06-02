# 🎮 Multi-Store Freebie Bot

An automated, cloud-hosted Python application that monitors live community deal trackers and automatically sends cross-platform alerts the exact second a PC game becomes **100% off (Free to Keep)**.

No server management required—the entire application runs completely free 24/7 utilizing GitHub Actions.

---

## ✨ Features

* **Zero Cost Hosting:** Uses GitHub Actions to execute entirely in the cloud for $0.
* **Hourly Scans:** Automatically wakes up every hour to check for new freebies.
* **Multi-Store Polymorphism:** Seamlessly filters and identifies deals across **Steam**, **Epic Games Store**, and **GOG**.
* **Smart Bundling:** Combines multiple free games into a single, clean summary rather than spamming your channels.
* **Dynamic HTML Emails:** Delivers dark-themed, sleek HTML notification cards with buttons custom-branded to the game's storefront platform.
* **Discord Integration:** Uses native Discord Webhooks to instantly push beautifully formatted embeds matching platform brand colors.
* **Anti-Spam Memory:** Locally tracks sent deals in `sent_games.txt` so you only get notified about a specific game once.

---

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **Libraries:**

  * `feedparser` (for parsing community RSS feeds)
  * `smtplib` (for secure SSL email transport)
* **Architecture:** Object-Oriented Programming (Polymorphic Inheritance)
* **Automation:** GitHub Actions (Cron Scheduler)

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── run_bot.yml      # GitHub Actions automation workflow
├── CODE_OF_CONDUCT.md   # Community standards guidelines
├── CONTRIBUTING.md      # Instructions for open-source contributors
├── LICENSE.md           # Legal MIT Open-Source License
├── main.py              # Main OOP Python logic (HTML email & Discord dispatch)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ⚙️ How It Works Under the Hood

### 1. The Trigger

GitHub Actions runs a cron job scheduled at:

```cron
0 * * * *
```

(every hour)

---

### 2. The Scanner

The script fetches a live, community-curated RSS feed tracking verified freebie platform findings.

---

### 3. The Object-Oriented Filter

The engine processes data through storefront-specific classes:

* `SteamScanner`
* `EpicGamesScanner`
* `GogScanner`

Each inherits from a generic `BaseScanner` and applies platform-specific pattern matching to detect valid deals.

---

### 4. The Dispatcher

If a new match is found (not already in `sent_games.txt`), the bot dynamically constructs:

* A styled multipart **HTML email payload**
* A contextual **Discord webhook embed**

---

### 5. The Memory Save

The workflow automatically commits the updated history log back to the repository, ensuring continuity for the next run.

---

## 🔒 Configuration & GitHub Secrets

This repository uses **Encrypted GitHub Secrets** to securely store credentials and webhook URLs. These are injected at runtime via environment variables (`os.environ`).

---

### Required Secrets (Email)

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
