from pathlib import Path
import json
from helpers.ocr_extract_helpers import extract_document_intelligence_payload
from helpers.foundry_restructure_helpers import map_ocr_payload_to_sharepoint_rows
try:
    from __main__ import mcp
except ImportError:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("PowerBI Server")

"""
List of Tools: 
1. Extract OCR from PDF and return JSON
2. Get ticket number or return null
3. Get material type or return null
4. Get time-in/time-out or return null
5. Upload to sharepoint site
"""

print("Loading test_tools.py...")

@mcp.tool()
def extract_and_map_ticket_pdf(pdf_path: str) -> str:
    """
    Extracts OCR data from a truck ticket PDF using Azure Document Intelligence,
    then maps the OCR output into SharePoint-ready ticket rows using Azure AI Foundry.
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    ocr_payload_json = extract_document_intelligence_payload(str(path))

    ocr_payload = json.loads(ocr_payload_json)

    sharepoint_rows = map_ocr_payload_to_sharepoint_rows(
        ocr_payload=ocr_payload,
        attachment_name=path.name,
    )

    # MCP tools should usually return strings, so return formatted JSON
    return json.dumps(
        sharepoint_rows,
        indent=2,
        ensure_ascii=False
    )


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
    Searches a PDF of a ticket to locate the time-in.

    """

    return

@mcp.tool()
def get_time_out(contents: str) -> str:
    """
    Searches a PDF of a ticket to locate the time-out.

    """

    return

@mcp.tool()
def upload_sharepoint(pdf_path: str, sharepoint_url: str):
    """
    Uploads a PDF of a ticket to a Sharepoint test.

    """

    return

