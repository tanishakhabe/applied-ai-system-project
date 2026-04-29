## AI Coach

This version adds an on-demand AI Coach that looks at the visible game state, recent guesses, and remaining attempts, then suggests the next best guess strategy.

- It only uses public round state and guess history.
- It does not read the secret number.
- It falls back to a local strategy if an API key is not configured.

To enable the LLM-backed version, set `OPENAI_API_KEY` in your environment before running Streamlit.

## System Diagram

See [system_diagram.svg](system_diagram.svg) for the full flow of the player, Streamlit UI, agentic coach, deterministic logic, testing, and human review points.

## Reliability and Evaluation
The project includes a pytest suite that covers the core game rules and the coach helpers, including:
- guess validation and hint logic
- closeness scoring
- coach state extraction
- prompt safety and heuristic coach output

## Reflection and Ethics
Some of the limitations and biases in my system are the restricted game modes and inputs. The game simply focuses on numbers, so there are not more, expanded features. The AI coach could be misused if a player simply "spams" the AI coach request button, instead of attempting their own guesses. The AI coach also learns from and is therefore bias towards the player's past guess history. 

To prevent misuse of the AI coach, we could add a limit to the number of times you can call the coach agent in a single round or level. In higher levels, your ability to call the coach agent is further limited.  

I was surprised by how quickly the AI can implement features, even with limited guidance. However, without checking the implementation you can end up with several errors and overcomplicated UI. 

For example, AI suggested moving the hints feature to the bottom of the page. But that did not make sense for gameplay and would require the player to scroll, so I rejected that suggestion. 