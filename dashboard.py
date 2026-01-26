from flask import Flask, render_template, request, jsonify, send_file
import tensorflow as tf
import cv2
import numpy as np
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
import base64
from collections import Counter
import io
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'web_uploads'

MODEL_PATH = 'YZDBHTS_colab.h5'
TARGET_SIZE = (224, 224)
LABELS = ["Külleme", "Leke", "Pas", "Sağlıklı"]
LABEL_EN = {"Külleme": "Powdery Mildew", "Leke": "Leaf Spot", "Pas": "Rust", "Sağlıklı": "Healthy"}

Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path('web_results').mkdir(exist_ok=True)

try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
except Exception as e:
    model = None

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img_resized = cv2.resize(img, TARGET_SIZE)
    img_array = np.expand_dims(img_resized, axis=0)
    img_normalized = (img_array / 127.5) - 1
    return img_normalized

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'success': False, 'error': 'Model yuklenemedi'})

    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'Resim bulunamadi'})

    file = request.files['image']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'Dosya secilmedi'})

    if file and allowed_file(file.filename):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"upload_{timestamp}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            processed_image = preprocess_image(filepath)

            start_time = time.time()
            predictions = model.predict(processed_image, verbose=0)
            inference_time = time.time() - start_time

            pred_index = np.argmax(predictions)
            prediction = LABELS[pred_index]
            prediction_en = LABEL_EN[prediction]
            confidence = float(predictions[0][pred_index])

            all_scores = {
                LABELS[i]: float(predictions[0][i])
                for i in range(len(LABELS))
            }

            result = {
                'success': True,
                'prediction': prediction,
                'prediction_en': prediction_en,
                'confidence': confidence,
                'all_scores': all_scores,
                'inference_time': inference_time,
                'timestamp': datetime.now().isoformat()
            }

            result_path = f"web_results/result_{timestamp}.json"
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            return jsonify(result)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'Gecersiz dosya tipi'})

@app.route('/stats')
def stats():
    try:
        results_dir = Path('web_results')
        result_files = list(results_dir.glob('*.json'))

        total = len(result_files)
        predictions = {label: 0 for label in LABELS}

        for result_file in result_files:
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pred = data.get('prediction', '')
                if pred in predictions:
                    predictions[pred] += 1

        return jsonify({
            'success': True,
            'total': total,
            'predictions': predictions
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
