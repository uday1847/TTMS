import asyncio
import httpx
import sys

async def verify_project():
    print("Starting Project Verification...")
    
    # Check Backend Health
    try:
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            resp = await client.get("/")
            resp.raise_for_status()
            print("[OK] Backend Health Check: Passed")
            
            # Attempt to login with the new admin email
            login_data = {
                "username_or_email": "admin@ttms.com",
                "password": "Admin@123"
            }
            resp = await client.post("/api/v1/auth/login", json=login_data)
            if resp.status_code == 200:
                print("[OK] Authentication: Passed (admin@ttms.com can log in)")
                token = resp.json().get("access_token")
            else:
                print(f"[FAIL] Authentication Failed: {resp.status_code} {resp.text}")
                sys.exit(1)
                
            # Verify Roles
            headers = {"Authorization": f"Bearer {token}"}
            resp = await client.get("/api/v1/roles", headers=headers)
            if resp.status_code == 200:
                roles = resp.json().get("data", [])
                if len(roles) >= 8:
                    print(f"[OK] Roles Verification: Passed ({len(roles)} roles found)")
                else:
                    print(f"[FAIL] Roles Verification Failed: Expected >=8, got {len(roles)}")
                    sys.exit(1)
            else:
                print(f"[FAIL] Failed to fetch roles: {resp.status_code}")
                
            # Verify Permissions
            resp = await client.get("/api/v1/permissions", headers=headers)
            if resp.status_code == 200:
                perms = resp.json().get("data", [])
                if len(perms) >= 34:
                    print(f"[OK] Permissions Verification: Passed ({len(perms)} permissions found)")
                else:
                    print(f"[FAIL] Permissions Verification Failed: Expected >=34, got {len(perms)}")
                    sys.exit(1)
            else:
                print(f"[FAIL] Failed to fetch permissions: {resp.status_code}")
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Verification Error: {e}")
        sys.exit(1)
        
    print("All Verifications Passed Successfully!")

if __name__ == "__main__":
    asyncio.run(verify_project())
