from messy_project.main import main


def test_main_returns_greeting():
    result = main("config/app.yaml")
    assert result == "Hello, World!"
