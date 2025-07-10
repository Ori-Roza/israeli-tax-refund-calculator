from pdf2image import convert_from_path
from pytesseract import pytesseract

from tax_authority_api.const import TAX_CODES_GROUPS
from tax_documents_parser.utils import extract_values_from_text


def parse_106_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    full_text = ""

    for image in images:
        text = pytesseract.image_to_string(image, lang='eng')  # or 'heb+eng' if desired
        full_text += text + "\n"

    return extract_values_from_text(full_text, TAX_CODES_GROUPS)
