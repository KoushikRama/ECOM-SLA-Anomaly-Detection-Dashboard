import json
from pathlib import Path

def load_data_config():
    config_path = Path(__file__).parent / "data-config.json"

    with open(config_path, "r") as f:
        return json.load(f)