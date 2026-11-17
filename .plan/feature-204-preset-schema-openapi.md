# Plan: #204 the default preset's schema in the OpenAPI document (Story 5 of #174)

Branch `feature/204-preset-schema-openapi`, stacked on `feature/180-demo-configurations` (PR #201). The PR targets that branch and
is retargeted to `main` once #201 is merged. Clean-main step skipped (maintainer: the local changes to `.vscode/settings.json`,
`deploy/ansible/ansible.cfg` and the untracked `config.rri-mtest.yaml.local` are carried, never committed).

## Findings (evidence)

- F1 Connexion 3.2.0 (ours) and 3.3.0 (latest) load no OpenAPI 3.1: `Specification.load` of `openapi: 3.1.0` raises
  `'3.1.0' does not match '^3\.0\.\d(-.+)?$'` (only `resources/schemas/v2.0`, `v3.0` ship). Its body validators are Draft 4.
- F2 `swagger_ui_bundle==1.1.0` (latest on PyPI) ships Swagger UI 4.15.5, which renders no 3.1 (5.x does).
- F3 A schema fixed in the routing spec would refuse a request (and fail the response) under another preset with members of
  its extensions: validation must follow the signalled preset.
- F4 Profile constraints in a body validator would answer 400 instead of 422 `02308`, and a PUT/PATCH is checked as the object
  it results in (`patched=True`), which a body-level check cannot do.
- F5 Connexion's `resolve_refs` keeps the siblings of a `$ref` (`node.update(retrieved)`), and the 3.0 Reference Object allows
  them: a marker next to the `$ref` reaches the validator. The response validator gets the ASGI scope; the request validator gets
  it in `wrap_receive`.
- F6 Body schema names: `gen.<def>` (drafts), `ext.<def>` (extension paths, planets fragment). The validator name is the name
  without the prefix, as the mappers use it (`SchemaScope.validate`); the Preset Schema key of an extension's own object is
  `own_definitions()[name]`. `protocol.PartialUpdate` (JSON Patch) has no definition in a Preset Schema.
- F7 400 from a body validator and from `map_request` render the same result code (`_default_result(400)`, 02001).
- F8 Default presets: epp-docker `epp-compatible` (EPP Compatibility Profile), demo bare `planets`, extended and inherit
  `planets-complete`, bound `planets` with the bound profile rocky-planets.

## Decisions (maintainer, 2026-11-17)

- D1 Two documents. Connexion routes from the 3.0 spec; the document served at `/openapi.json`, `/openapi.yaml` and `/ui/` is
  OpenAPI 3.1, built when the app is built from the routing spec, with the default preset's Preset Schema (profiles included).
- D2 Connexion's body validators (`validator_map`, ours) validate a body with the schemas of the request's preset (2020-12,
  without profiles: a failure is 400 as today); responses with the response preset's. The profile step (422 `02308`) stays in the
  mappers. A body without a definition in the Preset Schema (`protocol.PartialUpdate`) keeps Connexion's validation.
- D3 Swagger UI 5 committed to the repository (`swagger-ui-dist`), Connexion's `swagger_ui_template_dir` pointing at it.
- D4 Dev dependency `openapi-spec-validator` to test that the served document is valid OpenAPI 3.1 (my choice, see open questions).

## Design

- `rpp/http/body_definitions.py`: marks each body schema of the routing spec (request, response, array items) whose name has a
  definition with `x-rpp-definition: <validator name>`.
- `RppRequestBodyValidator`, `RppResponseBodyValidator`: with a marker, validate with the request / response scope of the
  request (`SchemaScope.validate`), else as today. The scopes come from the request context, which `PresetMiddleware` fills
  (`RequestSchemas`, the one place they are made; `context.request_schemas()` reads it).
- `rpp/http/served_document.py`: the 3.1 document: `openapi: 3.1.0`, the Preset Schema's `$defs` under `components/schemas`
  (references rewritten), each marked body pointing at its definition, the body schemas no longer referenced left out, and
  `info` naming the preset. A name the document already has with other content is a startup error.
- `rpp/http/served_specification.py`: a Connexion `OpenAPISpecification` for a document that is only served (no 3.0 check, no
  reference resolution). `SpecSnapshotSwaggerUIMiddleware` becomes the middleware that serves that document (given per app).

## Tasks

- [x] T0 Plan
- [~] T1 Tests first (unit): served document (base, extension, profile, defaults per demo config, valid 3.1), validation by
  the signalled preset, 400 / 422 unchanged, Swagger UI 5 served
- [ ] T2 Body markers and validators by preset
- [ ] T3 Served document and its middleware
- [ ] T4 Swagger UI 5 vendored
- [ ] T5 Docs: architecture.project.md, README.md, spec-issues.md (OpenAPI of a deployment)
- [ ] T6 Checks: lint-imports, unit, smoke (MTEST pending for the maintainer: `rpp` changes)

## Open questions

- Q1 D4: a dev dependency `openapi-spec-validator` for the 3.1 check, or the OAS 3.1 meta-schema committed under `tests/`?
