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
├── dist/                             # Production Cloudflare Pages build
│   ├── index.html                    # Quality inspection UI
│   ├── style.css                     # Dashboard styling
│   ├── app.js                        # Client-side CV & Grad-CAM engine
│   ├── samples/                      # Metallurgical specimens
│   └── _headers                      # Edge security and cache headers
├── tata est project/                 # FastAPI backend and web server
│   ├── server.py                     # FastAPI REST API with Grad-CAM & Sobel
│   ├── app.py                        # Streamlit visualizer
│   ├── run.bat                       # Windows launch script
│   ├── models/                        # ResNet-50 weights
│   └── samples/                      # Defect specimens
├── tata-steel-crack-detection/       # Deep learning pipeline and notebooks
│   ├── src/                          # Augmentation, training, evaluation, Grad-CAM
│   ├── notebooks/                    # EDA and transfer learning notebooks
│   ├── app/streamlit_app.py          # Streamlit inspection app
│   └── main.py                       # Pipeline runner
├── wrangler.toml                     # Cloudflare Pages deployment configuration
└── README.md
```

---

## 📜 Industrial Quality Standards

- **ASTM E381**: Macroetch testing and quality grading of steel products.
- **ISO 9001:2015 Clause 8.6**: Release of products and services inspection compliance.
- **EN 10163**: Specification for the delivery requirements for surface condition of hot-rolled steel plates, wide flats and sections.
