from dotenv import load_dotenv
import os

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient

load_dotenv()

client = DocumentIntelligenceAdministrationClient(
    endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    )
)

for model in client.list_models():
    print(model.model_id)

print(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"))

print(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_CUSTOM_MODEL_ID"))