"""Test the REAL endpoints found from page source."""
import requests
import json
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
email = "test123@gmail.com"

def show(label, r):
    print(f"\n  [{r.status_code}] {label}")
    try:
        d = r.json()
        print(f"       {json.dumps(d, indent=2)[:500]}")
    except:
        print(f"       {r.text[:300]}")

# ===================== AIRBNB =====================
print("=" * 60)
print("  AIRBNB - Real Endpoints")
print("=" * 60)

s = requests.Session()
s.headers.update({"User-Agent": UA})
r = s.get("https://www.airbnb.com/login", timeout=15)
API_KEY = "d306zoyjsyarp7ifhu67rjxn52tv0t20"
cookies = dict(s.cookies)
print(f"  Session cookies: {list(cookies.keys())}")

hdrs = {
    "User-Agent": UA,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.airbnb.com",
    "Referer": "https://www.airbnb.com/login",
    "X-Airbnb-Api-Key": API_KEY,
    "X-Airbnb-Supports-Airlock-V2": "true",
}

# 1. login_for_web
r1 = s.post(f"https://www.airbnb.com/api/v2/login_for_web?key={API_KEY}",
            headers=hdrs, json={"email": email, "password": "wrongpass123!"}, timeout=15)
show("login_for_web", r1)

# 2. signup_for_web
r2 = s.post(f"https://www.airbnb.com/api/v2/signup_for_web?key={API_KEY}",
            headers=hdrs, json={"email": email, "password": "Test123!", "first_name": "John", "last_name": "Doe"}, timeout=15)
show("signup_for_web", r2)

# 3. auth_flows
r3 = s.post(f"https://www.airbnb.com/api/v2/auth_flows?key={API_KEY}",
            headers=hdrs, json={"email": email}, timeout=15)
show("auth_flows", r3)

# 4. forgot_password_api (form POST)
r4 = s.post("https://www.airbnb.com/forgot_password_api",
            headers={**hdrs, "Content-Type": "application/x-www-form-urlencoded"},
            data={"email": email}, timeout=15)
show("forgot_password_api (form)", r4)

# 5. v3/authenticate with proper format
r5 = s.post(f"https://www.airbnb.com/api/v3/authenticate?key={API_KEY}",
            headers=hdrs,
            json={"operationName": "loginForWeb", "variables": {"input": {"email": email, "password": "wrong123!"}}, "extensions": {}},
            timeout=15)
show("v3/authenticate (graphql style)", r5)

# 6. v3/logins
r6 = s.post(f"https://www.airbnb.com/api/v3/logins?key={API_KEY}",
            headers=hdrs,
            json={"email": email, "password": "wrong123!"},
            timeout=15)
show("v3/logins", r6)

# ===================== SHEIN =====================
print("\n\n" + "=" * 60)
print("  SHEIN - Real Endpoints")
print("=" * 60)

s2 = requests.Session()
s2.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})

# Get session from shein - use ma.shein.com since it redirects there
r = s2.get("https://ma.shein.com/user/auth/login", timeout=15)
print(f"  Status: {r.status_code}, URL: {r.url}")
print(f"  Cookies: {list(s2.cookies.keys())[:10]}")

# Find CSRF token
csrf_matches = re.findall(r'name="csrf-token"\s+content="([^"]+)"', r.text)
if not csrf_matches:
    csrf_matches = re.findall(r'csrf[_-]?token["\s:=]+([a-zA-Z0-9_\-]{20,})', r.text)
csrf = csrf_matches[0] if csrf_matches else ""
print(f"  CSRF: {csrf[:40]}...")

shdrs = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://ma.shein.com",
    "Referer": "https://ma.shein.com/user/auth/login",
    "X-Requested-With": "XMLHttpRequest",
}
if csrf:
    shdrs["X-CSRF-Token"] = csrf
    shdrs["csrf-token"] = csrf

# 1. chekAccountExist - THE KEY ENDPOINT!
r1 = s2.post("https://ma.shein.com/api/auth/chekAccountExist",
             headers=shdrs, json={"email": email}, timeout=15)
show("chekAccountExist (email only)", r1)

# Try with more params
r1b = s2.post("https://ma.shein.com/api/auth/chekAccountExist",
              headers=shdrs, json={"email": email, "scene": "login", "type": 1}, timeout=15)
show("chekAccountExist (with scene)", r1b)

# Try alias param
r1c = s2.post("https://ma.shein.com/api/auth/chekAccountExist",
              headers=shdrs, json={"alias": email, "scene": "login"}, timeout=15)
show("chekAccountExist (alias)", r1c)

# 2. emailSignin
r2 = s2.post("https://ma.shein.com/api/auth/emailSignin",
             headers=shdrs, json={"email": email, "password": "wrong123!"}, timeout=15)
show("emailSignin", r2)

# 3. sendCode
r3 = s2.post("https://ma.shein.com/api/auth/sendCode",
             headers=shdrs, json={"email": email, "scene": "forgetpwd"}, timeout=15)
show("sendCode (forgetpwd)", r3)

# Try on us.shein.com too
print("\n-- Also try us.shein.com --")
s3 = requests.Session()
s3.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
s3.get("https://us.shein.com", timeout=15, allow_redirects=True)

ushdrs = {**shdrs, "Origin": "https://us.shein.com", "Referer": "https://us.shein.com/user/auth/login"}

r4 = s3.post("https://us.shein.com/api/auth/chekAccountExist",
             headers=ushdrs, json={"email": email}, timeout=15)
show("us.shein chekAccountExist", r4)

r5 = s3.post("https://us.shein.com/api/auth/emailSignin",
             headers=ushdrs, json={"email": email, "password": "wrong123!"}, timeout=15)
show("us.shein emailSignin", r5)

print("\n" + "=" * 60)
print("  DONE")
print("=" * 60)
