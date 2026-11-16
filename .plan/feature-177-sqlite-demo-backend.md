# Plan: SQLite demo backend with Planet and Satellite (#177)

Branch `feature/177-sqlite-demo-backend` from `main` (`f4f8ddc`). The requirements and acceptance criteria are in #177.
Part of #174, Story 1 of 4. Built on today's profile model. #178 moves it to presets.

## Tasks

- [~] T0 Plan (this file), for approval
- [ ] T1 Extension `org.example.rpp.extension.planets` 1.0: schema `.spec/planets-extension.schema.json` (copied by
      `copy_models.sh`), objects `planet` and `satellite`, and the specification `docs/demo/planets-extension.md` in
      the extension format of the guidelines, with examples checked by a unit test (as `test_rri_extension_doc.py`)
- [ ] T2 Core: `core/model/planet/` (Planet, Satellite, transfer state), `core/ports/planet_gateway.py` and
      `satellite_gateway.py`, `core/flows/planet/` (create, read, update, partial update, delete, transfer request,
      query, cancel, approve, reject, satellites of a planet), a planet transfer event in `core/model/message/`,
      `planets` and `satellites` on `RegistryBackend`
- [ ] T3 Adapter `registry_adapter/sqlite/`: SQLAlchemy 2.x models (planet, satellite, transfer, message, client),
      tables created at start, the gateways, the message queue, `SqliteBackend` (one user's session, credentials
      checked against the configured clients), sponsor checks
- [ ] T4 Settings: `rpp_backend: sqlite`, `rpp_sqlite_url`, `rpp_sqlite_clients` (user to password hash, `hashlib.scrypt`
      in a self-describing string), the generic backend profile `src/settings/profiles/sqlite.yaml` (objects `planet`,
      `satellite`, extension planets, profile `demo`), the RPP profile `src/rpp/schema/schemas/profiles/demo.yaml`,
      `config.demo.yaml`; the EPP and RRI profiles do not hold the objects
- [ ] T5 RPP: paths of the objects (`extension_paths.py`: `planet` from the template `domainName` with its transfer
      process, `satellite` from `host` without processes, and the Direct Access path `/planets/{id}/satellites`), DTOs,
      mappers, handlers, the message rendering of a planet transfer
- [ ] T6 Integration environment `sqlite-demo` (`config.demo.yaml`, an in-memory or temporary database, no
      credentials) and test cases `planet_*`, `satellite_*` and `planet_transfer`, the smoke ones marked
- [ ] T7 Import contracts in `pyproject.toml` for `core.model.planet` and `registry_adapter.sqlite`; `sqlalchemy` in
      `requirements.txt`
- [ ] T8 Docs: `overview.project.md` (third backend), `architecture.project.md` (the adapter, the extension objects),
      `testing.project.md` (the environment), `README.md`
- [ ] T9 Checks: `lint-imports`, unit, smoke (`epp-docker` and `sqlite-demo`). MTEST pending for the maintainer.

## Findings (evidence)

1. `rpp/http/extension_paths.py` makes the paths of an extension's objects from a base object's (`TEMPLATES`), today
   `requestContact` from `contact`. The domain name has the transfer paths (`/domainNames/{name}/processes/
   transferProcesses...`), the host has create, read, update and delete.
2. `ProfileMiddleware` answers 501 `02307` for a path of an object the profile has not or the backend does not hold,
   so the domain, contact and host paths need nothing new on the demo backend.
3. `core.model` object packages are independent (`pyproject.toml`, contract `core-model-objects`), so the planet
   package gets its own entry.
4. Authentication today passes the Basic credentials to the backend session (`RegistryBackend.verify_credentials`).

## Decisions

- D1 (maintainer) Planet and Satellite are defined by the demo extension, not built into the backend.
- D2 (maintainer) Satellite is top level, with a reference to its planet. A planet's satellites are a Direct Access
  data element.
- D3 (maintainer) Basic auth against configured clients. The user is the sponsoring client.
- D4 (maintainer) Planet transfer EPP style, no automatic approval. The satellites move with their planet.
- D5 (maintainer) Transfer events queue messages for the other client.

## Corrections

## Open questions

- Availability (`/planets/{id}/availability`) is not in #177. Left out unless the maintainer wants it.
- `.vscode/settings.json` and `config.rri-mtest.yaml.local` are the maintainer's local changes and stay unstaged.
