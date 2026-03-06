from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Quirrely API v2.0", "status": "running"}

@app.post("/analyze")
def analyze_text(data: dict):
    # Mock analysis for Vercel testing
    text = data.get("text", "")
    
    # Simple mock response
    return {
        "profile": {
            "primary": "assertive",
            "secondary": "open"
        },
        "confidence": 0.85,
        "word_count": len(text.split()),
        "suggestions": [
            "Your writing shows strong assertive patterns",
            "Consider varying your sentence structure"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0"}

# For Vercel deployment
from mangum import Mangum
handler = Mangum(app)