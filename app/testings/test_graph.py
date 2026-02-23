import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.graph.graph import build_graph

graph = build_graph()

initial_state = {
    "query": "عايزة اروح من سيدي جابر لمحطة مصر",
    "walking_cutoff": 1000.0,
    "max_transfers": 2
}

final_state = graph.invoke(initial_state)

# print("\n===== FINAL STATE =====\n")
# for k, v in final_state.items():
#     print(f"{k}: {v}")

print("\n===== FINAL ANSWER =====\n")
print(final_state.get("final_answer"))
