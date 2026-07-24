from pathlib import Path
import os
import sys
import json
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def get_foundry_client() -> OpenAI:
    """
    Creates an Azure AI Foundry OpenAI-compatible client.

    Expected endpoint format:
        https://<project-or-resource>.services.ai.azure.com/openai/v1
    """

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint or not api_key:
        raise RuntimeError(
            "Missing Azure OpenAI / Foundry credentials. "
            "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY."
        )

    return OpenAI(
        base_url=endpoint.rstrip("/"),
        api_key=api_key
    )


def get_foundry_deployment_name() -> str:
    """
    Gets the Azure AI Foundry deployment name.

    This must be the exact deployment name from Foundry, not necessarily the model name.
    """

    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    if not deployment_name:
        raise RuntimeError(
            "Missing AZURE_OPENAI_DEPLOYMENT_NAME."
        )

    return deployment_name


def get_sharepoint_ticket_schema() -> Dict[str, Any]:
    """
    JSON schema for SharePoint-ready truck ticket rows.
    """

    return {
        "type": "json_schema",
        "json_schema": {
            "name": "sharepoint_truck_ticket_rows",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "tickets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "ticket_number": {
                                    "type": ["string", "null"]
                                },
                                "page": {
                                    "type": ["string", "null"]
                                },
                                "attachment_name": {
                                    "type": ["string", "null"]
                                },
                                "job_number": {
                                    "type": ["string", "null"]
                                },
                                "material": {
                                    "type": ["string", "null"]
                                },
                                "quantity": {
                                    "type": ["string", "null"]
                                },
                                "unit": {
                                    "type": ["string", "null"]
                                },
                                "date": {
                                    "type": ["string", "null"]
                                },
                                "start_time": {
                                    "type": ["string", "null"]
                                },
                                "end_time": {
                                    "type": ["string", "null"]
                                },
                                "company": {
                                    "type": ["string", "null"]
                                },
                                "truck_number": {
                                    "type": ["string", "null"]
                                },
                                "rate": {
                                    "type": ["string", "null"]
                                },
                                "amount_due": {
                                    "type": ["string", "null"]
                                },
                                "attachment": {
                                    "type": ["string", "null"]
                                }
                            },
                            "required": [
                                "ticket_number",
                                "page",
                                "attachment_name",
                                "job_number",
                                "material",
                                "quantity",
                                "unit",
                                "date",
                                "start_time",
                                "end_time",
                                "company",
                                "truck_number",
                                "rate",
                                "amount_due",
                                "attachment"
                            ]
                        }
                    }
                },
                "required": ["tickets"]
            }
        }
    }


def build_foundry_mapping_prompt() -> str:
    """
    System prompt for mapping compact OCR/table output into SharePoint rows.
    """

    return """
You are a data extraction mapper for trucking invoices, truck tickets, delivery tickets, and hauling tickets.

You receive compact Azure Document Intelligence output from the prebuilt-invoice model.

The input usually contains:
- invoice_fields
- pages
- page-level tables
- table rows represented as pipe-delimited strings

Your job is to convert the extracted evidence into SharePoint-ready ticket rows.

Target SharePoint columns:
- ticket_number
- page
- attachment_name
- job_number
- material
- quantity
- unit
- date
- start_time
- end_time
- company
- truck_number
- rate
- amount_due
- attachment

Mapping rules:
1. ticket_number may appear as Ticket Number, Ticket #, Ticket#, Tag Number, Tag No., TAG NO., Delivery Ticket No., ProductCode, load tag, or similar.
2. job_number may appear as Job Number, Job #, Project Number, P.O. #, PO Number, Purchase Order, or similar.
3. material may appear as Material, Material Loaded, Commodity, Description, Product, Service, Work Type, Super Dump, DIRT, HMA, REC-AB, Rip Rap, Base Rock, Asphalt, etc.
4. quantity may appear as Quantity, Qty, Hours, Hrs, Tons Loaded, Weight, Units, Total Tons, Net Chargeable Time, loads, or tonnage.
5. unit should be inferred when obvious:
   - Hours, Hrs, or hourly work means "hours".
   - Tons Loaded, Weight, Total Tons, or tonnage means "tons".
   - Loads means "loads".
   - If unknown, use null.
6. date may appear in invoice fields, invoice line items, ticket tables, or page-level ticket headers.
7. start_time may appear as Start Time, Time In, Arrived, ARRIVED under LOADING, Loading Arrived, or similar.
8. end_time may appear as End Time, Time Out, Depart, DEPART under UNLOADING, Unloading Depart, or similar.
9. company should usually be the vendor or ticket company issuing the invoice or ticket.
10. truck_number may appear as Truck Number, Truck No., Truck NO., Tractor, Tractor Number, Vehicle Number, or similar.
11. rate may appear as Rate, UnitPrice, Unit Price, Hourly Rate, HRLY, or similar.
12. amount_due may appear as Amount, Amount Due, Line Amount, Invoice Total, Total, Total Charges, or similar.
13. attachment_name should be the source file name if available.
14. attachment should be null unless a URL or attachment path is explicitly provided.
15. If one table row represents one ticket, return one output row for that row.
16. If multiple rows share the same ticket number but represent different materials, loads, dates, times, quantities, or charges, return separate rows.
17. Preserve extracted values exactly when possible.
18. Do not invent missing values. Use null for missing values.
19. Prefer table rows over invoice summary fields when table rows clearly represent individual tickets.
20. Return only the structured JSON object matching the schema.
"""


