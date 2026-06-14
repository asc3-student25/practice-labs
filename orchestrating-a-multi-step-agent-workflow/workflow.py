"""
Multi-Step Agent Workflow Orchestration

Coordinates complex workflows with multiple sequential steps:
- Step-by-step execution with state management
- Conditional branching based on step results
- Data passing between steps
- Error recovery and retry logic
- Workflow visualization and logging

Run: python workflow.py
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pydantic_ai import Agent
import os
from dotenv import load_dotenv

load_dotenv()


class StepStatus(Enum):
    """Status of a workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in the workflow."""

    name: str
    agent: Optional[Agent] = None
    prompt_template: str = ""
    required_inputs: List[str] = field(default_factory=list)
    condition: Optional[Callable] = None  # Skip if condition returns False
    retry_count: int = 2
    handler: Optional[Callable[["WorkflowOrchestrator", "WorkflowStep"], Awaitable[Any]]] = None

    # Runtime state
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0


@dataclass
class WorkflowContext:
    """Shared state across workflow steps."""
    data: Dict[str, Any] = field(default_factory=dict)
    steps_completed: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def set(self, key: str, value: Any):
        """Store data."""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve data."""
        return self.data.get(key, default)

        handler=handler,
    def has(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.data


class WorkflowOrchestrator:
    """Orchestrates sequential workflow execution."""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[WorkflowStep] = []
        self.context = WorkflowContext()

    def add_step(
        self,
        name: str,
        agent: Optional[Agent] = None,
        prompt_template: str = "",
        required_inputs: Optional[List[str]] = None,
        condition: Optional[Callable] = None,
        retry_count: int = 2,
        handler: Optional[
            Callable[["WorkflowOrchestrator", WorkflowStep], Awaitable[Any]]
        ] = None,
    ) -> "WorkflowOrchestrator":
        """Add a step to the workflow."""
        if handler is None and (agent is None or not prompt_template):
            raise ValueError(
                "Step requires either a handler or both agent and prompt_template"
            )

        step = WorkflowStep(
            name=name,
            agent=agent,
            prompt_template=prompt_template,
            required_inputs=required_inputs or [],
            condition=condition,
            retry_count=retry_count,
            handler=handler,
        )
        self.steps.append(step)
        return self

    async def execute(self, initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the complete workflow.

        This orchestration loop is provided for you. It handles:
        - Seeding the shared context with initial_data
        - Iterating steps in order and printing progress banners
        - Skipping steps whose condition returns False
        - Validating that each step's required_inputs are present
        - Retrying a step up to retry_count + 1 times on failure
        - Recording final status, errors, and total duration

        It calls self._execute_step(step) to actually run each step — that
        is the method you will implement.
        """
        # Initialize context
        if initial_data:
            self.context.data.update(initial_data)

        self.context.start_time = datetime.now()

        print(f"\n{'='*60}")
        print(f"  Workflow: {self.name}")
        print(f"{'='*60}\n")

        # Execute each step
        for i, step in enumerate(self.steps, 1):
            print(f"Step {i}/{len(self.steps)}: {step.name}")
            print(f"{'─'*60}")

            try:
                # Check condition
                if step.condition and not step.condition(self.context):
                    step.status = StepStatus.SKIPPED
                    print(f"⊘ Skipped (condition not met)\n")
                    continue

                # Check required inputs
                missing = [
                    inp for inp in step.required_inputs if not self.context.has(inp)
                ]
                if missing:
                    raise ValueError(f"Missing required inputs: {missing}")

                # Execute step with retries
                step.status = StepStatus.RUNNING
                success = False

                for attempt in range(step.retry_count + 1):
                    step.attempts = attempt + 1

                    try:
                        result = await self._execute_step(step)
                        step.result = result
                        step.status = StepStatus.COMPLETED
                        self.context.steps_completed.append(step.name)
                        success = True
                        print(f"✓ Completed (attempt {attempt + 1})\n")
                        break

                    except Exception as e:
                        if attempt < step.retry_count:
                            print(f"⚠ Attempt {attempt + 1} failed: {e}")
                            print(f"  Retrying...")
                            await asyncio.sleep(1)
                        else:
                            raise

                if not success:
                    raise RuntimeError(
                        f"Step failed after {step.retry_count + 1} attempts"
                    )

            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                print(f"✗ Failed: {e}\n")

                # Stop workflow on failure
                self.context.end_time = datetime.now()
                return self._get_results()

        self.context.end_time = datetime.now()

        duration = (self.context.end_time - self.context.start_time).total_seconds()
        print(f"{'='*60}")
        print(f"  Workflow Completed in {duration:.1f}s")
        print(f"{'='*60}\n")

        return self._get_results()

    async def _execute_step(self, step: WorkflowStep) -> str:
        """Execute a single step.

        ``str.format`` raises ``KeyError`` if ``step.prompt_template``
        references a placeholder that isn't in ``self.context.data``.
        ``execute()`` validates ``step.required_inputs`` before reaching
        here, but does *not* parse the template — so a placeholder
        added in a Challenge extension without a matching
        ``required_inputs`` entry would surface as an unhelpful
        bare ``KeyError``. The except branch below converts that into
        a diagnostic naming both the step and the missing key.
        """
        if step.handler is not None:
            result = await step.handler(self, step)
            normalized = result if isinstance(result, str) else json.dumps(result)
            self.context.set(f"step_{step.name}_result", normalized)
            return normalized

        if step.agent is None:
            raise ValueError(f"Step '{step.name}' has no agent configured")

        try:
            prompt = step.prompt_template.format(**self.context.data)
        except KeyError as e:
            missing_key = e.args[0] if e.args else "<unknown>"
            raise KeyError(
                f"Step '{step.name}' prompt references missing key '{missing_key}'"
            ) from e

        result = await step.agent.run(prompt)
        self.context.set(f"step_{step.name}_result", result.output)
        return result.output

    def _get_results(self) -> Dict[str, Any]:
        """Get workflow results."""
        return {
            "status": (
                "completed"
                if all(
                    s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED)
                    for s in self.steps
                )
                else "failed"
            ),
            "context": self.context.data,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "result": s.result,
                    "error": s.error,
                    "attempts": s.attempts,
                }
                for s in self.steps
            ],
            "duration_seconds": (
                (self.context.end_time - self.context.start_time).total_seconds()
                if self.context.end_time
                else None
            ),
        }


# Example: Research workflow
async def research_workflow_example():
    """Demonstrate multi-step research workflow."""

    # Create specialized agents
    research_agent = Agent(
        os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
        system_prompt="You are a research assistant. Provide detailed, factual information.",
    )

    summarizer_agent = Agent(
        os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
        system_prompt="You are a summarizer. Create concise, clear summaries.",
    )

    outline_agent = Agent(
        os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
        system_prompt="You are an outline creator. Structure information clearly.",
    )

    # Build workflow
    workflow = WorkflowOrchestrator("Research Report Generation")

    workflow.add_step(
        name="research",
        agent=research_agent,
        prompt_template="Research the topic: {topic}. Provide detailed information.",
        required_inputs=["topic"],
    )

    workflow.add_step(
        name="summarize",
        agent=summarizer_agent,
        prompt_template="Summarize this research:\n\n{step_research_result}",
        required_inputs=["step_research_result"],
    )

    workflow.add_step(
        name="create_outline",
        agent=outline_agent,
        prompt_template="Create an outline for a report based on:\n\n{step_summarize_result}",
        required_inputs=["step_summarize_result"],
    )

    # Execute
    results = await workflow.execute(initial_data={"topic": "artificial intelligence"})

    # Display results
    print("\nFinal Results:")
    print(json.dumps(results, indent=2))


def classify_task(initial_data: Dict[str, Any]) -> str:
    """Classify task into a workflow category using simple rules."""
    text = " ".join(
        str(initial_data.get(k, "")) for k in ("task", "query", "input", "topic")
    ).lower()

    research_keywords = ["research", "analyze", "summary", "summarize", "report"]
    order_keywords = ["order", "payment", "invoice", "purchase", "shipping"]

    if any(k in text for k in order_keywords):
        return "order"
    if any(k in text for k in research_keywords):
        return "research"
    return "general"


def build_workflow_for_input(initial_data: Dict[str, Any]) -> WorkflowOrchestrator:
    """Factory that composes a workflow dynamically from classified input."""
    category = classify_task(initial_data)
    model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")

    if category == "research":
        research_agent = Agent(
            model,
            system_prompt="You are a research assistant. Provide detailed, factual information.",
        )
        summarizer_agent = Agent(
            model,
            system_prompt="You are a summarizer. Create concise, clear summaries.",
        )

        workflow = WorkflowOrchestrator("Dynamic Research Workflow")
        workflow.add_step(
            name="research",
            agent=research_agent,
            prompt_template="Research this topic: {topic}",
            required_inputs=["topic"],
        )
        workflow.add_step(
            name="summarize",
            agent=summarizer_agent,
            prompt_template="Summarize the following findings:\n\n{step_research_result}",
            required_inputs=["step_research_result"],
        )
        return workflow

    if category == "order":
        ops_agent = Agent(model, system_prompt="You handle order operations.")
        workflow = WorkflowOrchestrator("Dynamic Order Workflow")
        workflow.add_step(
            name="validate_order",
            agent=ops_agent,
            prompt_template="Validate this order request: {order}",
            required_inputs=["order"],
        )
        workflow.add_step(
            name="process_payment",
            agent=ops_agent,
            prompt_template="Process payment for this order: {order}",
            required_inputs=["order"],
        )
        workflow.add_step(
            name="send_confirmation",
            agent=ops_agent,
            prompt_template="Write a confirmation message for order: {order}",
            required_inputs=["order"],
        )
        return workflow

    general_agent = Agent(model, system_prompt="You are a helpful assistant.")
    workflow = WorkflowOrchestrator("Dynamic General Workflow")
    workflow.add_step(
        name="respond",
        agent=general_agent,
        prompt_template="Respond helpfully to this request: {task}",
        required_inputs=["task"],
    )
    return workflow


async def workflow_factory_example():
    """Demonstrate same factory producing different workflow paths."""
    inputs = [
        {"topic": "artificial intelligence trends", "task": "research and summarize"},
        {"order": "Laptop x1, $1299", "task": "process this order payment"},
    ]

    for i, payload in enumerate(inputs, start=1):
        category = classify_task(payload)
        workflow = build_workflow_for_input(payload)
        print(f"\n[Factory Demo {i}] category={category}, workflow={workflow.name}")
        results = await workflow.execute(initial_data=payload)
        print(f"[Factory Demo {i}] status={results['status']}")


# Example: Conditional workflow
async def conditional_workflow_example():
    """Demonstrate workflow with conditional steps."""

    agent = Agent(os.getenv("AI_MODEL", "openai:gpt-5.4-mini"))

    workflow = WorkflowOrchestrator("Order Processing")

    workflow.add_step(
        name="validate_order",
        agent=agent,
        prompt_template="Validate this order: {order}. Respond with VALID or INVALID.",
        required_inputs=["order"],
    )

    # Conditional step - only run if order is valid
    def order_is_valid(ctx):
        result = ctx.get("step_validate_order_result", "")
        return "VALID" in result.upper()

    workflow.add_step(
        name="process_payment",
        agent=agent,
        prompt_template="Process payment for order {order}",
        required_inputs=["order"],
        condition=order_is_valid,
    )

    workflow.add_step(
        name="send_confirmation",
        agent=agent,
        prompt_template="Generate confirmation email for processed order",
        condition=order_is_valid,
    )

    # Execute
    results = await workflow.execute(initial_data={"order": "Book x2, $29.99"})


async def nested_workflow_example():
    """Demonstrate a parent workflow step invoking a child workflow."""
    model = os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
    parent_agent = Agent(model, system_prompt="You are a helpful assistant.")

    async def run_child_workflow(parent: WorkflowOrchestrator, _: WorkflowStep) -> Dict[str, Any]:
        child = WorkflowOrchestrator("Child Research Workflow")
        researcher = Agent(
            model,
            system_prompt="You are a research assistant. Provide factual details.",
        )
        summarizer = Agent(
            model,
            system_prompt="You summarize findings clearly and concisely.",
        )

        child.add_step(
            name="collect",
            agent=researcher,
            prompt_template="Collect key facts about: {topic}",
            required_inputs=["topic"],
        )
        child.add_step(
            name="summarize",
            agent=summarizer,
            prompt_template="Summarize these findings:\n\n{step_collect_result}",
            required_inputs=["step_collect_result"],
        )

        child_results = await child.execute(initial_data={"topic": parent.context.get("topic", "")})

        normalized = {
            "status": child_results.get("status"),
            "summary": child_results.get("context", {}).get("step_summarize_result"),
            "facts": child_results.get("context", {}).get("step_collect_result"),
        }

        parent.context.set("nested_workflow", normalized)

        if child_results.get("status") != "completed":
            parent.context.set("nested_workflow_partial", normalized)
            raise RuntimeError("Nested workflow failed")

        return normalized

    parent = WorkflowOrchestrator("Parent Workflow with Nested Step")
    parent.add_step(
        name="prepare",
        agent=parent_agent,
        prompt_template="Create a one-line preface for topic: {topic}",
        required_inputs=["topic"],
    )
    parent.add_step(
        name="nested_research",
        handler=run_child_workflow,
        retry_count=1,
    )
    parent.add_step(
        name="finalize",
        agent=parent_agent,
        prompt_template=(
            "Use this preface: {step_prepare_result}\n"
            "and nested summary: {step_nested_research_result}\n"
            "to produce a final response."
        ),
        required_inputs=["step_prepare_result", "step_nested_research_result"],
    )

    results = await parent.execute(initial_data={"topic": "multi-agent orchestration"})
    print("\nNested Workflow Final Results:")
    print(json.dumps(results, indent=2))


async def main():
    """Main demonstration."""
    print("Workflow Orchestration Examples\n")

    await workflow_factory_example()

    print("\n" + "=" * 60 + "\n")

    await research_workflow_example()

    print("\n" + "=" * 60 + "\n")

    await conditional_workflow_example()

    print("\n" + "=" * 60 + "\n")

    await nested_workflow_example()


if __name__ == "__main__":
    asyncio.run(main())
