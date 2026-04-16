from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import AnalyzeRequest, AnalyzeResponse
from app.analyzer import analyze
from app.parser import parse_file, ParseError
from app.normalizer import normalize_billing_data

app = FastAPI(
    title="ThriftCloud API",
    description="Multi-cloud cost intelligence platform for AWS and Azure",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ThriftCloud API is running", "version": "1.0.0"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_billing(request: AnalyzeRequest):
    """
    Analyze billing data for a cloud provider.

    If billing_data is omitted, built-in sample data is used.
    Returns total cost, savings potential, efficiency score,
    recommendations, and per-service breakdown.
    """
    try:
        result = analyze(request.provider, request.billing_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return AnalyzeResponse(**result)


@app.post("/api/analyze/upload", response_model=AnalyzeResponse)
async def analyze_upload(
    provider: str = Form(..., description="Cloud provider: 'aws' or 'azure'"),
    file: UploadFile = File(..., description="Billing file (.csv, .txt, or .json)"),
):
    """
    Analyze an uploaded billing file.

    Accepts multipart/form-data with provider string and billing file.
    Supported formats: CSV, TXT (with service,cost headers), JSON.
    """
    contents = await file.read()

    try:
        billing_data = parse_file(contents, file.filename or "")
    except ParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Normalize uploaded service names to canonical forms
    billing_data = normalize_billing_data(billing_data, provider)

    try:
        result = analyze(provider, billing_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result["input_source"] = "uploaded_file"
    result["uploaded_file_name"] = file.filename

    return AnalyzeResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
