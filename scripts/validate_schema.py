import os
import yaml
from cerberus import Validator

# Define controlled subtype lists
VALID_ORG_SUBTYPES = {
    "Local Authority",
    "Government Department",
    "Research Partnership",
    "University",
    "Charity",
    "Consultancy",
    "Inspection Body",
    "Health Organisation",
    "Police Force",
    "Voluntary Sector",
    "Technology Provider",
    "Funder"
}

VALID_PERSON_SUBTYPES = {
    "DCS",
    "Consultant",
    "Practitioner",
    "Academic",
    "Analyst",
    "Service Lead",
    "Policy Advisor",
    "Director",
    "Programme Manager",
    "Data Specialist",
    "Commissioner",
    "Inspector"
}

# Base schema (used by cerberus, not SCCM strict)
schema = {
    '@type': {'type': 'string', 'required': True, 'allowed': ['AGENT', 'SERVICE', 'PERSON', 'ORGANIZATION']},
    'name': {'type': 'string', 'required': True},
    'subtype': {'type': 'string', 'required': False},
    'organisation': {'type': 'string', 'required': False},
    'projects': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'tags': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'region': {'type': 'string', 'required': False},
    'description': {'type': 'string', 'required': False},
    'notes': {'type': 'string', 'required': False},
    'role': {'type': 'string', 'required': False},
}

def validate_yaml_file(filepath):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)

    v = Validator(schema)
    if not v.validate(data):
        print(f"{filepath} has schema validation errors:")
        print(v.errors)
        return

    # SCCM-aligned subtype check
    entry_type = data.get('@type')
    subtype = data.get('subtype')

    if entry_type == "ORGANIZATION":
        if not subtype:
            print(f"{filepath}: Missing required 'subtype' for ORGANIZATION")
        elif subtype not in VALID_ORG_SUBTYPES:
            print(f"{filepath}: Invalid ORGANIZATION subtype '{subtype}'. Must be one of: {sorted(VALID_ORG_SUBTYPES)}")

    if entry_type == "PERSON":
        if not subtype:
            print(f"{filepath}: Missing recommended 'subtype' for PERSON")
        elif subtype not in VALID_PERSON_SUBTYPES:
            print(f"{filepath}: Invalid PERSON subtype '{subtype}'. Must be one of: {sorted(VALID_PERSON_SUBTYPES)}")

    else:
        print(f"{filepath} is valid")

if __name__ == "__main__":
    for root, _, files in os.walk("data"):
        for file in files:
            if file.endswith(".yaml"):
                validate_yaml_file(os.path.join(root, file))
