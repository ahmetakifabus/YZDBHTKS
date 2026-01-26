#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Bitki Hastalığı Tespit Sistemi
Advanced Plant Disease Detection System
Version: 2.0
"""

import numpy as np
import tensorflow as tf
import cv2
from picamera import PiCamera
import time
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import logging


# ===============================
# CONFIGURATION / YAPILANDIRMA
# ===============================

class Config:
    """Sistem yapılandırma sınıfı"""
    HEDEF_BOYUT = (224, 224)
    MODEL_YOLU = 'YZDBHTS_colab.h5'
    KAMERA_COZUNURLUK = (640, 480)
    ETIKETLER = ["Külleme", "Leke", "Pas", "Sağlıklı"]

    # Yeni özellikler
    SONUC_KLASORU = 'results'
    LOG_KLASORU = 'logs'
    GORUNTU_KLASORU = 'captured_images'
    MIN_GUVEN_SKORU = 0.70  # %70'in altındaki tahminler şüpheli

    # Renk kodları (terminal çıktısı için)
    RENKLER = {
        "Külleme": "\033[93m",  # Sarı
        "Leke": "\033[94m",  # Mavi
        "Pas": "\033[91m",  # Kırmızı
        "Sağlıklı": "\033[92m",  # Yeşil
        "RESET": "\033[0m"
    }


# ===============================
# LOGGING SETUP / LOG SİSTEMİ
# ===============================

def setup_logging():
    """Gelişmiş log sistemi kurulumu"""
    log_dir = Path(Config.LOG_KLASORU)
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"detection_log_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


# ===============================
# HELPER FUNCTIONS / YARDIMCI FONKSİYONLAR
# ===============================

def create_directories():
    """Gerekli klasörleri oluştur"""
    directories = [
        Config.SONUC_KLASORU,
        Config.LOG_KLASORU,
        Config.GORUNTU_KLASORU,
        f"{Config.SONUC_KLASORU}/json",
        f"{Config.SONUC_KLASORU}/annotated_images"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def load_model_safe(model_path, logger):
    """Güvenli model yükleme"""
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")

        logger.info(f"Model yükleniyor: {model_path}")
        model = tf.keras.models.load_model(model_path, compile=False)
        logger.info(f"✓ Model başarıyla yüklendi (Boyut: {os.path.getsize(model_path) / (1024 * 1024):.2f} MB)")

        return model

    except Exception as e:
        logger.error(f"✗ Model yükleme hatası: {e}")
        raise


def capture_image_safe(camera_resolution, logger):
    """Güvenli görüntü yakalama"""
    try:
        camera = PiCamera()
        camera.resolution = camera_resolution

        logger.info("Kamera hazırlanıyor...")
        time.sleep(2)  # Kamera odaklanma

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        foto_yolu = f"{Config.GORUNTU_KLASORU}/capture_{timestamp}.jpg"

        camera.capture(foto_yolu)
        camera.close()

        logger.info(f"✓ Fotoğraf kaydedildi: {foto_yolu}")
        return foto_yolu

    except Exception as e:
        logger.error(f"✗ Kamera hatası: {e}")
        raise


def preprocess_image(image_path, target_size, logger):
    """Görüntü ön işleme"""
    try:
        goruntu = cv2.imread(image_path)

        if goruntu is None:
            raise ValueError(f"Görüntü okunamadı: {image_path}")

        # Resize
        islenmis = cv2.resize(goruntu, target_size)

        # Normalizasyon (MobileNetV2 için -1 ile 1 arası)
        islenmis = np.expand_dims(islenmis, axis=0)
        islenmis = (islenmis / 127.5) - 1

        logger.info(f"✓ Görüntü işlendi: {islenmis.shape}")
        return goruntu, islenmis

    except Exception as e:
        logger.error(f"✗ Görüntü işleme hatası: {e}")
        raise


def predict_disease(model, processed_image, logger):
    """Hastalık tahmini yap"""
    try:
        logger.info("Tahmin yapılıyor...")

        start_time = time.time()
        tahminler = model.predict(processed_image, verbose=0)
        inference_time = time.time() - start_time

        en_yuksek_indeks = np.argmax(tahminler)
        sonuc_etiketi = Config.ETIKETLER[en_yuksek_indeks]
        guven_skoru = tahminler[0][en_yuksek_indeks]

        # Tüm sınıf skorlarını al
        all_scores = {
            Config.ETIKETLER[i]: float(tahminler[0][i])
            for i in range(len(Config.ETIKETLER))
        }

        result = {
            'prediction': sonuc_etiketi,
            'confidence': float(guven_skoru),
            'all_scores': all_scores,
            'inference_time': inference_time,
            'timestamp': datetime.now().isoformat(),
            'is_confident': guven_skoru >= Config.MIN_GUVEN_SKORU
        }

        logger.info(f"✓ Tahmin: {sonuc_etiketi} (%{guven_skoru * 100:.2f})")
        logger.info(f"✓ Süre: {inference_time:.3f} saniye")

        return result

    except Exception as e:
        logger.error(f"✗ Tahmin hatası: {e}")
        raise


def save_results(result, image_path, logger):
    """Sonuçları kaydet"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # JSON sonucu kaydet
        json_path = f"{Config.SONUC_KLASORU}/json/result_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ Sonuç kaydedildi: {json_path}")

        # Görüntüye etiket ekle
        annotate_image(image_path, result, timestamp, logger)

    except Exception as e:
        logger.error(f"✗ Sonuç kaydetme hatası: {e}")


