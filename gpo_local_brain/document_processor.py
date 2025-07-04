import os
from docx import Document
from PyPDF2 import PdfReader

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read(), None
        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs]), None
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages), None
        else:
            return None, f"Unsupported file type: {ext}"
    except Exception as e:
        return None, f"Error extracting text: {e}" 