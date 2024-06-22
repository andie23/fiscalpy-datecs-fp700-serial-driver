import re
import pdfplumber
import config

def pdf_to_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        max_pdf_pages = config.get_config("maximum_pdf_pages")
        if len(pdf.pages) > max_pdf_pages:
            raise Exception(f"PDF pages exceeds maximum limit {max_pdf_pages}")
        for page in pdf.pages:
            # Extract text from each page
            page_text = page.extract_text()
            # Concatenate text from all pages
            text += page_text + "\n"
    return text

def get_pdf_feature_score(features, text_line):
    for index in features:
        pattern = re.compile(re.escape(index), re.IGNORECASE)
        if pattern.search(text_line):
            return features[index]
    return 0

def detect_doc_type(text):
    features = config.get_config("feature_detection")
    receipt_score = 0
    invoice_score = 0
    org_score = 0

    for line in text.split('\n'):
        org_score += get_pdf_feature_score(
            features["org"], line
        )
        receipt_score += get_pdf_feature_score(
            features["receipt"], line
        )
        invoice_score += get_pdf_feature_score(
            features["invoice"], line
        )

    if org_score < len(features["org"]):
        return None

    if receipt_score > invoice_score:
        return "receipt"  
    
    if invoice_score > receipt_score:
        return "invoice"

    return None

if __name__ == "__main__":
    txt = pdf_to_text("C:\MRA\/another.pdf")
    print(detect_doc_type(txt))