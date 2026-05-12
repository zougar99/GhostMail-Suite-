"""Debug: See exactly what text SHEIN & Airbnb show after login attempts."""
import time, random, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

if os.name == "nt": os.system("")

def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    svc = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=svc, options=opts)
    d.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return d

def close_popups(d):
    for sel in ["[aria-label='Close']", "[class*='close']", "button[class*='close']"]:
        try:
            for el in d.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed():
                    d.execute_script("arguments[0].click();", el)
                    time.sleep(0.3)
        except: pass
    try:
        for b in d.find_elements(By.XPATH, "//button[contains(text(),'Accept') or contains(text(),'OK') or contains(text(),'Got')]"):
            if b.is_displayed():
                d.execute_script("arguments[0].click();", b)
    except: pass

print("Starting browser...")
d = make_driver()

# ====== SHEIN DEBUG ======
for test_email in ["test@gmail.com", "xyzfake99887766@gmail.com"]:
    print(f"\n{'='*60}")
    print(f"  SHEIN - Testing: {test_email}")
    print(f"{'='*60}")

    d.get("https://us.shein.com/user/auth/login")
    time.sleep(4)
    close_popups(d)
    time.sleep(1)

    # Screenshot
    d.save_screenshot(f"debug_shein_{test_email.split('@')[0]}.png")

    # Try to find and click email tab
    for sel in ["//span[contains(text(),'email')]", "//span[contains(text(),'Email')]",
                "//div[contains(text(),'email')]"]:
        try:
            el = d.find_element(By.XPATH, sel)
            if el.is_displayed():
                d.execute_script("arguments[0].click();", el)
                time.sleep(1)
                break
        except: pass

    # Find email input
    ei = None
    for sel in ["input[type='email']", "input[name='email']", "input[placeholder*='mail']",
                "input[placeholder*='Email']"]:
        try:
            ei = d.find_element(By.CSS_SELECTOR, sel)
            if ei.is_displayed(): break
            ei = None
        except: pass

    if not ei:
        print("  Could not find email input!")
        body = d.find_element(By.TAG_NAME, "body").text
        print(f"  Body text:\n{body[:500]}")
        continue

    # Find password input
    pi = None
    try:
        pi = d.find_element(By.CSS_SELECTOR, "input[type='password']")
    except: pass

    # Type
    ei.clear()
    ei.send_keys(test_email)
    time.sleep(0.5)
    if pi:
        pi.clear()
        pi.send_keys(f"WrongP@ss{random.randint(1000,9999)}")
    time.sleep(0.5)

    # Click sign in
    for sel in ["button[type='submit']", "button.j-sign-in"]:
        try:
            b = d.find_element(By.CSS_SELECTOR, sel)
            if b.is_displayed():
                d.execute_script("arguments[0].click();", b)
                break
        except: pass
    else:
        try:
            b = d.find_element(By.XPATH, "//button[contains(text(),'Sign') or contains(text(),'Log') or @type='submit']")
            d.execute_script("arguments[0].click();", b)
        except:
            if pi: pi.send_keys(Keys.RETURN)

    time.sleep(5)
    d.save_screenshot(f"debug_shein_after_{test_email.split('@')[0]}.png")

    # Get ALL visible text
    body = d.find_element(By.TAG_NAME, "body").text
    print(f"  Page URL: {d.current_url}")
    print(f"  Body text (first 800 chars):")
    print(f"  ---")
    print(f"  {body[:800]}")
    print(f"  ---")

    # Look for error/toast messages specifically
    for css in [".S-toast", "[class*='toast']", "[class*='error']", "[class*='tip']",
                "[class*='alert']", "[class*='message']", "[class*='notice']", "[role='alert']"]:
        try:
            els = d.find_elements(By.CSS_SELECTOR, css)
            for el in els:
                if el.text.strip():
                    print(f"  >> {css}: '{el.text.strip()}'")
        except: pass

# ====== AIRBNB DEBUG ======
for test_email in ["test@gmail.com", "xyzfake99887766@gmail.com"]:
    print(f"\n{'='*60}")
    print(f"  AIRBNB - Testing: {test_email}")
    print(f"{'='*60}")

    d.get("https://www.airbnb.com/login")
    time.sleep(4)
    close_popups(d)
    time.sleep(1)

    d.save_screenshot(f"debug_airbnb_{test_email.split('@')[0]}.png")

    # Click email option
    for sel in ["//button[contains(text(),'email')]", "//button[contains(text(),'Email')]",
                "//*[@data-testid='social-auth-button-email']"]:
        try:
            el = d.find_element(By.XPATH, sel)
            if el.is_displayed():
                d.execute_script("arguments[0].click();", el)
                time.sleep(2)
                break
        except: pass

    # Find email input
    ei = None
    for sel in ["input[type='email']", "input[name='email']", "#email-login-email",
                "input[placeholder*='Email']", "input[autocomplete='username']"]:
        try:
            el = d.find_element(By.CSS_SELECTOR, sel)
            if el.is_displayed():
                ei = el
                break
        except: pass

    if not ei:
        print("  Could not find email input!")
        body = d.find_element(By.TAG_NAME, "body").text
        print(f"  Body:\n{body[:500]}")
        continue

    ei.clear()
    ei.send_keys(test_email)
    time.sleep(0.5)

    # Click Continue
    for sel in ["button[type='submit']", "button[data-testid='signup-login-submit-btn']"]:
        try:
            b = d.find_element(By.CSS_SELECTOR, sel)
            if b.is_displayed():
                d.execute_script("arguments[0].click();", b)
                break
        except: pass
    else:
        try:
            b = d.find_element(By.XPATH, "//button[@type='submit' or contains(text(),'Continue')]")
            d.execute_script("arguments[0].click();", b)
        except:
            ei.send_keys(Keys.RETURN)

    time.sleep(5)
    d.save_screenshot(f"debug_airbnb_after_{test_email.split('@')[0]}.png")

    body = d.find_element(By.TAG_NAME, "body").text
    print(f"  Page URL: {d.current_url}")
    print(f"  Body text (first 800 chars):")
    print(f"  ---")
    print(f"  {body[:800]}")
    print(f"  ---")

    # Check for password field
    try:
        pf = d.find_elements(By.CSS_SELECTOR, "input[type='password']")
        vis = [p for p in pf if p.is_displayed()]
        print(f"  Password fields visible: {len(vis)}")
    except:
        print(f"  Password fields: could not check")

d.quit()
print("\nDone! Check screenshot files for visual debug.")
