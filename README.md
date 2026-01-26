ENGLISH SECTION
AI-Powered Plant Disease Detection System

Project Description

This project is a deep learning application developed to enhance agricultural productivity and diagnose plant diseases at an early stage. The system utilizes Raspberry Pi hardware and a specially trained Convolutional Neural Network (CNN) architecture to analyze plant leaf diseases in real-time.
Key Features

    High Accuracy: The model achieved an accuracy rate of 87.25% during testing.

    Extensive Dataset: Trained on a comprehensive dataset containing a total of 29,623 images.

    Four-Class Classification: The system can distinguish between Powdery Mildew, Leaf Spot, Rust diseases, and Healthy states.

    Edge Computing: Optimized with MobileNetV2 architecture for high performance on edge devices like Raspberry Pi.

Technical Specifications

    Architecture: MobileNetV2 (Transfer Learning).

    Training Environment: Google Colab (Using T4 GPU acceleration).

    Input Resolution: 224x224 pixels.

    Training Cycles: Optimized over 2 epochs.

Installation and Usage
    Install Dependencies:
    Bash:
    pip install tflite-runtime opencv-python numpy

Execute System: Ensure the model file (YZDBHTS_colab.h5) and the script (YZDBHTS.py) are in the same directory.

    Bash:
    python3 YZDBHTS.py

TÜRKÇE BÖLÜM
Yapay Zeka Destekli Bitki Hastalığı Tespit Sistemi

Proje Hakkında

Bu proje, tarımsal verimliliği artırmak ve bitki hastalıklarını erken aşamada teşhis etmek amacıyla geliştirilmiş bir derin öğrenme uygulamasıdır. Sistem, Raspberry Pi donanımı ve özel olarak eğitilmiş bir evrişimli sinir ağı (CNN) mimarisi kullanarak bitki yapraklarındaki hastalıkları gerçek zamanlı olarak analiz eder.
Temel Özellikler

    Yüksek Doğruluk: Yapılan testler sonucunda model %87.25 doğruluk oranına ulaşmıştır.

    Geniş Veri Seti: Model, toplamda 29.623 adet görüntü içeren kapsamlı bir veri seti ile eğitilmiştir.

    Dört Farklı Sınıflandırma: Sistem; Külleme, Leke, Pas hastalıklarını ve Sağlıklı durumunu birbirinden ayırt edebilir.

    Hızlı Çıkarım: MobileNetV2 mimarisi sayesinde Raspberry Pi gibi düşük donanımlı cihazlarda bile hızlı çalışır.

Teknik Detaylar

    Model Mimarisi: MobileNetV2 (Transfer Learning).

    Eğitim Platformu: Google Colab (T4 GPU desteği ile).

    Giriş Boyutu: 224x224 piksel.

    Optimizasyon: 2 Epoch (Tur) üzerinden optimize edilmiştir.

Kurulum ve Kullanım
    Kütüphaneleri Yükleyin:

    Terminal:
    pip install tflite-runtime opencv-python numpy

Sistemi Çalıştırın: Model dosyası (YZDBHTS_colab.h5) ve ana kod (YZDBHTS.py) aynı dizinde olmalıdır.

    Terminal:
    python3 YZDBHTS.py

Telif Hakkı ve Lisans / Copyright and License

TR: © 2026. Bu projenin tüm hakları saklıdır. Bu yazılım ve beraberindeki dosya koleksiyonu, eğitim
ve araştırma amaçlı geliştirilmiştir. İzinsiz kopyalanması veya ticari amaçla kullanılması yasaktır. Yapay zeka
eğitimi Google Colab yardımıyla gerçekleştirilmiştir.

EN: © 2026. All rights reserved. This software and its associated documentation are developed for educational and
research purposes. Unauthorized copying or commercial use is prohibited. The AI training was performed with the help
of Google Colab.
