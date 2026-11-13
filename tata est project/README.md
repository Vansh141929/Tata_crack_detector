# SteelGuard AI · Tata Steel Surface Quality Intelligence

Next-generation industrial surface inspection and defect explainability platform inspired by the Factory minimalist design system.

---

## 🌟 Key Features

- **Factory Minimalist Architecture:** High-contrast Swiss design system with clean white typography, dark bento-grid feature layout, ghosted metrics, and live telemetry cards.
- **ResNet-50 Deep Learning Engine:** Fine-tuned convolutional classifier across 6 certified defect signatures:
  1. `Crazing` (Thermal fatigue mold cracks - High Risk)
  2. `Linear Scratches` (Abrasive handling damage - High Risk)
  3. `Rolled-in Scale` (Descaling pressure drop - Medium Risk)
  4. `Pitted Surface` (Roll spalling & cavity wear - Medium Risk)
  5. `Surface Patches` (Uneven oxidation - Low Risk)
  6. `Slag Inclusions` (Non-metallic casting deoxidation - Low Risk)
- **Grad-CAM Explainability:** Real gradient-weighted class activation mapping on bottleneck conv layers (`conv5_block3_out`) with interactive opacity blending.
- **Computer Vision Synthesis:** Sobel gradient vectors and Laplacian surface energy contours for defect boundary delineation.
- **Enterprise Compliance:** ASTM E381 & ISO 9001:2015 quality inspection certificate generation with exportable JSON audit records.

---

## 🚀 How to Launch

### Option 1: Modern Web Application (Recommended · Port 8000)
```powershell
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

Or simply double-click `run.bat`.

---

### Option 2: Streamlit Dashboard (Port 8501)
```powershell
python -m streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 📂 Project Structure

```
tata est project/
├── models/
│   └── resnet50_crack_detector.h5    # Pretrained ResNet-50 weights
├── samples/                          # Reference metallurgical specimens
│   ├── crazing_sample.jpg
│   ├── scratches_sample.jpg
│   ├── rolled_in_scale_sample.jpg
│   ├── pitted_surface_sample.jpg
│   ├── patches_sample.jpg
│   └── inclusion_sample.jpg
├── static/                           # Modern Factory-inspired frontend
│   ├── index.html                    # HTML5 semantic structure
│   ├── style.css                     # Minimalist Swiss design system
│   └── app.js                        # Interactive inference & Grad-CAM controls
├── server.py                         # FastAPI backend & Grad-CAM pipeline
├── app.py                            # Streamlit edition
├── run.bat                           # 1-click startup script
└── README.md
```
