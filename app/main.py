from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import io
import os

# Kendi modüllerimizi import ediyoruz
from app.model_loader import load_all_models # <--- Sadece import ediyoruz, ÇAĞIRMIYORUZ
from app.processing import preprocess_for_colorization, postprocess_colorization

app = FastAPI(title="Nostalji Makinesi API")

# --- 1. CORS Ayarları (Değişiklik yok) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --- 2. Modelleri Yükleme (DEĞİŞİKLİK BURADA) ---
# Modelleri başta "None" olarak tanımlıyoruz
color_model = None
sr_model = None

@app.on_event("startup")
async def startup_event():
    # Modelleri, sunucu "startup" olayının İÇİNDE yüklüyoruz
    global color_model, sr_model # <--- Global değişkenleri değiştireceğimizi belirtiyoruz
    print("Startup olayı tetiklendi: Modeller yükleniyor...")
    
    color_model, sr_model = load_all_models()
    
    if color_model is None:
        print("KRİTİK HATA: Renklendirme modeli yüklenemedi.")
        # Burada bir hata fırlatmak, uygulamanın sağlıklı olmadığını belirtir
        raise RuntimeError("Kritik Hata: Renklendirme modeli yüklenemedi.")
        
    if sr_model is None:
        print("UYARI: Süper Çözünürlük modeli yüklenemedi. /enhance endpoint'i çalışmayacak.")
    
    print("Modeller başarıyla yüklendi, uygulama hazır.")


# --- 3. API ROTALARI (Değişiklik yok) ---
# (Buradaki @app.post, @app.get vb. kodların hepsi aynı kalacak)

@app.get("/api")
def read_root():
    return {"message": "Nostalji Makinesi API'sine hoş geldiniz! Arayüz için / adresine gidin."}

@app.post("/api/process-image/")
async def process_image(
    file: UploadFile = File(...),
    use_super_resolution: bool = Form(True)
):
    # Bu fonksiyonun çalışması için modellerin yüklenmiş olması gerekir
    if color_model is None:
        raise HTTPException(status_code=503, detail="Hata: Renklendirme modeli henüz hazır değil. Lütfen birkaç dakika sonra tekrar deneyin.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Geçersiz resim dosyası.")

    # --- AŞAMA 1: Renklendirme ---
    L_normalized, L_channel = preprocess_for_colorization(img_bgr)
    predicted_ab = color_model.predict(L_normalized)
    low_res_colored_bgr = postprocess_colorization(L_channel, predicted_ab)

    final_image = low_res_colored_bgr

    # --- AŞAMA 2: Süper Çözünürlük (İsteğe bağlı) ---
    if use_super_resolution:
        if sr_model is not None:
            print("Süper çözünürlük uygulanıyor...")
            try:
                final_image = sr_model.upsample(low_res_colored_bgr)
            except Exception as e:
                print(f"SR modeli uygulanırken hata oluştu: {e}")
        else:
            print("Süper çözünürlük istendi ancak model yüklenemedi.")

    # --- Sonucu Geri Gönder ---
    is_success, buffer = cv2.imencode(".png", final_image)
    if not is_success:
        raise HTTPException(status_code=500, detail="Resim encode edilirken hata oluştu.")
    
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/png")


# --- 4. Arayüzü Sunma (Değişiklik yok) ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")