"""
Login API Test Script
Tests the backend authentication endpoints comprehensively.
"""
import requests
import json

BASE = "http://localhost:8000/api/v1/auth/login"
ME_URL = "http://localhost:8000/api/v1/auth/me"

results = []

def test(name, func):
    try:
        result = func()
        results.append({"test": name, "result": result})
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        for k, v in result.items():
            print(f"  {k}: {v}")
    except Exception as e:
        results.append({"test": name, "result": {"ERROR": str(e)}})
        print(f"\nTEST: {name} -> EXCEPTION: {e}")

# Test 1: Correct credentials
def test_correct_credentials():
    r = requests.post(BASE, json={"username": "admin", "password": "admin123"})
    data = r.json()
    return {
        "status_code": r.status_code,
        "success": data.get("success"),
        "has_access_token": bool(data.get("data", {}).get("access_token")),
        "has_refresh_token": bool(data.get("data", {}).get("refresh_token")),
        "token_type": data.get("data", {}).get("token_type"),
        "expires_in": data.get("data", {}).get("expires_in"),
        "message": data.get("message"),
        "PASS": r.status_code == 200 and data.get("success") == True,
    }

test("1. Correct credentials (admin/admin123)", test_correct_credentials)

# Test 2: Wrong password
def test_wrong_password():
    r = requests.post(BASE, json={"username": "admin", "password": "wrongpassword"})
    data = r.json()
    return {
        "status_code": r.status_code,
        "detail": data.get("detail"),
        "PASS": r.status_code == 401,
    }

test("2. Wrong password", test_wrong_password)

# Test 3: Non-existent user
def test_nonexistent_user():
    r = requests.post(BASE, json={"username": "nonexistent", "password": "admin123"})
    data = r.json()
    return {
        "status_code": r.status_code,
        "detail": data.get("detail"),
        "PASS": r.status_code == 401,
    }

test("3. Non-existent user", test_nonexistent_user)

# Test 4: Empty body
def test_empty_body():
    r = requests.post(BASE, json={})
    data = r.json()
    return {
        "status_code": r.status_code,
        "detail": data.get("detail"),
        "PASS": r.status_code == 422,
    }

test("4. Empty body", test_empty_body)

# Test 5: Short username (below min_length=3)
def test_short_username():
    r = requests.post(BASE, json={"username": "ab", "password": "admin123"})
    data = r.json()
    return {
        "status_code": r.status_code,
        "detail": data.get("detail"),
        "PASS": r.status_code == 422,
    }

test("5. Short username (< 3 chars)", test_short_username)

# Test 6: Short password (below min_length=6)
def test_short_password():
    r = requests.post(BASE, json={"username": "admin", "password": "12345"})
    data = r.json()
    return {
        "status_code": r.status_code,
        "detail": data.get("detail"),
        "PASS": r.status_code == 422,
    }

test("6. Short password (< 6 chars)", test_short_password)

# Test 7: /me endpoint with valid token
def test_me_with_token():
    r = requests.post(BASE, json={"username": "admin", "password": "admin123"})
    token = r.json()["data"]["access_token"]
    r2 = requests.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    data = r2.json()
    return {
        "status_code": r2.status_code,
        "success": data.get("success"),
        "user_id": data.get("data", {}).get("id"),
        "username": data.get("data", {}).get("username"),
        "role": data.get("data", {}).get("role"),
        "PASS": r2.status_code == 200 and data.get("success") == True,
    }

test("7. /me with valid token", test_me_with_token)

# Test 8: /me endpoint without token
def test_me_without_token():
    r = requests.get(ME_URL)
    return {
        "status_code": r.status_code,
        "PASS": r.status_code == 403,  # HTTPBearer with auto_error=True returns 403
    }

test("8. /me without token (should 403)", test_me_without_token)

# Test 9: /me with invalid token
def test_me_with_invalid_token():
    r = requests.get(ME_URL, headers={"Authorization": "Bearer invalid_token_here"})
    return {
        "status_code": r.status_code,
        "PASS": r.status_code == 401,
    }

test("9. /me with invalid token", test_me_with_invalid_token)

# Test 10: Token refresh with valid refresh token
def test_token_refresh():
    r = requests.post(BASE, json={"username": "admin", "password": "admin123"})
    refresh_token = r.json()["data"]["refresh_token"]
    r2 = requests.post(
        "http://localhost:8000/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    data = r2.json()
    return {
        "status_code": r2.status_code,
        "success": data.get("success"),
        "has_new_access_token": bool(data.get("data", {}).get("access_token")),
        "has_new_refresh_token": bool(data.get("data", {}).get("refresh_token")),
        "PASS": r2.status_code == 200 and data.get("success") == True,
    }

test("10. Token refresh", test_token_refresh)

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
all_pass = all(r["result"].get("PASS", False) for r in results)
passed = sum(1 for r in results if r["result"].get("PASS", False))
total = len(results)
print(f"Passed: {passed}/{total}")
for r in results:
    status = "PASS" if r["result"].get("PASS", False) else "FAIL"
    print(f"  [{status}] {r['test']}")
print(f"\nOverall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
