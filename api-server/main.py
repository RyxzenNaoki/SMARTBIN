import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from utils.predict import predict_image
import time
from fastapi.middleware.cors import CORSMiddleware

# Definisikan variabel global untuk Firebase
firebase_admin = None
db = None
firebase_initialized = False

app = FastAPI(title="SmartBin Classification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Coba inisialisasi Firebase
try:
    import firebase_admin
    from firebase_admin import credentials, db as firebase_db
    
    # Cek beberapa lokasi yang mungkin untuk file kredensial
    possible_paths = [
        "./firebase-key.json",
        "./firebase_key.json",
        "../utils/firebase-key.json",
        "../utils/firebase_key.json",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Menggunakan kredensial Firebase dari: {path}")
            cred = credentials.Certificate(path)
            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://smartbin-b3035-default-rtdb.firebaseio.com/"
            })
            db = firebase_db  # Assign ke variabel global
            firebase_initialized = True
            break
    
    if not firebase_initialized:
        print("WARNING: File kredensial Firebase tidak ditemukan.")
        print("Fitur Firebase dinonaktifkan.")
except ImportError:
    print("Firebase Admin SDK tidak terinstal. Fitur Firebase dinonaktifkan.")
except Exception as e:
    print(f"Error saat inisialisasi Firebase: {e}")

@app.post("/classify")
async def classify_endpoint(file: UploadFile = File(...)):
    # Pastikan filename tidak None dan aman untuk digunakan sebagai nama file
    if file.filename is None:
        tmp_path = "uploaded_image.jpg"
    else:
        tmp_path = file.filename.replace(" ", "_")
    
    # Pastikan tmp_path tidak kosong
    if not tmp_path:
        tmp_path = "uploaded_image.jpg"
    
    print(f"Menyimpan file sementara ke: {tmp_path}")
    
    # Simpan file yang diupload
    try:
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error menyimpan file: {e}")

    # Klasifikasi gambar
    try:
        result, original_class = predict_image(tmp_path)
        print(f"Hasil klasifikasi: {result} (asli: {original_class})")
        
        # Simpan ke Firebase jika tersedia
        if firebase_initialized and db is not None:
            try:
                # Simpan hasil klasifikasi
                klasifikasi_ref = db.reference("/klasifikasi_terakhir")
                klasifikasi_ref.set({
                    "jenis": result,
                    "kelas_asli": original_class,
                    "timestamp": int(time.time() * 1000)
                })
                
                # Tambahkan ke riwayat klasifikasi
                history_ref = db.reference("/riwayat_klasifikasi").push()
                history_ref.set({
                    "jenis": result,
                    "kelas_asli": original_class,
                    "timestamp": int(time.time() * 1000)
                })
                
                # Update status untuk ESP32
                status_ref = db.reference("/status_sampah")
                status_ref.set({
                    "jenis": result,
                    "perlu_dibuka": True,  # Flag untuk ESP32 bahwa ada sampah baru
                    "timestamp": int(time.time() * 1000)
                })
                
                print("Hasil berhasil disimpan ke Firebase")
            except Exception as e:
                print(f"Error saat menyimpan ke Firebase: {e}")
        else:
            print("Hasil tidak disimpan ke Firebase (dinonaktifkan)")
    except Exception as e:
        print(f"Error saat klasifikasi: {e}")
        raise HTTPException(status_code=500, detail=f"Model error: {e}")
    finally:
        # Hapus file sementara jika ada
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                print(f"File sementara {tmp_path} berhasil dihapus")
            except Exception as e:
                print(f"Error saat menghapus file sementara: {e}")

    return {"jenis": result, "kelas_asli": original_class}

@app.get("/status")
async def status():
    firebase_status = "aktif" if firebase_initialized else "nonaktif"
    return {
        "status": "online", 
        "message": f"API server berjalan (Firebase: {firebase_status})"
    }

if __name__ == "__main__":
    import uvicorn
    print("Memulai server API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)