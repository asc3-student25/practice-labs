"""
Output Guardrails

Validates agent outputs for:
- Quality standards (length, completeness, helpfulness)
- Safety (profanity, inappropriate content)
- Policy compliance (no advice, no opinions)
- Professional tone

Run:
    python output_guards.py
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
import re


@dataclass
class OutputValidationResult:
    """Result of output validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    policy_violations: List[str]
    quality_score: float  # 0.0-1.0


class OutputGuardrails:
    """
     Validate agent outputs for quality and safety.

    Features:
     - Length and completeness checks
     - Profanity detection
     - Policy compliance verification
     - Quality scoring
    """

    # Content restrictions
    PROFANITY = [
        "damn",
        "hell",
        "crap",
        "fuck",
        "shit",
        "ass",
        "bitch",
        "bastard",
        "piss",
        "dick",
    ]

    # Inappropriate content patterns
    INAPPROPRIATE_PATTERNS = [
        r"\b(hate|violent|kill|die)\s+(you|them|him|her)\b",
        r"\b(stupid|idiot|moron|dumb)\s+(person|customer|user)\b",
    ]

    # Generic/unhelpful phrases
    GENERIC_PHRASES = [
        "i cannot help",
        "as an ai",
        "i am unable",
        "i do not have access",
        "i cannot provide",
        "i am not able",
    ]

    # Policy violation patterns
    ADVICE_PATTERNS = [
        r"you should (buy|sell|invest|trade)",
        r"i recommend (buying|selling|investing)",
        r"the best (stock|investment|option) is",
        r"you must (file|report|declare)",
        r"legally you (need|must|should)",
    ]

    OPINION_PATTERNS = [
        r"\bi think\b",
        r"\bi believe\b",
        r"\bin my opinion\b",
        r"\bpersonally\b",
        r"\bi feel that\b",
    ]

    # Length constraints
    MIN_LENGTH = 20
    MAX_LENGTH = 1000

    @classmethod
    def validate_output(cls, response: str) -> OutputValidationResult:
        """
        Comprehensive output validation.

        Args:
            response: Agent's response text

        Returns:
            OutputValidationResult with validation details
        """
        errors = []
        warnings = []
        policy_violations = []
        quality_score = 1.0  # Start at perfect, deduct for issues

        # Check for empty response
        if not response or not response.strip():
            errors.append("Response is empty")
            return OutputValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                policy_violations=policy_violations,
                quality_score=0.0,
            )

        response_lower = response.lower()

        # Length validation
        if len(response) < cls.MIN_LENGTH:
            errors.append(f"Response too short (min {cls.MIN_LENGTH} characters)")
            quality_score -= 0.3

        if len(response) > cls.MAX_LENGTH:
            warnings.append(f"Response very long (max {cls.MAX_LENGTH} recommended)")
            quality_score -= 0.1

        # Profanity check
        found_profanity = [word for word in cls.PROFANITY if word in response_lower]
        if found_profanity:
            errors.append(
                f"Contains inappropriate language: {', '.join(found_profanity)}"
            )
            quality_score -= 0.5

        # Inappropriate patterns
        for pattern in cls.INAPPROPRIATE_PATTERNS:
            if re.search(pattern, response_lower):
                errors.append(f"Contains inappropriate content")
                quality_score -= 0.4
                break

        # Generic/unhelpful responses
        generic_count = sum(
            1 for phrase in cls.GENERIC_PHRASES if phrase in response_lower
        )
        if generic_count > 0:
            warnings.append("Response contains generic phrases that may not be helpful")
            quality_score -= 0.2 * generic_count

        # Policy compliance - financial/legal advice
        for pattern in cls.ADVICE_PATTERNS:
            if re.search(pattern, response_lower):
                policy_violations.append(
                    "Cannot provide financial, legal, or tax advice"
                )
                quality_score -= 0.6
                break

        # Policy compliance - personal opinions
        for pattern in cls.OPINION_PATTERNS:
            if re.search(pattern, response_lower):
                policy_violations.append("Cannot express personal opinions")
                quality_score -= 0.3
                break

        # Ensure quality score doesn't go negative
        quality_score = max(0.0, quality_score)

        # Determine if valid
        is_valid = len(errors) == 0 and len(policy_violations) == 0

        return OutputValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            policy_violations=policy_violations,
            quality_score=quality_score,
        )

    @classmethod
    def check_factual_accuracy_markers(cls, response: str) -> List[str]:
        """
        Check for markers that suggest factual inaccuracy.

        Args:
            response: Response text

        Returns:
            List of detected issues
        """
        issues = []
        response_lower = response.lower()

        # Uncertainty markers
        uncertainty_phrases = [
            "i think maybe",
            "probably",
            "might be",
            "could be",
            "not sure",
            "uncertain",
        ]

        for phrase in uncertainty_phrases:
            if phrase in response_lower:
                issues.append(f"Contains uncertain language: '{phrase}'")

        # Absolute claims without sources
        absolute_claims = [
            "always",
            "never",
            "everyone",
            "no one",
            "definitely",
            "certainly",
        ]

        absolute_count = sum(
            1 for word in absolute_claims if f" {word} " in f" {response_lower} "
        )
        if absolute_count > 2:
            issues.append(
                f"Contains {absolute_count} absolute claims without citations"
            )

        return issues

    @classmethod
    def check_completeness(
        cls, response: str, expected_elements: List[str]
    ) -> Dict[str, bool]:
        """
        Check if response contains expected elements.

        Args:
            response: Response text
            expected_elements: List of expected keywords/phrases

        Returns:
            Dictionary with presence of each element
        """
        response_lower = response.lower()

        return {
            element: element.lower() in response_lower for element in expected_elements
        }

    @classmethod
    def grade_response(cls, response: str) -> Dict[str, any]:
        """
        Grade response on multiple dimensions.

        Args:
            response: Response text

        Returns:
            Dictionary with grades and feedback
        """
        validation = cls.validate_output(response)

        # Length score
        length_score = 1.0
        if len(response) < cls.MIN_LENGTH:
            length_score = len(response) / cls.MIN_LENGTH
        elif len(response) > cls.MAX_LENGTH:
            length_score = max(0.7, cls.MAX_LENGTH / len(response))

        # Helpfulness score (inverse of generic phrases)
        generic_count = sum(
            1 for phrase in cls.GENERIC_PHRASES if phrase in response.lower()
        )
        helpfulness_score = max(0.0, 1.0 - (generic_count * 0.3))

        # Safety score (profanity and inappropriate content)
        safety_score = 1.0 if not validation.errors else 0.0

        # Policy score
        policy_score = 1.0 if not validation.policy_violations else 0.0

        # Overall score
        overall_score = (
            validation.quality_score * 0.4
            + length_score * 0.2
            + helpfulness_score * 0.2
            + safety_score * 0.1
            + policy_score * 0.1
        )

        return {
            "overall_score": overall_score,
            "quality_score": validation.quality_score,
            "length_score": length_score,
            "helpfulness_score": helpfulness_score,
            "safety_score": safety_score,
            "policy_score": policy_score,
            "is_passing": overall_score >= 0.7,
            "feedback": {
                "errors": validation.errors,
                "warnings": validation.warnings,
                "policy_violations": validation.policy_violations,
            },
        }


