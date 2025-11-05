import tensorflow as tf
from tensorflow.keras.losses import MeanSquaredError
import cv2
import os


COLOR_MODEL_PATH = "models/colorization_unet_generator_best.h5"
SR_MODEL_PATH = "models/EDSR_x4.pb"
SR_MODEL_NAME = "edsr"
SR_SCALE = 4

def load_all_models():
    """
    Tüm yapay zeka modellerini belleğe yükler.
    """
    print("Modeller yükleniyor...")
    
    
    try:
        custom_objects = {'mse': MeanSquaredError()}
        color_model = tf.keras.models.load_model(COLOR_MODEL_PATH, custom_objects=custom_objects)
        print(f"Renklendirme modeli '{COLOR_MODEL_PATH}' başarıyla yüklendi.")
    except Exception as e:
        print(f"HATA: Renklendirme modeli yüklenemedi: {e}")
        color_model = None

    
    try:
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel(SR_MODEL_PATH)
        sr.setModel(SR_MODEL_NAME, SR_SCALE)
        print(f"Süper Çözünürlük modeli '{SR_MODEL_PATH}' başarıyla yüklendi.")
    except Exception as e:
        print(f"HATA: Süper Çözünürlük modeli yüklenemedi: {e}")
        sr = None

    return color_model, sr