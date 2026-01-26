$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`n[UYARI] Bu script yönetici olarak çalıştırılmalı!" -ForegroundColor Red
    Write-Host "PowerShell'i sağ tıklayın ve 'Yönetici olarak çalıştır' seçin.`n" -ForegroundColor Yellow
    pause
    exit 1
}
Clear-Host
Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🌿 Bitki Hastalığı Tespit Sistemi v2.0             ║" -ForegroundColor Green
Write-Host "║   Windows PowerShell Otomatik Kurulum                 ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "[BİLGİ] Sistem bilgileri:" -ForegroundColor Blue
Write-Host "  OS: $([System.Environment]::OSVersion.VersionString)"
Write-Host "  PowerShell: $($PSVersionTable.PSVersion)"
Write-Host "  Arch: $([System.Environment]::Is64BitOperatingSystem)"
Write-Host ""

Write-Host "[ADIM 1/9] Python kontrolü yapılıyor..." -ForegroundColor Blue
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python bulundu: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[HATA] Python bulunamadı!" -ForegroundColor Red
    Write-Host "`nPython 3.7+ kurmanız gerekiyor." -ForegroundColor Yellow
    Write-Host "İndirme: https://www.python.org/downloads/`n" -ForegroundColor Yellow
    Write-Host "ÖNEMLI: Kurulum sırasında 'Add Python to PATH' seçeneğini işaretleyin!`n" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "`n[ADIM 2/9] pip güncelleniyor..." -ForegroundColor Blue
python -m pip install --upgrade pip --quiet
Write-Host "[OK] pip güncellendi" -ForegroundColor Green

Write-Host "`n[ADIM 3/9] Proje klasörleri oluşturuluyor..." -ForegroundColor Blue
$folders = @(
    "results",
    "results\json",
    "results\annotated_images",
    "logs",
    "captured_images",
    "web_uploads",
    "web_results",
    "models",
    "static",
    "static\css",
    "static\js",
    "static\images"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  ✓ $folder oluşturuldu" -ForegroundColor Gray
    } else {
        Write-Host "  ✓ $folder zaten var" -ForegroundColor Gray
    }
}
Write-Host "[OK] Klasörler hazır" -ForegroundColor Green

# requirements.txt oluştur
Write-Host "`n[ADIM 4/9] requirements.txt oluşturuluyor..." -ForegroundColor Blue
$requirements = @"
tensorflow==2.13.0
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.0.0
flask==2.3.3
flask-cors==4.0.0
matplotlib==3.7.2
scipy==1.11.2
pandas==2.0.3
scikit-learn==1.3.0
h5py==3.9.0
werkzeug==2.3.7
python-dotenv==1.0.0
"@

$requirements | Out-File -FilePath "requirements.txt" -Encoding utf8
Write-Host "[OK] requirements.txt oluşturuldu" -ForegroundColor Green

Write-Host "`n[ADIM 5/9] Python paketleri kuruluyor..." -ForegroundColor Blue
Write-Host "Bu işlem 5-10 dakika sürebilir, lütfen bekleyin...`n" -ForegroundColor Yellow

$packages = Get-Content "requirements.txt" | Where-Object { $_ -match '\S' }
$total = $packages.Count
$current = 0

foreach ($package in $packages) {
    $current++
    $progress = [math]::Round(($current / $total) * 100)

    Write-Progress -Activity "Paketler kuruluyor" -Status "$package" -PercentComplete $progress
    Write-Host "[$current/$total] $package kuruluyor..." -ForegroundColor Cyan

    $result = python -m pip install "$package" --quiet --disable-pip-version-check 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $package kuruldu" -ForegroundColor Green
    } else {
        Write-Host "  [UYARI] $package kurulamadı (isteğe bağlı)" -ForegroundColor Yellow
    }
}

Write-Progress -Activity "Paketler kuruluyor" -Completed
Write-Host "`n[OK] Tüm paketler kuruldu" -ForegroundColor Green

Write-Host "`n[ADIM 6/9] Yapılandırma dosyası oluşturuluyor..." -ForegroundColor Blue
$config = @"

model:
  path: "YZDBHTS_colab.h5"
  input_size: [224, 224]
  labels:
    - "Külleme"
    - "Leke"
    - "Pas"
    - "Sağlıklı"

detection:
  min_confidence: 0.70
  save_results: true
  save_images: true

web:
  host: "0.0.0.0"
  port: 5000
  debug: false
  max_upload_size: 16

paths:
  results: "results"
  logs: "logs"
  images: "captured_images"
"@

$config | Out-File -FilePath "config.yaml" -Encoding utf8
Write-Host "[OK] config.yaml oluşturuldu" -ForegroundColor Green

Write-Host "`n[ADIM 7/9] Test scripti oluşturuluyor..." -ForegroundColor Blue
$testScript = @"
import sys
import importlib