def demo():
    """Demonstrate output guardrails."""
    print("=" * 60)
    print("  Output Guardrails Demonstration")
    print("=" * 60)

    test_responses = [
        # Good responses
        (
            "Our business hours are Monday through Friday, 9 AM to 5 PM EST. "
            "We're closed on weekends and major holidays. For urgent matters outside "
            "these hours, please use our 24/7 automated hotline at 1-800-555-0100.",
            True,
        ),
        (
            "To reset your password, visit our website and click 'Forgot Password' "
            "on the login page. You'll receive a reset link via email. If you need "
            "further assistance, our support team is available during business hours.",
            True,
        ),
        # Too short
        ("Yes, we can help.", False),
        # Contains profanity
        ("That's a damn good question. Let me help you with that shit.", False),
        # Generic/unhelpful
        ("I cannot help with that request as an AI assistant.", False),
        # Financial advice (policy violation)
        (
            "You should definitely invest in our premium savings account. "
            "I think it's the best option for you.",
            False,
        ),
        # Personal opinion (policy violation)
        (
            "In my opinion, you should file your taxes early. I believe that's "
            "the best approach.",
            False,
        ),
        # Too long (>1000 chars)
        ("x" * 1100, False),
    ]

    guard = OutputGuardrails()

    for i, (response, should_be_valid) in enumerate(test_responses, 1):
        print(f"\n{'─'*60}")
        print(f"Test Case {i}")
        print(f"{'─'*60}")

        # Display response (truncated)
        response_display = response[:80] + "..." if len(response) > 80 else response
        print(f"Response: {response_display}")

        # Validate
        result = guard.validate_output(response)

        print(f"\nValid: {result.is_valid} (expected: {should_be_valid})")
        print(f"Quality Score: {result.quality_score:.2f}")

        if result.errors:
            print(f"\nErrors:")
            for error in result.errors:
                print(f"  • {error}")

        if result.warnings:
            print(f"\nWarnings:")
            for warning in result.warnings:
                print(f"  • {warning}")

        if result.policy_violations:
            print(f"\nPolicy Violations:")
            for violation in result.policy_violations:
                print(f"  • {violation}")

        # Grade response
        grade = guard.grade_response(response)
        print(
            f"\nOverall Grade: {grade['overall_score']:.2f} ({'PASS' if grade['is_passing'] else 'FAIL'})"
        )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
