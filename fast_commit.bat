@echo off
setlocal enabledelayedexpansion

:: Renk ve Başlık
color 0B
title Ataturk AI Voice - Git Otomasyonu

echo ========================================
echo      Ataturk AI Voice - HIZLI COMMIT
echo ========================================

:: 1. Mevcut durumu göster
echo [+] Mevcut degisiklikler:
git status --short
echo.

:: 2. Değişiklik yoksa çıkış yap
git diff --quiet --exit-code
if %errorlevel% equ 0 (
    echo [!] Degisiklik bulunmadi. Islem iptal ediliyor.
    goto end
)

:: 3. Mesaj al
set /p msg="Commit mesaji girin (Bos ise 'Auto-update %date%'): "

if "!msg!"=="" (
    set msg=Auto-update %date% %time%
)

:: 4. Git İşlemleri
echo.
echo [+] Islemler baslatiliyor...

:: Add
git add .
if %errorlevel% neq 0 (
    echo [X] Dosyalar eklenirken hata olustu!
    goto end
)

:: Commit
git commit -m "!msg!"
if %errorlevel% neq 0 (
    echo [X] Commit sirasinda hata olustu!
    goto end
)

:: Push (Önce çekmeyi deneyerek çakışmayı önleme seçeneği eklenebilir)
echo [+] Veriler sunucuya gonderiliyor (Push)...
git push origin main
if %errorlevel% neq 0 (
    echo [X] Push basarisiz! Lutfen internet baglantisini veya uzak depoyu kontrol edin.
) else (
    echo.
    echo ========================================
    echo [OK] Islem basariyla tamamlandi!
    echo ========================================
)

:end
pause