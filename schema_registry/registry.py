import json
import os
from typing import Dict

import jsonschema


def validate_message(message: Dict, schema_name: str, version: int) -> bool:
    schema_path = os.path.join("schemas", schema_name, f"{version}.json")
    with open(schema_path) as f:
        schema = json.load(f)

    try:
        jsonschema.validate(message, schema)
    except jsonschema.ValidationError:
        return False

    return True
