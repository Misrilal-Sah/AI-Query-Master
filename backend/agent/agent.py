"""
AI Query Master - Main Agent Orchestrator
Coordinates tools, RAG, LLM, reflection, and evaluation for query and schema review.
"""
import json
import logging
import time
from typing import Dict, Any, Optional

from agent.llm_provider import get_llm_provider
from agent.rag_pipeline import get_rag_pipeline
from agent.tools import analyze_query, analyze_schema, generate_index_recommendation
from agent.reflection import SelfReflector
from agent.evaluator import QueryEvaluator

logger = logging.getLogger(__name__)


# ============================================================
# System prompts
# ============================================================
QUERY_REVIEW_PROMPT = """You are an expert {db_type} query analyst.

STATIC ANALYSIS RESULTS:
{static_analysis}

KNOWLEDGE BASE CONTEXT:
{rag_context}

INDEX RECOMMENDATIONS:
{index_recommendations}

STRICT RULES:
- ONLY flag issues that ACTUALLY EXIST in the given query
- Do NOT hallucinate issues (e.g. do NOT say "INT used for dates" if the schema uses TEXT)
- Do NOT give generic advice unrelated to this specific query
- Keep response proportional to query complexity (simple query = brief review)
- Do NOT discuss multi-tenancy, schema migration tools, or server tuning

Respond with this structure:

### Issues Found
| Severity | Issue | Why It Matters |
(only real issues in this query)

### Optimized Query
```sql
(the improved query only — no CREATE TABLE unless the user asked for DDL)
```

### Key Tips
(2-3 specific, actionable tips for THIS query)"""

SCHEMA_REVIEW_PROMPT = """You are an expert {db_type} schema designer.

STATIC ANALYSIS RESULTS:
{static_analysis}

KNOWLEDGE BASE CONTEXT:
{rag_context}

STRICT RULES:
- ONLY flag issues that ACTUALLY EXIST in the given schema
- Do NOT hallucinate (e.g. do NOT say "INT used for dates" if schema uses TEXT)
- Do NOT mention multi-tenancy patterns, schema migration tools, or pt-online-schema-change
- Do NOT invent transitive dependencies that don't exist
- Use correct terminology: if data is denormalized, say "denormalization" not "transitive dependency"
- Keep response focused and practical

Respond with this structure:

### Critical Issues
(missing PKs, FKs, wrong data types — only real ones)

### Performance Issues
(missing indexes on JOIN/WHERE columns)

### Security Issues
(e.g. password stored as plain text)

### Normalization Issues
(only if data genuinely needs normalizing)

### Improved Schema
```sql
(the complete corrected DDL)
```

### Index Suggestions
```sql
(only genuinely needed indexes)
```"""


