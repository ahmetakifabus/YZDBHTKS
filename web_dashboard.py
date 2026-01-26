#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌿 Professional Plant Disease Detection Web Dashboard
Ultra Advanced Web Interface with Real-time Analytics
"""

from flask import Flask, render_template_string, request, jsonify, send_file
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

# ===============================
# FLASK APP
# ===============================

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
    print(f"✓ Model loaded: {MODEL_PATH}")
except Exception as e:
    print(f"✗ Model loading error: {e}")
    model = None

# ===============================
# ULTRA ADVANCED HTML TEMPLATE
# ===============================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Plant Disease Detection Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --dark-bg: #1a1a2e;
            --dark-card: #16213e;
            --light-bg: #f8f9fa;
            --light-card: #ffffff;
            --text-dark: #2d3748;
            --text-light: #e2e8f0;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--light-bg);
            color: var(--text-dark);
            transition: var(--transition);
            overflow-x: hidden;
        }

        body.dark-mode {
            background: var(--dark-bg);
            color: var(--text-light);
        }

        /* Navbar */
        .navbar {
            background: var(--primary-gradient);
            padding: 1rem 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
            color: white;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .navbar-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .theme-toggle {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .theme-toggle:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }

        /* Main Container */
        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        /* Dashboard Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }

        body.dark-mode .stat-card {
            background: var(--dark-card);
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: var(--primary-gradient);
        }

        .stat-icon {
            width: 60px;
            height: 60px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #6b7280;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Main Content Area */
        .content-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        @media (max-width: 1024px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Upload Section */
        .upload-section {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        body.dark-mode .upload-section {
            background: var(--dark-card);
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            cursor: pointer;
            transition: var(--transition);
            background: linear-gradient(135deg, rgba(102,126,234,0.05) 0%, rgba(118,75,162,0.05) 100%);
            position: relative;
        }

        .upload-area:hover {
            border-color: #764ba2;
            background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
            transform: scale(1.02);
        }

        .upload-area.dragging {
            border-color: var(--success-color);
            background: rgba(16,185,129,0.1);
        }

        .upload-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }

        #imageInput, #batchInput {
            display: none;
        }

        /* Preview Section */
        .preview-section {
            margin-top: 2rem;
            display: none;
        }

        .image-preview-container {
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 1rem;
        }

        #imagePreview {
            width: 100%;
            display: block;
        }

        .preview-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 50%);
            display: flex;
            align-items: flex-end;
            padding: 1.5rem;
        }

        /* Buttons */
        .btn {
            background: var(--primary-gradient);
            color: white;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 5px 15px rgba(102,126,234,0.4);
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(102,126,234,0.6);
        }

        .btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
            transform: none;
        }

        .btn-secondary {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }

        /* Results Section */
        .result-container {
            margin-top: 2rem;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: none;
            animation: slideIn 0.5s ease-out;
        }

        body.dark-mode .result-container {
            background: var(--dark-card);
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        .prediction-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.8rem;
            font-weight: 700;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }

        .confidence-section {
            margin: 2rem 0;
        }

        .confidence-bar {
            height: 40px;
            background: #e5e7eb;
            border-radius: 50px;
            overflow: hidden;
            position: relative;
        }

        body.dark-mode .confidence-bar {
            background: #374151;
        }

        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--success-color) 0%, #059669 100%);
            transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1.2rem;
        }

        /* Charts */
        .chart-container {
            position: relative;
            height: 300px;
            margin: 2rem 0;
        }

        /* History Sidebar */
        .history-section {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            max-height: 800px;
            overflow-y: auto;
        }

        body.dark-mode .history-section {
            background: var(--dark-card);
        }

        .history-item {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            background: #f9fafb;
            cursor: pointer;
            transition: var(--transition);
        }

        body.dark-mode .history-item {
            background: #1a1a2e;
        }

        .history-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .history-thumbnail {
            width: 60px;
            height: 60px;
            border-radius: 10px;
            object-fit: cover;
            margin-right: 1rem;
        }

        /* Loading */
        .loading {
            display: none;
            text-align: center;
            padding: 3rem;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Comparison Mode */
        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 2rem;
        }

        /* Export Menu */
        .export-menu {
            position: relative;
            display: inline-block;
        }

        .export-dropdown {
            display: none;
            position: absolute;
            top: 100%;
            right: 0;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            min-width: 200px;
            margin-top: 0.5rem;
            z-index: 1000;
        }

        body.dark-mode .export-dropdown {
            background: var(--dark-card);
        }

        .export-dropdown.show {
            display: block;
            animation: fadeIn 0.2s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .export-item {
            padding: 1rem;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .export-item:hover {
            background: #f3f4f6;
        }

        body.dark-mode .export-item:hover {
            background: #1a1a2e;
        }

        /* Notifications */
        .notification {
            position: fixed;
            top: 100px;
            right: 2rem;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: none;
            animation: slideInRight 0.3s ease-out;
            z-index: 1001;
        }

        body.dark-mode .notification {
            background: var(--dark-card);
        }

        @keyframes slideInRight {
            from { transform: translateX(400px); }
            to { transform: translateX(0); }
        }

        .notification.show {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        body.dark-mode ::-webkit-scrollbar-track {
            background: #1a1a2e;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 5px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .navbar {
                padding: 1rem;
            }

            .container {
                padding: 0 1rem;
            }

            .dashboard-grid {
                grid-template-columns: 1fr;
            }

            .comparison-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <div class="navbar">
        <div class="navbar-brand">
            <i class="fas fa-leaf"></i>
            <span>Plant Disease Detection Pro</span>
        </div>
        <div class="navbar-controls">
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="themeIcon"></i>
                <span id="themeText">Dark Mode</span>
            </button>
            <div class="export-menu">
                <button class="btn btn-secondary" onclick="toggleExportMenu()">
                    <i class="fas fa-download"></i>
                    Export
                </button>
                <div class="export-dropdown" id="exportDropdown">
                    <div class="export-item" onclick="exportPDF()">
                        <i class="fas fa-file-pdf"></i> Export PDF
                    </div>
                    <div class="export-item" onclick="exportCSV()">
                        <i class="fas fa-file-csv"></i> Export CSV
                    </div>
                    <div class="export-item" onclick="exportJSON()">
                        <i class="fas fa-file-code"></i> Export JSON
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Notification -->
    <div class="notification" id="notification">
        <i class="fas fa-check-circle" style="color: var(--success-color); font-size: 1.5rem;"></i>
        <span id="notificationText">Success!</span>
    </div>

    <!-- Main Container -->
    <div class="container">
        <!-- Dashboard Stats -->
        <div class="dashboard-grid">
            <div class="stat-card">
                <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <i class="fas fa-camera"></i>
                </div>
                <div class="stat-value" id="totalScans">0</div>
                <div class="stat-label">Total Scans</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-value" id="healthyCount">0</div>
                <div class="stat-label">Healthy Plants</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white;">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="stat-value" id="diseasedCount">0</div>
                <div class="stat-label">Diseased Plants</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white;">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="stat-value">87.25%</div>
                <div class="stat-label">Model Accuracy</div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="content-grid">
            <!-- Upload & Results -->
            <div>
                <div class="upload-section">
                    <h2 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-upload"></i>
                        Upload Plant Image
                    </h2>

                    <div class="upload-area" id="uploadArea">
                        <div class="upload-icon">📸</div>
                        <h3>Drop your plant image here</h3>
                        <p style="color: #6b7280; margin: 1rem 0;">or click to browse</p>
                        <input type="file" id="imageInput" accept="image/*" />
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-secondary" onclick="document.getElementById('batchInput').click()">
                                <i class="fas fa-images"></i>
                                Multiple Images
                            </button>
                            <input type="file" id="batchInput" accept="image/*" multiple />
                        </div>
                    </div>

                    <div class="preview-section" id="previewSection">
                        <div class="image-preview-container">
                            <img id="imagePreview" />
                            <div class="preview-overlay">
                                <button class="btn" id="analyzeBtn">
                                    <i class="fas fa-microscope"></i>
                                    Analyze Now
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <h3>AI is analyzing your plant...</h3>
                        <p style="color: #6b7280;">This usually takes 2-3 seconds</p>
                    </div>

                    <div class="result-container" id="resultContainer">
                        <div class="result-header">
                            <h2 style="display: flex; align-items: center; gap: 0.5rem;">
                                <i class="fas fa-chart-pie"></i>
                                Detection Results
                            </h2>
                            <span class="prediction-badge" id="predictionBadge"></span>
                        </div>

                        <div class="confidence-section">
                            <h3 style="margin-bottom: 1rem;">Confidence Score</h3>
                            <div class="confidence-bar">
                                <div class="confidence-fill" id="confidenceFill">0%</div>
                            </div>
                        </div>

                        <div class="chart-container">
                            <canvas id="resultChart"></canvas>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 2rem;">
                            <div style="padding: 1rem; background: #f9fafb; border-radius: 10px;">
                                <p style="color: #6b7280; margin-bottom: 0.5rem;">Inference Time</p>
                                <p style="font-size: 1.5rem; font-weight: 700;" id="inferenceTime">-</p>
                            </div>
                            <div style="padding: 1rem; background: #f9fafb; border-radius: 10px;">
                                <p style="color: #6b7280; margin-bottom: 0.5rem;">Timestamp</p>
                                <p style="font-size: 1rem; font-weight: 600;" id="timestamp">-</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- History Sidebar -->
            <div class="history-section">
                <h2 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-history"></i>
                    Recent Scans
                </h2>
                <div id="historyList">
                    <p style="color: #6b7280; text-align: center; padding: 2rem;">
                        No scans yet. Upload an image to get started!
                    </p>
                </div>
            </div>
        </div>

        <!-- Analytics Dashboard -->
        <div class="upload-section" style="margin-top: 2rem;">
            <h2 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-chart-bar"></i>
                Analytics Dashboard
            </h2>
            <div class="chart-container" style="height: 400px;">
                <canvas id="analyticsChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Global state
        let history = [];
        let currentResult = null;
        let resultChart = null;
        let analyticsChart = null;

        // Theme toggle
        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            document.getElementById('themeIcon').className = isDark ? 'fas fa-sun' : 'fas fa-moon';
            document.getElementById('themeText').textContent = isDark ? 'Light Mode' : 'Dark Mode';
            localStorage.setItem('theme', isDark ? 'dark' : 'light');

            // Update charts
            if (resultChart) updateChartTheme(resultChart);
            if (analyticsChart) updateChartTheme(analyticsChart);
        }

        // Load saved theme
        window.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-mode');
                document.getElementById('themeIcon').className = 'fas fa-sun';
                document.getElementById('themeText').textContent = 'Light Mode';
            }
            loadHistory();
            updateAnalytics();
        });

        // Upload handling
        const uploadArea = document.getElementById('uploadArea');
        const imageInput = document.getElementById('imageInput');
        const batchInput = document.getElementById('batchInput');
        const previewSection = document.getElementById('previewSection');
        const imagePreview = document.getElementById('imagePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const resultContainer = document.getElementById('resultContainer');

        uploadArea.addEventListener('click', () => imageInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragging');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragging');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragging');
            const file = e.dataTransfer.files[0];
            handleImageSelect(file);
        });

        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            handleImageSelect(file);
        });

        batchInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            showNotification(`Processing ${files.length} images...`);
            files.forEach(file => handleImageSelect(file, true));
        });

        function handleImageSelect(file, batch = false) {
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.src = e.target.result;
                    previewSection.style.display = 'block';
                    resultContainer.style.display = 'none';

                    if (batch) {
                        analyzeImage(file);
                    }
                };
                reader.readAsDataURL(file);
            }
        }

        analyzeBtn.addEventListener('click', () => {
            const file = imageInput.files[0];
            if (file) analyzeImage(file);
        });

        async function analyzeImage(file) {
            const formData = new FormData();
            formData.append('image', file);

            loading.style.display = 'block';
            resultContainer.style.display = 'none';
            analyzeBtn.disabled = true;

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    displayResult(result);
                    addToHistory(result, imagePreview.src);
                    updateStats();
                    showNotification('Analysis complete!');
                } else {
                    showNotification('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Connection error: ' + error.message, 'error');
            } finally {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        }

        function displayResult(result) {
            currentResult = result;
            const badge = document.getElementById('predictionBadge');
            const fill = document.getElementById('confidenceFill');
            const inferenceTime = document.getElementById('inferenceTime');
            const timestamp = document.getElementById('timestamp');

            const colors = {
                'Külleme': '#f59e0b',
                'Leke': '#3b82f6',
                'Pas': '#ef4444',
                'Sağlıklı': '#10b981'
            };

            badge.textContent = result.prediction + ' / ' + result.prediction_en;
            badge.style.background = colors[result.prediction];
            badge.style.color = 'white';

            const confidence = (result.confidence * 100).toFixed(1);
            fill.style.width = confidence + '%';
            fill.textContent = confidence + '%';

            inferenceTime.textContent = result.inference_time.toFixed(3) + 's';
            timestamp.textContent = new Date(result.timestamp).toLocaleString();

            createResultChart(result.all_scores);
            resultContainer.style.display = 'block';
            resultContainer.scrollIntoView({ behavior: 'smooth' });
        }

        function createResultChart(scores) {
            const ctx = document.getElementById('resultChart').getContext('2d');

            if (resultChart) resultChart.destroy();

            const isDark = document.body.classList.contains('dark-mode');
            const textColor = isDark ? '#e2e8f0' : '#2d3748';

            resultChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(scores),
                    datasets: [{
                        label: 'Confidence Score',
                        data: Object.values(scores).map(v => v * 100),
                        backgroundColor: [
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(16, 185, 129, 0.8)'
                        ],
                        borderColor: [
                            'rgb(245, 158, 11)',
                            'rgb(59, 130, 246)',
                            'rgb(239, 68, 68)',
                            'rgb(16, 185, 129)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                color: textColor,
                                callback: function(value) {
                                    return value + '%';
                                }
                            },
                            grid: {
                                color: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: textColor
                            },
                            grid: {
                                color: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
                            }
                        }
                    }
                }
            });
        }

        function updateChartTheme(chart) {
            const isDark = document.body.classList.contains('dark-mode');
            const textColor = isDark ? '#e2e8f0' : '#2d3748';
            const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

            chart.options.scales.y.ticks.color = textColor;
            chart.options.scales.x.ticks.color = textColor;
            chart.options.scales.y.grid.color = gridColor;
            chart.options.scales.x.grid.color = gridColor;
            chart.update();
        }

        function addToHistory(result, imageSrc) {
            history.unshift({
                ...result,
                imageSrc: imageSrc,
                id: Date.now()
            });

            if (history.length > 10) history.pop();
            localStorage.setItem('scanHistory', JSON.stringify(history));
            renderHistory();
        }

        function loadHistory() {
            const saved = localStorage.getItem('scanHistory');
            if (saved) {
                history = JSON.parse(saved);
                renderHistory();
            }
        }

        function renderHistory() {
            const historyList = document.getElementById('historyList');

            if (history.length === 0) {
                historyList.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 2rem;">No scans yet</p>';
                return;
            }

            historyList.innerHTML = history.map(item => `
                <div class="history-item" onclick='showHistoryItem(${JSON.stringify(item).replace(/'/g, "&#39;")})'>
                    <div style="display: flex; align-items: center;">
                        <img src="${item.imageSrc}" class="history-thumbnail" />
                        <div style="flex: 1;">
                            <div style="font-weight: 600; margin-bottom: 0.25rem;">${item.prediction}</div>
                            <div style="color: #6b7280; font-size: 0.9rem;">${(item.confidence * 100).toFixed(1)}% confidence</div>
                            <div style="color: #9ca3af; font-size: 0.8rem;">${new Date(item.timestamp).toLocaleString()}</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function showHistoryItem(item) {
            imagePreview.src = item.imageSrc;
            previewSection.style.display = 'block';
            displayResult(item);
        }

        function updateStats() {
            document.getElementById('totalScans').textContent = history.length;
            const healthy = history.filter(h => h.prediction === 'Sağlıklı').length;
            const diseased = history.length - healthy;
            document.getElementById('healthyCount').textContent = healthy;
            document.getElementById('diseasedCount').textContent = diseased;

            updateAnalytics();
        }

        function updateAnalytics() {
            const ctx = document.getElementById('analyticsChart').getContext('2d');

            if (analyticsChart) analyticsChart.destroy();

            const counts = {};
            ['Külleme', 'Leke', 'Pas', 'Sağlıklı'].forEach(label => {
                counts[label] = history.filter(h => h.prediction === label).length;
            });

            const isDark = document.body.classList.contains('dark-mode');
            const textColor = isDark ? '#e2e8f0' : '#2d3748';

            analyticsChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(counts),
                    datasets: [{
                        data: Object.values(counts),
                        backgroundColor: [
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(16, 185, 129, 0.8)'
                        ],
                        borderColor: [
                            'rgb(245, 158, 11)',
                            'rgb(59, 130, 246)',
                            'rgb(239, 68, 68)',
                            'rgb(16, 185, 129)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: textColor,
                                padding: 20,
                                font: {
                                    size: 14
                                }
                            }
                        }
                    }
                }
            });
        }

        function toggleExportMenu() {
            document.getElementById('exportDropdown').classList.toggle('show');
        }

        function exportPDF() {
            showNotification('PDF export feature coming soon!');
            toggleExportMenu();
        }

        function exportCSV() {
            if (history.length === 0) {
                showNotification('No data to export', 'error');
                return;
            }

            const csv = [
                ['Timestamp', 'Prediction', 'Confidence', 'Inference Time'],
                ...history.map(h => [
                    h.timestamp,
                    h.prediction,
                    (h.confidence * 100).toFixed(2) + '%',
                    h.inference_time.toFixed(3) + 's'
                ])
            ].map(row => row.join(',')).join('\\n');

            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `plant_disease_results_${Date.now()}.csv`;
            a.click();

            showNotification('CSV exported successfully!');
            toggleExportMenu();
        }

        function exportJSON() {
            if (history.length === 0) {
                showNotification('No data to export', 'error');
                return;
            }

            const json = JSON.stringify(history, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `plant_disease_results_${Date.now()}.json`;
            a.click();

            showNotification('JSON exported successfully!');
            toggleExportMenu();
        }

        function showNotification(text, type = 'success') {
            const notification = document.getElementById('notification');
            const notificationText = document.getElementById('notificationText');
            notificationText.textContent = text;
            notification.classList.add('show');

            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        // Close export menu when clicking outside
        window.addEventListener('click', (e) => {
            if (!e.target.closest('.export-menu')) {
                document.getElementById('exportDropdown').classList.remove('show');
            }
        });
    </script>
</body>
</html>
'''


# ===============================
# HELPER FUNCTIONS
# ===============================

def preprocess_image(image_path):
    """Image preprocessing"""
    img = cv2.imread(image_path)
    img_resized = cv2.resize(img, TARGET_SIZE)
    img_array = np.expand_dims(img_resized, axis=0)
    img_normalized = (img_array / 127.5) - 1
    return img_normalized


def allowed_file(filename):
    """Check allowed file types"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===============================
# ROUTES
# ===============================

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint"""
    if model is None:
        return jsonify({'success': False, 'error': 'Model not loaded'})

    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'})

    file = request.files['image']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    if file and allowed_file(file.filename):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"upload_{timestamp}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            processed_image = preprocess_image(filepath)

            import time
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

    return jsonify({'success': False, 'error': 'Invalid file type'})


@app.route('/stats')
def stats():
    """Statistics endpoint"""
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


# ===============================
# MAIN
# ===============================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🌿 PROFESSIONAL PLANT DISEASE DETECTION WEB DASHBOARD")
    print("=" * 70)
    print("\n✓ Server starting...")
    print("✓ Open in browser: http://localhost:5000")
    print("✓ Press CTRL+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5000)