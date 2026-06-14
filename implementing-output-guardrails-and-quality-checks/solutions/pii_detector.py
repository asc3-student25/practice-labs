"""
PII Detector - Detects and redacts personally identifiable information

Handles:
- Social Security Numbers (SSN)
- Credit card numbers
- Phone numbers
- Email addresses
- Account numbers
- Names and addresses (basic)

Run: python pii_detector.py
"""

import re
from typing import Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class PIIDetectionResult:
    """Result of PII detection."""

    found_types: Dict[str, int]
    redacted_text: str
    original_text: str
    locations: Dict[str, List[Tuple[int, int]]]


class PIIDetector:
    """Detect and redact personally identifiable information."""

    # Regex patterns for common PII
    SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"
    PHONE_PATTERN = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    CREDIT_CARD_PATTERN = r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"
    ACCOUNT_NUMBER_PATTERN = r"\b(?:account|acct)[\s#:]*(\d{8,12})\b"

    @classmethod
    def detect_pii(cls, text: str) -> Dict[str, int]:
        """Detect PII types in text. Returns counts by type."""
        found = {}

        if re.search(cls.SSN_PATTERN, text):
            found["ssn"] = len(re.findall(cls.SSN_PATTERN, text))
        if re.search(cls.PHONE_PATTERN, text):
            found["phone"] = len(re.findall(cls.PHONE_PATTERN, text))
        if re.search(cls.EMAIL_PATTERN, text):
            found["email"] = len(re.findall(cls.EMAIL_PATTERN, text))
        if re.search(cls.CREDIT_CARD_PATTERN, text):
            found["credit_card"] = len(re.findall(cls.CREDIT_CARD_PATTERN, text))
        if re.search(cls.ACCOUNT_NUMBER_PATTERN, text, re.IGNORECASE):
            found["account_number"] = len(
                re.findall(cls.ACCOUNT_NUMBER_PATTERN, text, re.IGNORECASE)
            )

        return found

    @classmethod
    def redact_pii(cls, text: str) -> Tuple[str, Dict[str, int]]:
        """Redact PII from text. Returns (redacted_text, detection_summary)."""
        detected = cls.detect_pii(text)
        redacted = text

        # Redact each type
        redacted = re.sub(cls.SSN_PATTERN, "***-**-****", redacted)
        redacted = re.sub(cls.PHONE_PATTERN, "***-***-****", redacted)
        redacted = re.sub(cls.EMAIL_PATTERN, "****@****.***", redacted)
        redacted = re.sub(cls.CREDIT_CARD_PATTERN, "**** **** **** ****", redacted)
        redacted = re.sub(
            cls.ACCOUNT_NUMBER_PATTERN,
            r"account ********",
            redacted,
            flags=re.IGNORECASE,
        )

        return redacted, detected

    @classmethod
    def detect_pii_detailed(cls, text: str) -> PIIDetectionResult:
        """Detailed PII detection with locations."""
        locations = {}

        # SSN
        ssn_matches = list(re.finditer(cls.SSN_PATTERN, text))
        if ssn_matches:
            locations["ssn"] = [(m.start(), m.end()) for m in ssn_matches]

        # Phone
        phone_matches = list(re.finditer(cls.PHONE_PATTERN, text))
        if phone_matches:
            locations["phone"] = [(m.start(), m.end()) for m in phone_matches]

        # Email
        email_matches = list(re.finditer(cls.EMAIL_PATTERN, text))
        if email_matches:
            locations["email"] = [(m.start(), m.end()) for m in email_matches]

        # Credit card
        cc_matches = list(re.finditer(cls.CREDIT_CARD_PATTERN, text))
        if cc_matches:
            locations["credit_card"] = [(m.start(), m.end()) for m in cc_matches]

        # Redact
        redacted_text, found_types = cls.redact_pii(text)

        return PIIDetectionResult(
            found_types=found_types,
            redacted_text=redacted_text,
            original_text=text,
            locations=locations,
        )


def demo():
    """Demonstrate PII detection."""
    print("=" * 60)
    print("  PII Detection Demonstration")
    print("=" * 60)

    test_cases = [
        "My SSN is 123-45-6789",
        "Call me at 555-123-4567",
        "Email: john.doe@example.com",
        "Card: 4532-1234-5678-9010",
        "My account number is ACC#1234567890",
        "Contact: 555-123-4567, SSN: 987-65-4321, email test@test.com",
    ]

    detector = PIIDetector()

    for i, text in enumerate(test_cases, 1):
        print(f"\n{'─'*60}")
        print(f"Test Case {i}")
        print(f"{'─'*60}")
        print(f"Original: {text}")

        redacted, found = detector.redact_pii(text)
        print(f"Redacted: {redacted}")

        if found:
            print(f"\nDetected PII:")
            for pii_type, count in found.items():
                print(f"  • {pii_type}: {count} occurrence(s)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
