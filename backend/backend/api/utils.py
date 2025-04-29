import fitz  # PyMuPDF
import docx
import re

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def parse_resume(file_path):
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return None

    # Extract name, email, phone (basic NLP)
    name_match = re.search(r"([A-Z][a-z]+\s[A-Z][a-z]+)", text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_match = re.search(r"\+?\d{10,15}", text)

    return {
        "name": name_match.group(0) if name_match else "Unknown",
        "email": email_match.group(0) if email_match else "Unknown",
        "phone": phone_match.group(0) if phone_match else "Unknown",
        "raw_text": text,
    }
