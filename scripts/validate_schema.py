import yaml
from cerberus import Validator

schema = {
    '@type': {'type': 'string', 'required': True, 'allowed': ['AGENT', 'SERVICE']},
    'name': {'type': 'string', 'required': True},
    'subtype': {'type': 'string', 'required': False},
    'organisation': {'type': 'string', 'required': False},
    'projects': {'type': 'list', 'schema': {'type': 'string'}},
    'tags': {'type': 'list', 'schema': {'type': 'string'}},
    'region': {'type': 'string', 'required': False},
    'description': {'type': 'string', 'required': False},
}

def validate_yaml_file(filepath):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    v = Validator(schema)
    if not v.validate(data):
        print(f"{filepath} has validation errors:")
        print(v.errors)
    else:
        print(f"{filepath} is valid.")

if __name__ == "__main__":
    import os
    for root, _, files in os.walk("data"):
        for file in files:
            if file.endswith(".yaml"):
                validate_yaml_file(os.path.join(root, file))
