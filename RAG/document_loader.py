from pathlib import Path
from pypdf import PdfReader


DOCUMENTS_DIR = Path("documents")


def load_pdf(file_path):
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":

    pdf_path = DOCUMENTS_DIR / "Leave_and_Time-Off_Policy.pdf"

    text = load_pdf(pdf_path)

    print("Extracted text:")
    print(text[:3000])