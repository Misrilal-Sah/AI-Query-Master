"""
AI Query Master - Query Evaluation System
Calculates Performance, Security, Readability, and Complexity scores.
"""
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

EVALUATION_SYSTEM_PROMPT = """You are a database query evaluator. Score the given query on these metrics (0-100):

1. **Performance Score**: How well-optimized is the query?
   - 90-100: Excellent (uses indexes, efficient joins, no waste)
   - 70-89: Good (minor improvements possible)
   - 50-69: Fair (some performance issues)
   - 0-49: Poor (significant performance problems)

2. **Security Score**: How secure is the query?
   - 90-100: Excellent (parameterized, no injection risks)
   - 70-89: Good (mostly secure, minor concerns)
   - 50-69: Fair (some vulnerabilities)
   - 0-49: Poor (major security risks)

3. **Readability Score**: How readable and maintainable?
   - 90-100: Excellent (well-formatted, good aliases, clear)
   - 70-89: Good (readable but could be cleaner)
   - 50-69: Fair (somewhat hard to follow)
   - 0-49: Poor (very hard to read)

4. **Complexity Score**: How complex is the query? (lower = more complex)
   - 90-100: Simple (easy to understand)
   - 70-89: Moderate (some complexity)
   - 50-69: Complex (multiple joins or subqueries)
   - 0-49: Very complex (deeply nested, many operations)

Respond in JSON format:
{
    "performance_score": <0-100>,
    "security_score": <0-100>,
    "readability_score": <0-100>,
    "complexity_score": <0-100>,
    "overall_score": <0-100>,
    "grade": "<A/B/C/D/F>",
    "summary": "<brief overall assessment>"
}"""


class QueryEvaluator:
    """Evaluate queries and analyses with multi-dimensional scoring."""

    def __init__(self, llm_provider=None):
        self.llm = llm_provider

    def evaluate_query(
        self,
        query: str,
        db_type: str = "mysql",
        static_issues: list = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a query with both static and LLM-based scoring.

        Returns scores dict with performance, security, readability, complexity.
        """
        # Start with static scoring
        scores = self._static_score(query, static_issues or [])

        # Enhance with LLM scoring if available
        if self.llm:
            llm_scores = self._llm_score(query, db_type)
            if llm_scores:
                # Blend static and LLM scores (60% LLM, 40% static)
                for key in ["performance_score", "security_score",
                            "readability_score", "complexity_score"]:
                    if key in llm_scores and key in scores:
                        scores[key] = round(
                            llm_scores[key] * 0.6 + scores[key] * 0.4
                        )
                    elif key in llm_scores:
                        scores[key] = llm_scores[key]

                scores["grade"] = llm_scores.get("grade", scores.get("grade", "C"))
                scores["summary"] = llm_scores.get("summary", "")

        # Calculate overall
        scores["overall_score"] = round(
            (scores.get("performance_score", 50) +
             scores.get("security_score", 50) +
             scores.get("readability_score", 50) +
             scores.get("complexity_score", 50)) / 4
        )

        if "grade" not in scores:
            scores["grade"] = self._calculate_grade(scores["overall_score"])

        return scores

    def _static_score(self, query: str, issues: list) -> Dict[str, int]:
        """Calculate scores based on static analysis issues."""
        perf_score = 100
        sec_score = 100
        read_score = 100
        complexity_score = 100

        # Deduct for issues
        for issue in issues:
            severity = issue.get("severity", "info")
            issue_type = issue.get("type", "other")

            deduction = {"critical": 25, "error": 15, "warning": 10, "info": 5}.get(severity, 5)

            if issue_type == "performance":
                perf_score -= deduction
            elif issue_type == "security":
                sec_score -= deduction
            elif issue_type == "readability":
                read_score -= deduction
            elif issue_type == "schema":
                perf_score -= deduction // 2
                read_score -= deduction // 2

        # Complexity based on query structure
        import re
        join_count = len(re.findall(r"\bJOIN\b", query, re.IGNORECASE))
        subquery_count = query.upper().count("SELECT") - 1
        clause_count = sum(1 for kw in ["WHERE", "GROUP BY", "HAVING", "ORDER BY", "UNION"]
                           if kw in query.upper())

        complexity_score -= join_count * 5
        complexity_score -= subquery_count * 15
        complexity_score -= max(0, clause_count - 3) * 5

        return {
            "performance_score": max(0, min(100, perf_score)),
            "security_score": max(0, min(100, sec_score)),
            "readability_score": max(0, min(100, read_score)),
            "complexity_score": max(0, min(100, complexity_score)),
        }

    def _llm_score(self, query: str, db_type: str) -> Optional[Dict]:
        """Get LLM-based scoring."""
        prompt = f"""Evaluate this {db_type.upper()} query:

```sql
{query}
```

Provide scores for performance, security, readability, and complexity."""

        result = self.llm.generate(
            prompt=prompt,
            system_prompt=EVALUATION_SYSTEM_PROMPT,
            temperature=0.2,
            json_mode=True,
        )

        if not result["success"]:
            return None

        try:
            return json.loads(result["text"])
        except json.JSONDecodeError:
            text = result["text"]
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            return None

    def _calculate_grade(self, overall: int) -> str:
        """Calculate letter grade from overall score."""
        if overall >= 90:
            return "A"
        elif overall >= 80:
            return "B"
        elif overall >= 70:
            return "C"
        elif overall >= 60:
            return "D"
        return "F"

    def evaluate_schema(
        self,
        schema: str,
        db_type: str = "mysql",
        static_issues: list = None,
    ) -> Dict[str, Any]:
        """Evaluate schema quality."""
        issues = static_issues or []

        # Score based on issues
        design_score = 100
        perf_score = 100
        read_score = 100

        for issue in issues:
            severity = issue.get("severity", "info")
            deduction = {"critical": 20, "error": 15, "warning": 10, "info": 5}.get(severity, 5)

            if issue.get("type") == "schema":
                design_score -= deduction
            elif issue.get("type") == "performance":
                perf_score -= deduction
            elif issue.get("type") == "readability":
                read_score -= deduction

        overall = round((design_score + perf_score + read_score) / 3)

        return {
            "design_score": max(0, min(100, design_score)),
            "performance_score": max(0, min(100, perf_score)),
            "readability_score": max(0, min(100, read_score)),
            "overall_score": max(0, min(100, overall)),
            "grade": self._calculate_grade(overall),
            "total_issues": len(issues),
        }
