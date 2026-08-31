"""
PassStrength AI – Main Application Entry Point.

A production-quality, AI-powered password strength checker
combining Machine Learning, Information Theory, and Pattern Analysis.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Pre-load ML model on startup for faster first request."""
    try:
        from app.ml.predictor import PasswordPredictor
        predictor = PasswordPredictor()
        if predictor.model is not None:
            print("[OK] ML model loaded successfully on startup.")
        else:
            print("[WARN] ML model not found. Using rule-based fallback. "
                  "Run 'python -m app.ml.train_model' to train.")
    except Exception as e:
        print(f"[WARN] Could not pre-load ML model: {e}")
    yield


app = FastAPI(
    title="PassStrength AI",
    description="AI-powered password strength checker with Machine Learning, "
                "entropy analysis, pattern detection, and crack-time estimation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page."""
    template_path = os.path.join(
        os.path.dirname(__file__), "app", "templates", "index.html"
    )
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "<h1>PassStrength AI API is running</h1>"
            "<p>Frontend template not found. Visit <a href='/docs'>/docs</a> for API docs.</p>"
        )

