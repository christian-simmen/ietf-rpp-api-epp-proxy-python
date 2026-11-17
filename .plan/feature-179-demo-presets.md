# Plan: demo extensions, profiles and presets for Planet and Satellite (#179)

Branch `feature/179-demo-presets`, stacked on `feature/178-presets` (PR #192, itself on #176). The PR targets `main`.
Merge order: #176, #192, this PR. #180 stacks on this one. Worktree `/home/vscode/worktrees/rpp-presets`. Part of #174.

## Status

Checkpoint 1 (plan) reported, waiting for approval. Nothing is implemented.

## Tasks

- [~] T0 Plan approved
- [ ] T1 Generic: an Extension Schema may extend a definition of another extension (see D1), checked at start; the handler
      package and the OpenAPI fragment of an extension are optional (D5). Unit tests first.
- [ ] T2 Planets: the seam for members of other extensions on the RPP side (`MemberMapper`, D2) in create, read, PUT and PATCH of
      planets and satellites, and the scope of a PUT (D3). Unit tests first.
- [ ] T3 `planet-atmosphere`: package, schema, core model, RPP mapping, SQLite part with its `MemberHook`.
- [ ] T4 `satellite-orbit`: the same for the satellite.
- [ ] T5 Profile Schemas and definitions of the four profiles, the six presets, registered by the extensions that bring them (D4).
- [ ] T6 Specifications under `docs/demo/` (2 extensions, 4 profiles, 6 presets) and `tests/unit/test_demo_docs.py`.
- [ ] T7 Wire tests of the demo backend: one 422 `02308` case per constraint, the same request accepted without the profile, 400
      for members outside the preset, round trips of the members (create, read, PUT, PATCH, delete).
- [ ] T8 Docs: `architecture.project.md`, `testing.project.md`, `.spec/spec-issues.md`, `copy_models.sh`, `README.md` if it lists the demo.
- [ ] T9 Checks on the final commit (`lint-imports`, unit, smoke with rri-mtest), draft PR, report.

## What is built

Identifiers are under `org.example.rpp.<kind>.<key>`, every version is `1.0`, RPP version `1.0`. The file key is the last segment.

### Extensions (package `src/extensions/<pkg>/`, SQLite part `src/registry_adapter/sqlite/extensions/<pkg>/`)

| Key | Package | Adds | Members |
|---|---|---|---|
| `org.example.rpp.extension.planet-atmosphere` | `planet_atmosphere` | `atmosphere` to Planet (create, read, update) | `pressure` (bar, number >= 0, required), `dominantGas` (string, optional) |
| `org.example.rpp.extension.satellite-orbit` | `satellite_orbit` | `orbit` to Satellite (create, read, update) | `semiMajorAxis` (km, number > 0, required), `eccentricity` (0 <= e < 1), `inclination` (degrees, 0 to 180) |

Both extend definitions of the planets extension (`planet.create|read|update`, `satellite.create|read|update`), so each needs the planets
extension in the preset (D1). Both add an optional member (cardinality 0-1, read-write, Visibility default). Their schemas are in
`.spec/<key>-extension.schema.json`, copied by `copy_models.sh`. Definitions are named `ext.atmosphere.planet.create` and so on, and
`atmosphere` / `orbit` for the shared object.

### Profiles (each with a Profile Schema `.spec/<key>-profile.schema.json`, `url` = its `docs/demo/` specification)

| Key | Requires | Bases | Constraint | Refused by the demo backend |
|---|---|---|---|---|
| `rocky-planets` | planets | none | Planet `type` is `rocky` (`planet.create`, `planet.update`) | create, PUT and PATCH `replace /type` with `gas-giant` |
| `catalogued-satellites` | planets | none | Satellite `id` matches `^[a-z0-9]+(-[a-z0-9]+)*-[ivx]+$` (`satellite.create`) | create of `moon` (id is create-only, so no PUT or PATCH case) |
| `habitable-atmospheres` | planets, planet-atmosphere | none | `atmosphere` is required (`planet.create`, `planet.update`), `atmosphere.pressure` is 0.5 to 2 (the definition `atmosphere` of the extension) | create or PUT without `atmosphere`, PATCH `remove /atmosphere`, create and PATCH `replace /atmosphere` with pressure 5 |
| `habitable-rocky-planets` | planets (planet-atmosphere through its base) | `rocky-planets`, `habitable-atmospheres` | adds `radius` required (`planet.create`, `planet.update`) | create or PUT without `radius`, PATCH `remove /radius`; the bases' cases name the base profile |

Every constraint has a case the native PATCH or the create/PUT enforces (Q7 of #178: member paths and unconditional `required`); no
constraint is only a cross-member one.

### Presets (`url` = its specification)

| Key | Base presets | Extensions (own) | Profiles (own) |
|---|---|---|---|
| `planets` (exists, #177) | base | planets | none |
| `planets-atmosphere` | planets | planet-atmosphere | none |
| `planets-orbits` | planets | satellite-orbit | none |
| `planets-complete` | planets-atmosphere, planets-orbits | none | none |
| `catalogued-planets` | planets | none | rocky-planets, catalogued-satellites |
| `habitable-worlds` | planets-atmosphere, catalogued-planets | none | habitable-rocky-planets |

`planets-complete` is multiple inheritance of presets (planets reached twice, once in the result). `habitable-worlds` is multiple
inheritance with profiles: rocky-planets reached through `catalogued-planets` and through `habitable-rocky-planets`, applicable once.
#180 binds profiles (for example `habitable-atmospheres` to `planets-complete`) and configures the offers. The tests of #179 compose
offers and bindings with fixtures built on the config of `config.demo.yaml`; the file is not changed.

## Where the definitions live (D4)

A definition is brought by the extension that needs the others: `planets` (`catalogued-planets`, `rocky-planets`,
`catalogued-satellites`), `planet-atmosphere` (`planets-atmosphere`, `habitable-atmospheres`, `habitable-rocky-planets`,
`habitable-worlds`), `satellite-orbit` (`planets-orbits`, `planets-complete`). They are inline dicts in `rpp/schema/` modules read by
`register`, as `planets` does for its preset, with the Profile Schema loaded from the copied file. A definition that refers to an
extension that is not registered is only read when a configuration offers it.

## Acceptance criteria of #179, and how each is shown

1. Every extension, profile and preset has a specification in the guidelines format, with examples checked by a test.
   `docs/demo/planet-atmosphere-extension.md`, `satellite-orbit-extension.md` (guidelines §9 list), `<key>-profile.md` (Profile
   Specification Format, §Profiles) and `<key>-preset.md` (Preset Specification Format) for the preset `planets` too. Test
   `tests/unit/test_demo_docs.py` over all of them: extension docs as `test_planets_extension_doc.py` (marked examples valid or
   invalid against the Effective Schema, shown definitions equal to the schema, copy in the package equals `.spec/`); profile docs: the
   Profile Schema shown equals the file, `<!-- example valid <def> -->` passes both steps, `<!-- example violates <def> -->` passes
   step 1 and fails step 2 (guidelines: "valid without the profile and invalid with it"); preset docs: the Preset Overview table equals
   the definition (identifier, version, bases, extensions, profiles) and every id it names is defined.
2. Each profile constraint has an example valid without the profile and refused with 422 `02308` and `profile` by the demo backend.
   `tests/unit/test_demo_profiles_wire.py`: app of the demo config plus the extensions and the offers of the test; per constraint
   (table above) the request under a preset with the profile gives 422 `02308`, `profile` = the profile id (for `habitable-worlds`
   the base that owns the constraint), and the same body under a preset without it is 2xx. PATCH cases for `type`, `atmosphere` and
   `radius`.
3. A request with a member of an extension outside the signalled preset is a 400. Wire tests: `atmosphere` in create, PUT and PATCH
   (`/atmosphere`) under `planets`, `orbit` under `planets-atmosphere`; 400 `02001`, no write. The response of a planet under a preset
   without the extension has no `atmosphere` even where the planet has one.
4. #174 criteria on the demo set (flattening once, required extensions transitive, schema of a preset) have a case on the real
   definitions: `GET /presets/habitable-worlds`, its schema, discovery, and the start of an app that offers them all.

## Structural changes (to approve)

New packages `src/extensions/planet_atmosphere/` and `src/extensions/satellite_orbit/` (each `core/{model}`, `rpp/{dto,mapping,schema}`,
`register_<pkg>.py`), `src/registry_adapter/sqlite/extensions/{planet_atmosphere,satellite_orbit}/` (`PART`, `HOOKS`, models, hook),
`docs/demo/` documents, `.spec/` schemas, `tests/unit/` files. Generic code is changed in `rpp/schema` (D1) and `registration` (D5). In
`extensions/planets/rpp/mapping/` two files are added (`member_mapper.py`: the protocol; `member_mappers.py`: the registry) and the
create, read, PUT and PATCH mappers of planet and satellite call them. `pyproject.toml`: the extension contracts list the new packages
(`extension-layers`, `extension-rpp-layers`, `extension-core-layers`, `extension-core-pure`, `generic-not-extensions`); no new
`ignore_imports`.

## Wire contract decisions

- Members of an extension of the preset: a member outside the preset is undeclared, 400 `02001` (core RC4, json §4.9.1), checked by
  step 1 before any mapping. No new path, header, result code or Problem Detail field.
- A broken profile constraint is 422 `02308` with `profile` and `paths` (core §Problem Details, json §Profiles and Validation), as
  built in #178. Prose rules: none in the demo extensions (all bounds are schema), so no 400-before-422 mapper checks are needed.
- PATCH of a member: `add`, `replace` and `remove` with the path `/atmosphere` or `/orbit`, the whole member (D6). A deeper path is 400
  as `Path ... cannot be changed` is today. `remove` is allowed (cardinality 0-1).
- PUT: the members of the extensions of the request's preset are the representation (D3).
- Responses show the members of the response preset's extensions only (guidelines §5.13: a server MUST NOT include data of an extension
  the preset does not contain).

## Decisions

None yet. Open questions Q1 to Q7 are in the report of checkpoint 1; answers are recorded here.

## Open questions with recommendation

- Q1 (D1) An Extension Schema that adds members to a data object another extension defines. Json §Extension Framework maps
  `rpp:extends` to a base definition only, and the proxy refuses any other key. Recommendation: allow the key
  `<$id of the extension>#/$defs/<definition>` (the form `rpp:constraints` uses), the owner is derived, so the extension needs the owner
  in the preset, refused at start naming both (as for a profile's required extensions). The additivity check reads the base
  definition from the owner. No new field in `rpp:extension`. Record the gap in `.spec/spec-issues.md`.
- Q2 (D2) How the planets RPP code finds the mappers of members of other extensions. Recommendation: `MemberMappers` in the planets
  `rpp/mapping` (one for planet, one for satellite), filled by `register()` of the adding extension, process-global and idempotent like
  `EXTENSIONS`, and used only for ids in the request preset's `extensions`. Alternative: a field of `RegisteredExtension` read through
  the app, which makes the generic `registration` know of members.
- Q3 (D3) A PUT under a preset without an extension removes that extension's members today (`_replace_members`: a member not given is
  removed), which the client cannot see. Recommendation: `PlanetReplacement` and `SatelliteReplacement` get `scope` (the extension ids
  of the request preset) and the gateway replaces the members of those only. Alternative: keep and document the loss.
- Q4 (D4) The definitions are brought by the extension that needs the others (table above), a cross-extension preset is read only
  where the configuration offers it. Alternative: a neutral package `extensions/demo_definitions` that registers no extension.
- Q5 (D5) `atmosphere` and `orbit` have no paths: make `handlers` and `openapi` optional in `RegisteredExtension` (recommended), or
  ship an empty handler package.
- Q6 (D6) PATCH changes a member as a whole (`/atmosphere`), not `/atmosphere/pressure`. Recommendation: whole member, documented. The
  profile attribution of a nested change is not needed then.
- Q7 Member shapes (table of extensions) and the six presets are my proposal, as the issue leaves them to the plan. `habitable-worlds` and
  `planets-complete` can be dropped if the maintainer wants fewer documents.

## Findings (evidence)

1. `extension_additivity._Check` reads the base definition from `bundle_definitions()`: an extension that extends `planet.create`
   raises `KeyError` today. `ProfileConstraints` and `compose` already work on definitions of extensions, and `OfferedPresets._check_schemas`
   (`defs` = bundle plus the extensions' definitions) checks a profile against an extension's definition.
2. `RPPPlanet` and `RPPSatellite` are `Undefined.RAISE`, so a mapper takes the members of other extensions out before `parse_rpp`, after
   step 1.
3. `refuse_removal` looks a member up under the definition a constraint targets (`planet.update`), so a profile that requires `atmosphere`
   targets the planets definitions, and `habitable-atmospheres` also requires `planets` for that.
4. `SqliteGateway._replace_members` removes the members of every hook not given, and `to_planet` reads every hook, whatever the preset.
5. Visibility: members that other extensions add are `default`, so `data_objects` of the new extensions are empty.
