import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, generations, projects, assets, billing, usage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Database Tables
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")

    # 2. Check and ensure AI model baseline readiness
    checkpoint_file = (
        settings.CHECKPOINTS_DIR / "sargam_lstm_v1.pt"
        if (settings.CHECKPOINTS_DIR / "sargam_lstm_v1.pt").exists()
        else settings.CHECKPOINTS_DIR / "melodia_lstm_v1.pt"
    )
    vocab_file = settings.CHECKPOINTS_DIR / "vocab.json"
    if not (checkpoint_file.exists() and vocab_file.exists()):
        print("Model checkpoint missing. Running baseline dataset generation and training...")
        try:
            from ai.data.dataset_generator import generate_sample_compositions
            from ai.preprocessing.parse_dataset import preprocess_dataset
            from ai.training.train import train_model

            generate_sample_compositions()
            preprocess_dataset()
            train_model(epochs=30)
            print("Baseline LSTM model successfully trained and ready for inference!")
        except Exception as e:
            print(f"Notice: Initial training hook encountered: {e}")

    yield

app = FastAPI(
    title="Sargam AI API",
    description="Industry-Ready AI Music Generation SaaS Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(generations.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(assets.router, prefix=settings.API_V1_STR)
app.include_router(billing.router, prefix=settings.API_V1_STR)
app.include_router(usage.router, prefix=settings.API_V1_STR)

# Mount storage directory for direct static streaming if needed
app.mount("/storage", StaticFiles(directory=str(settings.STORAGE_DIR)), name="storage")

@app.get("/")
def root():
    return {
        "service": "Sargam AI API",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
