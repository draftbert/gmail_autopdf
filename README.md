# Gmail AutoPDF

A set-it-and-forget-it Dockerized tool that monitors your Gmail inbox, converts specific reports to clean PDFs, and uploads them directly to your OneDrive.

It handles the messy stuff—HTML rendering, PDF conversion, and cloud authentication—inside a container, so you don't have to deal with dependency hell.

## Quick Start

### 1. Prerequisites
You only need two things installed on your host machine:
- **Docker**
- **Rclone** (Only to generate the initial config file)

### 2. Setup Secrets
Create a file named `.env.secrets` in the root directory. This file is **gitignored** (or should be) to keep your credentials safe.
```ini
# Gmail Settings (Use an App Password!)
GMAIL_USER=your.email@gmail.com
GMAIL_PW=xxxx xxxx xxxx xxxx

# Telegram Notifications
TELEGRAM_IDA=123456789
TELEGRAM_TOKEN=your_bot_token_here

# OneDrive Config (Matches your Rclone setup)
ONEDRIVE_REMOTE=onedrive
ONEDRIVE_BASE_PATH=Backup/Emails

# Filter Criteria
SENDER=alerts@bank.com
KEYWORD_1=Daily Statement
KEYWORD_2=Confirmation
```

### 3. Configure Rclone (Host)
The container uses your local Rclone configuration. Run this once on your machine if you haven't already:
```bash
rclone config
```

Follow the steps to add a new remote (e.g., name it `onedrive`).

### 4. Run It
Just execute the helper script. It handles building, cleaning up old images, and mounting volumes.
```bash
sh run.sh
```

## How It Works (Docker)
This project runs fully isolated. The `run.sh` script mounts your local Rclone config directly into the container, so the internal Rclone instance knows exactly where to push files.

### The Stack
- **Base Image**: `python:3.11-bullseye` (Chosen over Alpine/Slim to ensure perfect wkhtmltopdf rendering without missing fonts or libraries).
- **PDF Engine**: `wkhtmltopdf` (Pre-installed in the container).
- **Sync**: `rclone` (Installs dynamically during build).

### Volumes & Persistence
The container mounts the following local paths:

- `~/.config/rclone/rclone.conf` → Maps credentials to the container.
- `./output` → PDFs are generated here before upload.
- `./backend/received_messages.txt` → Keeps track of processed emails.

## Configuration Guide

| Variable | Description |
|----------|-------------|
| `GMAIL_PW` | **Crucial**: Do not use your login password. Go to Google Account > Security > 2-Step Verification > App passwords to generate one. |
| `TELEGRAM_IDA` | Your Chat ID. You can find this by messaging @userinfobot. |
| `ONEDRIVE_REMOTE` | The exact name you gave the remote when running `rclone config`. |
| `SENDER` | The exact email address of the sender you want to track. |

## Project Structure
```
.
├── backend/
│   ├── app/                # Main Python logic
│   ├── Dockerfile          # Debian Bullseye based setup
│   └── requirements.txt    # Python dependencies
├── output/                 # Local PDF landing zone
├── .env.secrets            # Your credentials (create this!)
└── run.sh                  # One-click build & deploy script
```

## Troubleshooting

**"Rclone failed" error?**
Ensure the `ONEDRIVE_REMOTE` variable in `.env.secrets` matches the name in your local `rclone listremotes`.

**PDF looks weird?**
The container uses standard Linux fonts. If you need specific fonts, you may need to add a `COPY` instruction in the Dockerfile to move `.ttf` files into `/usr/share/fonts`.
