import os, shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from utils.predict import classify_image
import firebase_admin
from firebase_admin import credentials, db

app = FastAPI(title="SmartBin Classification API")

# Inisialisasi Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(__file__), "firebase_key.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DB_URL", "https://smartbin-b3035-default-rtdb.firebaseio.com/")
})

@app.post("/classify")
async def classify_endpoint(file: UploadFile = File(...)):
    # simpan sementara
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # klasifikasi
    try:
        result = classify_image(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {e}")
    finally:
        os.remove(tmp_path)

    # simpan ke Firebase RTDB
    ref = db.reference("/klasifikasi_terakhir")
    ref.set({"jenis": result})

    return {"jenis": result}
