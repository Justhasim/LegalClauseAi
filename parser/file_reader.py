import PyPDF2
from docx import Document
from PIL import Image
import pytesseract

def read_pdf(file):
    """Extract text from a PDF file."""
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_docx(file):
    """Extract text from a DOCX file."""
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def read_image(file):
    """Perform OCR on an image file to extract text."""
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

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
        raise ValueError("Unsupported file type")
