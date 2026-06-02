# 🎮 Steam Freebie Bot

An automated, cloud-hosted Python application that monitors live community deal trackers and automatically sends cross-platform alerts the exact second a game on Steam becomes **100% off (Free to Keep)**.

No server management required—the entire application runs completely free 24/7 utilizing GitHub Actions.

---

## ✨ Features

* **Zero Cost Hosting:** Uses GitHub Actions to execute entirely in the cloud for $0.
* **Hourly Scans:** Automatically wakes up every hour to check for new freebies.
* **Smart Bundling:** Combines multiple free games into a single, clean email summary rather than spamming your channels.
* **Rich HTML Emails:** Replaces plain text with dark-themed, sleek HTML notification cards featuring direct "Claim Game" buttons.
* **Discord Integration:** Supports native Discord Webhooks to instantly push beautifully formatted embeds directly into your server.
* **Anti-Spam Memory:** Locally tracks sent deals in `sent_games.txt` so you only get notified about a game once.

---

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **Libraries:**

  * `feedparser` (for parsing community RSS feeds)
  * `smtplib` (for secure SSL email transport)
* **Automation:** GitHub Actions (Cron Scheduler)

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── run_bot.yml      # GitHub Actions automation workflow
├── CODE_OF_CONDUCT.md   # Community standards guidelines
├── CONTRIBUTING.md      # Instructions for open-source contributors
├── LICENSE.md           # Legal MIT Open-Source License
├── main.py              # Main Python logic (HTML email & Discord dispatch)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ⚙️ How It Works Under the Hood

### 1. The Trigger

GitHub Actions runs a cron job scheduled at `0 * * * *` (every hour).

### 2. The Scanner

The script fetches a live, community-curated Reddit RSS feed tracking verified Steam store changes.

### 3. The Filter

It cross-references active entries against a strict rule matching "free/100% off" labels alongside direct Steam store domain validation.

### 4. The Dispatcher

If a new match is found that hasn't been logged in `sent_games.txt`, it:

* Builds a multipart HTML email payload
* Executes a Discord webhook POST request concurrently

### 5. The Memory Save

The workflow automatically commits the updated history log back to the repository so it's ready for the next hour's run.

---

## 🔒 Configuration & GitHub Secrets

This repository utilizes **Encrypted GitHub Secrets**. Your private credentials and webhook URLs are completely hidden from public view and injected safely at runtime via environment variables (`os.environ`).

### Required Secrets (For Email)

* `EMAIL_SENDER`: The automated account executing the transmission (e.g., your bot's Gmail)
* `EMAIL_PASSWORD`: A secure 16-character Google App Password
* `EMAIL_RECEIVER`: Your personal target inbox

### Optional Secrets (For Discord)

* `DISCORD_WEBHOOK_URL`: The native webhook URL generated from your Discord channel settings

> If left unconfigured, the bot will gracefully skip Discord and only deliver the email alerts.

---

## 🚀 Manual Maintenance & Testing

If you ever want to trigger a manual check without waiting for the hour to roll over:

1. Navigate to the **Actions** tab at the top of the repository
2. Select **Steam Freebie Bot** from the left sidebar
3. Click the **Run workflow** dropdown on the right side
4. Click the green button

---

## ⚖️ License

Distributed under the MIT License. See `LICENSE.md` for more information.
