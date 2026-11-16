# Plan: SQLite demo backend with Planet and Satellite (#177)

Branch `feature/177-sqlite-demo-backend` from `main` (`f4f8ddc`). The requirements and acceptance criteria are in #177.
Part of #174, Story 1 of 4. Built on today's profile model. #178 moves it to presets.

**Status: frozen by the maintainer (2026-11-16) after T1.** No further code until the maintainer resumes it. The core
work of T2 started before the freeze is not committed: it is in `git stash` ("177 T2 core work in progress
(frozen)"), to be reviewed against this plan, or dropped, when development resumes.

## Tasks

- [x] T0 Plan (this file), approved
- [x] T1 (`06360f6`) Extension `org.example.rpp.extension.planets` 1.0: schema `.spec/planets-extension.schema.json` (copied by
      `copy_models.sh` to `src/rpp/extensions/planets/schema/`), objects `planet` and `satellite`, and the specification `docs/demo/planets-extension.md` in
      the extension format of the guidelines, with examples checked by a unit test (as `test_rri_extension_doc.py`)
- [~] T2 (frozen, in the stash) Core: `core/model/planet/` (Planet, Satellite, replacements, transfer),
      `core/ports/planet_gateway.py` and `satellite_gateway.py`, `core/flows/planet/` (create and replace with read
      back, the satellite of a planet at its Direct Access path), `planets` and `satellites` on `RegistryBackend`. A
      planet transfer reuses the generic transfer process of the core (`ContactTransferProcess`, rendered as
      `transferProcess.read`) and `TransferEvent` of the messages with the object type `planet`
- [ ] T3 Adapter `registry_adapter/sqlite/`: SQLAlchemy 2.x models (planet, satellite, transfer, message, client),
      tables created at start, the gateways, the message queue, `SqliteBackend` (one user's session, credentials
      checked against the configured clients), sponsor checks
- [ ] T4 Settings: `rpp_backend: sqlite`, `rpp_sqlite_url`, `rpp_sqlite_clients` (user to password hash, `hashlib.scrypt`
      in a self-describing string), the generic backend profile `src/settings/profiles/sqlite.yaml` (objects `planet`,
      `satellite`, extension planets, profile `demo`), the RPP profile `src/rpp/schema/schemas/profiles/demo.yaml`,
      `config.demo.yaml`; the EPP and RRI profiles do not hold the objects
- [ ] T5 RPP, encapsulated in `src/rpp/extensions/planets/` (`dto`, `handlers`, `mapping`, `schema`):
      - paths (`extension_paths.py`): `planet` from the template `contact` (availability, create, read, update,
        delete and the generic transfer process, D9), `satellite` from `host` without processes, and the Direct Access
        path `/planets/{id}/satellites/{satelliteId}` (D8)
      - the Visibility of the data elements (`satellite` onDemand) from a data model of the extension next to its
        schema, which `rpp/schema/data_objects.py` loads besides the drafts'
      - the handlers resolvable by Connexion from the extension package
      - a partial update reads the object, applies the JSON Patch of json §5.2 to its update view, and replaces it
      - DTOs, mappers, handlers
- [ ] T6 Integration environment `sqlite-demo` (`config.demo.yaml`, an in-memory or temporary database, no
      credentials) and test cases `planet_*`, `satellite_*` and `planet_transfer`, the smoke ones marked
- [ ] T7 A start check that no definition of an extension has the name of a base definition or of another
      extension's, as unprefixed names (D10) could otherwise replace one in the combined schema
- [ ] T7b Import contracts in `pyproject.toml`: `core.model.planet` among the independent object packages,
      `registry_adapter.sqlite` among the independent protocols, the layers of each `rpp.extensions.<name>`
      (`handlers` over `mapping` over `dto | schema`), and the base `rpp` packages not importing `rpp.extensions`.
      `sqlalchemy` in `requirements.txt`
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
- D6 (maintainer) Planet and Satellite have the availability check (`/planets/{id}/availability`,
  `/satellites/{id}/availability`), as the domain name and the host.

- D7 (maintainer) The RPP code of an extension is encapsulated in `src/rpp/extensions/<name>/` with `dto`, `handlers`,
  `mapping` and `schema`. `<name>` is a Python package name (`planets` for `org.example.rpp.extension.planets`), as an
  identifier with dots cannot be one. `rpp/schema/extensions.py` loads the schemas of both places.
- D8 The Direct Access element of the satellites is `satellite` (cardinality 0+), as `transferProcess` of the
  Processes Object, so core Rule 3 gives `/planets/{id}/satellites/{satelliteId}`.
- D9 The transfer of a planet uses the base Transfer Process Object (`transferProcess.*`), as the contact's does. Its
  messages are the base Transfer Request and Transfer Outcome Messages with the object type `planet`.

- D10 (maintainer) An extension that defines new object types names their definitions as the base definitions are
  (`planet.create`, `planetType`), without the `ext.<name>.` prefix. The prefix stays for the sub-schemas an extension
  composes with a base definition (`rpp:extends`). `own_definitions` maps both forms.

## Corrections

- C1 The planets schema and specification of T1 used the prefix `ext.planets.`. Renamed after D10.

## Open questions

- Whether the RRI extension (`de.denic.rpp.rri`, request contacts) moves to `src/rpp/extensions/` too: not part of
  #177, a follow-up issue if the maintainer wants it.

- `.vscode/settings.json` and `config.rri-mtest.yaml.local` are the maintainer's local changes and stay unstaged.
