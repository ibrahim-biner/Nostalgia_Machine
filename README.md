# 🎞️ Nostalgia Machine: AI Photo Colorization & Super-Resolution

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)]([SENİN-HF-LINKIN-BURAYA])

Bring your old, faded, or black & white photos back to life! This application uses a powerful two-stage deep learning pipeline to automatically **colorize** your memories and then **upscale** them into sharp, high-resolution images.

### ✨ [Live Demo on Hugging Face Spaces]([https://huggingface.co/spaces/BronSS/Nostalgia_Machine])

---

### 🚀 How It Works

This isn't just a simple filter. Your image is processed by two separate AI models in a sequential pipeline to achieve the final result.



**Stage 1: AI Colorization (U-Net)**
* The original image is first fed into a **U-Net** deep learning model.
* This model was custom-trained for 20 epochs on over 120,000 images from the COCO dataset, learning complex relationships between objects and their natural colors.
* It outputs a `256x256` colorized version of the image.

**Stage 2: AI Super-Resolution (EDSR)**
* The `256x256` colorized image is often blurry and low-resolution.
* It is immediately passed to a pre-trained **EDSR (Enhanced Deep Super-Resolution)** model.
* This model doesn't just resize the image; it intelligently **re-creates and invents** sharp details, upscaling the image 4x to a final, crisp **`1024x1024`** resolution.

---

### 🛠️ Tech Stack (Kullanılan Teknolojiler)

This project is a full-stack MLOps application, combining backend, frontend, and cloud deployment.

* **Backend:**
    * **Python 3.9**
    * **FastAPI:** For creating the high-performance API endpoint.
    * **Uvicorn:** As the ASGI server.
* **Machine Learning:**
    * **TensorFlow & Keras:** For building and running the U-Net colorization model.
    * **OpenCV (dnn_superres):** For running the pre-trained EDSR super-resolution model.
    * **Scikit-image & NumPy:** For fast image preprocessing and color space (Lab) manipulation.
* **Frontend:**
    * **HTML5**
    * **CSS3:** For the "nostalgic" styling.
    * **JavaScript (Fetch API):** For handling asynchronous image uploads and displaying results.
* **DevOps / MLOps:**
    * **Docker:** For containerizing the entire application (frontend + backend + models).
    * **Hugging Face Spaces:** For deploying the Docker container and serving the live app.
    * **Git & Git LFS:** For version control and handling large model files.

---

---

### 🚀 How to Run Locally (Yerel Makinede Çalıştırma)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)[ibrahim-biner/Nostalgia_Machine].git
    cd [Nostalgia_Machine]
    ```

2.  **Install Git LFS:**
    This project uses Git LFS for large model files. Make sure you have it installed.
    ```bash
    git lfs install
    git lfs pull
    ```
    *(If LFS fails, you must manually download the `.h5` and `.pb` models into the `/models` folder)*

3.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

4.  **Install dependencies:**
    *(Make sure you use opencv-contrib-python for the super-resolution module)*
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the application:**
    ```bash
    python -m uvicorn app.main:app --reload
    ```

6.  Open your browser and go to `http://127.0.0.1:8000`.


