import random
import streamlit as st
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    get_guess_closeness,
)


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)


# FIX: Display the correct range and attempt limit based on selected difficulty, instead of hardcoded values
st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "guess_history" not in st.session_state:
    st.session_state.guess_history = []

# FIX: Ensure the secret number always matches the active difficulty range, and reset game state if it doesn't. This prevents issues when switching difficulties mid-game.
# Ensure the current secret always matches the active difficulty range.
if st.session_state.secret < low or st.session_state.secret > high:
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_history = []

st.subheader("Make a guess")

st.info(
    # FIX: Removed hardcoded range and attempt info, replaced with dynamic values based on difficulty 
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

st.subheader("Guess History")
if not st.session_state.guess_history:
    st.caption("No guesses yet. Submit one to see how close you are.")
else:
    for entry in reversed(st.session_state.guess_history):
        if not entry["valid"]:
            st.markdown(
                f"**Attempt {entry['attempt']}** - `{entry['guess']}`"
            )
            st.caption(f"Invalid guess: {entry['error']}")
            continue

        st.markdown(
            f"**Attempt {entry['attempt']}** - Guess `{entry['guess']}`"
        )
        st.caption(
            f"{entry['closeness_label']} ({entry['closeness_pct']}% close)"
        )
        st.progress(entry["closeness_pct"] / 100)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_history = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.session_state.guess_history.append(
            {
                "attempt": st.session_state.attempts,
                "guess": raw_guess,
                "valid": False,
                "error": err,
            }
        )
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        secret = st.session_state.secret

        outcome = check_guess(guess_int, secret)
        closeness_label, closeness_pct = get_guess_closeness(
            guess_int,
            secret,
            low,
            high,
        )

        st.session_state.guess_history.append(
            {
                "attempt": st.session_state.attempts,
                "guess": guess_int,
                "valid": True,
                "outcome": outcome,
                "distance": abs(guess_int - secret),
                "closeness_label": closeness_label,
                "closeness_pct": closeness_pct,
            }
        )

        # FIX: Flipped "Too High" and "Too Low" messages to match correct logic. 
        message_map = {
            "Win": "🎉 Correct!",
            "Too High": "📉 Go LOWER!",
            "Too Low": "📈 Go HIGHER!",
        }
        message = message_map.get(outcome)

        if show_hint and message:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
