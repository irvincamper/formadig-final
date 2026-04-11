#!/usr/bin/env python3
"""
Test script to diagnose login connection issues.
Run this AFTER starting run.py to verify the backend is working.
"""

import requests
import json
import time

BASE_URL = "http://localhost:10000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/auth/login"

print("=" * 80)
print("FORMADIG - Login Connection Test")
print("=" * 80)

# Test credentials (adjust to valid Supabase user)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

# ===== TEST 1: Check if server is running =====
print("\n[TEST 1] Checking if server is running...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"✅ Server is running (status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print(f"❌ CRITICAL: Cannot connect to server at {BASE_URL}")
    print("   Make sure run.py is running: python run.py")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# ===== TEST 2: Check if login endpoint exists =====
print("\n[TEST 2] Checking if /api/auth/login endpoint exists...")
try:
    # Send OPTIONS preflight request (CORS)
    response = requests.options(LOGIN_ENDPOINT, timeout=5)
    print(f"✅ Preflight OPTIONS request successful (status: {response.status_code})")
    print(f"   CORS headers: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
except requests.exceptions.ConnectionError:
    print(f"❌ Cannot reach {LOGIN_ENDPOINT}")
    exit(1)
except Exception as e:
    print(f"⚠️  OPTIONS request issue (may still work): {e}")

# ===== TEST 3: Test login with invalid credentials (should still connect) =====
print("\n[TEST 3] Testing login endpoint connectivity...")
payload = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD
}

try:
    response = requests.post(
        LOGIN_ENDPOINT,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"✅ Backend responded (status: {response.status_code})")
    print(f"   Response: {response.text[:200]}")
    
    # Even if auth fails, we know the server is working
    if response.status_code in [400, 401, 500]:
        print(f"   → Backend is WORKING but rejected the login")
        print(f"   → This is expected if credentials are wrong or Supabase is misconfigured")
    
except requests.exceptions.ConnectionError as e:
    print(f"❌ CRITICAL: Cannot connect to login endpoint")
    print(f"   Error: {e}")
    print(f"   → run.py may not have loaded the login backend")
    print(f"   → Check run.py output for backend loading errors")
    exit(1)
except requests.exceptions.Timeout:
    print(f"❌ Request timeout - server is slow or not responding")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# ===== TEST 4: Verify frontend can reach backend =====
print("\n[TEST 4] Checking frontend routing...")
try:
    response = requests.get(f"{BASE_URL}/modulos/login/vistas/login.html", timeout=5)
    if response.status_code == 200:
        print(f"✅ Login page is accessible from frontend")
    else:
        print(f"⚠️  Login page returned status: {response.status_code}")
except Exception as e:
    print(f"⚠️  Could not verify login page: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print("""
If all tests passed:
  → Your login backend is working properly
  → The issue might be in:
    - Browser CORS settings
    - Firewall blocking requests
    - Supabase credentials being invalid
    - Network connectivity

If tests failed:
  → Check run.py output for backend loading errors
  → Ensure SUPABASE_URL and SUPABASE_KEY are set
  → Make sure login_backend.py exists at the expected path
""")
