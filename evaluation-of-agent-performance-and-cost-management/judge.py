import os
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class JudgeScore(BaseModel):
    """Structured qualitative assessment from a judge agent."""

    helpfulness: int = Field(..., ge=1, le=5, description="How helpful the response is")
    correctness: int = Field(..., ge=1, le=5, description="How factually correct the response is")
    completeness: int = Field(..., ge=1, le=5, description="How fully it answers the question")
    rationale: str = Field(..., min_length=10, max_length=300)


class JudgeAgent:
    """LLM-as-judge for qualitative scoring."""

    def __init__(self, model: str | None = None):
        resolved = model or os.getenv("JUDGE_MODEL") or os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
        if ":" not in resolved:
            resolved = f"openai:{resolved}"

        self.agent = Agent(
            resolved,
            output_type=JudgeScore,
            system_prompt=(
                "You are an impartial QA judge for customer support responses. "
                "Return only the requested structured scores. "
                "Use a strict 1-5 scale where 5 is excellent and 1 is poor."
            ),
        )

    async def score(
        self,
        question: str,
        response: str,
        expected_response: Optional[str],
        expected_keywords: List[str],
    ) -> JudgeScore:
        """Score a response against question and expected guidance."""
        expected_text = expected_response if expected_response else "(not provided)"
        prompt = (
            f"Question:\n{question}\n\n"
            f"Agent Response:\n{response}\n\n"
            f"Expected Response Guidance:\n{expected_text}\n\n"
            f"Expected Keywords:\n{', '.join(expected_keywords) if expected_keywords else '(none)'}\n\n"
            "Score helpfulness, correctness, and completeness from 1-5 and provide a brief rationale."
        )
        result = await self.agent.run(prompt)
        return result.output
