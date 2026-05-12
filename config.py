# ─── SMTP Configuration ──────────────────────────────────────────────────────
# Fill in your SMTP details below.
# You can use Gmail, Outlook, custom SMTP, or any provider.
#
# Examples:
#   Gmail:    smtp.gmail.com      / port 587  (use App Password, not your real password)
#   Outlook:  smtp.office365.com  / port 587
#   Yahoo:    smtp.mail.yahoo.com / port 587
#   Custom:   your-smtp-server    / port 587 or 465
# ──────────────────────────────────────────────────────────────────────────────

SMTP_CONFIG = {
    "server":   "smtp.gmail.com",       # SMTP server address
    "port":     587,                     # 587 for TLS, 465 for SSL
    "use_ssl":  False,                   # True for port 465 (SSL), False for port 587 (TLS)
    "email":    "your-email@gmail.com",  # Your sender email
    "password": "your-app-password",     # Your app password (NOT your regular password)
}

# ─── Offer Configuration ─────────────────────────────────────────────────────
OFFER_CONFIG = {
    "offer_name":  "Airbnb Rewards",
    "offer_link":  "https://YOUR-OFFER-LINK-HERE.com",   # <-- Put your CPA offer link here
    "payout":      "$1.52",
    "offer_id":    "18442",
}

# ─── Sending Settings ────────────────────────────────────────────────────────
SEND_CONFIG = {
    "delay_between_emails": 3,    # Seconds between each email (avoid spam flags)
    "batch_size":           50,   # Emails per batch before longer pause
    "batch_delay":          60,   # Seconds to pause between batches
    "max_retries":          2,    # Retry count for failed emails
    "sender_name":          "Airbnb Rewards",  # Display name in inbox
}
