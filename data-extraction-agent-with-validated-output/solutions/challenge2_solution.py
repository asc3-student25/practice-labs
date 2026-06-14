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
    # YOUR CODE HERE
    # [SOLUTION]
    try:
        # Try full extraction
        result = main_agent.run_sync(f"Extract invoice data:\n{invoice_text}")
        return result.output
    except Exception as e:
        # Fall back to partial extraction
        print(f"Full extraction failed ({e}), trying partial...")

        partial_agent = Agent(
            os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
            output_type=PartialInvoiceData,
            system_prompt="""Extract whatever information you can find.
            List any problems or missing fields in extraction_errors.""",
        )

        result = partial_agent.run_sync(f"Extract: {invoice_text}")
        return result.output
    # [/SOLUTION]


if __name__ == "__main__":
    # YOUR CODE HERE
    # [SOLUTION]
    # Test with good invoice
    print("Testing with good invoice:")
    print(f"{'='*60}")
    result = robust_extract(INVOICE_1)
    if isinstance(result, InvoiceDataWithConfidence):
        print(f"✓ Full extraction successful")
        print(f"  Vendor: {result.vendor_name}")
        print(f"  Total: ${result.total_amount:.2f}")

    # Test with problematic invoice
    print("\n\nTesting with problematic invoice:")
    print(f"{'='*60}")
    result = robust_extract(PROBLEMATIC_INVOICE)
    if isinstance(result, PartialInvoiceData):
        print("⚠ Partial extraction:")
        print(f"  Vendor: {result.vendor_name or 'UNKNOWN'}")
        print(f"  Amount: {result.total_amount or 'UNKNOWN'}")
        print(f"  Errors: {', '.join(result.extraction_errors)}")
        print(f"  Raw snippet: {result.raw_text_snippet[:100]}...")
    # [/SOLUTION]
