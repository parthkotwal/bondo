from fastapi import FastAPI
from app.api.router import router as api_router
from app.models.utils import HealthResponse

app = FastAPI(
    title="bondo backend",
    version="0.1.0",
    description="Backend API for bondo (scikit-learn mentor).",
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok")

app.include_router(api_router)
