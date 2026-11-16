# Plan: SQLite demo backend with Planet and Satellite (#177)

Branch `feature/177-sqlite-demo-backend` from `main` (`f4f8ddc`). The requirements and acceptance criteria are in #177.
Part of #174, Story 1 of 4. Built on today's profile model. #178 moves it to presets.

**Status: unfrozen by the maintainer (2026-11-16).** Resumed after T1; the plan below is reviewed against the code. The
stack of PRs is #177, then #178 on #177, #179 on #178 and #180 on #179, each targeting `main` (maintainer decision). The
registration of extensions (D11 to D14) is built so that #178 and #179 register more extensions, profiles and presets
through it.

The core work started before the freeze was in `git stash` ("177 T2 core work in progress (frozen)"). It predated D11 to
D14. Decision (coder, delegated by the maintainer): reuse the model, ports and flows files, moved into
`src/extensions/planets/core/` (S1); drop its change of `RegistryBackend` (the `planets` and `satellites` attributes,
which D11 and D13 exclude). The stash stays in place until T3 has taken its files, then it is dropped by the coder.

## Target layout (D12)

```text
src/extensions/planets/            the extension package, named in the configuration
  __init__.py                      register(registry): every element of the pipeline below
  core/                            model, ports (gateways), flows
  rpp/                             dto, handlers, mapping, schema (schema, data model, OpenAPI fragment)
src/registry_adapter/sqlite/       the SQLite backend
  (common)                         database file and connection, migrations, clients and authentication,
                                   base classes, the message queue, the session (RegistryBackend)
  extensions/planets/              the SQLAlchemy models and gateways of the planets extension
```

## Tasks

- [x] T0 Plan (this file), approved
- [x] T1 (`06360f6`, `5e080e0`) Extension `org.example.rpp.extension.planets` 1.0: schema
      `.spec/planets-extension.schema.json`, objects `planet` and `satellite`, and the specification
      `docs/demo/planets-extension.md` in the extension format of the guidelines, with examples checked by a unit test.
      To move: the schema copy from `src/rpp/extensions/planets/schema/` to `src/extensions/planets/rpp/schema/`, and
      its loading from the folder scan of `rpp/schema/extensions.py` to the registration (T2)
- [ ] T2 Registration (D11, D13), see "Design of the registration" below. The configuration key `rpp_extensions` lists the module paths of the extension
      packages (`extensions.planets`). `main` imports each and calls `register(registry)`. The registry collects every
      element of the pipeline, and the generic code reads only the registry:
      - the schema and the definitions (`rpp/schema/extensions.py` without the folder scan of the encapsulated ones)
      - the data model of the objects (Visibility, for `includeElements`)
      - the OpenAPI fragment of the paths (D14), merged into the document by `create_app`
      - the handlers of the operations of the fragment, resolvable by Connexion
      - the objects, for `ProfileMiddleware` and discovery
      - the gateways per backend, found by the extension id on the session (`RegistryBackend.extension(id)`), with
        no named attribute per extension
      - the SQLite part of the extension (`registry_adapter.sqlite.extensions.<name>`), loaded by the SQLite backend
        for each configured extension
      - the backend profile leaves of the extension (the transfer operations of a planet), merged into the generic
        profile of the backend
- [ ] T3 Core of the extension, `src/extensions/planets/core/` (the files of the stash, moved, S1): model (Planet, Satellite, replacements, transfer),
      ports (planet and satellite gateways), flows (create and replace with read back, the satellite of a planet at its
      Direct Access path). A planet transfer reuses the generic transfer process of the core (`ContactTransferProcess`,
      rendered as `transferProcess.read`) and `TransferEvent` of the messages with the object type `planet` (D9)