def test_installation():
    print("🧪 Windows Kurulum Testi\n")
    tests = [
        ("tensorflow", "TensorFlow"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("flask", "Flask"),
    ]
    passed = 0
    for module, name in tests:
        try:
            importlib.import_module(module)
            print(f"✓ {name:15s} - OK")
            passed += 1
        except ImportError:
            print(f"✗ {name:15s} - HATA")
    print(f"\n{'='*40}")
    print(f"Başarılı: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)
"@

$testScript | Out-File -FilePath "test_installation.py" -Encoding utf8
Write-Host "[OK] test_installation.py oluşturuldu" -ForegroundColor Green

Write-Host "`n[ADIM 8/9] Hızlı başlatma scriptleri oluşturuluyor..." -ForegroundColor Blue

$webBat = @"
@echo off
color 0B
cls
echo.
echo ╔════════════════════════════════════════╗
echo ║  🌐 Web Arayüzü Başlatılıyor...      ║
echo ╚════════════════════════════════════════╝
echo.
echo Web arayüzünü tarayıcınızda açın:
echo.
echo    http://localhost:5000
echo.
echo Durdurmak için: CTRL+C
echo.
python web_dashboard_pro.py
pause
"@
$webBat | Out-File -FilePath "run_web.bat" -Encoding ascii

$webPs1 = @"
Clear-Host
Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🌐 Web Arayüzü Başlatılıyor...      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan
Write-Host "Web arayüzünü tarayıcınızda açın:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000`n" -ForegroundColor White
Write-Host "Durdurmak için: CTRL+C`n" -ForegroundColor Gray

try {
    Start-Process "http://localhost:5000"
} catch {
    Write-Host "Tarayıcı otomatik açılamadı, manuel olarak açın.`n" -ForegroundColor Yellow
}

python web_dashboard_pro.py
"@
$webPs1 | Out-File -FilePath "run_web.ps1" -Encoding utf8

$advancedBat = @"
@echo off
color 0E
cls
echo.
echo ╔════════════════════════════════════════╗
echo ║  🚀 Gelişmiş Tespit Sistemi          ║
echo ╚════════════════════════════════════════╝
echo.
python YZDBHTS_advanced.py --save-results
pause
"@
$advancedBat | Out-File -FilePath "run_advanced.bat" -Encoding ascii

Write-Host "[OK] Başlatma scriptleri oluşturuldu" -ForegroundColor Green

Write-Host "`n[ADIM 9/9] Model dosyası kontrol ediliyor..." -ForegroundColor Blue
if (Test-Path "YZDBHTS_colab.h5") {
    $size = (Get-Item "YZDBHTS_colab.h5").Length / 1MB
    Write-Host "[OK] Model bulundu ($([math]::Round($size, 2)) MB)" -ForegroundColor Green

    Copy-Item "YZDBHTS_colab.h5" "models\" -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Model models\ klasörüne kopyalandı" -ForegroundColor Green
} else {
    Write-Host "[UYARI] Model dosyası bulunamadı!" -ForegroundColor Yellow
    Write-Host "`nLütfen YZDBHTS_colab.h5 dosyasını bu klasöre kopyalayın." -ForegroundColor Red
    Write-Host "Model dosyası olmadan sistem çalışmayacaktır!`n" -ForegroundColor Red
}

Write-Host "`n[TEST] Kurulum test ediliyor...`n" -ForegroundColor Blue
python test_installation.py
$testResult = $LASTEXITCODE

Write-Host "`n`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          ✅ KURULUM TAMAMLANDI!                       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📁 Oluşturulan Dosyalar:" -ForegroundColor Cyan
Write-Host "   ├── requirements.txt"
Write-Host "   ├── config.yaml"
Write-Host "   ├── test_installation.py"
Write-Host "   ├── run_web.bat / run_web.ps1"
Write-Host "   └── run_advanced.bat`n"

Write-Host "📂 Oluşturulan Klasörler:" -ForegroundColor Cyan
Write-Host "   ├── results\"
Write-Host "   ├── logs\"
Write-Host "   ├── web_uploads\"
Write-Host "   ├── web_results\"
Write-Host "   └── models\`n"

Write-Host "🚀 Nasıl Kullanılır:" -ForegroundColor Cyan
Write-Host "`n   1. Web Arayüzü (Önerilen):"
Write-Host "      .\run_web.ps1" -ForegroundColor Yellow
Write-Host "      veya: run_web.bat`n" -ForegroundColor Yellow

Write-Host "   2. Gelişmiş Tespit:"
Write-Host "      run_advanced.bat`n" -ForegroundColor Yellow

if ($testResult -eq 0) {
    Write-Host "✅ Tüm testler başarılı!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Bazı paketlerde sorun var, lütfen kontrol edin." -ForegroundColor Yellow
}

if (-not (Test-Path "YZDBHTS_colab.h5")) {
    Write-Host "`n⚠️  ÖNEMLI: Model dosyasını eklemeyi unutmayın!" -ForegroundColor Red
    Write-Host "   YZDBHTS_colab.h5 dosyasını bu klasöre koyun.`n" -ForegroundColor Yellow
}

Write-Host "`nİyi çalışmalar! 🌿`n" -ForegroundColor Green
Write-Host "Devam etmek için bir tuşa basın..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")