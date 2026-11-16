# Plan: presets, profiles and extensions in the proxy (#178)

Branch `feature/178-presets`, Story 2 of #174. Requirements and acceptance criteria: #178 and the proxy criteria of #174.
Normative text: the accepted proposals in `.spec/proposals/174-presets/` (`data-objects.md` DO, `core.md` CO, `json.md` JS,
`extension-guidelines.md` EG, `draft-kowalik-rpp-epp-compatibility.md` EC).

## Base (maintainer decision: stacked PRs)

Created from `origin/feature/177-sqlite-demo-backend` (#181), then `origin/feature/174-presets` (#176) merged in. The merge
had no conflicts (it adds `.spec/proposals/174-presets/`, `.spec/spec-issues.md`, `docs/agents/specification.project.md`).
The PR targets `main`. Merge order: #176, #181, then this one. #179 and #180 stack on this branch.

The maintainer's unstaged `.vscode/settings.json` and untracked `config.rri-mtest.yaml.local` are carried across and never
staged. The clean-main/pull step is skipped by the maintainer's decision.

## Decisions carried over from #177 (orchestrator)

- D12: the RPP code of an extension is in `src/extensions/<name>/rpp/`, its SQLite part in
  `src/registry_adapter/sqlite/extensions/<name>/`. The issue's `src/rpp/extensions/<name>/` is superseded.
- D11/D13: extensions, and the presets and profiles an extension brings, are registered by configuration
  (`rpp_extensions`, `register(registry)`). Without it the generic code does not know them.
- D18: the effective schema and the validators are per app and per preset, not process-global. Registration of
  extensions (`EXTENSIONS`, the data model) is not redone.
- D24/D25: no JSON or RPP representation reaches core or a backend. Presets, profiles and profile validation are an
  RPP-layer concern.
- The demo profile `org.example.rpp.profile.planets` of #177 becomes the demo preset of I2. Multiple inheritance and
  bindings get their full demo configurations in #180, here they are covered by unit tests.

## Tasks

- [~] T0 Plan, approved by the orchestrator
- [ ] I1 Contract
- [ ] I2 Definitions
- [ ] I3 Checks at start
- [ ] I4 Configuration
- [ ] I5 Preset Schema
- [ ] I6 Two-step validation
- [ ] I7 Signalling
- [ ] I8 Endpoints
- [ ] I9 Discovery
- [ ] I10 Mappers
- [ ] I11 Tests
- [ ] I12 Docs
- [ ] I13 Checks: `lint-imports`, unit, full smoke including `rri-mtest` (no MTEST login retry), on the final commit

Approach per task: see the report of checkpoint 1 and the sections below. The orchestrator's answers are recorded under
"Decisions".

## Structural changes (to approve)

Generic code, all in `rpp` (RPP layer). Core and the backends do not change, but for the leaves of `BackendProfile`.

- `rpp/schema/` (one class per file): `RppPreset`, `RppProfile` (redefined), `Reference` (id, version), `Definitions`
  (the presets and profiles an app knows: the files in `schemas/presets/` and `schemas/profiles/`, and what the registry
  brings; built per app, no global dict), `OfferedPreset` (flattened extensions, profiles, bound profiles, applicable
  profiles), `OfferedPresets` (the choice, with the checks of I3), `PresetSchemas` (the Preset Schema document and the
  validators of each offered preset), `SchemaScope` (what a mapper validates with, replaces the `extensions` tuple and the
  global `_effective` cache of `validator.py`), `ProfileConstraintViolation`.
- Removed: `profile_schemas.py`, `rpp_profiles.py`, `schemas/profiles/{base,epp,rri}.yaml`, the extensions
  `epp-compatibility` and `profile-schemas` (schemas, copies, `SERVER_EXTENSIONS`, `docs/profile-schemas-extension.md` and its
  tests), `/profiles/{name}/schema` and `profile_schema_path.py`, `ProfileSchemaReference`.
- `rpp/http/`: `profile_*` modules renamed to `preset_*` (one name per concept): header, header signalling, media type
  signalling, signalling, middleware, selection, request presets. `problem.py` renders `profile` in the error object.
- `rpp/handlers/presets.py` (`presets_read`, `presets_schemaRead`), `handlers/profiles.py` (`profiles_read`), `mapping/preset/`,
  `mapping/profile/`, DTOs `RPPPreset`, `RPPPresetReference`, redefined `RPPProfile`, `RPPProfileReference`.
- `registration/RegisteredExtension`: `rpp_profiles` becomes `presets` and `profiles` (definitions as dicts, a profile
  with its Profile Schema). `extension_registration.register_all` no longer registers profiles globally.
- `core`: `BackendProfile` leaves `profiles`/`default_profile` become `presets`/`default_preset`, and `bound_profiles` is new.
  `Discovery` (core model) loses `profiles`, `extensions` and `profile_schemas`: the discovery mapper takes them from the
  offered presets, so no RPP concept stays in core.
- `settings`: `rpp_preset_signalling` (`Settings.preset_signalling`) replaces `rpp_profile_signalling`.
- Import contracts: `rpp.schema` still imports `registration` only for types, no new contract is expected.

## Wire contract decisions

Grounded in the proposals (DO data-objects, CO core, JS json, EG guidelines, EC compat draft):

- Header `RPP-Preset: preset=<id>;version=<v>`, ABNF and rules: CO C6 "Header Signalling". Absent: the default preset (CO RC1).
  Response carries `RPP-Preset` and `Vary: RPP-Preset`.
- Media type parameters `preset`, `preset-version`: CO C6 "Media Type Signalling". Absent: the default preset. Problem
  Details carry none. Result codes of every refusal stay today's (issue decision): 400 `02005`, `02003`, `02004`, `02001`
  for the header method, 415/406/400 for the media type method.
- 02308 (422) for a broken profile constraint, `profile` in each error object: CO C6 "Extensions and Profiles of a Request",
  CO C9. 400 for an extension member outside the preset: CO RC4. 400 for a request that fails the preset schema: JS C2 step 1.
- Endpoints `GET /presets/{id}`, `GET /presets/{id}/schema`, `GET /profiles/{id}`: CO C7, C8. The schema is a Direct Access
  data element in its native media type `application/schema+json`: CO C5 "Native Media Types", DO R6. `/presets/{id}` and
  `/profiles/{id}` need authentication, `/presets/{id}/schema` is public (issue; DO Read Operation Authorisation).
- Preset and Profile Data Objects: DO C8, JS C5 (read and reference views, `id`, `version` in every reference, flattened
  `extensions`, `profiles`, `requiredExtensions`; `boundProfiles`, `defaultPreset`; `schema` onDemand, embedded as an object
  with `includeElements=schema`).
- Discovery: `presets` (read view, `extensions`, `profiles`, `boundProfiles` required), `profiles` (reference view of every
  applicable profile), `extensions` of all offered presets, `objects` as today (DO R5, C7; JS C4). `profileSchemas` goes.
- Preset Schema: JS C6 "Preset Schema" (`$id` the URL of the schema sub-resource, `rpp:preset`, in-place composition, extension
  sub-schemas a profile constrains composed in place). Profile Schema format and `rpp:constraints`: JS C6 "Profile Schema".
  Two-step validation: JS C2.
- Definitions: EPP Compatibility Profile 1.0 `urn:ietf:params:rpp:profile:epp-compatibility` with the Profile Schema of EC
  (not the shorter one of JS C6, JS RJ9), presets `urn:ietf:params:rpp:preset:base` and `...:epp-compatible` (DO R7, C12),
  `de.denic.rpp.preset.rri`, the demo preset of the planets extension. One version of each (DO R3).

## Disagreements and gaps

1. The issue names `src/rpp/extensions/<name>/` (D12 moved it). Resolved by D12.
2. JS RJ9 (three constraints) and EC (also the JSContact Card and localizations) differ. I2 says the Profile Schema of the
   draft of EC: EC is followed.
3. JS C6 "Preset Schema": the document does not carry `unevaluatedProperties`, a validator adds them. Today's published
   effective schema carries them (`docs/profile-schemas-extension.md`, "what is published is what is enforced").
4. EC notes that its localization constraints assume members the base Card schema does not declare. JS C6 forbids a
   profile sub-schema to declare a property its target does not declare, and I3 makes that a refusal at start. The bundle
   declares `RecordLocalization` with `unevaluatedProperties: Localization`, so this needs checking against the real walk.
5. CO RC4 says an extension used outside the preset is 400. Today an object of an extension outside the profile (path
   `/planets` under a profile without it) is 501 `02307` from `ProfileMiddleware`.
6. CO RC6 (an operation an applicable profile makes unavailable is 02308) conflicts with the issue decision that the
   prose constraints keep today's behaviour (501). The issue wins: no profile of this story makes an operation unavailable.
7. DO C8 makes `url` of the Profile Data Object required (1) and of the Preset optional (0-1). Today's profiles have none.
8. JS C6 "Effective Schema" and the issue's I5 speak of validators with and without the applicable profiles. The attribution of
   a failure to one profile (JS C2) needs one more validator per profile.
9. CO C5 lists `application/schema+json` or a range including it for the schema read. Today's profile schema also takes
   `application/json`.

## Decisions

Plan approved by the orchestrator for the maintainer (2026-11-16). Answers:

- Q1 `bound_profiles: {<preset key>: [profile keys]}` is one map leaf of the backend profile (I4).
- Q2 Per-app `Definitions` catalogue, no new global. `EXTENSIONS` stays global (D18).
- Q3 Ship EC in full, run the walker on the real bundle. If the localization constraints fail the RJ4 rule (EC flags this,
  `draft-kowalik-rpp-epp-compatibility.md:457`), drop only those sub-schemas from the proxy's copy, keep the mapper checks,
  record the drop in `.spec/spec-issues.md` with a link to SIDN/ietf-rpp-jscontact-profile#36.
- Q4 Publish the Preset Schema without `unevaluatedProperties`, inject them for validation (json.md:389).
- Q5 `/presets/{id}/schema` is outside signalling (core RC7) and public (RC3: server policy). `Accept`: `application/schema+json`,
  a range including it, or none; anything else 406.
- Q6 Hand-edit `.spec/draft-ietf-rpp-data-objects.yaml` together with `.spec/auto`.
- Q7 Step 2 (json.md:72-77, RJ5) runs on the patched or replaced object without its server-managed read-only members.
  Responses are never validated against profiles. The proposals do not say how two-step validation applies to PATCH:
  recorded as a gap in `.spec/spec-issues.md`.
- Q8 Core RC4: an extension path whose extension is not in the signalled preset is a 400 with the result code the proxy
  already gives for schema-nonconforming content (to be checked and cited). A base object the backend lacks stays 501 `02307`.
- Q9 No invented IANA URLs. Profile `epp-compatibility` url `https://datatracker.ietf.org/doc/draft-kowalik-rpp-epp-compatibility/`;
  presets `base` and `epp-compatible` url `https://datatracker.ietf.org/doc/draft-ietf-rpp-data-objects/`. rri and demo presets
  have no `url`. Profile `url` is required (data-objects.md:573): for #179, the demo profiles point to their `docs/demo/` spec.
- Q10 Remove `profiles`, `extensions`, `profile_schemas` from core `Discovery`, pass the offered presets to the discovery mapper.
- Disagreements: 1 D12 wins. 2 EC wins. 3 proposal wins. 5 RC4 wins (Q8). 6 the issue wins: prose keeps 501, no profile of this
  story makes an operation unavailable; RC6 is recorded as not implemented in `RPP_IMPLEMENTATION_NOTES.md`. 7 Q9. 8 Q5.
  Those that diverge from a proposal are recorded in `.spec/spec-issues.md`.
- Test cases whose expectation changes from 400/501 to 422 under `epp-docker` are listed in the PR description with the
  constraint that causes each. The scripted `{rpp:profile}` to `{rpp:preset}` rename is its own commit.
