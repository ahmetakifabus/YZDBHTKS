import numpy as np
import tensorflow as tf
import cv2
import time
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import logging

class Config:
    HEDEF_BOYUT = (224, 224)
    MODEL_YOLU = 'YZDBHTS_colab.h5'
    KAMERA_COZUNURLUK = (640, 480)
    ETIKETLER = ["Külleme", "Leke", "Pas", "Sağlıklı"]
    SONUC_KLASORU = 'results'
    LOG_KLASORU = 'logs'
    GORUNTU_KLASORU = 'captured_images'
    MIN_GUVEN_SKORU = 0.70
    RENKLER = {
        "Külleme": "\033[93m",
        "Leke": "\033[94m",
        "Pas": "\033[91m",
        "Sağlıklı": "\033[92m",
        "RESET": "\033[0m"
    }

def setup_logging():
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

def create_directories():
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
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")
        logger.info(f"Model yükleniyor: {model_path}")
        model = tf.keras.models.load_model(model_path, compile=False)
        logger.info(f"Model başarıyla yüklendi (Boyut: {os.path.getsize(model_path) / (1024 * 1024):.2f} MB)")
        return model
    except Exception as e:
        logger.error(f"Model yükleme hatası: {e}")
        raise

def capture_image_safe(camera_resolution, logger):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Kamera açılamadı!")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_resolution[1])
        logger.info("Kamera hazırlanıyor...")
        time.sleep(2)
        ret, frame = cap.read()
        if not ret:
            raise Exception("Görüntü alınamadı!")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        foto_yolu = f"{Config.GORUNTU_KLASORU}/capture_{timestamp}.jpg"
        cv2.imwrite(foto_yolu, frame)
        cap.release()
        logger.info(f"Fotoğraf kaydedildi: {foto_yolu}")
        return foto_yolu
    except Exception as e:
        logger.error(f"Kamera hatası: {e}")
        raise

def preprocess_image(image_path, target_size, logger):
    try:
        goruntu = cv2.imread(image_path)
        if goruntu is None:
            raise ValueError(f"Görüntü okunamadı: {image_path}")
        islenmis = cv2.resize(goruntu, target_size)
        islenmis = np.expand_dims(islenmis, axis=0)
        islenmis = (islenmis / 127.5) - 1
        logger.info(f"Görüntü işlendi: {islenmis.shape}")
        return goruntu, islenmis
    except Exception as e:
        logger.error(f"Görüntü işleme hatası: {e}")
        raise

def predict_disease(model, processed_image, logger):
    try:
        logger.info("Tahmin yapılıyor...")
        start_time = time.time()
        tahminler = model.predict(processed_image, verbose=0)
        inference_time = time.time() - start_time
        en_yuksek_indeks = np.argmax(tahminler)
        sonuc_etiketi = Config.ETIKETLER[en_yuksek_indeks]
        guven_skoru = tahminler[0][en_yuksek_indeks]
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
        logger.info(f"Tahmin: {sonuc_etiketi} (%{guven_skoru * 100:.2f})")
        logger.info(f"Süre: {inference_time:.3f} saniye")
        return result
    except Exception as e:
        logger.error(f"Tahmin hatası: {e}")
        raise

def save_results(result, image_path, logger):
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = f"{Config.SONUC_KLASORU}/json/result_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Sonuç kaydedildi: {json_path}")
        annotate_image(image_path, result, timestamp, logger)
    except Exception as e:
        logger.error(f"Sonuç kaydetme hatası: {e}")