def load_ocr_payload_from_file(json_path: str | Path) -> Dict[str, Any]:
    """
    Loads a saved OCR extraction JSON file.
    """

    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(
            f"OCR extraction JSON file not found: {json_path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_user_payload(
    ocr_payload: Dict[str, Any],
    attachment_name: str | None = None,
) -> str:
    """
    Adds attachment context to the OCR payload before sending to Foundry.
    """

    payload = {
        "attachment_name": attachment_name,
        "ocr_extraction": ocr_payload
    }

    return json.dumps(
        payload,
        ensure_ascii=False
    )


def map_ocr_payload_to_sharepoint_rows(
    ocr_payload: Dict[str, Any],
    attachment_name: str | None = None,
) -> Dict[str, Any]:
    """
    Maps compact OCR extraction output into SharePoint-ready rows.
    """

    client = get_foundry_client()
    deployment_name = get_foundry_deployment_name()

    print(
        f"Calling Foundry deployment: {deployment_name}",
        file=sys.stderr
    )

    user_payload = build_user_payload(
        ocr_payload=ocr_payload,
        attachment_name=attachment_name,
    )

    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                "content": build_foundry_mapping_prompt()
            },
            {
                "role": "user",
                "content": user_payload
            }
        ],
        response_format=get_sharepoint_ticket_schema()
    )

    content = completion.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Foundry model returned an empty response."
        )

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Foundry model returned invalid JSON: {content}"
        ) from exc


def restructure_ocr_file_to_sharepoint_rows(
    ocr_json_path: str | Path,
    attachment: str | None = None
) -> Dict[str, Any]:
    """
    Testing helper:
    Loads an existing OCR extraction JSON file and sends it to Foundry.

    This avoids rerunning Document Intelligence while testing the prompt/model.
    """

    ocr_json_path = Path(ocr_json_path)

    ocr_payload = load_ocr_payload_from_file(
        ocr_json_path
    )

    attachment_name = ocr_payload.get("source_file")

    if attachment_name:
        attachment_name = Path(attachment_name).name
    else:
        attachment_name = ocr_json_path.name

    return map_ocr_payload_to_sharepoint_rows(
        ocr_payload=ocr_payload,
        attachment_name=attachment_name,
    )


def write_json_to_file(data: dict, output_path: Path):
    """
    Writes output JSON to a file.
    """

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


if __name__ == "__main__":
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    print(
        f"endpoint: {endpoint}",
        file=sys.stderr
    )
    print(
        f"deployment: {deployment}",
        file=sys.stderr
    )

    if len(sys.argv) > 1:
        ocr_json_file = sys.argv[1]
    else:
        ocr_json_file = "outputs/t1_layout_extraction.json"

    print(
        f"Testing Foundry restructuring on existing OCR file: {ocr_json_file}",
        file=sys.stderr
    )

    result = restructure_ocr_file_to_sharepoint_rows(
        ocr_json_path=ocr_json_file
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

    output_path = Path(
        f"{Path(ocr_json_file).stem}_sharepoint_rows.json"
    )

    write_json_to_file(
        result,
        output_path
    )

    print(
        f"Results written to {output_path}"
    )