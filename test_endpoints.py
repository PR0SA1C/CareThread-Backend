import os
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from security.jwt_handler import create_access_token

load_dotenv()

# 1. Fetch a real ABHA ID from the DB to test with
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)
with engine.connect() as conn:
    res = conn.execute(text("SELECT abha_id, full_name FROM patients LIMIT 1")).first()
    if not res:
        print("No patients found in DB! Please run seed script first.")
        exit(1)
    test_abha, test_name = res[0], res[1]

print(f"\n=======================================================")
print(f" TESTING TIMELINE ENDPOINT FOR: {test_name} ({test_abha})")
print(f"=======================================================")

# 2. Helper function to test the timeline endpoint with a specific role
def test_timeline_as(role: str, user_type: str = "ORG_STAFF"):
    token = create_access_token(
        data={
            "user_id": "test_user_id",
            "user_type": user_type,
            "department": role,
            "facility_id": "test_facility"
        }
    )
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://localhost:8000/api/v1/clinical/patients/{test_abha}/timeline", headers=headers)
    
    print(f"\n[LOGIN ROLE: {role or 'PATIENT'}]")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json().get("data", {})
        print(f"-> Encounters fetched: {len(data.get('encounters', []))}")
        print(f"-> Conditions fetched: {len(data.get('conditions', []))}")
        print(f"-> Medications fetched: {len(data.get('medications', []))}")
    else:
        print(f"-> Response: {response.text}")

# 3. Run the Tests!
test_timeline_as("ORG_RECEPTION")      # Should be 403 Forbidden
test_timeline_as("ORG_PHARMACIST")     # Should only see medications
test_timeline_as("ORG_DOCTOR")         # Should see all, but no restricted subclasses
test_timeline_as(None, "PATIENT")      # Should see absolutely everything
print("\n")
