"""
AI Query Master - Self-Reflection Engine
Evaluates and iteratively improves agent responses.
"""
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

REFLECTION_SYSTEM_PROMPT = """You are a database expert reviewing your own analysis.
Evaluate your previous response for ACCURACY and CONCISENESS.

CRITICAL: Check for these common mistakes:
- Hallucinated issues (claiming problems that don't exist in the input)
- Wrong terminology (e.g. saying "transitive dependency" when it's "denormalization")
- Generic filler advice (multi-tenancy, migration tools, server tuning) not relevant to the input
- Mentioning data types that don't match the actual schema

Score your response (0-100):
1. Accuracy: Are all flagged issues real? No hallucinations?
2. Relevance: Is every point specific to the given input?
3. Conciseness: No unnecessary padding or generic advice?
4. Completeness: Did you catch the important issues?

Respond in JSON format:
{
    "confidence": <0-100 overall confidence>,
    "criteria_scores": {
        "accuracy": <0-100>,
        "relevance": <0-100>,
        "conciseness": <0-100>,
        "completeness": <0-100>
    },
    "hallucinations": ["list any hallucinated/incorrect claims to remove"],
    "missing_items": ["list of genuinely missing but important items"],
    "should_improve": <true/false>
}"""


class SelfReflector:
    """Self-reflection engine that evaluates and improves responses."""

    def __init__(self, llm_provider, max_iterations: int = 2, min_confidence: float = 70.0):
        self.llm = llm_provider
        self.max_iterations = max_iterations
        self.min_confidence = min_confidence

    def reflect_and_improve(
        self,
        original_input: str,
        current_response: str,
        context: str = "",
        task_type: str = "query_review",
    ) -> Dict[str, Any]:
        """
        Perform self-reflection on a response.
        If confidence is low, iteratively improve.

        Returns:
            {
                "final_response": str,
                "confidence": float,
                "iterations": int,
                "reflection_log": list,
            }
        """
        reflection_log = []
        best_response = current_response
        best_confidence = 0
        iteration = 0

        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Reflection iteration {iteration}/{self.max_iterations}")

            # Step 1: Evaluate current response
            reflection = self._evaluate_response(
                original_input, best_response, context, task_type
            )

            if not reflection:
                logger.warning("Reflection failed, keeping current response")
                break

            confidence = reflection.get("confidence", 50)
            should_improve = reflection.get("should_improve", False)

            reflection_log.append({
                "iteration": iteration,
                "confidence": confidence,
                "missing_items": reflection.get("missing_items", []),
                "criteria_scores": reflection.get("criteria_scores", {}),
            })

            logger.info(f"Reflection {iteration}: confidence={confidence}%, "
                         f"should_improve={should_improve}")

            best_confidence = confidence

            # If confident enough, stop
            if confidence >= self.min_confidence and not should_improve:
                logger.info(f"✓ Confidence {confidence}% >= {self.min_confidence}%. Done.")
                break

            # Step 2: Improve the response
            if should_improve and iteration < self.max_iterations:
                improved = self._improve_response(
                    original_input, best_response, reflection, context, task_type
                )
                if improved:
                    best_response = improved
                    logger.info(f"Response improved in iteration {iteration}")

        return {
            "final_response": best_response,
            "confidence": best_confidence,
            "iterations": iteration,
            "reflection_log": reflection_log,
        }

    def _evaluate_response(
        self,
        original_input: str,
        response: str,
        context: str,
        task_type: str,
    ) -> Optional[Dict]:
        """Evaluate a response using the LLM."""
        prompt = f"""Evaluate this {task_type} response:

ORIGINAL INPUT:
{original_input[:2000]}

RESPONSE TO EVALUATE:
{response[:3000]}

CONTEXT (best practices retrieved):
{context[:1000]}

Evaluate the response quality and provide your assessment in JSON."""

        result = self.llm.generate(
            prompt=prompt,
            system_prompt=REFLECTION_SYSTEM_PROMPT,
            temperature=0.2,
            json_mode=True,
        )

        if not result["success"]:
            return None

        try:
            return json.loads(result["text"])
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            text = result["text"]
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            return {"confidence": 50, "should_improve": False}

    def _improve_response(
        self,
        original_input: str,
        current_response: str,
        reflection: Dict,
        context: str,
        task_type: str,
    ) -> Optional[str]:
        """Improve a response based on reflection feedback."""
        missing = reflection.get("missing_items", [])
        improvements = reflection.get("improvements", [])

        prompt = f"""Improve this {task_type} response based on the following feedback:

ORIGINAL INPUT:
{original_input[:2000]}

CURRENT RESPONSE:
{current_response[:3000]}

HALLUCINATIONS TO REMOVE:
{json.dumps(reflection.get('hallucinations', []), indent=2)}

MISSING ITEMS TO ADD:
{json.dumps(missing, indent=2)}

CONTEXT (best practices):
{context[:1000]}

STRICT RULES FOR IMPROVEMENT:
- REMOVE any hallucinated or incorrect claims listed above
- ADD only genuinely missing important items
- Do NOT add generic advice about multi-tenancy, migration tools, or server tuning
- Do NOT pad the response with filler
- Keep the same structure but make it more accurate"""

        system_prompt = f"""You are a senior database expert. Fix the {task_type} analysis.
Remove incorrect claims. Add only genuinely missing items. Stay concise."""

        result = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )

        if result["success"]:
            return result["text"]
        return None
