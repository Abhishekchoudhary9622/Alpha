"""
AlphaLens Main Application Server
FastAPI server serving financial API endpoints, authentication, user custom portfolios,
and the institutional fintech frontend.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api.routes import router as api_router
from backend.api.auth_routes import auth_router

app = FastAPI(
    title="AlphaLens — Market Intelligence Platform",
    description="Explainable Multimodal Probabilistic Machine Learning System for Financial Markets",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

# Mount Static frontend assets
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_index():
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"message": "AlphaLens API Core is running. Frontend initializing..."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AlphaLens Intelligence Core"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
