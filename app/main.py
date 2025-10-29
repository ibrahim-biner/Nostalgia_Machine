from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import io
import os

# Kendi modüllerimizi import ediyoruz
from app.model_loader import load_all_models
from app.processing import preprocess_for_colorization, postprocess_colorization

app = FastAPI(title="Nostalji Makinesi API")

# --- 1. CORS Ayarları (ÇOK ÖNEMLİ) ---
# Arayüzün API ile konuşabilmesi için bu gerekli.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Veya daha güvenlisi: ["http://127.0.0.1:8000", "https://*.hf.space"]
    allow_credentials=True,
    allow_methods=["*"], # GET, POST vb.
    allow_headers=["*"],
)

# --- 2. Modelleri Yükleme ---
# Sunucu başlarken modelleri yükle
color_model, sr_model = load_all_models()

@app.on_event("startup")
async def startup_event():
    if color_model is None:
        raise RuntimeError("Kritik Hata: Renklendirme modeli yüklenemedi.")
    if sr_model is None:
        print("Uyarı: Süper Çözünürlük modeli yüklenemedi. /enhance endpoint'i çalışmayacak.")


# --- 3. API ROTALARI ---
# Arayüz ile çakışmaması için API rotalarını "/api" ön eki ile ayırıyoruz.

@app.get("/api")
def read_root():
    return {"message": "Nostalji Makinesi API'sine hoş geldiniz! Arayüz için / adresine gidin."}

@app.post("/api/process-image/")
async def process_image(
    file: UploadFile = File(...),
    use_super_resolution: bool = Form(True)
):
    """
    Bir resmi renklendirir ve isteğe bağlı olarak süper çözünürlük uygular.
    """
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


# --- 4. Arayüzü Sunma (Static Files) ---
# Diğer tüm rotalardan SONRA gelmeli.
# "/" adresine gelen istekleri "frontend" klasöründeki "index.html"e yönlendirir.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")