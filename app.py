import os
import tempfile
import logging
import time
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our existing modules
from pdf_to_markdown import MarkdownConverter, pdf_to_markdown_text
from md_to_json import get_therapy_json, get_radiation_json, get_mistral_client
from therapy_models import TherapyReport
from rad_models import RadiationTherapyReport

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical Report Processing API (Therapy and Radiation)",
    description="Convert therapy and radiation PDF reports to structured JSON data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class TherapyResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    processing_time: Optional[float] = None

class RadiationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    mistral_api_configured: bool

# Global converter instance
_converter = None

def get_converter():
    """Get or create a global MarkdownConverter instance."""
    global _converter
    if _converter is None:
        api_key = os.environ.get('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set.")
        _converter = MarkdownConverter(api_key=api_key)
    return _converter

async def cleanup_temp_file(file_path: str):
    """Background task to cleanup temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup temporary file {file_path}: {e}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check if Mistral API is configured
        mistral_configured = bool(os.environ.get('MISTRAL_API_KEY'))
        
        # Try to initialize clients to verify configuration
        if mistral_configured:
            get_mistral_client()  # This will raise an error if API key is invalid
            get_converter()
        
        return HealthResponse(
            status="healthy",
            mistral_api_configured=mistral_configured
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

@app.post("/therapies", response_model=TherapyResponse)
async def process_therapy_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF therapy report to process")
):
    """
    Process a therapy PDF report and extract structured data.
    
    This endpoint:
    1. Accepts a PDF file upload
    2. Converts PDF to markdown using Mistral OCR
    3. Extracts structured therapy data using AI
    4. Returns structured JSON data
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        logger.info(f"Processing therapy report: {file.filename} ({len(content)} bytes)")
        
        # Step 1: Convert PDF to Markdown
        logger.info("Converting PDF to markdown...")
        converter = get_converter()
        markdown_text = pdf_to_markdown_text(temp_file_path, converter, with_images=False)
        
        if not markdown_text.strip():
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
        
        # Step 2: Extract structured therapy data
        logger.info("Extracting structured therapy data...")
        structured_data = get_therapy_json(markdown_text)
        
        if not structured_data:
            raise HTTPException(status_code=400, detail="Failed to extract structured data from document")
        
        # Validate against Pydantic model
        try:
            therapy_report = TherapyReport(**structured_data)
            validated_data = therapy_report.model_dump()
        except Exception as validation_error:
            logger.warning(f"Data validation warning: {validation_error}")
            # Return unvalidated data with warning
            validated_data = structured_data
        
        processing_time = time.time() - start_time
        logger.info(f"Successfully processed {file.filename} in {processing_time:.2f} seconds")
        
        # Schedule cleanup of temporary file
        background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        return TherapyResponse(
            success=True,
            message=f"Successfully processed therapy report: {file.filename}",
            data=validated_data,
            processing_time=processing_time
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing therapy report {file.filename}: {e}")
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/radiation", response_model=RadiationResponse)
async def process_radiation_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF radiation therapy report to process")
):
    """
    Process a radiation therapy PDF report and extract structured data.
    
    This endpoint:
    1. Accepts a PDF file upload
    2. Converts PDF to markdown using Mistral OCR
    3. Extracts structured radiation therapy data using AI
    4. Returns structured JSON data
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        logger.info(f"Processing radiation therapy report: {file.filename} ({len(content)} bytes)")
        
        # Step 1: Convert PDF to Markdown
        logger.info("Converting PDF to markdown...")
        converter = get_converter()
        markdown_text = pdf_to_markdown_text(temp_file_path, converter, with_images=False)
        
        if not markdown_text.strip():
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
        
        # Step 2: Extract structured radiation therapy data
        logger.info("Extracting structured radiation therapy data...")
        structured_data = get_radiation_json(markdown_text)
        
        if not structured_data:
            raise HTTPException(status_code=400, detail="Failed to extract structured data from document")
        
        # Validate against Pydantic model
        try:
            radiation_report = RadiationTherapyReport(**structured_data)
            validated_data = radiation_report.model_dump()
        except Exception as validation_error:
            logger.warning(f"Data validation warning: {validation_error}")
            # Return unvalidated data with warning
            validated_data = structured_data
        
        processing_time = time.time() - start_time
        logger.info(f"Successfully processed {file.filename} in {processing_time:.2f} seconds")
        
        # Schedule cleanup of temporary file
        background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        return RadiationResponse(
            success=True,
            message=f"Successfully processed radiation therapy report: {file.filename}",
            data=validated_data,
            processing_time=processing_time
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing radiation therapy report {file.filename}: {e}")
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Medical Report Processing API",
        "version": "1.0.0",
        "description": "Process therapy and radiation PDF reports and extract structured data",
        "endpoints": {
            "health": "GET /health - Check API health status",
            "therapies": "POST /therapies - Process therapy PDF report (chemotherapy, biological, etc.)",
            "radiation": "POST /radiation - Process radiation therapy PDF report"
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check if API key is configured
    if not os.environ.get('MISTRAL_API_KEY'):
        logger.error("MISTRAL_API_KEY environment variable not set!")
        exit(1)
    
    logger.info("Starting Medical Report Processing API...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 