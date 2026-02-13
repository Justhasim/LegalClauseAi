import os
import PyPDF2
from docx import Document
from PIL import Image
import pytesseract
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def read_pdf(file):
    """Extract text from a PDF file."""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_docx(file):
    """Extract text from a DOCX file."""
    try:
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def read_image(file):
    """
    Perform local OCR on an image file using Pytesseract (Free & Open Source).
    Works best for English documents.
    Note: Requires Tesseract-OCR installed on the system.
    """
    try:
        # Common Windows path for Tesseract
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        image = Image.open(file)
        # Simple extraction for English
        text = pytesseract.image_to_string(image, lang='eng')
        
        if not text.strip():
            return "Notice: No text could be detected in this image. Please ensure the document is in English and clear."
            
        return text
    except Exception as e:
        error_msg = str(e)
        if "tesseract is not installed" in error_msg.lower() or "system cannot find the file" in error_msg.lower():
            return "Error: Tesseract OCR is not found. To use image upload for free:\n1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki\n2. Install it to the default path."
        return f"Error reading image: {error_msg}"

def read_file(file):
    """
    Auto-detect file type and read content.
    Supports: PDF, DOCX, Images
    """
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        return read_pdf(file)
    elif filename.endswith('.docx'):
        return read_docx(file)
    elif filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        return read_image(file)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or Image file.")
        