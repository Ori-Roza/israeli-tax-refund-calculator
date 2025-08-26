import fitz
from PIL import Image as PILImage
from pytesseract import pytesseract

from tax_authority_api.const import TAX_CODES_GROUPS
from tax_authority_api.schemes import Report106Codes
from tax_documents_parser.utils import extract_values_from_text



def pdf_to_images(path: str, dpi: int = 200):
    doc = fitz.open(path)
    scale = dpi / 72.0
    mat = fitz.Matrix(scale, scale)
    out = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)  # RGB, no alpha
        mode = "RGBA" if pix.alpha else "RGB"
        # Use the module-level function via alias to avoid shadowing
        img = PILImage.frombytes(mode, (pix.width, pix.height), pix.samples)
        out.append(img)
    doc.close()
    return out

def parse_106_pdf(pdf_path: str) -> Report106Codes:
    images = pdf_to_images(pdf_path)
    full_text = ""

    for image in images:
        text = pytesseract.image_to_string(image, lang='eng')  # or 'heb+eng' if desired
        full_text += text + "\n"

    return extract_values_from_text(full_text, TAX_CODES_GROUPS)
