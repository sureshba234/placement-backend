from pypdf import PdfReader
from docx import Document
import io


def extract_text_from_resume(file_field):
    """
    Extracts raw text from an uploaded resume file (PDF or DOCX).
    """
    filename = file_field.name.lower()
    file_field.seek(0)
    content = file_field.read()

    if filename.endswith('.pdf'):
        reader = PdfReader(io.BytesIO(content))
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        return text

    elif filename.endswith('.docx'):
        doc = Document(io.BytesIO(content))
        text = '\n'.join(para.text for para in doc.paragraphs)
        return text

    else:
        raise ValueError(f"Unsupported resume file type: {filename}")
