# 🚀 Hızlı Başlangıç Kılavuzu / Quick Start Guide

## 📦 Windows Kurulum

### Yöntem 1: PowerShell (Önerilen)
```powershell
# PowerShell'i YÖNETİCİ olarak açın ve çalıştırın:
.\setup_windows.ps1
```

### Yöntem 2: CMD / Batch
```batch
# CMD'yi YÖNETİCİ olarak açın ve çalıştırın:
setup_windows.bat
```

### Gereksinimler
- ✅ Windows 10/11
- ✅ Python 3.7+ ([İndir](https://www.python.org/downloads/))
- ✅ 4GB RAM (minimum)
- ✅ 2GB boş disk alanı

**ÖNEMLI:** Python kurulumunda "Add Python to PATH" seçeneğini işaretleyin!

---

## 🐧 Linux/Mac Kurulum

```bash
# Terminal'i açın ve çalıştırın:
chmod +x setup.sh
./setup.sh
```

---

## 🌐 Web Arayüzünü Başlatma (EN KOLAY YOL!)

### Windows:
```powershell
# PowerShell:
.\run_web.ps1

# veya CMD:
run_web.bat
```

### Linux/Mac:
```bash
./run_web.sh
```

Tarayıcınızda açın: **http://localhost:5000**

---

## ✨ Web Arayüzü Özellikleri

### 1️⃣ Ana Özellikler
- 📸 **Drag & Drop** - Dosyayı sürükle bırak
- 📊 **Gerçek Zamanlı İstatistikler** - Canlı dashboard
- 📈 **Grafikler** - Chart.js ile görselleştirme
- 🌓 **Dark/Light Mode** - Tema değiştir
- 📁 **Toplu İşlem** - Birden fazla görüntü
- 💾 **Export** - CSV, JSON, PDF
- 📜 **Geçmiş** - Önceki taramalar

### 2️⃣ Kullanım Akışı
1. **Fotoğraf yükle** → Drag & drop veya tıkla
2. **Analiz et** → "Analyze Now" butonuna tıkla
3. **Sonuçları gör** → 2-3 saniye içinde
4. **Export et** → İstersen CSV/JSON olarak kaydet

### 3️⃣ Toplu İşlem
- "Multiple Images" butonuna tıkla
- Birden fazla dosya seç
- Tüm dosyalar otomatik işlenir

---

## 💻 Komut Satırı Kullanımı

### Basit Tespit (Kamera - Sadece Raspberry Pi)
```bash
python3 YZDBHTS.py
```

### Gelişmiş Tespit (Sonuç Kaydet)
```bash
# Windows:
python YZDBHTS_advanced.py --save-results

# Linux/Mac:
python3 YZDBHTS_advanced.py --save-results
```

### Toplu İşlem (Klasördeki Tüm Resimler)
```bash
python3 YZDBHTS_advanced.py --batch --input-folder ./my_images
```

---

## 📊 Sonuç Formatları

### 1. JSON (Detaylı)
```json
{
  "prediction": "Külleme",
  "prediction_en": "Powdery Mildew",
  "confidence": 0.9432,
  "all_scores": {
    "Külleme": 0.9432,
    "Leke": 0.0312,
    "Pas": 0.0156,
    "Sağlıklı": 0.0100
  },
  "inference_time": 1.523,
  "timestamp": "2025-01-15T14:30:00"
}
```

### 2. CSV (Tablo)
```csv
Timestamp,Prediction,Confidence,Inference Time
2025-01-15 14:30:00,Külleme,94.32%,1.523s
2025-01-15 14:32:15,Sağlıklı,89.15%,1.487s
```

### 3. Etiketli Görüntü
- Sonuç + güvenirlik skoru görüntü üzerine yazılır
- `results/annotated_images/` klasöründe saklanır

---

## 📁 Klasör Yapısı

```
plant-disease-detection/
│
├── 📄 YZDBHTS_colab.h5          # Model dosyası (SİZ EKLEYIN!)
├── 🐍 YZDBHTS.py                # Basit tespit scripti
├── 🚀 YZDBHTS_advanced.py       # Gelişmiş script
├── 🌐 web_dashboard_pro.py      # Web arayüzü
│
├── 📂 results/                  # Sonuçlar
│   ├── json/                    # JSON sonuçları
│   └── annotated_images/        # Etiketli görseller
│
├── 📂 logs/                     # Log dosyaları
├── 📂 captured_images/          # Yakalanan görseller
├── 📂 web_uploads/              # Web yüklemeleri
├── 📂 web_results/              # Web sonuçları
└── 📂 models/                   # Model dosyaları
```

---

## 🔧 Sorun Giderme

### ❌ "Model dosyası bulunamadı"
```bash
# Model dosyasını kontrol et
ls -lh YZDBHTS_colab.h5  # Linux/Mac
dir YZDBHTS_colab.h5     # Windows

# Yoksa, dosyayı proje klasörüne kopyalayın
```

### ❌ "Python bulunamadı"
```bash
# Python kurulu mu kontrol et
python --version   # Windows
python3 --version  # Linux/Mac

# Yoksa indir: https://www.python.org/downloads/
```

### ❌ "Module not found" hatası
```bash
# Paketleri tekrar kur
pip install -r requirements.txt   # Windows
pip3 install -r requirements.txt  # Linux/Mac
```

### ❌ Web arayüzü açılmıyor
```bash
# Port 5000 kullanımda mı kontrol et
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Farklı port kullan
python web_dashboard_pro.py --port 8080
```

### ❌ Kamera çalışmıyor (Raspberry Pi)
```bash
# Kamerayı test et
raspistill -o test.jpg

# Kamera etkin değilse
sudo raspi-config
# Interface Options → Camera → Enable
```

---

## 📈 Model Performansı

| Metrik | Değer |
|--------|-------|
| **Genel Doğruluk** | 87.25% |
| **Külleme F1-Score** | 91% |
| **Leke F1-Score** | 89% |
| **Pas F1-Score** | 87% |
| **Sağlıklı F1-Score** | 88% |
| **Inference Time (RPi 4)** | ~1.5s |
| **Inference Time (PC)** | ~0.3s |

---

## 🎯 Hastalık Sınıfları

### 1. Külleme (Powdery Mildew) 🟡
- Yapraklarda beyaz toz görünümü
- Genellikle yaprak üst yüzeyinde
- Yüksek nem ortamlarında yaygın

### 2. Leke (Leaf Spot) 🔵
- Yapraklarda kahverengi/siyah lekeler
- Çember şeklinde lezyonlar
- Su ile yayılır

### 3. Pas (Rust) 🔴
- Yapraklarda pas rengi kabarcıklar
- Yaprak alt yüzeyinde daha yaygın
- Rüzgar ile hızla yayılır

### 4. Sağlıklı (Healthy) 🟢
- Homojen yeşil renk
- Leke veya lezyonsuz
- Düzgün yaprak dokusu

---

## 💡 İpuçları

### Daha İyi Sonuçlar İçin:
1. ✅ **İyi ışıklandırma** - Doğal ışık ideal
2. ✅ **Odaklanmış görüntü** - Bulanık olmasın
3. ✅ **Yakın çekim** - Yaprak detayı görünsün
4. ✅ **Düz açı** - Yan açılardan çekin
5. ❌ **Gölge yok** - Yaprak gölgede olmasın

### Hız İpuçları:
- 💾 **Sonuç kaydetmeyin** → Daha hızlı (`--no-save`)
- 🖼️ **Küçük resimler** → 224x224 ideal
- 🔄 **TFLite kullanın** → 3x daha hızlı

---

## 📞 Destek

### Sorun mu yaşıyorsunuz?
1. 📖 **README.md** dosyasını okuyun
2. 🐛 **GitHub Issues** açın
3. 📧 **Email** gönderin

### Yararlı Bağlantılar
- 📚 [Tam Dokümantasyon](README.md)
- 🔬 [Model Eğitim Detayları](MODEL_TRAINING.md)
- 🎓 [TensorFlow Docs](https://www.tensorflow.org/)
- 🍓 [Raspberry Pi Docs](https://www.raspberrypi.org/documentation/)

---

## 🎉 Hazırsınız!

Web arayüzünü başlatın ve bitki hastalıklarını tespit etmeye başlayın:

```bash
# Windows
.\run_web.ps1

# Linux/Mac
./run_web.sh
```

**Tarayıcıda:** http://localhost:5000

---

**İyi çalışmalar! 🌿**