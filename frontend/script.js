document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const uploadArea = document.getElementById("upload-area");
    const submitButton = document.getElementById("submit-button");
    const loader = document.getElementById("loader");
    
    const resultsContainer = document.getElementById("results");
    const originalBox = document.getElementById("original-box");
    const originalImage = document.getElementById("original-image");
    const resultBox = document.getElementById("result-box");
    const resultImage = document.getElementById("result-image");
    const downloadButton = document.getElementById("download-button");

    let uploadedFile = null;

    // Dosya seçme alanını etkinleştirme
    uploadArea.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            uploadedFile = e.target.files[0];
            uploadArea.querySelector("p").textContent = `Dosya seçildi: ${uploadedFile.name}`;
            
            // Orijinal resmi önizlemede göster
            const reader = new FileReader();
            reader.onload = (e) => {
                originalImage.src = e.target.result;
                originalImage.style.display = "block";
                originalBox.style.display = "block";
                resultBox.style.display = "none";
                resultsContainer.style.display = "flex";
                downloadButton.style.display = "none";
            };
            reader.readAsDataURL(uploadedFile);
        }
    });

    // Formu gönderme
    form.addEventListener("submit", async (e) => {
        e.preventDefault(); // Sayfanın yeniden yüklenmesini engelle
        if (!uploadedFile) {
            alert("Lütfen önce bir resim dosyası seçin.");
            return;
        }

        // Yükleme ekranını göster
        loader.style.display = "flex";
        submitButton.disabled = true;
        submitButton.textContent = "İşleniyor...";

        // Form verilerini hazırla
        const formData = new FormData();
        formData.append("file", uploadedFile);
        
        const useSuperRes = document.getElementById("use-super-resolution").checked;
        formData.append("use_super_resolution", useSuperRes);

        try {
            // API'ye POST isteği gönder
            // Hata almamak için tam URL'yi veya göreceli yolu kullan
            // const response = await fetch("http://127.0.0.1:8000/api/process-image/", {
            const response = await fetch("/api/process-image/", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                // Başarılı olursa: Gelen resim verisini al
                const imageBlob = await response.blob();
                const imageObjectURL = URL.createObjectURL(imageBlob);

                // Sonuç resmini ve indirme butonunu göster
                resultImage.src = imageObjectURL;
                resultImage.style.display = "block";
                resultBox.style.display = "block";
                
                downloadButton.href = imageObjectURL;
                downloadButton.download = `nostalji_${uploadedFile.name}`;
                downloadButton.style.display = "inline-block";

            } else {
                // Başarısız olursa: Sunucudan gelen hatayı göster
                const errorData = await response.json();
                alert(`Bir hata oluştu: ${errorData.detail || 'Bilinmeyen sunucu hatası'}`);
            }

        } catch (error) {
            console.error("Fetch hatası:", error);
            alert(`Ağ hatası: Sunucuya bağlanılamadı. API'nin çalıştığından emin misin? ${error.message}`);
        } finally {
            // Her durumda yükleme ekranını gizle ve butonu aktif et
            loader.style.display = "none";
            submitButton.disabled = false;
            submitButton.textContent = "İşlemi Başlat";
        }
    });
});