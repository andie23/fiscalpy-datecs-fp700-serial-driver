import re
import pdfplumber
import config
import receipt

def pdf_to_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        max_pdf_pages = config.get_config(config.K_MAX_PDF_PAGES)
        if len(pdf.pages) > max_pdf_pages:
            raise Exception(f"PDF pages exceeds maximum limit {max_pdf_pages}")
        for page in pdf.pages:
            # Extract text from each page
            page_text = page.extract_text()
            # Concatenate text from all pages
            text += page_text + "\n"
    return text

def get_line_index_score(indexes, text_line):
    for index in indexes:
        pattern = re.compile(re.escape(index), re.IGNORECASE)
        if pattern.search(text_line):
            return indexes[index]
    return 0

def is_receipt_doc_type(text):
    indexes = config.get_config(config.K_DOC_IDENTIFICATION_INDEX)
    receipt_score = 0

    for line in text.split('\n'):
        receipt_score += get_line_index_score(
            indexes[config.K_RECEIPT], line
        )
        if receipt_score >= config.MIN_DOC_IDENTIFICATION_SCORE:
            return True
    return False

if __name__ == "__main__":
    txt = pdf_to_text("c:\mra\\invoice.pdf")
    print(receipt.parse(txt))