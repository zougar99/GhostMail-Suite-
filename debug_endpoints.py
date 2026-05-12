"""
Deep debug - find REAL working endpoints for Airbnb & SHEIN.
Tests every possible endpoint path and shows what works.
"""
import requests
import json
import re
import sys

s = requests.Session()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
s.headers.update({"User-Agent": UA})

email = "test123unique@gmail.com"

def test_url(method, url, headers=None, json_data=None, data=None, label=""):
    try:
        if method == "GET":
            r = s.get(url, headers=headers, timeout=15, allow_redirects=True)
        else:
            r = s.post(url, headers=headers, json=json_data, data=data, timeout=15, allow_redirects=True)
        body = r.text[:300].replace("\n", " ")
        print(f"  [{r.status_code}] {label}")
        if r.status_code != 404:
            print(f"       {body}")
        return r
    except Exception as e:
        print(f"  [ERR] {label} -> {e}")
        return None

print("=" * 70)
print("  AIRBNB ENDPOINT DISCOVERY")
print("=" * 70)

# First get airbnb session
print("\n-- Getting Airbnb session cookies --")
r = s.get("https://www.airbnb.com", timeout=15)
print(f"  Cookies: {list(s.cookies.keys())}")

# Find API key in page
keys = re.findall(r'"key"\s*:\s*"([a-z0-9]{20,})"', r.text)
api_key = keys[0] if keys else "d306zoyjsyarp7ifhu67rjxn52tv0t20"
print(f"  API Key: {api_key}")

# Find any interesting API URLs
api_urls = re.findall(r'"/api/v[23]/[^"]{5,50}"', r.text)
if api_urls:
    print(f"  Found API URLs in page: {api_urls[:10]}")

hdrs = {
    "User-Agent": UA,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.airbnb.com",
    "Referer": "https://www.airbnb.com/login",
    "X-Airbnb-Api-Key": api_key,
    "X-Airbnb-Supports-Airlock-V2": "true",
}

print("\n-- Testing Airbnb endpoints --\n")

# v2 endpoints
test_url("POST", f"https://www.airbnb.com/api/v2/authenticate?key={api_key}", hdrs,
         json_data={"email": email, "password": "wrongpass123"}, label="v2/authenticate")

test_url("POST", f"https://www.airbnb.com/api/v2/logins?key={api_key}", hdrs,
         json_data={"email": email, "password": "wrongpass123"}, label="v2/logins")

test_url("POST", f"https://www.airbnb.com/api/v2/forgot_passwords?key={api_key}", hdrs,
         json_data={"email": email}, label="v2/forgot_passwords")

test_url("POST", f"https://www.airbnb.com/api/v2/auth_requests?key={api_key}", hdrs,
         json_data={"email": email}, label="v2/auth_requests")

test_url("POST", f"https://www.airbnb.com/api/v2/signups?key={api_key}", hdrs,
         json_data={"email": email, "password": "Test123!", "first_name": "A", "last_name": "B"},
         label="v2/signups")

# v3 endpoints  
test_url("POST", f"https://www.airbnb.com/api/v3/authenticate?key={api_key}", hdrs,
         json_data={"email": email, "password": "wrongpass123"}, label="v3/authenticate")

test_url("POST", f"https://www.airbnb.com/api/v3/logins?key={api_key}", hdrs,
         json_data={"email": email, "password": "wrongpass123"}, label="v3/logins")

# Account check style
test_url("POST", f"https://www.airbnb.com/api/v2/accounts/check?key={api_key}", hdrs,
         json_data={"email": email}, label="v2/accounts/check")

test_url("POST", f"https://www.airbnb.com/api/v2/users/check?key={api_key}", hdrs,
         json_data={"email": email}, label="v2/users/check")

# Login page to find form
print("\n-- Fetching Airbnb login page --\n")
r2 = s.get("https://www.airbnb.com/login", timeout=15, allow_redirects=True)
print(f"  Login page status: {r2.status_code}, URL: {r2.url}")

# Search for API endpoints in login page JS
endpoints_in_js = re.findall(r'/api/v[23]/\w+', r2.text)
if endpoints_in_js:
    unique_eps = list(set(endpoints_in_js))
    print(f"  Endpoints found in login page: {unique_eps}")

