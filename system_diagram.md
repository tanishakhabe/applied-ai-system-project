# AI System Diagram

```mermaid
flowchart LR
    U[Human player / reviewer] -->|enters guess or requests help| UI[Streamlit UI in app.py]
    UI -->|visible game state| S[Game state + history]
    S -->|structured context| A[Agentic coach in coach_utils.py]
    A -->|optional API call| M[LLM model via OPENAI_API_KEY]
    A -->|fallback advice| H[Heuristic coach]
    M --> P[Parsed coach response]
    H --> P
    P -->|suggestion + recommended guess| UI
    UI -->|submit guess| L[Deterministic game logic in logic_utils.py]
    L -->|hint / win / lose / score| UI

    subgraph Checking
        T[pytest tests/test_game_logic.py]
        E[Output validation and prompt/schema checks]
        R[Retriever]
    end

    T -->|verifies deterministic rules and coach helpers| L
    T -->|verifies coach state extraction| A
    E -->|checks coach output stays within allowed state| P
    U -->|reviews coach suggestion and game result| E
    R -. not implemented in this project .-> A

    style R stroke-dasharray: 5 5
```

## Flow Summary

1. The human player enters a guess or asks for help in the Streamlit UI.
2. The UI passes the visible round state and guess history into the agentic coach.
3. The coach either calls the LLM or uses the local heuristic fallback, then returns advice.
4. The same guess still goes through deterministic game logic for hints, win/loss, and score updates.
5. Tests check the pure logic and coach helpers, while the human can review the coach response in the UI.

## Notes

- **Retriever**: shown as a dashed future/optional component, but it is not implemented in the current codebase.
- **Agent**: implemented in `coach_utils.py` and wired into `app.py`.
- **Evaluator**: represented by output validation and the coach helper tests.
- **Tester**: implemented with `pytest` in `tests/test_game_logic.py`.
