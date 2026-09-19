import os
import random
import uuid
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)

with engine.begin() as conn:
    patients = conn.execute(text("SELECT id FROM patients")).fetchall()
    if not patients:
        print("No patients found. Please run main seed scripts first.")
        exit(1)
        
    print(f"Generating mock vitals for {len(patients)} patients...")
    count = 0
    
    for p in patients:
        p_id = p[0]
        # Get their encounters
        encounters = conn.execute(text("SELECT id, started_at FROM encounters WHERE patient_id = :pid"), {"pid": p_id}).fetchall()
        
        for enc in encounters:
            enc_id, enc_date = enc[0], enc[1]
            
            # Generate realistic clinical vitals
            vital_id = str(uuid.uuid4())
            temp = round(random.uniform(36.5, 38.2), 1)
            sys_bp = random.randint(110, 140)
            dia_bp = random.randint(70, 90)
            hr = random.randint(60, 100)
            rr = random.randint(12, 20)
            spo2 = random.randint(95, 100)
            weight = round(random.uniform(55.0, 90.0), 2)
            height = round(random.uniform(150.0, 185.0), 1)
            
            conn.execute(
                text("""
                    INSERT INTO vitals (
                        id, patient_id, encounter_id, body_temperature_celsius, 
                        blood_pressure_systolic, blood_pressure_diastolic, 
                        heart_rate_bpm, respiratory_rate_bpm, spo2_percent, body_weight_kg, height_cm,
                        recorded_at, source, created_at
                    ) VALUES (
                        :id, :pid, :eid, :temp, :sys, :dia, :hr, :rr, :spo2, :weight, :height,
                        :rec_at, 'manual', CURRENT_TIMESTAMP
                    )
                """),
                {
                    "id": vital_id, "pid": p_id, "eid": enc_id, "temp": temp,
                    "sys": sys_bp, "dia": dia_bp, "hr": hr, "rr": rr, "spo2": spo2,
                    "weight": weight, "height": height, "rec_at": enc_date
                }
            )
            count += 1

    print(f"Successfully injected {count} realistic vital readings into the database!")
