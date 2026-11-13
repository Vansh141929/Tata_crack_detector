# 🛡️ SteelGuard AI · Tata Steel Surface Quality Intelligence

> **Enterprise-grade industrial surface inspection and defect explainability platform designed for continuous casting and hot strip mill lines at Tata Steel.**

Certified compliance engine under **ASTM E381** & **ISO 9001:2015**.

---

## 🌟 Architecture & Highlights

- **⚡ Cloudflare Pages Edge Deployment:** High-contrast Swiss minimalist dashboard running globally on Cloudflare edge CDN (`dist/`).
- **🔍 Explainable AI (Grad-CAM):** Gradient-weighted Class Activation Mapping computed across ResNet-50 bottleneck layers (`conv5_block3_out`) with real-time opacity blending.
- **📐 Computer Vision Delineation:** High-frequency Sobel spatial gradient filters for edge contour extraction and crack surface area quantification.
- **🏷️ Multi-Class Certified Defect Taxonomy:**
  1. `Crazing Cracks` (High Risk · Thermal fatigue in casting molds)
  2. `Linear Scratches` (High Risk · Guide roller abrasive damage)
  3. `Rolled-in Scale` (Medium Risk · Descaling header pressure breakdown)
  4. `Pitted Surface` (Medium Risk · Work roll surface spalling)
  5. `Surface Patches` (Low Risk · Localized coolant splash / uneven oxidation)
  6. `Slag Inclusion` (Low Risk · Non-metallic deoxidation particles)
- **📋 Compliance Certification:** Automatic JSON inspection certificate generation adhering to industrial audit standards.

---

## 📂 Repository Structure

```
tata-steel-crack-detection/
├── dist/                             # 🚀 Production Cloudflare Pages build
│   ├── index.html                    # High-contrast quality inspection UI
│   ├── style.css                     # Minimalist industrial styling
│   ├── app.js                        # Client-side CV & Grad-CAM engine
│   ├── samples/                      # Certified metallurgical specimens
│   └── _headers                      # Edge security and cache headers
├── tata est project/                 # 🌐 Modern FastAPI Backend & Web Server
│   ├── server.py                     # FastAPI REST API with Grad-CAM & Sobel
│   ├── app.py                        # Streamlit visualizer
│   ├── run.bat                       # One-click Windows launch script
│   ├── models/                       # ResNet-50 weights
│   └── samples/                      # High-resolution defect specimens
├── tata-steel-crack-detection/       # 🧠 Deep Learning Pipeline & Notebooks
│   ├── src/                          # Augmentation, training, evaluation, gradcam
│   ├── notebooks/                    # EDA and transfer learning notebooks
│   ├── app/streamlit_app.py          # Interactive Streamlit inspection app
│   └── main.py                       # Pipeline runner
├── wrangler.toml                     # Cloudflare Pages deployment configuration
└── README.md                         # Comprehensive documentation
```

---

## 🚀 Quick Start Guide

### 1. View Cloudflare Pages Web App Locally
Open `dist/index.html` directly in any web browser, or serve with:
```powershell
npx serve dist
```

### 2. Run Local Python API Server (FastAPI + ResNet-50)
```powershell
cd "tata est project"
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)**.

### 3. Run Streamlit Analytics Dashboard
```powershell
cd "tata-steel-crack-detection"
python -m streamlit run app/streamlit_app.py
```
Open **[http://localhost:8501](http://localhost:8501)**.

---

## ☁️ Deploying to Cloudflare Pages

### Option A: Via GitHub CI/CD (Recommended)
1. Push this repository to your GitHub account.
2. In the [Cloudflare Dashboard](https://dash.cloudflare.com):
   - Go to **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git**.
   - Select your repository.
   - Set **Build output directory** to `dist`.
   - Click **Save and Deploy**.
3. Every `git push` automatically redeploys your live application!

### Option B: Via Wrangler CLI
```powershell
npx wrangler login
npx wrangler pages deploy dist --project-name tata-steel-crack-detection
```

---

## 📜 Industrial Quality Standards
- **ASTM E381**: Macroetch testing and quality grading of steel products.
- **ISO 9001:2015 Clause 8.6**: Release of products and services inspection compliance.
- **EN 10163**: Specification for the delivery requirements for surface condition of hot-rolled steel plates, wide flats and sections.
