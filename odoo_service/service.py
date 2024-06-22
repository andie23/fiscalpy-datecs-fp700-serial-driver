import re
import pdfplumber
import config

MIN_FEATURE_PASS_MARK = 5

def pdf_to_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text from each page
            page_text = page.extract_text()
            # Concatenate text from all pages
            text += page_text + "\n"
    return text

def resolve_feature_score(features, text_line):
    for index in features:
        pattern = re.compile(re.escape(index), re.IGNORECASE)
        if pattern.search(text_line):
            return features[index]
    return 0

def detect_doc_type(text):
    org_score = 0
    receipt_score = 0
    invoice_score = 0
    features = config.get_config("features")

    for line in text.split('\n'):
        org_score += resolve_feature_score(
            features["org"], line
        )
        receipt_score += resolve_feature_score(
            features["receipt"], line
        )
        invoice_score += resolve_feature_score(
            features["invoice"], line
        )
    if org_score < len(features["org"]):
        return None

    if receipt_score >= invoice_score:
        return "receipt"  
    
    if invoice_score >= receipt_score:
        return "invoice"

    if receipt_score == invoice_score:
        return "receipt"
    return None

if __name__ == "__main__":
    txt = pdf_to_text("C:\MRA\/another.pdf")
    print(detect_doc_type(txt))