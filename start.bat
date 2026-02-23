@echo off
setlocal

echo.
echo ============================================
echo   ATATURK AI BASLATICISI v2.2
echo ============================================
echo.

:: 0. Port Temizligi (8000 portunu kullanan varsa kapat)
echo [BILGI] Port 8000 kontrol ediliyor...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo [BILGI] PID %%a tarafindan kullanilan port temizleniyor...
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 >nul


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
if exist tools\cloudflared.exe (
    start "Cloudflare Tunnel" tools\cloudflared.exe tunnel --url http://localhost:8000
) else (
    echo [UYARI] tools\cloudflared.exe bulunamadi! Internet erisimi olmayacak.
    echo Lutfen cloudflared.exe'yi tools klasorune indirin.
)



:: 5. Ollama Kontrolu ve Baslatma
echo [BILGI] Ollama kontrol ediliyor...
where ollama >nul 2>nul
if %errorlevel% equ 0 (
    echo [BILGI] Ollama bulundu, servis baslatiliyor...
    :: Arka planda baslat, halihazirda calisiyorsa hata vermez
    start "Ollama Engine" /min ollama serve
) else (
    echo [UYARI] Ollama sistemde bulunamadi! Chat ozelligi calismayabilir.
    echo Lutfen https://ollama.com adresinden indirin.
)

:: 6. Uygulamayi Baslat

echo [BILGI] API Sunucusu baslatiliyor...
echo.
echo Lutfen acilan diger penceredeki (Cloudflare) linki kullanin.
echo.
venv\Scripts\python.exe main.py

pause
