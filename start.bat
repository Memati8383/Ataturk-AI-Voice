@echo off
setlocal

echo.
echo ============================================
echo   ATATURK AI BASLATICISI v2.1
echo ============================================
echo.

:: 1. Python Sanal Ortam (venv) Kontrolu
if not exist "venv\Scripts\python.exe" (
    echo [BILGI] Sanal ortam bulunamadi, olusturuluyor...
    python -m venv venv
    if errorlevel 1 (
        echo [HATA] Sanal ortam olusturulamadi! Python'un sistemde yuklu oldugundan emin olun.
        pause
        exit /b
    )
)

:: 2. PIP Surumunu Ayarla (Kritik: omegaconf hatasi icin pip<24.1 gerekli)
echo [BILGI] PIP surumu 24.0'a sabitleniyor (rvc-python uyumlulugu icin)...
venv\Scripts\python.exe -m pip install pip==24.0

:: 3. Gerekli Kutuphaneleri Kur
echo [BILGI] Kutuphaneler kontrol ediliyor (venv)...
:: Ilk once torch (CUDA destekli - varsa hizli calisir)
venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

:: Diger kutuphaneler
echo [BILGI] Diger bagimliliklar yukleniyor...
venv\Scripts\python.exe -m pip install fastapi uvicorn python-multipart requests ollama edge-tts rvc-python

:: 4. Cloudflared Tunnel Baslat (Arka planda start ile)
echo [BILGI] Cloudflare Tunnel baslatiliyor...
if exist cloudflared.exe (
    start "Cloudflare Tunnel" cloudflared.exe tunnel --url http://localhost:8000
) else (
    echo [UYARI] cloudflared.exe bulunamadi! Internet erisimi olmayacak.
    echo Lutfen cloudflared.exe'yi bu klasore indirin.
)

:: 5. Uygulamayi Baslat
echo [BILGI] API Sunucusu baslatiliyor...
echo.
echo Lutfen acilan diger penceredeki (Cloudflare) linki kullanin.
echo.
venv\Scripts\python.exe main.py

pause
