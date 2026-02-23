@echo off
setlocal enabledelayedexpansion

echo ========================================
echo      Ataturk AI Voice - HIZLI COMMIT
echo ========================================

:: Değişiklikleri kontrol et
git status --short

echo.
set /p msg="Commit mesaji girin (Bos birakirsa 'Update' kullanilir): "

if "!msg!"=="" (
    set msg=Update
)

echo.
echo Devisiklikler ekleniyor...
git add .

echo Commit atiliyor: "!msg!"
git commit -m "!msg!"

echo Gonderiliyor (Push)...
git push origin main

echo.
echo ========================================
echo Islem tamamlandi!
echo ========================================
pause
