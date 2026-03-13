import pytest

from logic_utils import (
    check_guess,
    get_guess_closeness,
    get_range_for_difficulty,
    parse_guess,
)

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# FIX: Add tests for parse_guess to ensure it correctly handles out-of-range inputs based on two example difficulty settings. 
@pytest.mark.parametrize("difficulty", ["Easy", "Hard"])
def test_parse_guess_rejects_out_of_range_for_difficulty(difficulty):
    min_val, max_val = get_range_for_difficulty(difficulty)

    below_ok, below_value, below_error = parse_guess(str(min_val - 1), min_val, max_val)
    assert below_ok is False
    assert below_value is None
    assert below_error == f"Guess must be between {min_val} and {max_val}."

    above_ok, above_value, above_error = parse_guess(str(max_val + 1), min_val, max_val)
    assert above_ok is False
    assert above_value is None
    assert above_error == f"Guess must be between {min_val} and {max_val}."

# FIX: Add tests for parse_guess to ensure it correctly rejects decimal inputs, which are not valid guesses in the game. This test verifies that the function returns an appropriate error message when a decimal number is provided.
def test_parse_guess_rejects_decimal_input():
    ok, value, error = parse_guess("3.14", 1, 100)
    assert ok is False
    assert value is None
    assert error == "Only whole numbers are allowed." 


def test_get_guess_closeness_exact():
    label, pct = get_guess_closeness(25, 25, 1, 50)
    assert label == "Exact"
    assert pct == 100


def test_get_guess_closeness_far_guess_is_cold():
    label, pct = get_guess_closeness(1, 50, 1, 50)
    assert label == "Cold"
    assert pct < 10


def test_get_guess_closeness_near_guess_is_hot_or_warm():
    label, pct = get_guess_closeness(48, 50, 1, 50)
    assert label in {"Very Hot", "Warm"}
    assert pct > 90