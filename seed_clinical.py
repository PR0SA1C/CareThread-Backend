import os
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)

CONDITIONS = [
    ("Type 2 Diabetes Mellitus", "E11.9"),
    ("Essential Hypertension", "I10"),
    ("Acute Bronchitis", "J20.9"),
    ("Migraine without aura", "G43.009"),
    ("Gastroesophageal reflux disease", "K21.9"),
    ("Hypothyroidism", "E03.9"),
    ("Asthma, unspecified", "J45.909"),
    ("Iron deficiency anemia", "D50.9")
]

MEDICATIONS = {
    "Type 2 Diabetes Mellitus": [("Metformin", "500mg", "Twice daily"), ("Glipizide", "5mg", "Once daily")],
    "Essential Hypertension": [("Amlodipine", "5mg", "Once daily"), ("Lisinopril", "10mg", "Once daily")],
    "Acute Bronchitis": [("Azithromycin", "250mg", "Once daily for 5 days"), ("Albuterol inhaler", "2 puffs", "Every 4-6 hours PRN")],
    "Migraine without aura": [("Sumatriptan", "50mg", "At onset of migraine"), ("Ibuprofen", "400mg", "Every 6 hours PRN")],
    "Gastroesophageal reflux disease": [("Omeprazole", "20mg", "Once daily before breakfast"), ("Pantoprazole", "40mg", "Once daily")],
    "Hypothyroidism": [("Levothyroxine", "50mcg", "Once daily in morning")],
    "Asthma, unspecified": [("Albuterol inhaler", "2 puffs", "Every 4 hours PRN"), ("Fluticasone", "110mcg", "2 puffs twice daily")],
    "Iron deficiency anemia": [("Ferrous Sulfate", "325mg", "Once daily with food")]
}

def seed_clinical():
    with engine.begin() as conn:
        print("Fetching existing patients, doctors, and hospitals...")
        patients = [row[0] for row in conn.execute(text("SELECT id FROM patients")).fetchall()]
        practitioners = conn.execute(text("SELECT id, facility_id FROM practitioners")).fetchall()
        
        if not patients or not practitioners:
            print("No patients or practitioners found! Please run the base seed script first.")
            return

        print(f"Generating clinical histories for {len(patients)} patients...")
        
        encounters_count = 0
        conditions_count = 0
        medications_count = 0

        for patient_id in patients:
            num_encounters = random.randint(1, 4)
            
            for _ in range(num_encounters):
                practitioner = random.choice(practitioners)
                practitioner_id = practitioner[0]
                facility_id = practitioner[1]
                
                encounter_id = str(uuid.uuid4())
                started_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
                
                condition_desc, icd10 = random.choice(CONDITIONS)
                
                # 1. CREATE ENCOUNTER
                conn.execute(
                    text("""
                        INSERT INTO encounters (id, patient_id, facility_id, practitioner_id, encounter_type, reason, notes, started_at, ended_at, source, created_at)
                        VALUES (:id, :pat_id, :fac_id, :prac_id, :type, :reason, :notes, :started_at, :ended_at, :source, :created_at)
                    """),
                    {
                        "id": encounter_id,
                        "pat_id": patient_id,
                        "fac_id": facility_id,
                        "prac_id": practitioner_id,
                        "type": random.choice(["first_visit", "follow_up", "emergency", "telemedicine"]),
                        "reason": f"Patient presented with symptoms of {condition_desc.lower()}",
                        "notes": "Standard consultation. Vitals normal. Prescribed medication based on diagnosis.",
                        "started_at": started_at,
                        "ended_at": started_at + timedelta(hours=1),
                        "source": random.choice(["manual", "abdm_sync", "import"]),
                        "created_at": started_at
                    }
                )
                encounters_count += 1
                
                # 2. CREATE CONDITION
                condition_id = str(uuid.uuid4())
                conn.execute(
                    text("""
                        INSERT INTO conditions (id, patient_id, encounter_id, icd10_code, description, status, onset_date, recorded_at, sensitivity_subclass)
                        VALUES (:id, :pat_id, :enc_id, :icd, :desc, :status, :onset, :recorded, :sens)
                    """),
                    {
                        "id": condition_id,
                        "pat_id": patient_id,
                        "enc_id": encounter_id,
                        "icd": icd10,
                        "desc": condition_desc,
                        "status": random.choice(["active", "resolved", "chronic"]),
                        "onset": (started_at - timedelta(days=random.randint(1, 14))).date(),
                        "recorded": started_at,
                        "sens": "standard"
                    }
                )
                conditions_count += 1
                
                # 3. CREATE MEDICATION
                med_list = MEDICATIONS.get(condition_desc, [])
                if med_list:
                    med_name, med_dose, med_freq = random.choice(med_list)
                    conn.execute(
                        text("""
                            INSERT INTO medications (id, patient_id, encounter_id, prescribing_practitioner_id, name, dosage, frequency, start_date, end_date, status, created_at, sensitivity_subclass)
                            VALUES (:id, :pat_id, :enc_id, :prac_id, :name, :dose, :freq, :start, :end, :status, :created, :sens)
                        """),
                        {
                            "id": str(uuid.uuid4()),
                            "pat_id": patient_id,
                            "enc_id": encounter_id,
                            "prac_id": practitioner_id,
                            "name": med_name,
                            "dose": med_dose,
                            "freq": med_freq,
                            "start": started_at.date(),
                            "end": (started_at + timedelta(days=random.randint(7, 30))).date(),
                            "status": random.choice(["active", "completed", "stopped"]),
                            "created": started_at,
                            "sens": "standard"
                        }
                    )
                    medications_count += 1

        print(f"=== Mock Trial Complete ===")
        print(f"Generated {encounters_count} Encounters (Doctor Visits)")
        print(f"Generated {conditions_count} Diagnoses (Conditions)")
        print(f"Generated {medications_count} Prescriptions (Medications)")

if __name__ == "__main__":
    seed_clinical()
