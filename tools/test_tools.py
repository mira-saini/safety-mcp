from pathlib import Path
import sys
import io
import pytesseract
import fitz  # PyMuPDF
import pytesseract
from PIL import Image


try:
    from __main__ import mcp
except ImportError:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("PowerBI Server")

"""
List of Tools: 
1. Get ticket number or return null
2. Get material type or return null
3. Get time-in/time-out or return null
4. Upload to sharepoint site
"""

print("Loading test_tools.py...")

@mcp.tool()
def extract_ocr(pdf_path: str) -> str:
    """
    Extracts text from a PDF and returns it as a string.
    Uses direct PDF text extraction first, then falls back to OCR using PyMuPDF + Tesseract.
    Does NOT require Poppler.
    """

    print(f"Processing PDF: {pdf_path}", file=sys.stderr)

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image

    doc = fitz.open(str(path))
    ocr_text = []

    zoom = 4  # Increase for better OCR quality
    matrix = fitz.Matrix(zoom, zoom)

    for page_number in range(len(doc)):
        print(f"OCR page {page_number + 1}/{len(doc)}", file=sys.stderr)

        page = doc[page_number]

        pix = page.get_pixmap(matrix=matrix, alpha=False)

        image_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("L")

        text = pytesseract.image_to_string(image,config="--oem 3 --psm 4").strip()

        if text:
            ocr_text.append(text)

    doc.close()

    if ocr_text:
        print("OCR extraction succeeded.", file=sys.stderr)
        return "\n\n".join(ocr_text)

    return ""


@mcp.tool()
def get_ticket_number(contents: str) -> str:
    """
    Searches a PDF of a ticket to locate the ticket number.

    """

    return

@mcp.tool()
def get_material_type(contents: str) -> str:
    """
    Searches a PDF of a ticket to locate the material type.

    """

    return

@mcp.tool()
def get_time_in(contents: str) -> str:
    """
    Searches a PDF of a ticket to locate the time-out.

    """

    return

@mcp.tool()
def get_time_out(contents: str) -> str:
    """
    Searches a PDF of a ticket to locate the time-in.

    """

    return

@mcp.tool()
def upload_sharepoint(pdf_path: str, sharepoint_url: str):
    """
    Uploads a PDF of a ticket to a Sharepoint test.

    """

    return

