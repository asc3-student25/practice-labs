import os

from messy_project.helpers import greet
from messy_project.old_utils import load_config

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "app.yaml",
)


def main(config_path=DEFAULT_CONFIG_PATH):
    cfg = load_config(config_path)
    return greet(cfg.get("name", "world"))


if __name__ == "__main__":
    print(main())
