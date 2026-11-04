from fastapi import FastAPI

from app.api.routes.analyses import router as analyses_router

app = FastAPI(
    title="AI Business Intelligence Platform",
    description="Analyze structured business data and generate actionable recommendations.",
    version="0.1.0",
)

app.include_router(analyses_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
