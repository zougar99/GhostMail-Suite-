import smtplib
import time
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from config import SMTP_CONFIG, OFFER_CONFIG, SEND_CONFIG
from template import TEMPLATES


# ─── Colors ───────────────────────────────────────────────────────────────────
class C:
    G  = "\033[92m"   # Green
    R  = "\033[91m"   # Red
    Y  = "\033[93m"   # Yellow
    CY = "\033[96m"   # Cyan
    W  = "\033[97m"   # White
    B  = "\033[1m"    # Bold
    RS = "\033[0m"    # Reset


BANNER = rf"""{C.CY}
   _____ _____  ___    __  __       _ _           
  / ____|  __ \/ _ \  |  \/  |     (_) |          
 | |    | |__) | |_| || \  / | __ _ _| | ___ _ __ 
 | |    |  ___/|  _ | | |\/| |/ _` | | |/ _ \ '__|
 | |____| |    | | | || |  | | (_| | | |  __/ |   
  \_____|_|    |_| |_||_|  |_|\__,_|_|_|\___|_|   
                                                    
        CPA Offer Email Sender Tool
{C.RS}"""


def print_line():
    print(f"{C.W}{'='*65}{C.RS}")


def load_emails(filepath="emails.txt"):
    """Load email list from file."""
    if not os.path.exists(filepath):
        print(f"{C.R}[!] File not found: {filepath}{C.RS}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip() and "@" in line]

    if not emails:
        print(f"{C.R}[!] No valid emails found in {filepath}{C.RS}")
        sys.exit(1)

    return emails


def connect_smtp():
    """Establish SMTP connection."""
    try:
        if SMTP_CONFIG["use_ssl"]:
            server = smtplib.SMTP_SSL(SMTP_CONFIG["server"], SMTP_CONFIG["port"], timeout=30)
        else:
            server = smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"], timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
        print(f"{C.G}[+] SMTP connected successfully!{C.RS}")
        return server
    except smtplib.SMTPAuthenticationError:
        print(f"{C.R}[!] SMTP Authentication failed! Check your email/password in config.py{C.RS}")
        print(f"{C.Y}    Tip: For Gmail, use an App Password (not your regular password){C.RS}")
        sys.exit(1)
    except Exception as e:
        print(f"{C.R}[!] SMTP connection failed: {e}{C.RS}")
        sys.exit(1)


def send_email(server, recipient, subject, html_body, sender_name, sender_email):
    """Send a single email."""
    msg = MIMEMultipart("alternative")
    msg["From"]    = f"{sender_name} <{sender_email}>"
    msg["To"]      = recipient
    msg["Subject"] = subject
    msg["X-Mailer"] = "Airbnb-Rewards-Mailer"

    # Attach HTML body
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    server.sendmail(sender_email, recipient, msg.as_string())


def save_log(results, log_file="send_log.txt"):
    """Save sending log."""
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"CPA Mailer Send Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 65 + "\n\n")

        sent     = [r for r in results if r["status"] == "sent"]
        failed   = [r for r in results if r["status"] == "failed"]

        f.write(f"SENT SUCCESSFULLY ({len(sent)}):\n")
        for r in sent:
            f.write(f"  [OK] {r['email']}\n")

        f.write(f"\nFAILED ({len(failed)}):\n")
        for r in failed:
            f.write(f"  [FAIL] {r['email']} - {r.get('error', 'unknown')}\n")

        f.write(f"\nTotal: {len(results)} | Sent: {len(sent)} | Failed: {len(failed)}\n")

    print(f"\n{C.CY}[*] Log saved to: {log_file}{C.RS}")


def main():
    print(BANNER)
    print_line()

    # ── Step 1: Load emails ──────────────────────────────────────────────
    print(f"\n{C.Y}[?] Email list source:{C.RS}")
    print(f"    {C.W}1{C.RS} - Load from file")
    print(f"    {C.W}2{C.RS} - Enter manually")
    choice = input(f"\n{C.CY}>>> Choice (1/2): {C.RS}").strip()

    if choice == "1":
        filepath = input(f"{C.CY}>>> File path (default: emails.txt): {C.RS}").strip()
        if not filepath:
            filepath = "emails.txt"
        emails = load_emails(filepath)
    elif choice == "2":
        print(f"{C.Y}[*] Enter emails one per line. Type 'done' when finished:{C.RS}")
        emails = []
        while True:
            e = input(f"{C.W}    > {C.RS}").strip()
            if e.lower() == "done":
                break
            if "@" in e:
                emails.append(e)
        if not emails:
            print(f"{C.R}[!] No emails entered.{C.RS}")
            sys.exit(1)
    else:
        print(f"{C.R}[!] Invalid choice.{C.RS}")
        sys.exit(1)

    print(f"\n{C.G}[+] Loaded {len(emails)} email(s){C.RS}")

    # ── Step 2: Choose template ──────────────────────────────────────────
    print(f"\n{C.Y}[?] Choose email template:{C.RS}")
    for key, tpl in TEMPLATES.items():
        print(f"    {C.W}{key}{C.RS} - {tpl['name']}")

    tpl_choice = input(f"\n{C.CY}>>> Template (1/2/3): {C.RS}").strip()
    if tpl_choice not in TEMPLATES:
        tpl_choice = "1"

    template_func = TEMPLATES[tpl_choice]["func"]
    template_name = TEMPLATES[tpl_choice]["name"]
    print(f"{C.G}[+] Using template: {template_name}{C.RS}")

    # ── Step 3: Confirm offer link ───────────────────────────────────────
    print(f"\n{C.Y}[*] Current offer link: {C.W}{OFFER_CONFIG['offer_link']}{C.RS}")
    new_link = input(f"{C.CY}>>> Enter new link (or press Enter to keep current): {C.RS}").strip()
    if new_link:
        OFFER_CONFIG["offer_link"] = new_link
    offer_link = OFFER_CONFIG["offer_link"]

    # ── Step 4: Confirm & Send ───────────────────────────────────────────
    print()
    print_line()
    print(f"{C.B}{C.CY}  SEND CONFIGURATION{C.RS}")
    print_line()
    print(f"  SMTP Server   : {SMTP_CONFIG['server']}:{SMTP_CONFIG['port']}")
    print(f"  Sender Email  : {SMTP_CONFIG['email']}")
    print(f"  Sender Name   : {SEND_CONFIG['sender_name']}")
    print(f"  Template      : {template_name}")
    print(f"  Offer Link    : {offer_link}")
    print(f"  Recipients    : {len(emails)}")
    print(f"  Delay         : {SEND_CONFIG['delay_between_emails']}s between emails")
    print_line()

    confirm = input(f"\n{C.Y}[?] Start sending? (y/n): {C.RS}").strip().lower()
    if confirm != "y":
        print(f"{C.R}[!] Cancelled.{C.RS}")
        sys.exit(0)

    # ── Connect SMTP ─────────────────────────────────────────────────────
    print(f"\n{C.CY}[*] Connecting to SMTP server...{C.RS}")
    server = connect_smtp()

    # ── Send emails ──────────────────────────────────────────────────────
    print(f"\n{C.CY}[*] Sending emails...{C.RS}\n")

    results = []
    sent_count = 0
    fail_count = 0

    for i, email in enumerate(emails, 1):
        print(f"{C.W}[{i}/{len(emails)}] Sending to: {email}{C.RS}", end="  ")

        subject, html_body = template_func(offer_link, email)

        retries = 0
        success = False

        while retries <= SEND_CONFIG["max_retries"]:
            try:
                send_email(
                    server, email, subject, html_body,
                    SEND_CONFIG["sender_name"], SMTP_CONFIG["email"]
                )
                sent_count += 1
                success = True
                print(f"{C.G}[SENT]{C.RS}")
                results.append({"email": email, "status": "sent"})
                break
            except smtplib.SMTPServerDisconnected:
                # Reconnect and retry
                print(f"{C.Y}[RECONNECTING...]{C.RS}", end=" ")
                try:
                    server = connect_smtp()
                except Exception:
                    pass
                retries += 1
            except Exception as e:
                retries += 1
                if retries > SEND_CONFIG["max_retries"]:
                    fail_count += 1
                    print(f"{C.R}[FAILED] {e}{C.RS}")
                    results.append({"email": email, "status": "failed", "error": str(e)})
                else:
                    time.sleep(1)

        # Rate limiting
        if i < len(emails):
            # Batch pause
            if i % SEND_CONFIG["batch_size"] == 0:
                print(f"\n{C.Y}[*] Batch pause ({SEND_CONFIG['batch_delay']}s)...{C.RS}\n")
                time.sleep(SEND_CONFIG["batch_delay"])
            else:
                time.sleep(SEND_CONFIG["delay_between_emails"])

    # ── Close connection ─────────────────────────────────────────────────
    try:
        server.quit()
    except Exception:
        pass

    # ── Summary ──────────────────────────────────────────────────────────
    print()
    print_line()
    print(f"{C.B}{C.CY}  SEND SUMMARY{C.RS}")
    print_line()
    print(f"  Total       : {len(results)}")
    print(f"  {C.G}Sent        : {sent_count}{C.RS}")
    print(f"  {C.R}Failed      : {fail_count}{C.RS}")
    print(f"  Success Rate: {(sent_count/len(results)*100):.1f}%" if results else "  N/A")
    print_line()

    # ── Save log ─────────────────────────────────────────────────────────
    save_log(results)
    print(f"\n{C.CY}[*] Done!{C.RS}\n")


if __name__ == "__main__":
    main()
