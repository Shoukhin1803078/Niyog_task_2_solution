from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import PyPDF2  
from typing import Optional
from openai import OpenAI
import logging
import time
from pathlib import Path
import shutil
import asyncio
from functools import lru_cache
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF Q&A API",
    description="API to extract text from PDFs and answer questions using LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Settings:
    UPLOAD_DIR: str = "uploads"
    MAX_PDF_SIZE_MB: int = 10
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 200
    
  
    PDF_FILE_PATH: str = "uploads/current.pdf"
    
    def __init__(self):
        
        Path(self.UPLOAD_DIR).mkdir(exist_ok=True)
        
        if not self.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not found in environment variables. Make sure you have a .env file with OPENAI_API_KEY=your-key")
        
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)

@lru_cache()
def get_settings():
    return Settings()

pdf_text = ""
pdf_processed = False

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str

class PDFUploadResponse(BaseModel):
    message: str

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyPDF2"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() or "" 
                
        if not text.strip():
            logger.warning(f"No text extracted from PDF: {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list:
    """Split text into chunks for processing by the LLM"""
    if not text:
        return []
        
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk:
            chunks.append(chunk)
    return chunks

async def get_answer_from_llm(question: str, context: str, settings: Settings) -> str:
    """Get answer from OpenAI API using the latest client structure"""
    try:
        
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not found. Please check your .env file.")
            
        def call_openai():
            response = settings.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided PDF content. Only use the information from the PDF to answer questions. If the answer cannot be found in the PDF, say so clearly."},
                    {"role": "user", "content": f"Based on the following PDF content, please answer this question: {question}\n\nPDF CONTENT:\n{context}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response
        
        response = await asyncio.to_thread(call_openai)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error getting answer from LLM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting answer from LLM: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup"""
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        logger.warning("WARNING: OPENAI_API_KEY not set in .env file. The API will not be able to answer questions.")
    logger.info("Started PDF Q&A API")

@app.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """Upload and process a PDF file"""
    global pdf_text, pdf_processed
    
    pdf_text = ""
    pdf_processed = False
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
       
        file.file.seek(0, 2)  
        file_size = file.file.tell()
        file.file.seek(0) 
        
        if file_size > settings.MAX_PDF_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds maximum allowed size ({settings.MAX_PDF_SIZE_MB}MB)"
            )
        
        with open(settings.PDF_FILE_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving PDF: {str(e)}")
    
    background_tasks.add_task(process_pdf, settings)
    
    return PDFUploadResponse(
        message="PDF successfully uploaded and processing started"
    )

async def process_pdf(settings: Settings):
    """Process PDF and store extracted text in global variable"""
    global pdf_text, pdf_processed
    
    try:
        # Extract text from PDF
        start_time = time.time()
        pdf_text = extract_text_from_pdf(settings.PDF_FILE_PATH)
        pdf_processed = True
        
        processing_time = time.time() - start_time
        logger.info(f"PDF processed in {processing_time:.2f} seconds. Text length: {len(pdf_text)}")
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        pdf_processed = False

@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    settings: Settings = Depends(get_settings)
):
    """Answer a question based on PDF content"""
    global pdf_text, pdf_processed
    
    if not pdf_processed:
        raise HTTPException(status_code=400, detail="No PDF has been uploaded or processing is not complete. Please upload a PDF first.")
    
    if not pdf_text.strip():
        return QuestionResponse(answer="The PDF appears to be empty or contains no extractable text. Please upload a text-based PDF.")
    
    if len(pdf_text) > settings.CHUNK_SIZE:
        chunks = chunk_text(pdf_text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        logger.info(f"Split PDF into {len(chunks)} chunks for processing")
        
        context = chunks[0]
        
    else:
        context = pdf_text
    
    
    answer = await get_answer_from_llm(request.question, context, settings)
    
    return QuestionResponse(answer=answer)



@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(e)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)