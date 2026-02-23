import json
import sys
import os

# Add app/ directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.routing_client import find_route  
if __name__ == "__main__":
    test_input = {
        "start_lat": 31.1939924,
        "start_lon": 29.922089,
        "end_lat": 31.2105511,
        "end_lon": 29.9462273,
        "max_transfers": 2,
        "walking_cutoff": 1000.0
    }

    result = find_route(
        start_lat=test_input["start_lat"],
        start_lon=test_input["start_lon"],
        end_lat=test_input["end_lat"],
        end_lon=test_input["end_lon"],
        max_transfers=test_input["max_transfers"],
        walking_cutoff=test_input["walking_cutoff"]
    )

    with open("test_route_output.json", "w") as f:
        json.dump(result, f, indent=4)
        


# main_test.py
# from app.graph.nodes import parse, geocode, route, format

# # حالة اختبارية
# state = {
#     "query": "عايزة اروح من سيدي جابر لمحطة مصر ؟",
#     "origin": None,
#     "destination": None,
#     "origin_geo": None,
#     "destination_geo": None,
#     "route_response": None,
#     "formatted": None,
# }

# # 1️⃣ Parse node
# state = parse.parse_node(state)
# print("بعد Parse:", state)

# # 2️⃣ Geocode node
# state = geocode.geocode_node(state)
# print("بعد Geocode:", state)

# # 3️⃣ Route node
# # state = route.route_node(state)
# # print("بعد Route:", state)

# # # # 4️⃣ Format node
# # state = format.format_node(state)
# # print("بعد Format:", state)

# # لو كله تمام، هتلاقي final_answer متولد في state["final_answer"]
# print("\nالناتج النهائي للـUser:")
# print(state.get("origin"))
# print(state.get("destination"))
# print(state.get("destination_geo"))
# print(state.get("origin_geo"))
# # print(state.get("route_response"))
# # print(state.get("final_answer"))
