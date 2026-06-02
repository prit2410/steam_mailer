# 🎮 Steam Freebie Bot

An automated, cloud-hosted Python application that monitors live deal trackers and automatically emails you the exact second a game on Steam becomes **100% off (Free to Keep)**. 

No server management required—the entire application runs completely free 24/7 utilizing GitHub Actions.

---

## ✨ Features
* **Zero Cost Hosting:** Uses GitHub Actions to execute entirely in the cloud for $0.
* **Hourly Scans:** Automatically wakes up every hour to check for new freebies.
* **Smart Bundling:** Combines multiple free games into a single, clean email summary rather than spamming your inbox.
* **Direct Store Links:** Sends you the direct `store.steampowered.com` link to claim your game instantly.
* **Anti-Spam Memory:** Locally tracks sent deals in `sent_games.txt` so you only get notified about a game once.

---

## 🛠️ Technology Stack
* **Language:** Python 3.10+
* **Libraries:** `feedparser` (for parsing community RSS feeds), `smtplib` (for secure SSL email transport)
* **Automation:** GitHub Actions (Cron Scheduler)

---

## 📂 Repository Structure
```text
├── .github/workflows/
│   └── run_bot.yml      # GitHub Actions automation workflow
├── main.py              # Main Python logic for filtering & emailing
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
