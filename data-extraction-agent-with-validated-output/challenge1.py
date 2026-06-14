import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from models import InvoiceDataWithConfidence
from sample_invoices import NOISY_INVOICE

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

# Agent that handles noisy input
agent = Agent(
    model,
    output_type=InvoiceDataWithConfidence,
    system_prompt="""You are an expert invoice extraction system that handles noisy input.

Common issues to handle:
- OCR errors (0→O, 1→I, etc.)
- Inconsistent formatting
- Typos and misspellings
- Missing or implicit dates

Normalize data:
- Clean vendor names
- Convert dates to YYYY-MM-DD format
- Parse amounts even with inconsistent formatting

Additionally, provide confidence scores (0.0-1.0) for your extractions:
- 1.0: Information is explicit and unambiguous
- 0.7-0.9: Information is present but requires interpretation
- 0.4-0.6: Information is unclear or partially missing
- 0.0-0.3: Information is not present or highly ambiguous

If multiple interpretations are possible, choose the most business-reasonable one.""",
)


def extract_invoice(invoice_text: str) -> InvoiceDataWithConfidence:
    """Extract structured data from invoice text."""
    result = agent.run_sync(f"Extract invoice data from this text:\n\n{invoice_text}")
    return result.output


if __name__ == "__main__":
    print("=== Noisy Invoice Extraction Test Run ===")
    try:
        data = extract_invoice(NOISY_INVOICE)

        print(
            f"Vendor: {getattr(data, 'vendor_name', None)} "
            f"(confidence: {getattr(data, 'vendor_name_confidence', 'N/A')})"
        )
        print(
            f"Total: {getattr(data, 'total', None)} "
            f"(confidence: {getattr(data, 'total_confidence', 'N/A')})"
        )
        print(
            f"Invoice Number: {getattr(data, 'invoice_number', None)} "
            f"(confidence: {getattr(data, 'invoice_number_confidence', 'N/A')})"
        )
        print(
            f"Date: {getattr(data, 'date', None)} "
            f"(confidence: {getattr(data, 'date_confidence', 'N/A')})"
        )

        print(f"Needs review: {data.needs_review()}")
    except Exception as e:
        print(f"Extraction failed: {e}")