# Search for GraphQL operations
gql_ops = re.findall(r'"operationName"\s*:\s*"(\w+)"', r2.text)
if gql_ops:
    print(f"  GraphQL operations: {list(set(gql_ops))}")

# Check account_check endpoint patterns
test_url("POST", "https://www.airbnb.com/api/v2/account_check", hdrs,
         json_data={"email": email}, label="v2/account_check")

test_url("GET", f"https://www.airbnb.com/api/v2/users?email={email}&key={api_key}",
         hdrs, label="v2/users?email=")

# Try the actual forgot password web page
print("\n-- Airbnb forgot password page --\n")
r3 = s.get("https://www.airbnb.com/forgot_password", timeout=15)
print(f"  Status: {r3.status_code}")
# Look for form action or API calls
forms = re.findall(r'action="([^"]*)"', r3.text)
if forms:
    print(f"  Form actions: {forms}")
api_in_forgot = re.findall(r'/api/v[23]/[^\s"\'<>]{3,60}', r3.text)
if api_in_forgot:
    print(f"  API in forgot page: {list(set(api_in_forgot))}")


print("\n\n" + "=" * 70)
print("  SHEIN ENDPOINT DISCOVERY")
print("=" * 70)

s2 = requests.Session()
s2.headers.update({"User-Agent": UA})

shein_domains = ["https://us.shein.com", "https://www.shein.com", "https://m.shein.com"]

for domain in shein_domains:
    print(f"\n-- Testing domain: {domain} --\n")
    
    try:
        r = s2.get(f"{domain}/user/auth/login", timeout=15, allow_redirects=True)
        print(f"  Login page: {r.status_code} -> {r.url}")
        
        # Find API endpoints
        apis = re.findall(r'/(?:api|user)/(?:auth|member)/\w+', r.text)
        if apis:
            print(f"  APIs found: {list(set(apis))[:15]}")
        
        # Find CSRF tokens
        csrf = re.findall(r'(?:csrf|token|_token)["\s:=]+([a-zA-Z0-9_\-]{20,})', r.text)
        if csrf:
            print(f"  Tokens: {csrf[:3]}")
    except Exception as e:
        print(f"  Error: {e}")

print()

# Test SHEIN API endpoints
shdrs = {
    "User-Agent": UA,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://us.shein.com",
    "Referer": "https://us.shein.com/user/auth/login",
    "X-Requested-With": "XMLHttpRequest",
}

print("-- Testing SHEIN endpoints --\n")

shein_eps = [
    ("POST", "/api/auth/login", {"email": email, "password": "wrong123"}),
    ("POST", "/user/auth/login", {"email": email, "password": "wrong123"}),
    ("POST", "/api/members/login", {"email": email, "password": "wrong123"}),
    ("POST", "/api/member/login", {"email": email, "password": "wrong123"}),
    ("POST", "/api/auth/sendcode/forgetpwd", {"email": email}),
    ("POST", "/user/auth/sendcode", {"email": email, "scene": "forgetpwd"}),
    ("POST", "/api/auth/forgetPassword/send", {"email": email}),
    ("POST", "/api/members/forgetPassword", {"email": email}),
    ("POST", "/api/member/resetPassword/sendCode", {"email": email}),
    ("POST", "/api/auth/register", {"email": email, "password": "Test123!"}),
    ("POST", "/user/auth/register", {"email": email, "password": "Test123!"}),
    ("POST", "/api/members/register", {"email": email, "password": "Test123!"}),
    ("POST", "/api/auth/checkEmail", {"email": email}),
    ("POST", "/api/members/check", {"email": email}),
    ("POST", "/api/member/email/check", {"email": email}),
    ("POST", "/api/auth/verifyEmail", {"email": email}),
    ("POST", "/user/auth/quickLogin", {"email": email}),
    ("POST", "/api/auth/quickRegister/emailCheck", {"email": email}),
]

for method, path, payload in shein_eps:
    for domain in ["https://us.shein.com", "https://www.shein.com"]:
        url = domain + path
        r = test_url(method, url, shdrs, json_data=payload, label=f"{domain}{path}")
        if r and r.status_code != 404 and r.status_code != 403:
            break  # Found a working domain, no need to try others

print("\n" + "=" * 70)
print("  DISCOVERY COMPLETE")
print("=" * 70)
