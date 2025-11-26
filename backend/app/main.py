from fastapi import FastAPI
from app.api.router import router as api_router
from app.models.utils import HealthResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="bondo backend",
    version="0.1.0",
    description="Backend API for bondo (scikit-learn mentor).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok")

app.include_router(api_router)
