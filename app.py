import random
import streamlit as st
from coach_utils import build_coach_context, generate_coach_advice
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


def render_coach_panel(coach_result: dict | None, guess_input_key: str):
    if not coach_result:
        st.caption("No coach advice yet. Analyze the current position to get a recommendation.")
        return

    mode_label = "AI response" if coach_result.get("mode") == "ai" else "Heuristic fallback"
    title_col, action_col = st.columns([3, 1])

    with title_col:
        st.markdown(f"**{coach_result['title']}**")
        st.caption(mode_label)

    with action_col:
        if coach_result.get("recommended_guess") is not None:
            if st.button("AI suggested guess", key=f"use_coach_guess_{guess_input_key}"):
                st.session_state[guess_input_key] = str(coach_result["recommended_guess"])
                st.rerun()

        if st.button("Clear", key=f"clear_coach_result_{guess_input_key}"):
            st.session_state.coach_result = None
            st.rerun()

    detail_col, guess_col = st.columns([2, 1])
    with detail_col:
        st.write(coach_result["suggestion"])
        st.caption(coach_result["explanation"])

    with guess_col:
        st.metric("Recommended guess", coach_result.get("recommended_guess", "-"))


def render_ui_styles():
    st.markdown(
        """
        <style>
        .app-shell {
            padding-top: 0.25rem;
        }
        .hero-card {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 1rem;
            background: linear-gradient(180deg, rgba(248, 249, 252, 0.98), rgba(255, 255, 255, 0.96));
            margin-bottom: 1rem;
        }
        .hero-kicker {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(49, 51, 63, 0.72);
            margin-bottom: 0.25rem;
        }
        .hero-title {
            font-size: 1.4rem;
            font-weight: 700;
            margin: 0;
        }
        .hero-subtitle {
            margin-top: 0.25rem;
            color: rgba(49, 51, 63, 0.8);
        }
        .section-card {
            padding: 1rem;
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 1rem;
            background: white;
            box-shadow: 0 8px 24px rgba(49, 51, 63, 0.04);
        }
        .coach-frame {
            min-height: 100%;
        }
        .coach-empty {
            color: rgba(49, 51, 63, 0.68);
            font-size: 0.95rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")
render_ui_styles()

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

if "coach_result" not in st.session_state:
    st.session_state.coach_result = None

# FIX: Ensure the secret number always matches the active difficulty range, and reset game state if it doesn't. This prevents issues when switching difficulties mid-game.
# Ensure the current secret always matches the active difficulty range.
if st.session_state.secret < low or st.session_state.secret > high:
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_history = []
    st.session_state.coach_result = None

st.subheader("Make a guess")

st.info(
    # FIX: Removed hardcoded range and attempt info, replaced with dynamic values based on difficulty 
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

guess_input_key = f"guess_input_{difficulty}"

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">Round overview</div>
        <div class="hero-title">Manual guessing stays front and center.</div>
        <div class="hero-subtitle">Use the input box to play normally, then open the coach if you want help.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Difficulty", difficulty)
metric_col2.metric("Attempts left", attempt_limit - st.session_state.attempts)
metric_col3.metric("Score", st.session_state.score)

guess_col, coach_col = st.columns([1.15, 0.95], gap="large")

with guess_col:
    st.markdown(
        """
        <div class="section-card">
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Make a guess")
    raw_guess = st.text_input(
        "Enter your guess",
        key=guess_input_key,
        placeholder=f"Type a number between {low} and {high}",
    )

    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        submit = st.button("Submit Guess 🚀", use_container_width=True)
    with action_col2:
        new_game = st.button("New Game 🔁", use_container_width=True)
    with action_col3:
        show_hint = st.checkbox("Show hint", value=True)

with coach_col:
    st.markdown(
        """
        <div class="section-card coach-frame">
            <div class="hero-kicker">AI Coach</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Ask for advice based on the current visible game state.")
    if st.button("Analyze current position 🤖", key="ask_ai_coach", use_container_width=True):
        coach_context = build_coach_context(
            difficulty=difficulty,
            low=low,
            high=high,
            attempt_limit=attempt_limit,
            attempts=st.session_state.attempts,
            score=st.session_state.score,
            status=st.session_state.status,
            history=st.session_state.history,
            guess_history=st.session_state.guess_history,
        )
        with st.spinner("Thinking..."):
            st.session_state.coach_result = generate_coach_advice(coach_context)

    render_coach_panel(st.session_state.coach_result, guess_input_key)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

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

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_history = []
    st.session_state.coach_result = None
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
