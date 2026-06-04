from .helpers import greet
from .old_utils import load_config


def main(config_path="config/app.yaml"):
    cfg = load_config(config_path)
    return greet(cfg.get("name", "world"))


if __name__ == "__main__":
    print(main())