class QueryAgent:
    """Main AI agent that orchestrates query and schema review features."""

    def __init__(self):
        self.llm = get_llm_provider()
        self.rag = get_rag_pipeline()
        self.reflector = SelfReflector(self.llm)
        self.evaluator = QueryEvaluator(self.llm)

    async def review_query(self, query: str, db_type: str = "mysql") -> Dict[str, Any]:
        """
        Query Review & Optimization
        Full agentic loop: parse → RAG → tools → LLM → reflect → evaluate
        """
        start_time = time.time()
        steps = []

        # Step 1: Static Analysis (Tool Call)
        steps.append({"step": 1, "action": "Static Analysis", "status": "running"})
        static_result = analyze_query(query, db_type)
        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Found {static_result['total_issues']} issues"

        # Step 2: RAG Retrieval
        steps.append({"step": 2, "action": "Knowledge Base Search", "status": "running"})
        rag_results = self.rag.search(
            f"SQL query optimization best practices {db_type} "
            f"{'performance issues' if static_result['total_issues'] > 0 else 'query review'}",
            db_type=db_type,
            k=5,
        )
        rag_context = "\n\n".join([
            f"[{r['source']}] (relevance: {r['score']:.2f})\n{r['text']}"
            for r in rag_results
        ])
        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Retrieved {len(rag_results)} knowledge chunks"

        # Step 3: Index Recommendations (Tool Call)
        steps.append({"step": 3, "action": "Index Analysis", "status": "running"})
        index_recs = generate_index_recommendation(query, "", db_type)
        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Generated {len(index_recs)} index recommendations"

        # Step 4: LLM Reasoning
        steps.append({"step": 4, "action": "AI Analysis", "status": "running"})
        prompt = QUERY_REVIEW_PROMPT.format(
            db_type=db_type.upper(),
            static_analysis=json.dumps(static_result["issues"], indent=2),
            rag_context=rag_context,
            index_recommendations=json.dumps(index_recs, indent=2),
        )

        llm_result = self.llm.generate(
            prompt=f"Analyze this {db_type} query:\n\n```sql\n{query}\n```",
            system_prompt=prompt,
            temperature=0.3,
        )

        if not llm_result["success"]:
            return {"error": "LLM analysis failed", "details": llm_result}

        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Used {llm_result['provider']}"

        # Step 5: Self-Reflection
        steps.append({"step": 5, "action": "Self-Reflection", "status": "running"})
        reflection_result = self.reflector.reflect_and_improve(
            original_input=query,
            current_response=llm_result["text"],
            context=rag_context,
            task_type="query_review",
        )
        steps[-1]["status"] = "done"
        steps[-1]["result"] = (
            f"Confidence: {reflection_result['confidence']}% "
            f"({reflection_result['iterations']} iterations)"
        )

        # Step 6: Evaluation
        steps.append({"step": 6, "action": "Scoring", "status": "running"})
        scores = self.evaluator.evaluate_query(query, db_type, static_result["issues"])
        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Overall: {scores['overall_score']}/100 (Grade: {scores['grade']})"

        elapsed = round(time.time() - start_time, 2)

        return {
            "success": True,
            "feature": "query_review",
            "input": query,
            "db_type": db_type,
            "analysis": reflection_result["final_response"],
            "static_issues": static_result["issues"],
            "index_recommendations": index_recs,
            "scores": scores,
            "confidence": reflection_result["confidence"],
            "reflection_log": reflection_result["reflection_log"],
            "steps": steps,
            "sources": [r["source"] for r in rag_results],
            "provider": llm_result["provider"],
            "time_seconds": elapsed,
        }

    async def review_schema(self, schema: str, db_type: str = "mysql") -> Dict[str, Any]:
        """
        Schema Review
        """
        start_time = time.time()
        steps = []

        # Step 1: Static Schema Analysis
        steps.append({"step": 1, "action": "Schema Analysis", "status": "running"})
        static_result = analyze_schema(schema, db_type)
        steps[-1]["status"] = "done"
        steps[-1]["result"] = (
            f"Found {static_result['total_issues']} issues in "
            f"{static_result['tables_found']} tables"
        )

        # Step 2: RAG Retrieval
        steps.append({"step": 2, "action": "Knowledge Base Search", "status": "running"})
        rag_results = self.rag.search(
            f"database schema design best practices {db_type} normalization indexing",
            db_type=db_type,
            k=5,
        )
        rag_context = "\n\n".join([
            f"[{r['source']}] (relevance: {r['score']:.2f})\n{r['text']}"
            for r in rag_results
        ])
        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Retrieved {len(rag_results)} knowledge chunks"

        # Step 3: LLM Analysis
        steps.append({"step": 3, "action": "AI Analysis", "status": "running"})
        prompt = SCHEMA_REVIEW_PROMPT.format(
            db_type=db_type.upper(),
            static_analysis=json.dumps(static_result["issues"], indent=2),
            rag_context=rag_context,
        )

        llm_result = self.llm.generate(
            prompt=f"Review this {db_type} schema:\n\n```sql\n{schema}\n```",
            system_prompt=prompt,
            temperature=0.3,
        )

        if not llm_result["success"]:
            return {"error": "LLM analysis failed", "details": llm_result}

        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Used {llm_result['provider']}"

        # Step 4: Self-Reflection
        steps.append({"step": 4, "action": "Self-Reflection", "status": "running"})
        reflection_result = self.reflector.reflect_and_improve(
            original_input=schema,
            current_response=llm_result["text"],
            context=rag_context,
            task_type="schema_review",
        )
        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Confidence: {reflection_result['confidence']}%"

        # Step 5: Evaluation
        steps.append({"step": 5, "action": "Scoring", "status": "running"})
        scores = self.evaluator.evaluate_schema(schema, db_type, static_result["issues"])
        steps[-1]["status"] = "done"
        steps[-1]["result"] = f"Overall: {scores['overall_score']}/100"

        elapsed = round(time.time() - start_time, 2)

        return {
            "success": True,
            "feature": "schema_review",
            "input": schema,
            "db_type": db_type,
            "analysis": reflection_result["final_response"],
            "static_issues": static_result["issues"],
            "scores": scores,
            "confidence": reflection_result["confidence"],
            "reflection_log": reflection_result["reflection_log"],
            "steps": steps,
            "sources": [r["source"] for r in rag_results],
            "provider": llm_result["provider"],
            "time_seconds": elapsed,
        }


# Singleton
_agent: Optional[QueryAgent] = None


def get_agent() -> QueryAgent:
    """Get or create the singleton agent."""
    global _agent
    if _agent is None:
        _agent = QueryAgent()
    return _agent
