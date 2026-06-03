import sys
import time
import re
import imaplib
import email
import asyncio
import httpx
from datetime import datetime

API_URL = "http://localhost:8000"

def fetch_otp_from_inbox(target_email: str, subject_filter: str = "Your verification code") -> str:
    print(f"Polling Gmail IMAP for {target_email} with subject '{subject_filter}'...")
    start_time = time.time()
    # Poll up to 60 seconds
    while time.time() - start_time < 60:
        try:
            # Connect via SSL
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login("jeswanthjoel8779@gmail.com", "vtre dftt whls oxed")
            mail.select("inbox")
            
            # Search for emails matching the subject
            status, messages = mail.search(None, f'(SUBJECT "{subject_filter}")')
            if status == "OK" and messages[0]:
                message_ids = messages[0].split()
                for msg_id in reversed(message_ids):
                    status, msg_data = mail.fetch(msg_id, "(RFC822)")
                    if status == "OK":
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        to_header = msg.get("To", "")
                        # Verify the destination is our target alias
                        if target_email.lower() in to_header.lower():
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode()
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode()
                            
                            # Find 6 digit OTP
                            match = re.search(r"\b(\d{6})\b", body)
                            if match:
                                code = match.group(1)
                                mail.logout()
                                print(f"OTP retrieved: {code}")
                                return code
            mail.logout()
        except Exception as e:
            print(f"IMAP poll error: {e}")
        time.sleep(3)
    raise TimeoutError(f"Could not retrieve OTP for {target_email} in 60s")