def annotate_image(image_path, result, timestamp, logger):
    """Görüntüye sonuç etiketi ekle"""
    try:
        img = cv2.imread(image_path)

        # Etiket bilgileri
        text = f"{result['prediction']} - %{result['confidence'] * 100:.1f}"

        # Arka plan rengi (güven skoru düşükse kırmızı, yüksekse yeşil)
        color = (0, 255, 0) if result['is_confident'] else (0, 0, 255)

        # Metin ekle
        cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, color, 2, cv2.LINE_AA)

        # Zaman damgası ekle
        cv2.putText(img, timestamp, (10, img.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Kaydet
        output_path = f"{Config.SONUC_KLASORU}/annotated_images/annotated_{timestamp}.jpg"
        cv2.imwrite(output_path, img)

        logger.info(f"✓ Etiketli görüntü: {output_path}")

    except Exception as e:
        logger.error(f"✗ Görüntü etiketleme hatası: {e}")


def print_detailed_result(result):
    """Detaylı sonucu terminale yazdır"""
    pred = result['prediction']
    conf = result['confidence'] * 100
    color = Config.RENKLER.get(pred, "")
    reset = Config.RENKLER["RESET"]

    print("\n" + "=" * 60)
    print(f"{color}{'   YAPAY ZEKA TESPİT SONUCU':^60}{reset}")
    print("=" * 60)
    print(f"\n  📊 Tahmin Edilen Durum: {color}{pred}{reset}")
    print(f"  🎯 Güvenirlik Oranı: {color}%{conf:.2f}{reset}")
    print(f"  ⏱️  İşlem Süresi: {result['inference_time']:.3f} saniye")
    print(f"  ⚠️  Güvenilir mi?: {'✓ EVET' if result['is_confident'] else '✗ HAYIR (Düşük güven)'}")

    print(f"\n  📈 Tüm Sınıf Skorları:")
    for label, score in sorted(result['all_scores'].items(),
                               key=lambda x: x[1], reverse=True):
        bar_length = int(score * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        label_color = Config.RENKLER.get(label, "")
        print(f"     {label_color}{label:12s}{reset} │{bar}│ %{score * 100:.1f}")

    print("\n" + "=" * 60 + "\n")


def batch_process_images(model, image_folder, logger):
    """Toplu görüntü işleme"""
    image_files = list(Path(image_folder).glob("*.jpg")) + \
                  list(Path(image_folder).glob("*.png"))

    logger.info(f"Toplu işlem başlıyor: {len(image_files)} görüntü")

    results = []
    for img_path in image_files:
        try:
            original, processed = preprocess_image(str(img_path),
                                                   Config.HEDEF_BOYUT, logger)
            result = predict_disease(model, processed, logger)
            result['image_path'] = str(img_path)
            results.append(result)

            print(f"✓ {img_path.name}: {result['prediction']} (%{result['confidence'] * 100:.1f})")

        except Exception as e:
            logger.error(f"✗ {img_path.name} işlenemedi: {e}")

    # Toplu sonuçları kaydet
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    batch_result_path = f"{Config.SONUC_KLASORU}/json/batch_result_{timestamp}.json"

    with open(batch_result_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"✓ Toplu işlem tamamlandı: {batch_result_path}")
    return results


# ===============================
# MAIN FUNCTION / ANA FONKSİYON
# ===============================

def main():
    """Ana program döngüsü"""

    # Argüman ayrıştırıcı
    parser = argparse.ArgumentParser(
        description='Gelişmiş Bitki Hastalığı Tespit Sistemi'
    )
    parser.add_argument('--batch', action='store_true',
                        help='Toplu işlem modu')
    parser.add_argument('--input-folder', type=str,
                        help='Toplu işlem için görüntü klasörü')
    parser.add_argument('--save-results', action='store_true',
                        help='Sonuçları kaydet')
    parser.add_argument('--model-path', type=str, default=Config.MODEL_YOLU,
                        help='Model dosya yolu')

    args = parser.parse_args()

    # Kurulum
    logger = setup_logging()
    create_directories()

    logger.info("=" * 60)
    logger.info("Bitki Hastalığı Tespit Sistemi v2.0 Başlatılıyor...")
    logger.info("=" * 60)

    try:
        # Model yükle
        model = load_model_safe(args.model_path, logger)

        # Toplu işlem modu
        if args.batch and args.input_folder:
            results = batch_process_images(model, args.input_folder, logger)

            # Özet istatistikler
            print(f"\n📊 TOPLU İŞLEM ÖZETİ:")
            print(f"  Toplam: {len(results)}")
            for label in Config.ETIKETLER:
                count = sum(1 for r in results if r['prediction'] == label)
                print(f"  {label}: {count}")

        # Tekli işlem modu
        else:
            # Görüntü yakala
            foto_yolu = capture_image_safe(Config.KAMERA_COZUNURLUK, logger)

            # Görüntü işle
            original, islenmis = preprocess_image(foto_yolu,
                                                  Config.HEDEF_BOYUT, logger)

            # Tahmin yap
            result = predict_disease(model, islenmis, logger)

            # Sonuçları göster
            print_detailed_result(result)

            # Sonuçları kaydet
            if args.save_results:
                save_results(result, foto_yolu, logger)

        logger.info("✓ İşlem başarıyla tamamlandı!")

    except KeyboardInterrupt:
        logger.info("\n⚠️  Program kullanıcı tarafından durduruldu.")

    except Exception as e:
        logger.error(f"\n✗ Kritik hata: {e}")
        raise

    finally:
        logger.info("Program sonlandırılıyor...")


if __name__ == "__main__":
    main()