from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True, kw_only=True)
class RegisteredExtension:
    """Everything one extension adds to the pipeline, as its `register` states it. The registry holds it as data: it
    imports nothing of the proxy, and the code that reads it (the app, a backend) knows what each part is.

    - `id`: the extension id of its RPP schema.
    - `schema`: the parsed RPP extension schema (guidelines §8).
    - `data_objects`: the top-level data elements of each object it defines, with their Visibility
      (`{object: {element: visibility}}`), which `includeElements` reads.
    - `objects`: the identifiers of the objects it defines.
    - `openapi`: a function that builds its OpenAPI fragment (`{"paths": ..., "components": {"schemas": ...}}`).
      Every operationId of it is a fully qualified function name in `handlers`.
    - `handlers`: the package of its handler modules.
    - `backend_parts`: the module of its part in each backend that can hold it (`{"sqlite": "registry_adapter..."}`).
    - `profile_layer`: the leaves it adds to the backend profile, with `objects` and `extensions` to add to those the
      generic profile lists; `profile_leaves` the type of each leaf of it that the profile does not have.
    - `presets`: the presets it brings (`{key: definition}`, as a preset file of `rpp/schema/schemas/presets` states it).
    - `profiles`: the profiles it brings (`{key: definition}`, as a profile file states it, with its Profile Schema, if
      any, as `schema`).
    """
    id: str
    schema: dict
    data_objects: dict[str, dict[str, str]]
    objects: tuple[str, ...]
    openapi: Callable[[], dict]
    handlers: str
    backend_parts: dict[str, str] = field(default_factory=dict)
    profile_layer: dict[str, Any] = field(default_factory=dict)
    profile_leaves: dict[str, type] = field(default_factory=dict)
    presets: dict[str, dict] = field(default_factory=dict)
    profiles: dict[str, dict] = field(default_factory=dict)