async def test_auth_and_multitenancy():
    # Use unique suffixes for unique users/orgs on each run
    uid = int(time.time())
    email_a1 = f"jeswanthjoel8779+a1_{uid}@gmail.com"
    email_a2 = f"jeswanthjoel8779+a2_{uid}@gmail.com"
    email_b1 = f"jeswanthjoel8779+b1_{uid}@gmail.com"
    
    password = "SecurePassword123!"
    org_a = f"Org_A_{uid}"
    org_b = f"Org_B_{uid}"
    pin_a = "111111"
    pin_b = "222222"

    async with httpx.AsyncClient() as client:
        # ==========================================
        # 1. ORG A - USER A1 REGISTRATION & OTP
        # ==========================================
        print("\n--- Registering User A1 (Org A) ---")
        reg_payload = {
            "organization_name": org_a,
            "full_name": "User A1",
            "email": email_a1,
            "password": password,
            "organization_pin": pin_a
        }
        res = await client.post(f"{API_URL}/api/v1/auth/register", json=reg_payload)
        print("Register status:", res.status_code)
        assert res.status_code == 200, res.text
        
        # Wait and fetch OTP from Gmail
        otp_a1 = fetch_otp_from_inbox(email_a1, "Your verification code")
        
        # Verify OTP
        verify_payload = {"email": email_a1, "otp_code": otp_a1}
        res = await client.post(f"{API_URL}/api/v1/auth/verify-otp", json=verify_payload)
        print("Verify OTP status:", res.status_code)
        assert res.status_code == 200, res.text

        # Login User A1
        login_payload = {"email": email_a1, "password": password}
        res = await client.post(f"{API_URL}/api/v1/auth/login", json=login_payload)
        print("Login status:", res.status_code)
        assert res.status_code == 200, res.text
        tokens_a1 = res.json()
        token_a1 = tokens_a1["access_token"]

        # ==========================================
        # 2. ORG A - USER A2 REGISTRATION (JOIN ORG A)
        # ==========================================
        print("\n--- Registering User A2 (Joining Org A) ---")
        reg_payload2 = {
            "organization_name": org_a,
            "full_name": "User A2",
            "email": email_a2,
            "password": password,
            "organization_pin": pin_a
        }
        res = await client.post(f"{API_URL}/api/v1/auth/register", json=reg_payload2)
        print("Register User A2 status:", res.status_code)
        assert res.status_code == 200, res.text
        
        otp_a2 = fetch_otp_from_inbox(email_a2, "Your verification code")
        res = await client.post(f"{API_URL}/api/v1/auth/verify-otp", json={"email": email_a2, "otp_code": otp_a2})
        assert res.status_code == 200, res.text

        # Login User A2
        res = await client.post(f"{API_URL}/api/v1/auth/login", json={"email": email_a2, "password": password})
        tokens_a2 = res.json()
        token_a2 = tokens_a2["access_token"]

        # ==========================================
        # 3. ORG B - USER B1 REGISTRATION
        # ==========================================
        print("\n--- Registering User B1 (Org B) ---")
        reg_payload3 = {
            "organization_name": org_b,
            "full_name": "User B1",
            "email": email_b1,
            "password": password,
            "organization_pin": pin_b
        }
        res = await client.post(f"{API_URL}/api/v1/auth/register", json=reg_payload3)
        print("Register User B1 status:", res.status_code)
        assert res.status_code == 200, res.text
        
        otp_b1 = fetch_otp_from_inbox(email_b1, "Your verification code")
        res = await client.post(f"{API_URL}/api/v1/auth/verify-otp", json={"email": email_b1, "otp_code": otp_b1})
        assert res.status_code == 200, res.text

        # Login User B1
        res = await client.post(f"{API_URL}/api/v1/auth/login", json={"email": email_b1, "password": password})
        tokens_b1 = res.json()
        token_b1 = tokens_b1["access_token"]

        # ==========================================
        # 4. MULTI-TENANCY VERIFICATION
        # ==========================================
        print("\n--- Uploading Candidate Resume as User A1 ---")
        # Prepend %PDF magic number to pass the security scanner
        dummy_pdf_content = b"%PDF-1.4\n%EOF\nJohn Doe Resume\nSkills: Python, FastAPI, Postgres\nExperience: 5 years of professional software experience."
        files = {"file": ("resume.pdf", dummy_pdf_content, "application/pdf")}
        data = {"candidate_name": "John Doe", "email": "johndoe@example.com"}
        headers_a1 = {"Authorization": f"Bearer {token_a1}"}
        
        res = await client.post(f"{API_URL}/api/v1/resumes/upload", data=data, files=files, headers=headers_a1)
        print("Upload status:", res.status_code)
        assert res.status_code == 202, res.text
        
        # Give celery task some time to process
        print("Waiting for processing...")
        await asyncio.sleep(4)

        # User A2 lists candidates (Should see A1's upload)
        headers_a2 = {"Authorization": f"Bearer {token_a2}"}
        res = await client.get(f"{API_URL}/api/v1/candidates", headers=headers_a2)
        candidates_a2 = res.json()
        print(f"Candidates visible to User A2: {[c['full_name'] for c in candidates_a2]}")
        assert any(c["full_name"] == "John Doe" for c in candidates_a2), "A1's upload not shared with A2"

        # User B1 lists candidates (Should NOT see John Doe)
        headers_b1 = {"Authorization": f"Bearer {token_b1}"}
        res = await client.get(f"{API_URL}/api/v1/candidates", headers=headers_b1)
        candidates_b1 = res.json()
        print(f"Candidates visible to User B1: {[c['full_name'] for c in candidates_b1]}")
        assert not any(c["full_name"] == "John Doe" for c in candidates_b1), "A1's upload leaked to B1"
        print("-> Multi-tenancy check passed: Org A shared, Org B isolated.")

        # ==========================================
        # 5. FORGOT PASSWORD FLOW
        # ==========================================
        print("\n--- Triggering Forgot Password for User A1 ---")
        res = await client.post(f"{API_URL}/api/v1/auth/forgot-password", json={"email": email_a1})
        print("Forgot password status:", res.status_code)
        assert res.status_code == 200, res.text
        
        # Fetch OTP code
        reset_otp = fetch_otp_from_inbox(email_a1, "Reset your password")
        
        # Verify reset OTP
        res = await client.post(f"{API_URL}/api/v1/auth/verify-reset-otp", json={"email": email_a1, "otp_code": reset_otp})
        print("Verify reset OTP status:", res.status_code)
        assert res.status_code == 200, res.text
        reset_token = res.json()["reset_token"]

        # Reset password
        new_password = "BrandNewPassword123!"
        reset_payload = {
            "email": email_a1,
            "reset_token": reset_token,
            "new_password": new_password,
            "confirm_password": new_password
        }
        res = await client.post(f"{API_URL}/api/v1/auth/reset-password", json=reset_payload)
        print("Reset password status:", res.status_code)
        assert res.status_code == 200, res.text

        # Verify login works with new password
        res = await client.post(f"{API_URL}/api/v1/auth/login", json={"email": email_a1, "password": new_password})
        print("Login with new password status:", res.status_code)
        assert res.status_code == 200, res.text

        # ==========================================
        # 6. RATE LIMITS
        # ==========================================
        print("\n--- Testing Rate Limits ---")
        # Trigger login limit (5/min) by hitting endpoint 7 times
        rate_limit_triggered = False
        for i in range(7):
            res = await client.post(f"{API_URL}/api/v1/auth/login", json={"email": email_a1, "password": "wrong"})
            if res.status_code == 429:
                print(f"Login rate limit hit at request {i+1}. Retry-After: {res.headers.get('Retry-After')}")
                rate_limit_triggered = True
                break
        assert rate_limit_triggered, "Login rate limit not triggered"

        # ==========================================
        # 7. LOAD TESTING
        # ==========================================
        print("\n--- Load Testing (/ready with 50 concurrency) ---")
        tasks = [client.get(f"{API_URL}/ready") for _ in range(50)]
        start_load = time.time()
        results = await asyncio.gather(*tasks)
        end_load = time.time()
        latencies = [res.elapsed.total_seconds() * 1000 for res in results]
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        errors = sum(1 for res in results if res.status_code != 200)
        print(f"P95 Latency: {p95:.2f}ms")
        print(f"Error count: {errors}/50")
        assert errors == 0, f"Load test had errors: {errors}"
        
        print("\n=== ALL DESIRED STAGES AND TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(test_auth_and_multitenancy())
