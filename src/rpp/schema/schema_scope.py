import re

import jsonschema
from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from rpp.schema.effective_schema import UNEVALUATED, bundle_definitions, compose
from rpp.schema.extensions import EXTENSIONS, own_definitions
from rpp.schema.profile_constraint_violation import ProfileConstraintViolation

_UNEXPECTED = re.compile(r"\((.*) (?:was|were) unexpected\)")


def _path(error) -> str:
    return "$" + "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path)


def _build(definitions: dict, names) -> dict[str, Draft202012Validator]:
    """The validator of each definition `names` stand for; an extension's own object (`requestContact.create`) is
    validated by the name a base object's would have."""
    own = own_definitions()
    validators = {}
    for name in names:
        target = name if name in definitions else own.get(name)
        if target in definitions:
            validators[name] = Draft202012Validator({"$ref": f"#/$defs/{target}", "$defs": definitions})
    return validators


class SchemaScope:
    """What a request under one preset validates with (D18: per preset, not process-global): the validators of every
    definition for the extensions of the preset, without its applicable profiles and with them, and one per profile, to name
    the one a failure belongs to. They are built when the app is built and a request only looks them up.

    `validate` is the validation of the preset without profiles: a failure is a request that does not conform to the preset
    (400). `validate_request` is the two steps of json §Profiles and Validation: a failure of the second step only is a
    `ProfileConstraintViolation`. A scope without an app (the mappers' own tests) is `SchemaScope.of`.
    """

    def __init__(self, extensions, profiles=()):
        self.extensions = tuple(extension.id for extension in extensions)
        self._profiles = tuple(profile for profile in profiles if profile.schema is not None)
        names = {*bundle_definitions(), *own_definitions(self.extensions)}
        self._plain = _build(compose(extensions, (), True), names)
        if not self._profiles:
            self._full = self._plain
            self._single = {}
        else:
            self._full = _build(compose(extensions, self._profiles, True), names)
            self._single = {} if len(self._profiles) == 1 else {
                profile.id: _build(compose(extensions, (profile,), True), names) for profile in self._profiles}
        self.profile_ids = tuple(profile.id for profile in self._profiles)

    _of: dict[tuple[str, ...], "SchemaScope"] = {}

    @classmethod
    def of(cls, extension_ids=()) -> "SchemaScope":
        """The scope of some extensions and no profile, built on first use: for what maps without an app. The app never
        does that, it passes the scope of the preset (a defect where it does not: `SchemaNotBuilt`)."""
        key = tuple(extension_ids)
        if key not in cls._of:
            scope = cls([EXTENSIONS[ext] for ext in key])
            everything = tuple(EXTENSIONS)
            # what maps without an app finds the object of an extension the scope was not given in the scope of all of them
            scope._fallback = cls.of(everything) if key != everything else None
            cls._of[key] = scope
        return cls._of[key]

    _fallback: "SchemaScope | None" = None

    def _lookup(self, validators: dict, name: str):
        validator = validators.get(name)
        if validator is None and self._fallback is not None:
            validator = self._fallback._plain.get(name)
        if validator is None:
            raise SchemaNotBuilt(f"No schema {name} was built for the extensions {', '.join(self.extensions) or '(none)'}")
        return validator

    def validate(self, name: str, data) -> None:
        """Validates `data` against a definition of the preset without profiles. A member no schema declares is refused as an
        undeclared property (json §4.9.1), the same `ValueError` the dataclasses' check raises."""
        try:
            self._lookup(self._plain, name).validate(data)
        except jsonschema.ValidationError as error:
            if error.validator == UNEVALUATED:
                names = _UNEXPECTED.search(error.message)
                raise ValueError(f"Undeclared property: {names.group(1) if names else error.message}") from None
            raise

    def validate_request(self, name: str, data, patched: bool = False) -> None:
        """The two steps. `patched`: `data` is an object a client's patch or replacement results in, whose read-only members
        the server manages: a failure that concerns one of them is not the client's."""
        self.validate(name, data)
        if self._full is self._plain:
            return
        errors = list(self._lookup(self._full, name).iter_errors(data))
        if patched:
            server_managed = self._read_only(name)
            errors = [error for error in errors if not (error.absolute_path and error.absolute_path[0] in server_managed)]
        if not errors:
            return
        profile = self._attribute(name, data, patched)
        error = best_match(errors)
        raise ProfileConstraintViolation(profile, _path(error), _reason(error, profile))

    def _attribute(self, name: str, data, patched: bool) -> str | None:
        if len(self._profiles) == 1:
            return self._profiles[0].id
        for profile in self._profiles:
            if any(self._lookup(self._single[profile.id], name).iter_errors(data)):
                return profile.id
        return None

    @staticmethod
    def _read_only(name: str) -> frozenset:
        schema = bundle_definitions().get(name, {})
        return frozenset(member for member, sub in schema.get("properties", {}).items() if sub.get("readOnly"))


def _reason(error, profile) -> str:
    of = f" of the profile {profile}" if profile else " of a profile"
    if error.validator == "required":
        return f"{error.message}, which a constraint{of} requires"
    return f"The value breaks the constraint '{error.validator}'{of}"


class SchemaNotBuilt(LookupError):
    """A request asked for a validator that no preset of the app has: a defect, not a refusal of the request."""
