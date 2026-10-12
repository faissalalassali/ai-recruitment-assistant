import os
from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
        return ""

def process_all_cvs():
    input_dir = 'downloaded_cvs'
    if not os.path.exists(input_dir):
        print(f"Directory '{input_dir}' does not exist. Download CVs first.")
        return

    files = os.listdir(input_dir)
    if not files:
        print("No CV files found in the directory.")
        return

    print(f"Found {len(files)} file(s) to process.\n")

    for filename in files:
        file_path = os.path.join(input_dir, filename)
        text = ""

        if filename.endswith('.pdf'):
            print(f"Extracting text from PDF: {filename}")
            text = extract_text_from_pdf(file_path)
        elif filename.endswith('.docx'):
            print(f"Extracting text from DOCX: {filename}")
            text = extract_text_from_docx(file_path)
        else:
            continue

        cleaned_text = " ".join(text.split())
        
        print(f"-> Extracted {len(cleaned_text)} characters successfully.")
        print(f"-> Preview: {cleaned_text[:150]}...\n" + "="*50)

if __name__ == '__main__':
    process_all_cvs()