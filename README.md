# 🧭 El Osta AI Agent 

**El Osta** (The Captain) is a smart, AI-powered public transit companion for Alexandria, Egypt. This repository hosts the intelligent agent core, interacts with geocoding and routing services, and delivers human-friendly transit directions.

## 🌟 Project Overview

This agent serves as the "brain" of the El Osta application. It translates a user's natural language query (e.g., "How do I get from Sidi Gaber to Misr Station?") into structured data, fetches precise coordinates, calculates the best route using a custom routing engine, and formats the response back into natural language.

### Key Features
*   **Natural Language Understanding:** Uses LLMs (Google Gemini) to parse complex user queries in English, Arabic, or Franco-Arabic.
*   **Intelligent Routing:** Orchestrates a workflow to find optimal public transit routes involving buses, trams, and microbuses.
*   **Graph-Based Architecture:** Built on [LangGraph](https://python.langchain.com/docs/langgraph) to manage state and control the flow of the conversation and data processing.
*   **Modular Services:** Cleanly separated logic for Geocoding, Routing (gRPC), and LLM interaction.
*   **Streamlit UI:** Includes a comprehensive multi-page dashboard for end-users and developers to interact with and test the agent.

---

## 🏗️ Agent Architecture

The core of this project is a stateful graph defined in `app/graph/graph.py`. The agent follows a linear pipeline:

1.  **Parse Node (`parse.py`):**
    *   **Input:** User's natural language string.
    *   **Action:** Calls the LLM to extract the `origin`, `destination`, and any preferences (walking distance, max transfers).
    *   **Output:** Structured JSON with start/end locations.

2.  **Geocode Node (`geocode.py`):**
    *   **Input:** Location names from the Parse step.
    *   **Action:** Queries a local database (PostGIS) or external geocoders to resolve names into `(latitude, longitude)` coordinates.
    *   **Output:** Coordinates for start and end points.

3.  **Route Node (`route.py`):**
    *   **Input:** Coordinates and transit preferences.
    *   **Action:** Sends a gRPC request to the dedicated El Osta Routing Server.
    *   **Output:** A list of valid transit journeys (paths).

4.  **Format Node (`format.py`):**
    *   Takes the complex JSON response from the router and transforms it into a natural, conversational instruction list using the LLM.

### State Management
The `AgentState` (defined in `app/graph/state.py`) keeps track of:
*   `user_query`: Original input.
*   `parsed_data`: Extracted locations.
*   `coordinates`: Lat/Long pairs.
*   `raw_routes`: Journey objects from the gRPC server.
*   `final_response`: Human-readable text.

---

## 🛠️ Services Detail

The `app/services/` directory contains the integration logic for external systems:

*   **LLM Service (`llm.py`):** Configures the Google Gemini Pro model with specific system prompts for parsing and formatting.
*   **Routing Client (`routing_client.py`):** A high-performance gRPC client that communicates with the El Osta Routing Server. It handles message serialization using the generated stubs in `grpc_stubs/`.
*   **Geocoding Service (`geocoding_serv.py`):** Executes spatial queries against the PostGIS database. It searches for landmarks, street names, and transit stops.
*   **Format Utility (`format_output.py`):** Post-processing logic to ensure the AI output matches the user's preferred language and tone.

---

## 📂 Project Structure Explained

```text
├── app/
│   ├── app.py                  # Streamlit Setup & Main Entry for UI
│   ├── config.py               # Configuration constants
│   ├── main.py                 # CLI/Script entry point to run the graph
│   │
│   ├── pages/                  # Streamlit Pages
│   │   ├── 1_🤖_El_Osta_AI.py    # Main AI Chat Interface
│   │   ├── 2_🚌_Routing_Test.py  # Developer tool for testing routing API
│   │   └── 3_📍_Geocoding.py     # Developer tool for testing geocoding
│   │
│   ├── graph/                  # LangGraph Definitions
│   │   ├── graph.py            # The graph topology (nodes & edges)
│   │   ├── state.py            # AgentState definition (TypedDict)
│   │   └── nodes/              # Individual step implementations
│   │       ├── parse.py        # Extract intent from text
│   │       ├── geocode.py      # Resolve addresses
│   │       ├── route.py        # Fetch routes
│   │       └── format.py       # Generate final answer
│   │
│   ├── services/               # External Integrations
│   │   ├── llm.py              # Interface for Google Gemini LLM
│   │   ├── routing_client.py   # gRPC Client definition
│   │   ├── geocoding_serv.py   # Database/API Geocoding logic
│   │   └── format_output.py    # Utilities to clean text output
│   │
│   ├── ui/                     # UI Styling & Theming
│   │   └── theme.py            # CSS Injection & Theme Management
│   │
│   ├── grpc/                   # Protocol Buffer Definitions
│   │   └── routing.proto       # Service contract
│   └── grpc_stubs/             # Generated gRPC Python Code

├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```


## 🚀 Getting Started

### Prerequisites

*   **Python 3.10+**
*   **Google Gemini API Key:** Required for natural language processing tasks.
*   **Routing Server:** Access to an instance of the [El Osta Routing Server](https://github.com/Marwan051/final_project_routing_server).
*   **Database:** Access to a PostGIS database from the [Database Repository](https://github.com/Marwan051/final-project-database).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RowanFayez/El_osta-Agent.git
    cd El_osta-Agent
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Create a `.env` file in the root directory and provide the necessary credentials:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
PG_DB_NAME=transport_db
PG_USER=postgres
PG_PASSWORD=postgres

```
4. **run database docker container**
at : https://github.com/Marwan051/final-project-database?tab=readme-ov-file 

5. **run routing server docker container**
at : https://github.com/Marwan051/final_project_routing_server 

### Running the Agent

#### 1. Streamlit UI (Recommended)
To launch the interactive dashboard and chat interface:
```bash
streamlit run app/app.py
```

#### Work for Second Semester

1. Train a Router on Different Types of Prompts
* Prepare and categorize prompts that users might input (short, long, complex, or multi-lingual).
* Fine-tune the routing logic so queries are sent to the correct module (Trip Planneing, information about route, etc.).
* Evaluate performance with test prompts and measure accuracy in selecting the right handler.
2. Build a RAG (Retrieval-Augmented Generation) Model for Route Queries
* Connect the model to the routes database to answer user queries dynamically.


3. Implement Short-Term and Long-Term Memory
* Short-Term Memory: Store recent queries and their context during a single session for follow-ups.
* Long-Term Memory: Maintain persistent user preferences, frequent routes, and learning patterns across sessions.
Ensure memory integration doesn’t slow down real-time responses.
