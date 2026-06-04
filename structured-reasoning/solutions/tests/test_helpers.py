from messy_project.helpers import format_output, greet


def test_greet_returns_hello():
    assert greet("World") == "Hello, World!"


def test_format_output_stringifies():
    assert format_output(42) == "42"