def annotate_image(image_path, result, timestamp, logger):
    try:
        img = cv2.imread(image_path)
        text = f"{result['prediction']} - %{result['confidence'] * 100:.1f}"
        color = (0, 255, 0) if result['is_confident'] else (0, 0, 255)
        cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        cv2.putText(img, timestamp, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        output_path = f"{Config.SONUC_KLASORU}/annotated_images/annotated_{timestamp}.jpg"
        cv2.imwrite(output_path, img)
        logger.info(f"Etiketli görüntü: {output_path}")
    except Exception as e:
        logger.error(f"Görüntü etiketleme hatası: {e}")

def print_detailed_result(result):
    pred = result['prediction']
    conf = result['confidence'] * 100
    color = Config.RENKLER.get(pred, "")
    reset = Config.RENKLER["RESET"]
    print("\n" + "=" * 60)
    print(f"{color}{'   YAPAY ZEKA TESPIT SONUCU':^60}{reset}")
    print("=" * 60)
    print(f"\n  Tahmin Edilen Durum: {color}{pred}{reset}")
    print(f"  Güvenirlik Oranı: {color}%{conf:.2f}{reset}")
    print(f"  İşlem Süresi: {result['inference_time']:.3f} saniye")
    print(f"  Güvenilir mi?: {'EVET' if result['is_confident'] else 'HAYIR (Düşük güven)'}")
    print(f"\n  Tüm Sınıf Skorları:")
    for label, score in sorted(result['all_scores'].items(), key=lambda x: x[1], reverse=True):
        bar_length = int(score * 40)
        bar = "#" * bar_length + "-" * (40 - bar_length)
        label_color = Config.RENKLER.get(label, "")
        print(f"     {label_color}{label:12s}{reset} |{bar}| %{score * 100:.1f}")
    print("\n" + "=" * 60 + "\n")

def batch_process_images(model, image_folder, logger):
    image_files = list(Path(image_folder).glob("*.jpg")) + list(Path(image_folder).glob("*.png"))
    logger.info(f"Toplu işlem başlıyor: {len(image_files)} görüntü")
    results = []
    for img_path in image_files:
        try:
            original, processed = preprocess_image(str(img_path), Config.HEDEF_BOYUT, logger)
            result = predict_disease(model, processed, logger)
            result['image_path'] = str(img_path)
            results.append(result)
            print(f"Ok {img_path.name}: {result['prediction']} (%{result['confidence'] * 100:.1f})")
        except Exception as e:
            logger.error(f"Hata {img_path.name} işlenemedi: {e}")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    batch_result_path = f"{Config.SONUC_KLASORU}/json/batch_result_{timestamp}.json"
    with open(batch_result_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"Toplu işlem tamamlandı: {batch_result_path}")
    return results

def main():
    parser = argparse.ArgumentParser(description='Gelişmiş Bitki Hastalığı Tespit Sistemi')
    parser.add_argument('--batch', action='store_true', help='Toplu işlem modu')
    parser.add_argument('--input-folder', type=str, help='Toplu işlem için görüntü klasörü')
    parser.add_argument('--save-results', action='store_true', help='Sonuçları kaydet')
    parser.add_argument('--model-path', type=str, default=Config.MODEL_YOLU, help='Model dosya yolu')
    args = parser.parse_args()
    logger = setup_logging()
    create_directories()
    logger.info("=" * 60)
    logger.info("Bitki Hastalığı Tespit Sistemi v2.0 Başlatılıyor...")
    logger.info("=" * 60)
    try:
        model = load_model_safe(args.model_path, logger)
        if args.batch and args.input_folder:
            results = batch_process_images(model, args.input_folder, logger)
            print(f"\nTOPLU İŞLEM ÖZETİ:")
            print(f"  Toplam: {len(results)}")
            for label in Config.ETIKETLER:
                count = sum(1 for r in results if r['prediction'] == label)
                print(f"  {label}: {count}")
        else:
            foto_yolu = capture_image_safe(Config.KAMERA_COZUNURLUK, logger)
            original, islenmis = preprocess_image(foto_yolu, Config.HEDEF_BOYUT, logger)
            result = predict_disease(model, islenmis, logger)
            print_detailed_result(result)
            if args.save_results:
                save_results(result, foto_yolu, logger)
        logger.info("İşlem başarıyla tamamlandı!")
    except KeyboardInterrupt:
        logger.info("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.error(f"\nKritik hata: {e}")
        raise
    finally:
        logger.info("Program sonlandırılıyor...")

if __name__ == "__main__":
    main()