# GhostMail Suite

A collection of Python tools for email account checking, CPA email marketing, and email list management.

## Tools

### 1. Airbnb Email Checker (`airbnb_checker.py`)
Checks whether email addresses are registered on Airbnb using Selenium browser automation.
- Multi-threaded (parallel browser instances)
- Page reuse (no reload per email = 3-5x faster)
- Real-time results with live ETA and stats
- Resume support (skip already checked)
- Auto-saves results and registered-only hits

```bash
python airbnb_checker.py -f emails.txt -t 4 --resume
```

### 2. SHEIN Email Checker (`shein_checker.py`)
Checks whether email addresses are registered on SHEIN using Selenium browser automation.
Same features as Airbnb Checker (multi-thread, resume, live stats).

```bash
python shein_checker.py -f emails.txt -t 4 --resume
```

### 3. CPA Mailer (`mailer.py`)
Send CPA offer emails via SMTP with configurable templates, delays, batch processing, and retry logic.

```bash
python mailer.py
```

### 4. Email Splitter (`splitter.py`)
Split email:password combo lists into clean separate files (emails only, passwords only, clean combos).

```bash
python splitter.py combos.txt
```

### 5. Debug Utilities
- `debug_endpoints.py` - Discover API endpoints for Airbnb & SHEIN
- `debug_csrf.py` - Test CSRF tokens and authentication endpoints
- `debug_selenium.py` - Debug Selenium browser behavior with screenshots
- `debug_real.py` - Test real API endpoints found from page source

## Setup

```bash
pip install -r requirements.txt
pip install selenium webdriver-manager
```

Edit `config.py` with your SMTP credentials and offer details.

## Requirements

- Python 3.8+
- Chrome browser (for Selenium checkers)
- `requests`
- `selenium`
- `webdriver-manager`
