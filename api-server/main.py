import os
import shutil
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from utils.predict import predict_image
import firebase_admin
from firebase_admin import credentials, db
import threading
import time

app = FastAPI(title="SmartBin Classification API")

# Inisialisasi Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(__file__), "firebase_key.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DB_URL", "https://smartbin-b3035-default-rtdb.firebaseio.com/")
})

@app.post("/classify")
async def classify_endpoint(file: UploadFile = File(...)):
    # Simpan sementara
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Klasifikasi
    try:
        result = predict_image(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {e}")
    finally:
        os.remove(tmp_path)

    # Simpan ke Firebase RTDB
    ref = db.reference("/klasifikasi_terakhir")
    ref.set({"jenis": result})

    return {"jenis": result}

# Fungsi real-time dari kamera
def real_time_classification():
    cap = cv2.VideoCapture(0)  # Gunakan kamera default
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Gagal mengakses kamera.")
            break

        # Simpan frame sementara
        tmp_img_path = "frame.jpg"
        cv2.imwrite(tmp_img_path, frame)

        # Prediksi
        try:
            pred = predict_image(tmp_img_path)
            print(f"Prediksi: {pred}")
            db.reference("/klasifikasi_terakhir").set({"jenis": pred})
        except Exception as e:
            print(f"Error klasifikasi: {e}")

        time.sleep(5)  # jeda antar prediksi

    cap.release()
    cv2.destroyAllWindows()

# Jalankan thread kamera saat script dijalankan langsung
if __name__ == "__main__":
    threading.Thread(target=real_time_classification, daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
