from pathlib import Path
import os
import sys
import json

from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential


load_dotenv()


def get_document_intelligence_client():
    endpoint = (
        os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT_CUSTOM_MODEL")
        or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    )

    key = (
        os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY_CUSTOM_MODEL")
        or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    )

    if not endpoint or not key:
        raise RuntimeError(
            "Missing Azure Document Intelligence credentials."
        )

    return DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )


def field_value_to_json(field):

    if field is None:
        return None

    if getattr(field, "value_string", None) is not None:
        return field.value_string

    if getattr(field, "value_number", None) is not None:
        return field.value_number

    if getattr(field, "value_integer", None) is not None:
        return field.value_integer

    if getattr(field, "value_date", None) is not None:
        return str(field.value_date)

    if getattr(field, "value_time", None) is not None:
        return str(field.value_time)

    if getattr(field, "value_currency", None) is not None:
        currency = field.value_currency

        return {
            "amount": getattr(currency, "amount", None),
            "currency_code": getattr(currency, "currency_code", None)
        }

    if getattr(field, "value_address", None) is not None:
        address = field.value_address

        return {
            "street_address": getattr(address, "street_address", None),
            "city": getattr(address, "city", None),
            "state": getattr(address, "state", None),
            "postal_code": getattr(address, "postal_code", None)
        }

    if getattr(field, "value_array", None) is not None:
        return [
            field_value_to_json(item)
            for item in field.value_array
        ]

    if getattr(field, "value_object", None) is not None:
        return {
            key: field_value_to_json(value)
            for key, value in field.value_object.items()
        }

    return getattr(field, "content", None)


def table_to_rows(table):
    """
    Converts an Azure DI table into compact LLM-friendly rows.
    """

    rows = [
        [""] * table.column_count
        for _ in range(table.row_count)
    ]

    for cell in table.cells:

        content = (cell.content or "").strip()

        if content:
            rows[cell.row_index][cell.column_index] = content

    formatted_rows = []

    for row in rows:

        cleaned = [
            value.strip()
            for value in row
            if value and value.strip()
        ]

        if cleaned:
            formatted_rows.append(
                " | ".join(cleaned)
            )

    return formatted_rows


def get_table_page_number(table):

    if not table.bounding_regions:
        return None

    return table.bounding_regions[0].page_number


def extract_document_intelligence_payload(pdf_path: str) -> str:

    print(
        f"Processing PDF: {pdf_path}",
        file=sys.stderr
    )

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    client = get_document_intelligence_client()

    with open(path, "rb") as pdf_file:

        poller = client.begin_analyze_document(
            model_id="prebuilt-invoice",
            body=pdf_file,
            content_type="application/pdf"
        )

    result = poller.result()

    output = {
        "source_file": str(path),
        "invoice_fields": {},
        "pages": {}
    }

    #
    # Invoice fields
    #
    if result.documents:

        document = result.documents[0]

        for field_name, field in (document.fields or {}).items():
            output["invoice_fields"][field_name] = (
                field_value_to_json(field)
            )

    #
    # Page containers
    #
    for page in result.pages or []:

        output["pages"][f"page_{page.page_number}"] = {
            "tables": []
        }

    #
    # Tables
    #
    for table in result.tables or []:

        page_number = get_table_page_number(table)

        if page_number is None:
            continue

        rows = table_to_rows(table)

        if not rows:
            continue

        output["pages"][f"page_{page_number}"]["tables"].append(
            rows
        )

    #
    # Remove empty pages
    #
    output["pages"] = {
        page_key: page_data
        for page_key, page_data in output["pages"].items()
        if page_data["tables"]
    }

    return json.dumps(
        output,
        indent=2,
        ensure_ascii=False
    )


def write_json_to_file(data: dict, output_path: Path):

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


if __name__ == "__main__":

    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        pdf_file = "resources/documents/truck_tickets/t2.pdf"

    result_json = extract_document_intelligence_payload(
        pdf_file
    )

    print(result_json)

    output_path = Path(
        f"{Path(pdf_file).stem}_invoice_extraction.json"
    )

    write_json_to_file(
        json.loads(result_json),
        output_path
    )

    print(
        f"Results written to {output_path}"
    )