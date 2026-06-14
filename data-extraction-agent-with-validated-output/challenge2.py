import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from models import InvoiceDataWithConfidence, PartialInvoiceData
from sample_invoices import INVOICE_1, PROBLEMATIC_INVOICE

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Make sure .env file exists in the same directory as this script."
    )

# Get model from environment variable
model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
print(f"Using model: {model}")

# Main extraction agent
main_agent = Agent(
    model,
    output_type=InvoiceDataWithConfidence,
    system_prompt="""You are an expert invoice data extraction system.
    
    Extract structured information from invoice text, including:
    - Vendor name and invoice number
    - Invoice date in YYYY-MM-DD format
    - Totals and tax information
    - Payment terms
    
    Additionally, provide confidence scores (0.0-1.0) for your extractions.
    If information is unclear or missing, use null for optional fields.""",
)


def robust_extract(invoice_text: str) -> InvoiceDataWithConfidence | PartialInvoiceData:
    """Extract with fallback to partial data."""
    try:
        return main_agent.run_sync(invoice_text).output
    except Exception as e:
        print(f"Full extraction failed: {e}")
        fallback_agent = Agent(
            model,
            output_type=PartialInvoiceData,
            system_prompt=(
                "Extract what you can from the invoice into the schema. "
                "Set unclear fields to null and add brief issues to extraction_errors."
            ),
        )
        return fallback_agent.run_sync(invoice_text).output
    
if __name__ == "__main__":
    result_1 = robust_extract(INVOICE_1)
    print("INVOICE_1 returns InvoiceDataWithConfidence:", isinstance(result_1, InvoiceDataWithConfidence))
    print("Vendor:", getattr(result_1, "vendor_name", None))
    print("Invoice Number:", getattr(result_1, "invoice_number", None))

    result_2 = robust_extract(PROBLEMATIC_INVOICE)
    print("PROBLEMATIC_INVOICE returns PartialInvoiceData:", isinstance(result_2, PartialInvoiceData))
    print("Vendor:", getattr(result_2, "vendor_name", None))
    print("Invoice Number:", getattr(result_2, "invoice_number", None))
    print("Extraction Errors:", getattr(result_2, "extraction_errors", None))
    raw_text = getattr(result_2, "raw_text_snippet", None)
    print("Raw Text Snippet Preview:", (raw_text[:120] + "...") if isinstance(raw_text, str) and len(raw_text) > 120 else raw_text)