- [ ] T4 SQLite backend, `src/registry_adapter/sqlite/` (D12):
      - common: SQLAlchemy 2.x engine and file or memory database, migrations (each part's tables in its own
        metadata, created at start, with a schema version per part), clients and authentication, base classes of the
        models and gateways, the message queue (`MessageGateway`), `SqliteBackend` (one user's session, sponsor id)
      - `extensions/planets/`: the models (planet, satellite, transfer) and the gateways, with the sponsor checks, the
        pending transfer, the satellites that move with their planet, and the messages of a transfer
- [ ] T5 Settings: `rpp_backend: sqlite`, `rpp_sqlite_url`, `rpp_sqlite_clients` (user to password hash,
      `hashlib.scrypt` in a self-describing string), `rpp_extensions`, the generic backend profile
      `src/settings/profiles/sqlite.yaml` (no objects of its own), the RPP profile `demo`, `config.demo.yaml`
- [ ] T6 RPP of the extension, `src/extensions/planets/rpp/`: the OpenAPI fragment (availability, create, read, update
      and delete of both objects, the transfer of a planet, the Direct Access path
      `/planets/{id}/satellites/{satelliteId}`, D8), DTOs, mappers, handlers. A partial update reads the object, applies
      the JSON Patch of json §5.2 to its update view, and replaces it
- [ ] T7 Integration environment `sqlite-demo` (`config.demo.yaml`, a temporary database, no credentials) and test
      cases `planet_*`, `satellite_*` and `planet_transfer`, the smoke ones marked. A unit test that an app built
      without `rpp_extensions` has no planet path and no loaded module of `extensions`
- [ ] T8 Checks at start: no definition of an extension has the name of a base definition or of another extension's
      (D10); an extension named in the configuration loads and registers, or the app does not start
- [ ] T9 Import contracts in `pyproject.toml`: no generic package (`core`, `rpp`, `registry_adapter` outside
      `registry_adapter.sqlite.extensions`, `settings`) imports `extensions`; inside `extensions.<name>`, `rpp` over
      `core`, and the layers of `rpp` (`handlers` over `mapping` over `dto | schema`); `registry_adapter.sqlite.extensions`
      imports `extensions.<name>.core` only; `registry_adapter.sqlite` independent of `epp` and `rri`. `sqlalchemy` in
      `requirements.txt`
- [ ] T10 Docs: `overview.project.md` (third backend), `architecture.project.md` (the registration of extensions,
      the SQLite backend), `testing.project.md` (the environment), `README.md`
- [ ] T11 Checks: `lint-imports`, unit, smoke (`epp-docker` and `sqlite-demo`). MTEST pending for the maintainer.

## Design of the registration (T2)

- `src/registration/` (new generic package, pure Python, stdlib only): `ExtensionRegistry` and `load_extensions(paths)`.
  `main` builds one registry per app from `rpp_extensions`, imports each module and calls `register(registry)`. An
  extension module imports generic `core`, `rpp.schema` types and `registration`, never an adapter.
- What it holds, one entry per extension id: the RPP extension schema; the data model of its objects (Visibility); the
  OpenAPI fragment (paths and schemas); the package of its handlers; its object identifiers; the factory of its
  gateways (`session -> object`, by extension id); the name of its SQLite part; the backend profile leaves it adds.
- Per app and passed explicitly: the OpenAPI fragments (`create_app`), the handler resolver, the objects
  (`ProfileMiddleware`, discovery), the gateways (`RegistryBackend.extension(id)`), the profile leaves
  (`BackendProfile.from_layers` with the registered leaves), the SQLite part (`SqliteBackend`).
- Process-global and additive, as the schema machinery already is (`EXTENSIONS`, `own_definitions`, the validator
  cache `_effective`): the extension schema and the data model. They are keyed by extension id, so registering twice
  is idempotent, and a profile reaches a definition only through its `extensions`. `EXTENSIONS` keeps the built-in
  ones (the `schemas/extensions` folder) and gains `register_extension()`; the folder scan of `rpp/extensions/` is
  removed.
- The handlers of a fragment: operationIds are fully qualified module paths
  (`extensions.planets.rpp.handlers.planet_handlers.planets_create`), resolved by a resolver that takes the registered
  handler packages and otherwise falls back to the `RelativeResolver('rpp.handlers')`.
- `RegistryBackend` gains `extension(extension_id)`, which returns the gateways object of that extension (for planets,
  a `PlanetsGateways` with `planets` and `satellites`) or raises `KeyError`. EPP and RRI answer `KeyError` (they have
  no extension gateways). The flows of the extension take that object, not the backend.
- Backend profile leaves of the extension: `BackendProfile.from_layers` takes the registry's extra leaves next to
  `LEAVES`, so the closed list stays closed (an unregistered leaf is still an error).
- The SQLite backend has stub gateways for domain, contact, host and request contact (the `RegistryBackend`
  protocol still has them): each returns the not-supported error. `ProfileMiddleware` answers 501 `02307` first.
- #183 moves the RRI extension to the same mechanism; #178 and #179 add extensions, profiles and presets with it.

## Findings (evidence)

1. `rpp/http/extension_paths.py` makes the paths of an extension's objects from a base object's (`TEMPLATES`), today
   `requestContact` from `contact`. D14 replaces this for the planets extension by its own OpenAPI fragment.
2. `ProfileMiddleware` answers 501 `02307` for a path of an object the profile has not or the backend does not hold,
   so the domain, contact and host paths need nothing new on the demo backend.
3. The extension packages of the RPP code today are found by folder: `rpp/schema/extensions.py` loads every
   `schemas/extensions/*.json` and, since T1, every `rpp/extensions/*/schema/*.schema.json`. D11 replaces the scan for
   the encapsulated extensions.
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
- D7 (maintainer, superseded by D12) The RPP code of an extension in `src/rpp/extensions/<name>/`.
- D8 The Direct Access element of the satellites is `satellite` (cardinality 0+), as `transferProcess` of the
  Processes Object, so core Rule 3 gives `/planets/{id}/satellites/{satelliteId}`.
- D9 The transfer of a planet uses the base Transfer Process Object (`transferProcess.*`), as the contact's does. Its
  messages are the base Transfer Request and Transfer Outcome Messages with the object type `planet`.
- D10 (maintainer) An extension that defines new object types names their definitions as the base definitions are
  (`planet.create`, `planetType`), without the `ext.<name>.` prefix. The prefix stays for the sub-schemas an extension
  composes with a base definition (`rpp:extends`). `own_definitions` maps both forms.
- D11 (maintainer) The planets extension is registered by configuration: the environment configuration names the
  extensions to load, and each one registers its part of the pipeline. Without it in the configuration, the generic
  code does not know the extension exists: no import, no name, no path, no attribute of `RegistryBackend`.
- D12 (maintainer) An extension has its own tree `src/extensions/<name>/` with `core/` (model, ports, flows) and
  `rpp/` (dto, handlers, mapping, schema). The SQLite backend is in `src/registry_adapter/sqlite/`: a common part
  (database file and connection, migrations, clients and authentication, base classes) and `extensions/<name>/` with
  the model-specific part of each extension. `<name>` is a Python package name (`planets`).
- D13 (maintainer) Registration: `rpp_extensions` in the configuration lists the module paths, each module has
  `register(registry)`, and every element of the pipeline (schema, data model, paths, handlers, objects, gateways,
  the SQLite part, the backend profile leaves) is registered. The session offers the gateways of an extension by its
  id instead of named attributes.
- D14 (maintainer) An extension brings its own OpenAPI fragment of its paths.
- D15 (maintainer) Only the planets extension uses the mechanism in #177. The RRI extension moves to it in #183. The
  EPP and RRI backends stay as they are.

## Corrections

- C1 The planets schema and specification of T1 used the prefix `ext.planets.`. Renamed after D10.
- C2 The schema copy of T1 is in `src/rpp/extensions/planets/schema/` and found by a folder scan. Both change with
  D12 and D13 (T1, T2).

- D16 (maintainer, 2026-11-16) #177 is unfrozen. PRs are stacked, each targeting `main`: #178 on #177, #179 on #178,
  #180 on #179.
- D17 (coder, delegated) The stash is reused for model, ports and flows (S1), without its `RegistryBackend` change.

## Stash decision (S1)

Reused, moved to `src/extensions/planets/core/{model,ports,flows}/` with imports changed: `Planet`,
`PlanetReplacement`, `PlanetTransfer`, `Satellite`, `SatelliteReplacement`, `PlanetGateway`, `SatelliteGateway`, and
the flows of planet and satellite. The flows take the extension's gateways object instead of `backend.planets`.
Dropped: the `planets` and `satellites` attributes on `core/ports/registry_backend.py` (D11, D13).

## Open questions

- `.vscode/settings.json` and `config.rri-mtest.yaml.local` are the maintainer's local changes and stay unstaged.
