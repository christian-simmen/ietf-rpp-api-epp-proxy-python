# Plan: #180 demo configurations (Story 4 of #174)

Branch `feature/180-demo-configurations`, stacked on `feature/179-demo-presets` (PR #199). The PR targets `main`.
Merge order: #176, #192, #199, then this PR. `origin/main` is already contained in the base (no merge needed).
Worktree `/home/vscode/worktrees/rpp-presets`, mutex taken there. Clean-main step skipped (maintainer).

## Decisions of the orchestrator (apply)

- Backend never sees JSON. A response uses the response preset (guidelines 5.13). RPP and extension prose rules answer before 02308
  (core.md:235). A member outside the preset is 400 `02001`. The native PATCH enforces per-member constraints and unconditional
  `required` only. Under media-type signalling the Content-Type preset must be listed in Accept (core.md:188, :195).

## Tasks

- [x] T0 Plan approved
- [x] T1 Tests first (unit): `tests/unit/test_demo_configurations.py`, `tests/unit/test_refused_configurations.py`; selector `contains` on a map leaf
- [x] T2 Test-only definitions `tests/refused_configs/` and the refused configs
- [x] T3 Configs `config.demo-extended.yaml`, `config.demo-bound.yaml`, `config.demo-inherit.yaml`
- [x] T4 Environments `sqlite-demo-extended`, `sqlite-demo-bound`, `sqlite-demo-inherit`
- [x] T5 Integration cases (groups `demo_discovery`, `demo_preset_read`, `demo_binding`) and `when` on the generic cases a binding refuses
- [~] T6 Docs: testing.project.md, architecture.project.md, README.md, deploy README mention if needed
- [ ] T7 Checks on the final commit (lint-imports, unit, smoke incl. rri-mtest), draft PR

## Configurations (all: `rpp_backend: sqlite`, same clients and passwords as config.demo.yaml, in-memory database)

`config.demo.yaml` and `sqlite-demo` stay unchanged and ARE the bare configuration of the issue (planets preset only, default
`planets`, no binding). No `config.demo-bare.yaml` duplicate (open question 1).

| Config / environment | `rpp_extensions` | `presets` (default first in bold) | `bound_profiles` | signalling |
|---|---|---|---|---|
| `config.demo.yaml` / `sqlite-demo` (bare, exists) | planets | base, **planets** | none | header |
| `config.demo-extended.yaml` / `sqlite-demo-extended` | planets, planet_atmosphere, satellite_orbit | base, planets, planets-atmosphere, planets-orbits, **planets-complete** | none | header |
| `config.demo-bound.yaml` / `sqlite-demo-bound` | all three | base, **planets**, planets-atmosphere, planets-complete, catalogued-planets | planets: rocky-planets; planets-atmosphere: habitable-atmospheres; planets-complete: habitable-rocky-planets (transitive requirement of planet-atmosphere through its base habitable-atmospheres, which planets-complete holds through two bases); catalogued-planets: none (its definition already has two profiles) | media-type |
| `config.demo-inherit.yaml` / `sqlite-demo-inherit` | all three | base, planets, planets-atmosphere, planets-orbits, **planets-complete**, catalogued-planets, habitable-worlds | none | header |

Descriptor `preset` = the default preset of the config (the `{rpp:*}` placeholders). Generic `planet_*`/`satellite_*` groups run in every
demo environment, so each environment also proves the extensions and the bases do not disturb the plain objects. Environments
need no credentials (`literal` registrars as `sqlite-demo`), `max_workers: 8`, facts copied from `sqlite-demo`. Cases are in the smoke suite.

Signalling: bound uses `media-type` (exercises Content-Type in Accept, response preset), others `header`. The case-level `when` on
`env.preset_signalling` is used where a literal header is written.

Selecting a case for a config: top-level `when` with `profile.presets` equal to the offered list (an existing selector fact),
and `profile.bound_profiles` for the binding cases. `contains` today needs a collection; small change to
`tests/helper/selectors.py`: `contains` on a map leaf tests the key (`{"profile.bound_profiles": {"contains": "planets"}}`), with a
unit test in `tests/unit/test_integration_selectors.py`.

Generic cases that need what `rocky-planets` refuses (gas-giant, ice-giant, moonlike types): `planet_create/test2, test4`,
`planet_update/test1, test4`, `planet_transfer/test1, test12` get `"when": {"profile.bound_profiles": {"not": {"contains": "planets"}}}`
with a `comment` (skipped on sqlite-demo-bound, where the default preset binds rocky-planets). Their types are re-checked when implementing.

## Acceptance criteria of #180 and the cases that show them

1. Environment per config, no credentials, in smoke: the three descriptors above, cases marked `smoke`.
2. Composition shown (discovery, Preset and Profile Data Objects, preset schema), bound separate, bases flattened.
   - Integration (`demo_discovery/`, one case per config, selected by `profile.presets`): discovery lists the offered presets and each extension.
     Bound: discovery `profiles` lists rocky-planets, habitable-atmospheres, habitable-rocky-planets (the bound profile and its bases).
   - Integration (`demo_preset_read/`): `GET /presets/{id}`.
     extended `planets-complete`: extensions planets, planet-atmosphere, satellite-orbit (union of two bases), no profiles, no bound.
     bound `planets`: `profiles: []`, `boundProfiles: [rocky-planets]`. bound `catalogued-planets`: `profiles` = rocky-planets and
     catalogued-satellites, `boundProfiles: []` (definition and binding apart). bound `planets-complete`: `boundProfiles: [habitable-rocky-planets]`.
     inherit `habitable-worlds`: extensions planets and planet-atmosphere, `profiles` rocky-planets, catalogued-satellites, habitable-rocky-planets.
     `GET /profiles/{id}` for habitable-rocky-planets: `baseProfiles` and flattened `requiredExtensions` (planets and planet-atmosphere).
     `GET /presets/{id}/schema` (public, `application/schema+json`): `$defs` has the profile sub-schemas that apply (bound: `profile.rocky.type` in `planets`;
     inherit `habitable-worlds`: rocky, habitable, habitableRocky) and the extension sub-schemas of the preset only.
   - Absence and "once" cannot be asserted by the subset body compare, so the exact assertions are unit tests that compose the real
     config files (`test_demo_configurations.py`, parametrized over the four files): exact preset list, extension ids each once,
     `profiles`/`boundProfiles` lists, base profiles flattened once (rocky-planets through the preset and through habitable-rocky-planets appears once in `applicable`),
     schema `$defs` exact, discovery `extensions` each once.
3. Same request accepted without the binding, refused 422 `02308` with it (decision Q7). The pair needs no explicit preset: group `demo_binding/`,
   two cases with the identical request POST /planets `type: gas-giant` under the default preset `planets` (headers `{rpp:*}` as every case):
   - `test1-a_preset_without_the_profile_accepts_a_gas_giant`: 201. `when` `profile.bound_profiles` does not contain `planets` (sqlite-demo; extended and inherit default to planets-complete, so they skip it).
   - `test2-the_bound_profile_refuses_the_same_request`: 422, `RPP-Code 02308`, error `result` 02308, `profile` = rocky-planets. `when` `profile.bound_profiles` contains `planets` (sqlite-demo-bound).
   Extra pairs on non-default presets (habitable-atmospheres on planets-atmosphere, habitable-rocky-planets on planets-complete, 400 for an atmosphere member under planets):
   the runner placeholders get an optional preset key, `{rpp:preset:KEY}`, `{rpp:accept:KEY}`, `{rpp:content-type:KEY}` (KEY = key of a preset of the config, resolved per signalling method),
   with a unit test; no literal headers per environment. If that is not clean, they are dropped from the integration suite and kept as unit tests on the real configs.
4. Must-not-start configs: below.

## The configurations that must not start

Not shipped as demos and not in the integration environments (they cannot run). Unit tests compose each with the real loader:
`compose(load_settings(path))` raises `ValueError`, and one test starts it as a process (`python -c "import main"` in `src/` with
`RPP_CONFIG_FILE`, timeout, short-lived) and asserts a non-zero exit and the message on stderr. Unit test: `tests/unit/test_refused_configurations.py`
(pins the exact message with `pytest.raises(match=...)`, as `test_offered_presets.py` does).

Location: `tests/refused_configs/` (a package, so `rpp_extensions` can name `tests.refused_configs.cycle`, which works because the tests import `tests.*` today),
holding the YAML files and the test-only extension modules. The shipped demo extensions stay valid. The test-only modules
(`cycle.py`, `version_clash.py`, `profile_cycle.py`) each have `register(registry)` that adds a data-only `RegisteredExtension`
(fixture shape of `tests/helper/preset_fixtures.py`: own id, empty schema, only `presets`/`profiles`). Risk to verify first
in T1: compose must accept an extension without a sqlite part (the fixture shape does in `create_app`; `backend_parts` is checked per backend).

| File | Definitions | Message (exact, from the checks of `OfferedPresets`/`PresetFlattening`) |
|---|---|---|
| `missing-extension.yaml` | demo definitions; planets, planet_atmosphere; `planets` bound `habitable-atmospheres` | `The profile org.example.rpp.profile.habitable-atmospheres requires the extension org.example.rpp.extension.planet-atmosphere, which the preset org.example.rpp.preset.planets does not contain` |
| `missing-extension-transitive.yaml` | demo; `planets` bound `habitable-rocky-planets` (requirement only through base habitable-atmospheres) | `The profile org.example.rpp.profile.habitable-rocky-planets requires the extension org.example.rpp.extension.planet-atmosphere, which the preset org.example.rpp.preset.planets does not contain` |
| `preset-cycle.yaml` | `cycle.py`: presets cycle-a builds on cycle-b builds on cycle-a; offered cycle-a | `The preset org.example.rpp.preset.cycle-a builds on itself: org.example.rpp.preset.cycle-a -> org.example.rpp.preset.cycle-b -> org.example.rpp.preset.cycle-a` |
| `profile-cycle.yaml` | `profile_cycle.py`: profiles cycle-x and cycle-y on each other, bound to `planets` | `The profile org.example.rpp.profile.cycle-x builds on itself: org.example.rpp.profile.cycle-x -> org.example.rpp.profile.cycle-y -> org.example.rpp.profile.cycle-x` |
| `version-clash.yaml` | `version_clash.py`: presets clash-a (planets 1.0) and clash-b (planets 2.0), preset clash builds on both; offered clash | `The preset org.example.rpp.preset.clash contains the extension org.example.rpp.extension.planets in the versions 1.0 and 2.0` |

Messages are quoted from the current source and confirmed against the real output in T1 (tests first, failing for the missing files);
where the real text differs the test pins the real text and the plan is corrected. No wording change in `src/` is planned.

## Structural changes

- New: three root configs, three environment files, `tests/refused_configs/` (YAML plus three test-only modules), new case groups, two unit test files.
- `tests/helper/selectors.py`: `contains` on a map leaf (key). `tests/helper/demo_app.py` docstring mention of #180 updated (it keeps building ad-hoc compositions).
- No change under `src/`. No new top-level directory (the `tests/` subpackage is within the existing tree; proposal for approval).
- Docs: testing.project.md (environments, SQLite demo section lists four environments and what each shows, refused configs), architecture.project.md
  (the demo configurations in "Registered extensions"/presets), README (how to run each), overview unchanged.
- Check script: `lint-imports` unchanged (tests are outside the root packages).

## Wire decisions (no change; cited)

- Refused binding/cycle/clash: startup error, no wire (data-objects "Applicable Profiles"/Inheritance rules; #174 acceptance).
- Break of a profile constraint: 422 `02308` with `profile` (core.md:235 order: prose rules before 02308; JSON Schema step 1 stays 400).
- Member of an extension outside the preset: 400 `02001`.
- Bound config uses media-type signalling: Content-Type preset must be in Accept (core.md:188, :195); response uses the response preset.
- PATCH: per-member constraints and unconditional `required` only (so the transitive-profile case uses POST/PUT for radius `required`).

## Answers of the orchestrator (recorded)

- Q1 yes: `config.demo.yaml` / `sqlite-demo` is the bare configuration (say so in testing.project.md and the PR text, the issue names `config.demo-bare.yaml`). Q2, Q3, Q5, Q6 yes. Q4 yes, but verify first that compose accepts a data-only extension without a sqlite part; if not, stop and report before touching `src/`.
- Q7: the pair uses the default preset (above); extra pairs via `{rpp:preset:KEY}` placeholders, else unit tests.
- Refusal messages: tests first, pin the real output. A message that does not name both sides of the conflict (profile and extension, full cycle path, both versions and the preset) is reported, the test is not weakened.

## Open questions (recommendation) -- all answered, see above

1. `config.demo-bare.yaml`: rename `config.demo.yaml`, duplicate it, or keep? Recommend keep `config.demo.yaml`/`sqlite-demo` as the bare config (it is exactly "the planets preset only"; it is referenced by README, deploy example, docs, tests). The set is documented as bare/extended/bound/inherit.
2. Default of extended and inherit is `planets-complete` (generic cases run with all extensions available) while bound is `planets`. Recommend as written.
3. Generic cases skipped on bound by a `when` on `profile.bound_profiles` (needs the selector extension). Alternative: leave bound's default unbound and give up the pair on `planets`. Recommend the selector extension.
4. Test-only definitions in `tests/refused_configs/` (not under `src/`). Recommend.
5. One subprocess test for the process exit, rest in-process. Recommend.
6. Deploy example (`deploy/ansible/.../sqlite-demo.yaml.j2`) not extended with the new configs. Recommend leaving as is.

## Checks (process.project.md), on the final commit, no edits during the run

`PYTHONPATH=src lint-imports`; `pytest -n 4 tests/unit`; `pytest -n 4 -m smoke tests/integration` incl. rri-mtest (no retry of a login refusal).

## Findings

- The risk of Q4 held: `compose` refuses a data-only extension ("rpp_extensions: the extension ... has no part in the sqlite backend",
  `registry_setup.py`). Resolved without a change under `src/`: the test-only extensions have a SQLite part without tables
  (`tests/refused_configs/definitions_sqlite_part.py`).
- The refusal messages are as planned and each names both sides (profile and extension and preset; the whole cycle path; both versions and the preset).
  The tests pin them; no message was weakened.
- Placeholders with a key (`{rpp:preset:KEY}` ...) work for both signalling methods, so the extra pairs of `demo_binding/` are integration cases. Unit test in `test_runner_presets.py`.
- A list in an expected body must have the length of the actual one (`recusive_compare_existing`), so the integration cases assert "each once" too.
  Mutations (a wrong profile, an extra bound profile) fail the cases.
- sqlite-demo-bound skips six generic cases (types other than rocky), see the `when`/`comment` in them. `sqlite_drafts_objects/test5` and the planets step of `preset_read/test1` got a `when` for the bare configuration.
