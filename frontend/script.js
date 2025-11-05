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

    
    uploadArea.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            uploadedFile = e.target.files[0];
            uploadArea.querySelector("p").textContent = `Dosya seçildi: ${uploadedFile.name}`;
            
            
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

    
    form.addEventListener("submit", async (e) => {
        e.preventDefault(); 
        if (!uploadedFile) {
            alert("Lütfen önce bir resim dosyası seçin.");
            return;
        }

        r
        loader.style.display = "flex";
        submitButton.disabled = true;
        submitButton.textContent = "İşleniyor...";

        
        const formData = new FormData();
        formData.append("file", uploadedFile);
        
        const useSuperRes = document.getElementById("use-super-resolution").checked;
        formData.append("use_super_resolution", useSuperRes);

        try {
            
            const response = await fetch("/api/process-image/", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {

                const imageBlob = await response.blob();
                const imageObjectURL = URL.createObjectURL(imageBlob);

                
                resultImage.src = imageObjectURL;
                resultImage.style.display = "block";
                resultBox.style.display = "block";
                
                downloadButton.href = imageObjectURL;
                downloadButton.download = `nostalji_${uploadedFile.name}`;
                downloadButton.style.display = "inline-block";

            } else {
                
                const errorData = await response.json();
                alert(`Bir hata oluştu: ${errorData.detail || 'Bilinmeyen sunucu hatası'}`);
            }

        } catch (error) {
            console.error("Fetch hatası:", error);
            alert(`Ağ hatası: Sunucuya bağlanılamadı. API'nin çalıştığından emin misin? ${error.message}`);
        } finally {
            
            loader.style.display = "none";
            submitButton.disabled = false;
            submitButton.textContent = "İşlemi Başlat";
        }
    });
});