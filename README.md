# 🎮 Game Glitch Investigator: The Impossible Guesser

## Original Project

The original project from Modules 1-3 was **The Impossible Guesser**, a Streamlit number guessing game. Its original goal was to let the player guess a secret number within a difficulty-based range, receive higher/lower hints, and track progress across attempts. The project originally focused on debugging broken game logic, fixing Streamlit state issues, and making the game testable.

## Title and Summary

This project is a polished number guessing game with an **AI Coach**. It matters because it shows how a small deterministic app can be extended with AI in a useful, bounded way: the game still runs on clear rules, while the coach helps the player think through the next move.

## What It Does

- Lets the player choose a difficulty level: Easy, Normal, or Hard.
- Accepts manual number guesses through a text input.
- Returns hints such as higher/lower and tracks guess history.
- Calculates score and ends the round on a win or loss.
- Provides an optional AI Coach that analyzes the visible game state and suggests the next guess.

## Architecture Overview

The architecture is split into two main layers:

- `app.py` handles the Streamlit UI, session state, layout, and user interaction.
- `logic_utils.py` contains deterministic game rules such as range validation, hint logic, and closeness scoring.
- `coach_utils.py` builds the AI coach context, generates a recommendation, and falls back to a local heuristic if no API key is available.
- `tests/test_game_logic.py` verifies the core rules and the coach helper functions.

The system diagram in `system_diagram.md` shows the flow from human input to the UI, into the game logic and coach, and back to the player. It also highlights where testing and human review happen. The retriever is shown only as a possible future component; it is not implemented in this project.

## Setup Instructions

1. Open the project folder in VS Code or your terminal.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. If you want the LLM-backed coach, set your API key first:

   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

   Optional settings:

   ```bash
   export OPENAI_MODEL="gpt-4.1-mini"
   export OPENAI_BASE_URL="https://api.openai.com"
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

5. Run the tests:

   ```bash
   pytest
   ```

## Sample Interactions

These examples use the built-in heuristic coach, which is what you get when no API key is configured.

### Example 1: Midgame coaching

- Input: Difficulty = Normal, guesses = `10`, then `40`, then ask for AI help.
- AI output:
  - Title: `Coach recommends 25`
  - Suggestion: `Try 25 next.`
  - Explanation: The coach narrows the visible range and recommends the midpoint to reduce uncertainty.

### Example 2: Recent low/high feedback

- Input: Difficulty = Easy, guesses = `5` then `15`, then ask for AI help.
- AI output:
  - Title: `Coach recommends 10`
  - Suggestion: `Try 10 next.`
  - Explanation: The coach infers the remaining range from the prior hints and suggests the midpoint.

### Example 3: Round already solved

- Input: Correct guess submitted, then ask for AI help.
- AI output:
  - Title: `Round already solved`
  - Suggestion: `You already won this round.`
  - Explanation: Start a new game to use the coach on another puzzle.

## Design Decisions

I built the project this way to keep the game rules deterministic and the AI layer advisory only. That separation makes the app easier to test and prevents the coach from changing the actual outcome of the game.

I chose an agentic coach instead of a retriever or a fine-tuned model because the project is small and the gameplay state is already structured. A retriever would add complexity without much benefit here, and a fine-tuned model would not be justified without a larger labeled dataset.

The main trade-off is that the coach is less powerful than a trained or retrieval-based assistant, but it is far simpler to ship and reason about. The local heuristic fallback also keeps the app usable when no API key is configured.

## Testing Summary

What worked:

- The core game logic tests passed after the logic was separated into a separate file `logic_utils.py`.
- The coach helper tests passed, including state extraction and prompt safety checks.
- The Streamlit app runs with both the heuristic fallback and the API-based coach path.

What did not work at first:

- I introduced an indentation bug while moving the hint display, which caused a Streamlit compilation error.
- After I initially added the AI Coach feature, the UI got really buggy and cluttered. I had to clean up the UI separately and focus on having two separate components on the screen, the original guess and the AI suggested guess. 

What I learned:

- Small UI changes in Streamlit can break execution if indentation or state ordering is off.
- AI features are easier to manage when the visible state is packaged into a single structured context.
- Tests are useful not just for game rules, but also for validating the boundaries around AI behavior.

## Reflection

This project taught me that AI is most useful when it is constrained by the structure of the problem. The strongest result was not a flashy model, but a clean separation between deterministic game logic, a coach that reasons from visible state, and tests that keep the system honest.

It also reinforced that debugging AI-assisted software is still normal software engineering: state management, UI ordering, and error handling matter just as much as the model call. Overall, the project showed me how to build AI into an app in a way that is practical, testable, and easy to explain.
