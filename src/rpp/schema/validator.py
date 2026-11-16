from rpp.schema import request_schemas
from rpp.schema.schema_scope import SchemaNotBuilt, SchemaScope  # noqa: F401 - SchemaNotBuilt is re-exported


def validate_schema(schema_name, data, extensions: tuple[str, ...] = ()):
    """Validates `data` against a definition for the given extensions, without any profile: the preset schema, a 400 where
    it fails. Under a request of an app the validators are those the app built for its presets; without an app (the mappers'
    own tests) they are built on first use."""
    current = request_schemas.current()
    scope = current.for_extensions(extensions) if current else SchemaScope.of(extensions)
    scope.validate(schema_name, data)


def validate_request_schema(schema_name, data, extensions: tuple[str, ...] = (), patched: bool = False,
                            member: str | None = None):
    """The two steps of json §Profiles and Validation, for what a client sent: the preset schema (400), then the applicable
    profiles of the preset of the request (`ProfileConstraintViolation`, 422). `patched`: `data` is the object a patch or a
    replacement results in. `member`: only what concerns this member of `data` is checked against the profiles, for a patch
    that has no object to validate but the value of one member."""
    current = request_schemas.current()
    scope = current.request if current else SchemaScope.of(extensions)
    scope.validate_request(schema_name, data, patched, member)


def refuse_removal_by_profile(schema_name, member, extensions: tuple[str, ...] = ()):
    """A removal of a member that an applicable profile of the request requires is a broken constraint of that profile."""
    current = request_schemas.current()
    scope = current.request if current else SchemaScope.of(extensions)
    scope.refuse_removal(schema_name, member)
