from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import io
import os


from app.model_loader import load_all_models 
from app.processing import preprocess_for_colorization, postprocess_colorization

app = FastAPI(title="Nostalji Makinesi API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


color_model = None
sr_model = None

@app.on_event("startup")
async def startup_event():
    
    global color_model, sr_model 
    print("Startup olayı tetiklendi: Modeller yükleniyor...")
    
    color_model, sr_model = load_all_models()
    
    if color_model is None:
        print("KRİTİK HATA: Renklendirme modeli yüklenemedi.")
        
        raise RuntimeError("Kritik Hata: Renklendirme modeli yüklenemedi.")
        
    if sr_model is None:
        print("UYARI: Süper Çözünürlük modeli yüklenemedi. /enhance endpoint'i çalışmayacak.")
    
    print("Modeller başarıyla yüklendi, uygulama hazır.")




@app.get("/api")
def read_root():
    return {"message": "Nostalji Makinesi API'sine hoş geldiniz! Arayüz için / adresine gidin."}

@app.post("/api/process-image/")
async def process_image(
    file: UploadFile = File(...),
    use_super_resolution: bool = Form(True)
):
    
    if color_model is None:
        raise HTTPException(status_code=503, detail="Hata: Renklendirme modeli henüz hazır değil. Lütfen birkaç dakika sonra tekrar deneyin.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Geçersiz resim dosyası.")

   
    L_normalized, L_channel = preprocess_for_colorization(img_bgr)
    predicted_ab = color_model.predict(L_normalized)
    low_res_colored_bgr = postprocess_colorization(L_channel, predicted_ab)

    final_image = low_res_colored_bgr

   
    if use_super_resolution:
        if sr_model is not None:
            print("Süper çözünürlük uygulanıyor...")
            try:
                final_image = sr_model.upsample(low_res_colored_bgr)
            except Exception as e:
                print(f"SR modeli uygulanırken hata oluştu: {e}")
        else:
            print("Süper çözünürlük istendi ancak model yüklenemedi.")

    
    is_success, buffer = cv2.imencode(".png", final_image)
    if not is_success:
        raise HTTPException(status_code=500, detail="Resim encode edilirken hata oluştu.")
    
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/png")



app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")