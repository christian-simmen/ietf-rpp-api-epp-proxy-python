"""Every example of docs/rri/rri-extension.md that names a definition is checked against the Effective Schema of a
deployment that offers the extension, as guidelines §9 requires of an extension specification."""
import json
import re
from pathlib import Path

import pytest
from jsonschema import ValidationError

from rpp.schema.validator import validate_schema
from tests.helper.profiles import RRI_PROFILE

DOC = Path(__file__).parents[2] / "docs" / "rri" / "rri-extension.md"

EXAMPLE = re.compile(r"```json (valid|invalid) ([\w.]+)\n(.*?)```", re.DOTALL)

EXAMPLES = [pytest.param(kind, schema, json.loads(body), id=f"{n}-{kind}-{schema}")
            for n, (kind, schema, body) in enumerate(EXAMPLE.findall(DOC.read_text(encoding="utf-8")), start=1)]


def test_the_document_has_valid_and_invalid_examples():
    kinds = {param.values[0] for param in EXAMPLES}

    assert kinds == {"valid", "invalid"}


@pytest.mark.parametrize("kind, schema, example", EXAMPLES)
def test_an_example_validates_as_it_says(kind, schema, example):
    if kind == "valid":
        validate_schema(schema, example, extensions=RRI_PROFILE.extensions)
    else:
        with pytest.raises(ValidationError):
            validate_schema(schema, example, extensions=RRI_PROFILE.extensions)
