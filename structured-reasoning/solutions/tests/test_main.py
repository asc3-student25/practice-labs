import os

from messy_project.main import main

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config",
    "app.yaml",
)


def test_main_returns_greeting():
    assert main(CONFIG_PATH) == "Hello, World!"
