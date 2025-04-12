import json

import yaml



def read_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

