import json
import os
import urllib.error
import urllib.request


def infer_bounds_from_history(low: int, high: int, guess_history: list):
    """Infer the remaining valid range from prior guess feedback."""
    inferred_low = low
    inferred_high = high

    for entry in guess_history:
        if not entry.get("valid"):
            continue

        guess = int(entry.get("guess"))
        outcome = entry.get("outcome")

        if outcome == "Too High":
            inferred_high = min(inferred_high, guess - 1)
        elif outcome == "Too Low":
            inferred_low = max(inferred_low, guess + 1)
        elif outcome == "Win":
            inferred_low = guess
            inferred_high = guess

    return inferred_low, inferred_high


def recommend_next_guess(inferred_low: int, inferred_high: int, low: int, high: int):
    """Recommend the next guess using a binary-search style strategy."""
    if inferred_low > inferred_high:
        return (low + high) // 2

    return (inferred_low + inferred_high) // 2


def build_coach_context(
    *,
    difficulty: str,
    low: int,
    high: int,
    attempt_limit: int,
    attempts: int,
    score: int,
    status: str,
    history: list,
    guess_history: list,
):
    """Build the visible game state used by the coach."""
    inferred_low, inferred_high = infer_bounds_from_history(low, high, guess_history)
    attempts_left = max(attempt_limit - attempts, 0)
    recommended_guess = recommend_next_guess(inferred_low, inferred_high, low, high)

    recent_valid_guesses = [
        {
            "attempt": entry.get("attempt"),
            "guess": entry.get("guess"),
            "outcome": entry.get("outcome"),
            "closeness_label": entry.get("closeness_label"),
            "closeness_pct": entry.get("closeness_pct"),
        }
        for entry in guess_history
        if entry.get("valid")
    ]

    return {
        "difficulty": difficulty,
        "range_low": low,
        "range_high": high,
        "attempt_limit": attempt_limit,
        "attempts": attempts,
        "attempts_left": attempts_left,
        "score": score,
        "status": status,
        "history": history,
        "recent_valid_guesses": recent_valid_guesses[-5:],
        "inferred_low": inferred_low,
        "inferred_high": inferred_high,
        "recommended_guess": recommended_guess,
    }


def format_coach_prompt(context: dict):
    """Create a prompt for the AI coach using only visible state."""
    return (
        "You are an in-app coach for a number guessing game. "
        "Use only the visible state provided below. Do not mention or infer any secret number. "
        "Give concise advice that helps the player choose the next guess. "
        "Return strict JSON with keys: title, suggestion, explanation, recommended_guess.\n\n"
        f"Visible state:\n{json.dumps(context, indent=2)}"
    )


def heuristic_coach(context: dict):
    """Local fallback advice when an LLM call is unavailable."""
    attempts_left = context["attempts_left"]
    inferred_low = context["inferred_low"]
    inferred_high = context["inferred_high"]
    recommended_guess = context["recommended_guess"]

    if context["status"] == "won":
        return {
            "mode": "heuristic",
            "title": "Round already solved",
            "suggestion": "You already won this round.",
            "explanation": "Start a new game to use the coach on another puzzle.",
            "recommended_guess": recommended_guess,
        }

    if attempts_left == 0:
        return {
            "mode": "heuristic",
            "title": "No attempts left",
            "suggestion": "The round is over, so there is no next guess.",
            "explanation": "Start a new game and try a midpoint-first strategy next time.",
            "recommended_guess": recommended_guess,
        }

    if inferred_low > inferred_high:
        return {
            "mode": "heuristic",
            "title": "Feedback looks inconsistent",
            "suggestion": "Review the recent hints and restart if the range no longer makes sense.",
            "explanation": "The current hints do not leave a valid remaining interval, so the prior inputs may be inconsistent.",
            "recommended_guess": recommended_guess,
        }

    if attempts_left <= 2:
        urgency = "You are close to the limit, so use the midpoint of the remaining range."
    else:
        urgency = "Use a binary-search style split to reduce the range quickly."

    range_text = f"{inferred_low}-{inferred_high}" if inferred_low <= inferred_high else f"{context['range_low']}-{context['range_high']}"

    return {
        "mode": "heuristic",
        "title": f"Coach recommends {recommended_guess}",
        "suggestion": f"Try {recommended_guess} next.",
        "explanation": (
            f"The visible hints narrow the range to {range_text}. {urgency} "
            f"You have {attempts_left} attempts left and the active difficulty is {context['difficulty']}."
        ),
        "recommended_guess": recommended_guess,
    }


def _parse_model_response(response_text: str, fallback: dict):
    """Parse the model response into the coach response schema."""
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return fallback

    return {
        "mode": "ai",
        "title": str(parsed.get("title") or fallback["title"]),
        "suggestion": str(parsed.get("suggestion") or fallback["suggestion"]),
        "explanation": str(parsed.get("explanation") or fallback["explanation"]),
        "recommended_guess": parsed.get("recommended_guess", fallback["recommended_guess"]),
    }


def _call_openai(prompt: str, model: str, api_key: str, base_url: str, timeout: int = 20):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a concise coach that only uses the provided game state. Return strict JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"]


def generate_coach_advice(context: dict):
    """Generate advice using an LLM when configured, otherwise use the heuristic fallback."""
    fallback = heuristic_coach(context)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return fallback

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
    prompt = format_coach_prompt(context)

    try:
        response_text = _call_openai(prompt, model, api_key, base_url)
    except (urllib.error.URLError, KeyError, TimeoutError, ValueError, json.JSONDecodeError):
        return {
            **fallback,
            "mode": "heuristic",
            "title": f"{fallback['title']} (fallback)",
            "explanation": fallback["explanation"] + " The AI request could not be completed, so a local fallback was used.",
        }

    return _parse_model_response(response_text, fallback)