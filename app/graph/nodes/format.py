import time

from app.services.format_output import format_server_journeys_for_user_llm


def format_node(state: dict) -> dict:
    """
    state متوقع فيه:
    - route_response
    - origin
    - destination
    """
    print("[FORMAT] Starting format node")
    start = time.time()

    route_response = state.get("route_response")
    origin = state.get("origin")
    dest = state.get("destination")

    journeys = (route_response or {}).get("journeys", []) if isinstance(route_response, dict) else []
    print(f"[FORMAT] Got {len(journeys)} journeys to format")

    # 1️⃣ فلترة وترتيب (حسب أقل مشي ثم أقل تكلفة ثم أقل وقت)
    def _rank(j: dict) -> tuple:
        summary = j.get("summary") or {}
        return (
            float(summary.get("walking_distance_meters", 0)),
            float(summary.get("cost", 0)),
            float(summary.get("total_time_minutes", 0)),
        )

    best_journeys = sorted(journeys, key=_rank)[:3]

    # 2️⃣ formatting (LLM)
    user_text = format_server_journeys_for_user_llm(
        journeys=best_journeys,
        origin=origin,
        dest=dest
    )

    print(f"[FORMAT] Done in {time.time()-start:.1f}s")

    return {
        **state,
        "final_answer": user_text
    }
