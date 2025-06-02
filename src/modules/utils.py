import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file.

    Parameters:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    raw_text = ""
    if file_path.endswith('.pdf'):
        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                raw_text = raw_text + text
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")
    return raw_text