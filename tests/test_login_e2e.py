"""
Full End-to-End Login Test - Simulating Browser Behavior
Tests the complete login flow as the frontend would execute it.
"""
import requests
import json

BASE = "http://localhost:3000"

results = []

def test(name, func):
    try:
        result = func()
        results.append({"test": name, "passed": result.get("PASS", False), "result": result})
        status = "PASS" if result.get("PASS") else "FAIL"
        print(f"\n[{status}] {name}")
        for k, v in result.items():
            if k != "PASS":
                print(f"  {k}: {v}")
    except Exception as e:
        results.append({"test": name, "passed": False, "result": {"ERROR": str(e)}})
        print(f"\n[FAIL] {name} -> EXCEPTION: {e}")

# ============================================================
# Test 1: Full login flow (simulating what Login.vue does)
# ============================================================
def test_full_login_flow():
    """Simulates: authStore.login -> authApi.login -> /api/v1/auth/login"""
    
    # Step 1: Login request (what authApi.login does)
    login_resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/json"},
    )
    
    if login_resp.status_code != 200:
        return {"PASS": False, "login_status": login_resp.status_code, "login_body": login_resp.text}
    
    login_data = login_resp.json()
    
    if not login_data.get("success"):
        return {"PASS": False, "login_success": False, "login_body": login_data}
    
    token_data = login_data.get("data", {})
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    
    if not access_token or not refresh_token:
        return {"PASS": False, "error": "Missing tokens"}
    
    # Step 2: Get current user (what authApi.getCurrentUser does after login)
    me_resp = requests.get(
        f"{BASE}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    if me_resp.status_code != 200:
        return {"PASS": False, "me_status": me_resp.status_code, "me_body": me_resp.text}
    
    me_data = me_resp.json()
    
    if not me_data.get("success"):
        return {"PASS": False, "me_success": False, "me_body": me_data}
    
    user_info = me_data.get("data", {})
    
    return {
        "PASS": True,
        "login_status": login_resp.status_code,
        "login_success": login_data.get("success"),
        "has_access_token": bool(access_token),
        "has_refresh_token": bool(refresh_token),
        "token_type": token_data.get("token_type"),
        "me_status": me_resp.status_code,
        "user_id": user_info.get("id"),
        "username": user_info.get("username"),
        "role": user_info.get("role"),
        "is_active": user_info.get("is_active"),
    }

test("Test 1: Full login flow (admin/admin123)", test_full_login_flow)

# ============================================================
# Test 2: Login with wrong password (simulating browser)
# ============================================================
def test_wrong_password_browser():
    """Simulates: user enters wrong password, frontend shows error"""
    resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    
    data = resp.json()
    detail = data.get("detail", "")
    
    return {
        "PASS": resp.status_code == 401,
        "status_code": resp.status_code,
        "detail": detail,
        "has_error_message": bool(detail),
    }

test("Test 2: Wrong password (should show error)", test_wrong_password_browser)

# ============================================================
# Test 3: Empty form submission (frontend validation)
# ============================================================
def test_empty_form():
    """Simulates: user clicks login without entering anything"""
    # The frontend has form validation rules:
    # username: required, min 3, max 50
    # password: required, min 6, max 128
    # Frontend should block submission before API call
    # But let's test what happens if empty data reaches the API
    resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "", "password": ""},
    )
    
    data = resp.json()
    
    return {
        "PASS": resp.status_code == 422,
        "status_code": resp.status_code,
        "error": data.get("error"),
        "detail": data.get("detail"),
        "note": "Frontend should block this with form validation before API call",
    }

test("Test 3: Empty form submission", test_empty_form)

# ============================================================
# Test 4: Dashboard access after login (simulating router guard)
# ============================================================
def test_dashboard_after_login():
    """Simulates: after login, user navigates to /dashboard"""
    # First login
    login_resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_resp.json()["data"]["access_token"]
    
    # Then access dashboard API (the router guard checks auth, then dashboard loads data)
    dash_resp = requests.get(
        f"{BASE}/api/v1/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    return {
        "PASS": dash_resp.status_code == 200,
        "dashboard_status": dash_resp.status_code,
        "dashboard_data": dash_resp.json() if dash_resp.status_code == 200 else dash_resp.text,
    }

test("Test 4: Dashboard access after login", test_dashboard_after_login)

