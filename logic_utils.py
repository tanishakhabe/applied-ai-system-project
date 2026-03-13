def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    # FIX: Updated Normal difficulty range to 1-50 and Hard difficulty range to 1-100 to provide a more appropriate challenge level for each setting. This change enhances the gameplay experience by making Normal more accessible and Hard more challenging.
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100

    # FIX: Added error handling for unknown difficulty levels to prevent silent failures and provide clearer feedback during development and testing.
    raise ValueError(f"Unknown difficulty level: {difficulty}")


def parse_guess(raw: str, min_val: int = None, max_val: int = None):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    # FIX: Added validation to reject decimal numbers, ensuring that only whole number guesses are accepted. This prevents confusion and maintains the integrity of the guessing game, which is designed around integer values.
    if "." in raw:
        return False, None, "Only whole numbers are allowed."

    try:
        value = int(raw)
    except Exception:
        return False, None, "That is not a number."
    
    # FIX: Add range validation to parse_guess to ensure guesses outside the difficulty range are rejected with an appropriate error message. This centralizes all input validation logic in one function, making it easier to maintain and test.
    if min_val is not None and max_val is not None:
        if value < min_val or value > max_val:
            return False, None, f"Guess must be between {min_val} and {max_val}."
    
    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome string.

    outcome examples: "Win", "Too High", "Too Low"
    """
    # Normalize input types because app.py may pass secret as a string.
    guess_val = int(guess)
    secret_val = int(secret)

    if guess_val == secret_val:
        return "Win"
    
    # FIX: Flipped "Too High" and "Too Low" logic to match correct behavior. If guess is greater than secret, it should be "Too High", and if it's less, it should be "Too Low".
    if guess_val > secret_val:
        return "Too High"
    else:
        return "Too Low"


def get_guess_closeness(guess: int, secret: int, low: int, high: int):
    """Return a closeness label and percentage score for a guess.

    The percentage is normalized to the active range so it stays meaningful
    across difficulties.
    """
    span = max(high - low, 1)
    distance = abs(int(guess) - int(secret))
    ratio = distance / span
    closeness_pct = max(0, round((1 - ratio) * 100))

    if distance == 0:
        label = "Exact"
    elif ratio <= 0.05:
        label = "Very Hot"
    elif ratio <= 0.15:
        label = "Warm"
    elif ratio <= 0.30:
        label = "Cool"
    else:
        label = "Cold"

    return label, closeness_pct


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")
