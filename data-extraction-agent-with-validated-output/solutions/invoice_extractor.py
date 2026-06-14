import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from models import InvoiceDataWithConfidence
from sample_invoices import INVOICE_1, INVOICE_2, INVOICE_3

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

agent = Agent(
    model,
    output_type=InvoiceDataWithConfidence,
    system_prompt="""You are an expert invoice data extraction system.
    
    Extract structured information from invoice text, including:
    - Vendor name and invoice number
    - Invoice date in YYYY-MM-DD format
    - Totals and tax information
    - Payment terms
    
    Additionally, provide confidence scores (0.0-1.0) for your extractions:
    - 1.0: Information is explicit and unambiguous
    - 0.7-0.9: Information is present but requires interpretation
    - 0.4-0.6: Information is unclear or partially missing
    - 0.0-0.3: Information is not present or highly ambiguous
    
    If information is unclear or missing, use null for optional fields.
    Be precise with numbers—extract exactly as stated.""",
)


def extract_invoice(invoice_text: str) -> InvoiceDataWithConfidence:
    """Extract structured data from invoice text."""
    result = agent.run_sync(f"Extract invoice data from this text:\n\n{invoice_text}")
    return result.output


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    invoices = [
        ("ABC Office Supplies", INVOICE_1),
        ("ACME Catering", INVOICE_2),
        ("Informal Email", INVOICE_3),
    ]

    for name, invoice_text in invoices:
        print(f"\n{'='*60}")
        print(f"Processing: {name}")
        print(f"{'='*60}")

        try:
            extracted = extract_invoice(invoice_text)
            print(
                f"✓ Vendor: {extracted.vendor_name} (confidence: {extracted.vendor_confidence:.2f})"
            )
            print(
                f"✓ Total: ${extracted.total_amount:.2f} (confidence: {extracted.amount_confidence:.2f})"
            )
            print(f"✓ Invoice #: {extracted.invoice_number or 'N/A'}")
            print(f"✓ Date: {extracted.invoice_date or 'N/A'}")
            print(f"✓ Needs Review: {extracted.needs_review()}")
        except Exception as e:
            print(f"✗ Extraction failed: {e}")
    # [/SOLUTION]