# ============================================================
# Test 5: Access protected route without token (router guard)
# ============================================================
def test_protected_route_no_token():
    """Simulates: unauthenticated user tries to access /dashboard"""
    resp = requests.get(f"{BASE}/api/v1/dashboard/stats")
    
    return {
        "PASS": resp.status_code in [401, 403],
        "status_code": resp.status_code,
        "note": "Frontend router guard should redirect to /login",
    }

test("Test 5: Protected route without token", test_protected_route_no_token)

# ============================================================
# Test 6: Token refresh flow
# ============================================================
def test_token_refresh():
    """Simulates: token expires, frontend auto-refreshes"""
    # Login to get tokens
    login_resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    tokens = login_resp.json()["data"]
    
    # Refresh token
    refresh_resp = requests.post(
        f"{BASE}/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    
    data = refresh_resp.json()
    new_tokens = data.get("data", {})
    
    return {
        "PASS": refresh_resp.status_code == 200 and data.get("success") == True,
        "refresh_status": refresh_resp.status_code,
        "has_new_access_token": bool(new_tokens.get("access_token")),
        "has_new_refresh_token": bool(new_tokens.get("refresh_token")),
        "tokens_are_different": new_tokens.get("access_token") != tokens["access_token"],
    }

test("Test 6: Token refresh flow", test_token_refresh)

# ============================================================
# Test 7: Logout flow
# ============================================================
def test_logout():
    """Simulates: user clicks logout"""
    # Login first
    login_resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_resp.json()["data"]["access_token"]
    
    # Logout
    logout_resp = requests.post(
        f"{BASE}/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    return {
        "PASS": logout_resp.status_code == 200,
        "logout_status": logout_resp.status_code,
        "logout_body": logout_resp.json(),
    }

test("Test 7: Logout flow", test_logout)

# ============================================================
# Test 8: Login with teacher account
# ============================================================
def test_teacher_login():
    """Test login with teacher credentials"""
    resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "teacher", "password": "teacher123"},
    )
    
    if resp.status_code != 200:
        return {"PASS": False, "status": resp.status_code, "body": resp.text}
    
    data = resp.json()
    token = data["data"]["access_token"]
    
    # Get user info
    me_resp = requests.get(
        f"{BASE}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user = me_resp.json()["data"]
    
    return {
        "PASS": resp.status_code == 200 and user["role"] == "teacher",
        "login_status": resp.status_code,
        "user_role": user["role"],
        "username": user["username"],
    }

test("Test 8: Teacher account login", test_teacher_login)

# ============================================================
# Test 9: Login with student account
# ============================================================
def test_student_login():
    """Test login with student credentials"""
    resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "student", "password": "student123"},
    )
    
    if resp.status_code != 200:
        return {"PASS": False, "status": resp.status_code, "body": resp.text}
    
    data = resp.json()
    token = data["data"]["access_token"]
    
    # Get user info
    me_resp = requests.get(
        f"{BASE}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user = me_resp.json()["data"]
    
    return {
        "PASS": resp.status_code == 200 and user["role"] == "student",
        "login_status": resp.status_code,
        "user_role": user["role"],
        "username": user["username"],
    }

test("Test 9: Student account login", test_student_login)

# ============================================================
# Test 10: Check CORS headers
# ============================================================
def test_cors():
    """Check if CORS headers are properly set"""
    resp = requests.options(
        f"{BASE}/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    
    cors_origin = resp.headers.get("access-control-allow-origin", "")
    cors_methods = resp.headers.get("access-control-allow-methods", "")
    
    return {
        "PASS": resp.status_code in [200, 204] and bool(cors_origin),
        "status_code": resp.status_code,
        "cors_origin": cors_origin,
        "cors_methods": cors_methods,
        "all_headers": dict(resp.headers),
    }

test("Test 10: CORS configuration", test_cors)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
passed = sum(1 for r in results if r["passed"])
total = len(results)
print(f"\nPassed: {passed}/{total}")
print()
for r in results:
    status = "PASS" if r["passed"] else "FAIL"
    print(f"  [{status}] {r['test']}")
print()
if passed == total:
    print("ALL TESTS PASSED - Login functionality is working correctly!")
else:
    print(f"WARNING: {total - passed} test(s) FAILED!")
    for r in results:
        if not r["passed"]:
            print(f"  FAILED: {r['test']}")
            print(f"    Details: {r['result']}")
