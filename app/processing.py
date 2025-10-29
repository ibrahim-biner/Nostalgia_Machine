import cv2
import numpy as np
from skimage.color import rgb2lab, lab2rgb

IMG_SIZE = 256

def preprocess_for_colorization(bgr_image: np.ndarray):
    """
    Gelen BGR resmi alır, renklendirme modelinin girdisine (L kanalı)
    ve sonradan birleştirmek için orijinal L kanalına dönüştürür.
    """
    # a. RGB'ye çevir ve 256x256 boyutlandır
    img_rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (IMG_SIZE, IMG_SIZE))
    
    # b. [0, 1] aralığına normalize et
    img_float = img_resized.astype(np.float32) / 255.0
    
    # c. Lab'a çevir
    img_lab = rgb2lab(img_float)
    
    # d. L kanalını ayır
    L_channel = img_lab[:, :, 0] # Bu orijinal L, sonradan kullanılacak
    
    # e. Model girdisi için L kanalını normalize et ([-1, 1])
    L_normalized = (L_channel / 50.0) - 1.0
    L_normalized = L_normalized.reshape(1, IMG_SIZE, IMG_SIZE, 1) # Batch boyutu ekle

    return L_normalized, L_channel

def postprocess_colorization(original_L_channel: np.ndarray, predicted_ab_normalized: np.ndarray) -> np.ndarray:
    """
    Orijinal L kanalı ile modelin tahmin ettiği ab kanallarını birleştirir
    ve BGR formatında bir çıktı resmine dönüştürür.
    """
    # a. Tahmin edilen ab kanallarını de-normalize et ([-1, 1] -> [-128, 128])
    predicted_ab = predicted_ab_normalized[0] * 128.0
    
    # b. Orijinal L ile TAHMİN EDİLEN ab'yi birleştir
    output_lab = np.zeros((IMG_SIZE, IMG_SIZE, 3))
    output_lab[:, :, 0] = original_L_channel
    output_lab[:, :, 1:] = predicted_ab
    
    # c. Lab'dan RGB'ye çevir
    output_rgb = lab2rgb(output_lab)
    output_rgb = (output_rgb * 255).astype(np.uint8) # [0, 1] -> [0, 255]
    
    # d. FastAPI'de (ve OpenCV'de) standart olan BGR'ye geri dön
    output_bgr = cv2.cvtColor(output_rgb, cv2.COLOR_RGB2BGR)
    
    return output_bgr