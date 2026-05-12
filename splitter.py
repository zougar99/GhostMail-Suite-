#!/usr/bin/env python3
"""
Email:Password Splitter - Separates combo lists into clean files.
Supports formats: email:pass, email;pass, email|pass, email,pass
"""

import os
import sys
import re

if os.name == "nt":
    os.system("")

class C:
    G  = "\033[38;5;46m"
    R  = "\033[38;5;196m"
    Y  = "\033[38;5;226m"
    CY = "\033[38;5;51m"
    W  = "\033[38;5;255m"
    GR = "\033[38;5;245m"
    B  = "\033[1m"
    RS = "\033[0m"

BANNER = rf"""
{C.CY}{C.B}
    +==========================================+
    |     EMAIL : PASSWORD  SPLITTER           |
    |     Combo List Separator Tool            |
    +==========================================+
{C.RS}"""


def split_combos(input_file, output_dir="."):
    """Split email:password combos into separate files."""

    if not os.path.exists(input_file):
        print(f"  {C.R}[!] File not found: {input_file}{C.RS}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"  {C.CY}[*] Reading {input_file}...{C.RS}")
    print(f"  {C.W}[*] Total lines: {len(lines)}{C.RS}")
    print()

    emails_only = []
    passwords_only = []
    combos_clean = []
    skipped = 0
    dupes = 0
    seen_emails = set()

    for line in lines:
        # Detect separator: try : ; | ,
        email = None
        password = None

        for sep in [":", ";", "|", "\t"]:
            if sep in line:
                parts = line.split(sep, 1)  # Split only on first occurrence
                if len(parts) == 2 and "@" in parts[0]:
                    email = parts[0].strip()
                    password = parts[1].strip()
                    break

        # If no separator found, check if it's just an email
        if email is None and "@" in line:
            email = line.strip()
            password = ""

        # Validate email format
        if email and re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", email):
            # Check duplicates
            if email.lower() in seen_emails:
                dupes += 1
                continue
            seen_emails.add(email.lower())

            emails_only.append(email.lower())
            if password:
                passwords_only.append(password)
                combos_clean.append(f"{email.lower()}:{password}")
            else:
                passwords_only.append("")
                combos_clean.append(email.lower())
        else:
            skipped += 1

    # ── Save files ────────────────────────────────────────────────────────
    base = os.path.splitext(os.path.basename(input_file))[0]

    # 1. Emails only
    emails_file = os.path.join(output_dir, f"{base}_emails.txt")
    with open(emails_file, "w", encoding="utf-8") as f:
        for e in emails_only:
            f.write(e + "\n")

    # 2. Passwords only
    passwords_file = os.path.join(output_dir, f"{base}_passwords.txt")
    with open(passwords_file, "w", encoding="utf-8") as f:
        for p in passwords_only:
            if p:
                f.write(p + "\n")

    # 3. Clean combos (email:password)
    combos_file = os.path.join(output_dir, f"{base}_clean.txt")
    with open(combos_file, "w", encoding="utf-8") as f:
        for c in combos_clean:
            f.write(c + "\n")

    # ── Display results ───────────────────────────────────────────────────
    print(f"  {C.W}{'='*55}{C.RS}")
    print(f"  {C.B}{C.W}  RESULTS{C.RS}")
    print(f"  {C.W}{'='*55}{C.RS}")
    print()
    print(f"  {C.G}  Valid combos   : {len(emails_only)}{C.RS}")
    print(f"  {C.Y}  Duplicates     : {dupes}{C.RS}")
    print(f"  {C.R}  Skipped/Invalid: {skipped}{C.RS}")
    print()
    print(f"  {C.W}{'='*55}{C.RS}")
    print(f"  {C.B}{C.W}  OUTPUT FILES{C.RS}")
    print(f"  {C.W}{'='*55}{C.RS}")
    print()
    print(f"  {C.G}  [+] Emails only    -> {emails_file}{C.RS}")
    print(f"       ({len(emails_only)} emails)")
    print()
    print(f"  {C.G}  [+] Passwords only -> {passwords_file}{C.RS}")
    print(f"       ({len([p for p in passwords_only if p])} passwords)")
    print()
    print(f"  {C.G}  [+] Clean combos   -> {combos_file}{C.RS}")
    print(f"       ({len(combos_clean)} lines)")
    print()
    print(f"  {C.W}{'='*55}{C.RS}")

    # ── Preview ───────────────────────────────────────────────────────────
    print(f"\n  {C.CY}  PREVIEW (first 5):{C.RS}\n")
    for i, e in enumerate(emails_only[:5]):
        pw = passwords_only[i] if i < len(passwords_only) and passwords_only[i] else "---"
        print(f"    {C.W}{e:<40}{C.RS} {C.GR}|{C.RS}  {C.Y}{pw}{C.RS}")

    if len(emails_only) > 5:
        print(f"    {C.GR}... +{len(emails_only)-5} more{C.RS}")

    print(f"\n  {C.CY}[*] Done!{C.RS}\n")


def main():
    print(BANNER)

    # Check command line args
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input(f"  {C.CY}>>> Combo file (default: emails.txt): {C.RS}").strip()
        if not input_file:
            input_file = "emails.txt"

    split_combos(input_file)


if __name__ == "__main__":
    main()
