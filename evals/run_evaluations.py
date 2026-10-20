
import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agentforge.core.agent import build_agent, run_agent
from agentforge.core.config import settings
from agentforge.evaluation import score_case


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "evals" / "cases.json"
REPORT_PATH = ROOT / "evals" / "latest-report.json"


async def main() -> int:
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Configure it in your .env file "
            "to run persistent agent evaluations."
        )

    cases = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    results = []

    database_url = settings.database_url.get_secret_value()

    # Open the PostgreSQL checkpointer for this evaluation run.
    async with AsyncPostgresSaver.from_conn_string(
        database_url
    ) as checkpointer:
        await checkpointer.setup()

        # Compile the graph with persistence enabled.
        graph = build_agent(checkpointer=checkpointer)

        for case in cases:
            print(f"Running evaluation: {case['id']}")

            try:
                result = await run_agent(
                    case["message"],
                    graph=graph,
                    thread_id=f"eval-{case['id']}-{uuid4().hex}",
                )
                scored = score_case(case, result)

            except Exception as exc:
                scored = {
                    "id": case["id"],
                    "passed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }

            results.append(scored)
            print(f"  {'PASS' if scored['passed'] else 'FAIL'}")

            if scored.get("missing_keywords"):
                print("  Missing keywords:", scored["missing_keywords"])

            if scored.get("missing_tools"):
                print("  Missing tools:", scored["missing_tools"])

            if scored.get("error"):
                print("  Error:", scored["error"])

    passed = sum(item["passed"] for item in results)
    total = len(results)
    pass_rate = passed / total if total else 0.0

    report = {
        "passed": passed,
        "total": total,
        "pass_rate": round(pass_rate, 4),
        "results": results,
    }

    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nEvaluation result: {passed}/{total} passed")
    print(f"Pass rate: {pass_rate:.1%}")
    print(f"Report saved to: {REPORT_PATH}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    # Psycopg async connections need a SelectorEventLoop on Windows.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    raise SystemExit(asyncio.run(main()))
