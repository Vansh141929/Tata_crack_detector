import os
import io
import time
import base64
import numpy as np
import cv2
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Suppress TensorFlow verbose logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

app = FastAPI(title="SteelGuard AI - Tata Steel Surface Inspection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
STATIC_DIR = os.path.join(BASE_DIR, "static")

CLASS_NAMES = [
    "crazing", "inclusion", "patches",
    "pitted_surface", "rolled-in_scale", "scratches",
]

CLASS_METADATA = {
    "crazing": {
        "display": "Crazing",
        "risk": "HIGH",
        "color": "#e02f2f",
        "score": 85,
        "description": "Network of fine surface cracks forming a web-like pattern caused by rapid thermal cycling in continuous casting molds.",
        "cause": "Thermal fatigue & mold flux lubrication failure",
        "action": "Immediate mold water spray adjustment & slab surface scarfing.",
    },
    "inclusion": {
        "display": "Inclusion",
        "risk": "LOW",
        "color": "#16a34a",
        "score": 25,
        "description": "Non-metallic oxide or sulfide particles entrapped in the steel matrix during ladle deoxidation or casting.",
        "cause": "Tundish slag entrainment or deoxidation residue",
        "action": "Flag coil for secondary non-critical stamping applications.",
    },
    "patches": {
        "display": "Patches",
        "risk": "LOW",
        "color": "#16a34a",
        "score": 20,
        "description": "Irregular discoloured or rough localized surface regions caused by uneven scale breakdown or coolant splashing.",
        "cause": "High-pressure descaling header pressure drops",
        "action": "Inspect descaler nozzle alignment; clear for standard cold rolling.",
    },
    "pitted_surface": {
        "display": "Pitted Surface",
        "risk": "MEDIUM",
        "color": "#d97706",
        "score": 55,
        "description": "Localized small cavities or crater depressions caused by rolled-in scale fallout or roll surface spalling.",
        "cause": "Work roll surface degradation or pickling over-etch",
        "action": "Schedule work roll replacement on Mill Stand F3/F4.",
    },
    "rolled-in_scale": {
        "display": "Rolled-in Scale",
        "risk": "MEDIUM",
        "color": "#d97706",
        "score": 60,
        "description": "Dark iron oxide flakes mechanically pressed into the steel strip surface during roughing or finishing passes.",
        "cause": "Inadequate primary descaling pressure before roughing",
        "action": "Verify descaler pump pressure > 180 bar; acid pickling line review.",
    },
    "scratches": {
        "display": "Scratches",
        "risk": "HIGH",
        "color": "#e02f2f",
        "score": 90,
        "description": "Prominent longitudinal abrasive scoring marks caused by mechanical contact with guide chutes, aprons, or coilers.",
        "cause": "Guide roller misalignment or foreign metal pickup on guides",
        "action": "Halt roll line entry table; polish guide plates; reject automotive coil.",
    },
}

MODEL = None
GRAD_MODEL = None

def init_model():
    global MODEL, GRAD_MODEL
    model_paths = [
        os.path.join(MODELS_DIR, "resnet50_crack_detector.h5"),
        os.path.join(BASE_DIR, "..", "tata-steel-crack-detection", "models", "resnet50_crack_detector.h5"),
    ]
    for p in model_paths:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            try:
                print(f"[Model] Loading ResNet-50 weights from: {p}")
                MODEL = tf.keras.models.load_model(p, compile=False)
                # Build Grad-CAM sub-model
                base = MODEL.get_layer("resnet50")
                target_layer = base.get_layer("conv5_block3_out")
                base_sub = tf.keras.models.Model(inputs=base.inputs, outputs=[target_layer.output, base.output])
                
                inputs = tf.keras.Input(shape=(224, 224, 3))
                conv_out, base_out = base_sub(inputs)
                x = base_out
                for layer in MODEL.layers[1:]:
                    x = layer(x)
                GRAD_MODEL = tf.keras.models.Model(inputs=inputs, outputs=[conv_out, x])
                print("[Model] Model and Grad-CAM sub-model initialized successfully!")
                return
            except Exception as e:
                print(f"[Model] Error loading model from {p}: {e}")
    print("[Model] Warning: Model file not loaded, falling back to CV heuristic mode.")

init_model()

def compute_gradcam(img_tensor, pred_idx):
    if GRAD_MODEL is not None:
        try:
            with tf.GradientTape() as tape:
                convs, preds = GRAD_MODEL(img_tensor)
                tape.watch(convs)
                class_score = preds[:, pred_idx]
            grads = tape.gradient(class_score, convs)
            pooled = tf.reduce_mean(grads, axis=(0, 1, 2))
            cam = (convs[0] @ pooled[..., tf.newaxis]).numpy().squeeze()
            cam = np.maximum(cam, 0)
            cam /= (cam.max() + 1e-8)
            return cam.astype(np.float32)
        except Exception as e:
            print(f"[GradCAM] Error: {e}")

    # Fallback pseudo-GradCAM using laplacian + high-frequency energy
    orig = img_tensor[0].numpy()
    gray = cv2.cvtColor((orig * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    lap = np.abs(lap)
    lap = cv2.GaussianBlur(lap, (15, 15), 0)
    lap /= (lap.max() + 1e-8)
    return lap.astype(np.float32)

def generate_edge_map(img_rgb):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    mag = np.hypot(sobelx, sobely)
    mag = np.uint8(np.clip(mag / (mag.max() + 1e-5) * 255, 0, 255))
    
    # Overlay in industrial cyan/red
    edge_colored = np.zeros_like(img_rgb)
    edge_colored[mag > 35] = [224, 47, 47]  # Red defect edges
    edge_colored[mag > 80] = [255, 215, 0]  # Yellow high-intensity cracks
    
    blend = cv2.addWeighted(img_rgb, 0.65, edge_colored, 0.35, 0)
    return blend, float(np.mean(mag > 35) * 100)

def to_base64(img_rgb):
    buf = io.BytesIO()
    Image.fromarray(img_rgb).save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

@app.get("/")
def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>SteelGuard AI Frontend Initializing...</h1>")

@app.get("/api/samples")
def get_samples():
    samples_list = [
        {"id": "crazing", "name": "Crazing Cracks", "class": "crazing", "risk": "HIGH", "file": "crazing_sample.jpg"},
        {"id": "scratches", "name": "Linear Scratches", "class": "scratches", "risk": "HIGH", "file": "scratches_sample.jpg"},
        {"id": "rolled_in_scale", "name": "Rolled-in Scale", "class": "rolled-in_scale", "risk": "MEDIUM", "file": "rolled_in_scale_sample.jpg"},
        {"id": "pitted_surface", "name": "Pitted Surface", "class": "pitted_surface", "risk": "MEDIUM", "file": "pitted_surface_sample.jpg"},
        {"id": "patches", "name": "Surface Patches", "class": "patches", "risk": "LOW", "file": "patches_sample.jpg"},
        {"id": "inclusion", "name": "Slag Inclusion", "class": "inclusion", "risk": "LOW", "file": "inclusion_sample.jpg"},
    ]
    return JSONResponse(samples_list)

@app.get("/api/sample-image/{filename}")
def get_sample_image(filename: str):
    path = os.path.join(SAMPLES_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Sample image not found")

@app.post("/api/predict")
async def predict(
    file: UploadFile = File(None),
    sample_id: str = Form(None)
):
    start_time = time.time()
    img_bytes = None

    if file is not None and file.filename != "":
        img_bytes = await file.read()
    elif sample_id:
        sample_map = {
            "crazing": "crazing_sample.jpg",
            "scratches": "scratches_sample.jpg",
            "rolled_in_scale": "rolled_in_scale_sample.jpg",
            "rolled-in_scale": "rolled_in_scale_sample.jpg",
            "pitted_surface": "pitted_surface_sample.jpg",
            "patches": "patches_sample.jpg",
            "inclusion": "inclusion_sample.jpg",
        }
        filename = sample_map.get(sample_id, f"{sample_id}_sample.jpg")
        sample_path = os.path.join(SAMPLES_DIR, filename)
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                img_bytes = f.read()

    if img_bytes is None:
        raise HTTPException(status_code=400, detail="No image file or valid sample provided")

    # Decode image
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h_orig, w_orig = img_rgb.shape[:2]

    # Preprocess for model (224, 224, normalized 0..1)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_norm = img_resized.astype(np.float32) / 255.0
    img_tensor = np.expand_dims(img_norm, axis=0)

    # Model inference
    if MODEL is not None:
        raw_preds = MODEL.predict(img_tensor, verbose=0)[0]
        # Softmax normalize if needed
        exp_preds = np.exp(raw_preds - np.max(raw_preds))
        probs = exp_preds / np.sum(exp_preds)
    else:
        # Fallback heuristic
        gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
        var = cv2.Laplacian(gray, cv2.CV_64F).var()
        probs = np.zeros(6, dtype=np.float32)
        if var > 350: probs[5] = 0.88; probs[0] = 0.08
        elif var > 150: probs[0] = 0.84; probs[5] = 0.10
        else: probs[2] = 0.65; probs[1] = 0.25
        probs /= np.sum(probs)

    pred_idx = int(np.argmax(probs))
    pred_class = CLASS_NAMES[pred_idx]
    confidence = float(probs[pred_idx])

    # Compute Grad-CAM
    cam = compute_gradcam(tf.cast(img_tensor, tf.float32), pred_idx)
    cam_resized = cv2.resize(cam, (w_orig, h_orig))
    cam_uint8 = np.uint8(255 * cam_resized)
    heatmap_colored = cv2.applyColorMap(cam_uint8, cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    # Blended Grad-CAM overlay
    gradcam_overlay = cv2.addWeighted(img_rgb, 0.55, heatmap_rgb, 0.45, 0)

    # Edge Focus Map
    edge_map, defect_area_pct = generate_edge_map(img_rgb)

    meta = CLASS_METADATA.get(pred_class, {
        "display": pred_class.title(),
        "risk": "MEDIUM",
        "color": "#d97706",
        "score": 50,
        "description": "Surface anomaly detected.",
        "cause": "Mechanical or thermal stress",
        "action": "Visual inspection required.",
    })

    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    prob_distribution = [
        {
            "class": c,
            "display": CLASS_METADATA[c]["display"],
            "prob": round(float(probs[i]) * 100, 2),
            "risk": CLASS_METADATA[c]["risk"],
            "color": CLASS_METADATA[c]["color"],
        }
        for i, c in enumerate(CLASS_NAMES)
    ]
    prob_distribution.sort(key=lambda x: x["prob"], reverse=True)

    return JSONResponse({
        "status": "success",
        "latency_ms": elapsed_ms,
        "prediction": {
            "class": pred_class,
            "display": meta["display"],
            "confidence": round(confidence * 100, 2),
            "risk_level": meta["risk"],
            "risk_score": meta["score"],
            "risk_color": meta["color"],
            "description": meta["description"],
            "root_cause": meta["cause"],
            "action": meta["action"],
            "defect_area_pct": round(defect_area_pct, 1),
        },
        "probabilities": prob_distribution,
        "images": {
            "original": to_base64(img_rgb),
            "gradcam": to_base64(gradcam_overlay),
            "heatmap_raw": to_base64(heatmap_rgb),
            "edge_map": to_base64(edge_map),
        }
    })

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    print("[Server] Starting SteelGuard AI server on http://localhost:8000 ...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
