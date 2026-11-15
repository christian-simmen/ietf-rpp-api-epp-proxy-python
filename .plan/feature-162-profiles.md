# Plan: profiles, Profile Data Object and per-request profile (#162)

Branch `feature/162-profiles`, from `main`. #163 (RPP-Profile header) and #164 (media type parameters) stack on it.
Spec: data-objects §4 and §18, json §6.11 and §8.8, core §11, §12.3, §12.4, §16.1.6, extension-guidelines §8.6.

## Decisions (maintainer, given with the task)

- D1 Three profiles, all version 1.0, one YAML each:
  - base `io.github.pawel-kow.rpp.profile.base`: objects domainName, contact, host; no extensions.
  - epp `urn:ietf:params:rpp:profile:epp-compatibility`: baseProfile base; lists the constraint-only extension
    `urn:ietf:params:rpp:extension:epp-compatibility` 1.0 (no schema members, no validation change: the EPP backend
    enforces those constraints under any profile).
  - rri `de.denic.rpp.profile.rri`: baseProfile base; objects domainName, contact, requestContact (host explicitly not
    supported, overriding base); extension `de.denic.rpp.rri`.
- D2 EPP server offers {base, epp}, default epp. RRI server offers {base, rri}, default rri. Set in `config.yaml` and
  `config.rri-mtest.yaml`.
- D3 The signalling method switch `rpp_profile_signalling: header|media-type` is #163's, not this issue's.
- D4 The selected profile drives the extensions of the combined schema and the allowed object and extension paths.
  Paths outside the profile are refused before any backend command.
- D5 With the default profile nothing changes on the wire (discovery excepted, see W5); existing tests stay green.

## Decisions (orchestrator, plan approval)

- D6 Q1: the published profile is not narrowed: `GET /profiles/base` lists host on RRI too. The effective objects a request
  may use = selected profile objects ∩ backend objects. Under base on RRI `/hosts` gets W1 (501, 02307). Profile objects
  need not be a subset of the backend's; profile extensions must be held. Discovery `objects` stays the backend's.
- D7 Q2 approved (offered set and `default_profile` in `BackendProfile`). Q3 approved (404, 02303). Q5 and Q6 approved.
- D8 Q4 approved (501, 02307). Citation: core line ~1211 ("MUST return 404 Not Found or 501 Not Implemented", §16.1.6
  being Process Listing) plus the result code table for 02307. Every case asserting 02101 for RRI `/hosts` is updated;
  say so in the PR. W1 to W5 approved; W5 is a deliberate wire change, recorded in the PR description.
- MTEST: pending unless this machine is on the allowlist (to be recorded).

## Tasks

- [x] T0 Plan approved
- [x] T1 Extension file for the epp constraint extension (`.spec/epp-compatibility.schema.json`, `rpp:extends` and
      `$defs` empty), copied by `copy_models.sh`; the loader and `check_known` take it unchanged
- [x] T2 Profile definitions and catalog (`rpp/schema`): `RppProfile`, `RppProfiles`, the three YAMLs, startup checks
- [x] T3 `BackendProfile`: `profiles` leaf holds the offered profile keys, new leaf `default_profile`; epp.yaml and
      rri.yaml set them; `extensions` of epp gets the constraint extension
- [x] T4 Resolver and per-request context in `rpp/http`: `ProfileResolver` (returns the default today), middleware that
      stores the selected profile and refuses paths outside it, `request_profile()` in `rpp/http/context.py`
- [x] T5 Handlers and mappers read the request's profile for `extensions` and `objects` instead of the static one
- [x] T6 `create_app`: extension paths for the union of the offered profiles' extensions
- [x] T7 `GET /profiles/{name}`: handler `rpp/handlers/profiles.py`, mapper `rpp/mapping/profile/profile.py`
- [x] T8 Discovery from the catalog (profiles, extensions, objects)
- [~] T9 Config files, tests (unit, wire, startup checks), docs (`architecture.project.md`, `testing.project.md`,
      `spec-issues.md` for gaps), full checks, draft PR

## Findings (evidence)

F1 `BackendProfile` (`core/capabilities/backend_profile.py`) has leaves `objects`, `profiles` (tuple of names, epp.yaml:
`urn:ietf:params:rpp:profile:epp-compatibility`, rri.yaml: `[]`) and `extensions`. Discovery
(`handlers/discovery.py`) copies all three; nothing else reads `profiles`.
F2 Mappers take `profile=backend_profile()` and read `profile.extensions` (domains, domain_patch, domain_replacement,
domain_wanted, domain_transfer_process, domain_request_contacts) and `profile.objects` (`domains.py:32`, "host" check).
Handlers call `domains.model_to_rpp(domain, backend_profile().extensions)`.
F3 `create_app` calls `check_known(profile.extensions)` and `add_extension_paths(spec, profile.extensions)`; the
`/requestContacts` paths exist only if an offered extension defines them (`rpp/http/extension_paths.py`).
F4 `GET /profiles/{name}` (`profiles_read`) is in `openapi.yaml` and has no handler, so it answers 501 by the resolver.
`profile.read` and `profile.reference` are in the schema bundle.
F5 Import-linter: `rpp` may not import `settings`; layers `handlers -> mapping | http -> dto | schema`; `core` is
stdlib only; `settings` imports nothing of the project. New code must fit these contracts without changing them.
F6 Handlers run in Connexion's pipeline, not in Flask's `before_request`, so the guard is a Connexion middleware (to be
confirmed by a spike at the start of T4; fallback: a decorator written once and applied in `rpp_operation`).

## Approach

### A. Definition (one place)

New in `src/rpp/schema/` (mirrors `extensions.py` and its `schemas/extensions/`, and fits the layers):

- `schemas/profiles/base.yaml`, `epp.yaml`, `rri.yaml`: `name`, `description`, `version`, `rppVersion`, `baseProfile`
  (name or absent), `objects`, `extensions` (ids). Lists are explicit and complete, no merging with the base profile
  (so rri's `objects` simply has no host, which is the "override").
- `rpp_profile.py`: `RppProfile` (frozen dataclass of those fields, plus `key`, the file stem).
- `rpp_profiles.py`: `RppProfiles`, the catalog of one server: `offered` (ordered), `default`, `get(name)`,
  `union_extensions()`, `union_objects()`. Built by `RppProfiles.build(keys, default_key, backend_profile)`, which makes
  the startup checks: every key known; exactly one default and it is offered; inheritance depth 1 (a base profile has no
  `baseProfile`); no profile is its own base; a `baseProfile` must itself be offered (so `baseProfile` is readable);
  no extension twice in a profile; every extension implemented (`EXTENSIONS`) and held by the backend
  (`BackendProfile.extensions`); (objects need not be held, D6). Names unique.
  A failure is a `ValueError` at start, like `check_known`.
- (Superseded by D6) The published profile is the definition as is; only `request_profile()` intersects objects.

### B. Configuration and BackendProfile (reconciling the existing `profiles` leaf)

Recommendation (Q2): no new config section. The `profiles` leaf of `BackendProfile` stops being RPP profile names (urns
that discovery printed) and becomes the offered profile keys (`base`, `epp`, `rri` = YAML stems), and a new leaf
`default_profile` (string) names the default. The generic `epp.yaml` sets `profiles: [base, epp]`, `default_profile: epp`,
and `extensions: [urn:ietf:params:rpp:extension:epp-compatibility]`; `rri.yaml` sets `[base, rri]`, `rri`. `objects` and
`extensions` stay what the backend can hold (the ceiling the catalog is checked against). `config.yaml` and
`config.rri-mtest.yaml` state `profiles` and `default_profile` under `rpp_backend_profile` (D2), where the layering
already lets a server narrow or replace a list. The unit tests that pass `EPP_PROFILE` and `RRI_PROFILE` keep working
unchanged, and `create_app(sessions, profile, ...)` keeps its signature: the catalog is built inside it from the profile.
Alternative: separate keys `rpp_profiles` and `rpp_default_profile` with a `Settings` section, `create_app` taking the
catalog, and 21 test files updated. Not recommended.

### C. Per-request profile, the seam for #163 and #164

- `rpp/http/profile_resolver.py`: class `ProfileResolver(catalog)` with `resolve(scope) -> RppProfile`. Today it
  returns `catalog.default`. #163 reads the `RPP-Profile` header and #164 the `Content-Type` and `Accept` parameters
  inside this one method (it gets the ASGI scope, so headers are there), and raises a `ProblemException` for an unknown
  profile or version. Nothing else changes in those issues.
- `rpp/http/profile_middleware.py`: ASGI middleware at `AFTER_SECURITY` (an unauthenticated request is still a 401, not
  a hint about profiles). It calls the resolver, stores the `RppProfile` in the request context
  (`scope["extensions"]["connexion_context"]`, next to `token_info`), and checks the path's object against it.
- `rpp/http/context.py`: `selected_profile() -> RppProfile` and `request_profile() -> BackendProfile`, the latter being
  the backend profile with `objects` and `extensions` narrowed to the selected profile (`with_changes`; one instance per
  profile, made when the app is built). Handlers and mappers that today take `backend_profile()` for `extensions` and
  `objects` take `request_profile()`; mappers keep their `profile=` parameter and are unchanged. Discovery and name
  lookups keep `backend_profile()`.

### D. Which paths a profile allows

The first path segment names the object: `domains` → domainName, `contacts` → contact, `hosts` → host, and for an
object an extension defines, the plural of its identifier (`requestContacts` → requestContact, derived from `EXTENSIONS`
the way `extension_paths.py` makes them). `messages`, `.well-known/rpp` and `profiles` belong to no object and are always
allowed. A path of an object not in the selected profile's `objects` is refused in the middleware, before validation
and before any backend command. Extension members inside a body are not routing: they are refused by the combined
schema of the profile as an undeclared member, a 400 exactly as today without the extension.

### E. Schema

`validate_schema(name, data, extensions=profile.extensions)` already composes per call, so the narrowed
`request_profile().extensions` is all the combined schema needs. `create_app` still adds the extension paths for the
union of the extensions of the offered profiles (the paths must exist for any profile that may be selected).

### F. Profile read and discovery

- `GET /profiles/{name}`: handler `rpp/handlers/profiles.py` (no registry command; authentication as the OpenAPI
  document declares for the operation), mapper `rpp/mapping/profile/profile.py` building `profile.read` (`@type`,
  `name`, `description`, `version`, `rppVersion`, `objects`, `extensions` as Extension Objects, `baseProfile` reference,
  `defaultProfile`), validated with `validate_schema("profile.read", ...)`. Name not offered: 404, RPP-Code 2303 (Q3).
  The name is the full profile name from the YAML (url-encoded colons accepted as path syntax).
- Discovery: `profiles` the offered names in order, `extensions` the union of the offered profiles' extensions (ids,
  ordered, deduplicated), `objects` the union of their objects, all from the catalog.

## Wire contract decisions (proposed)

W1 A path of an object outside the selected profile: HTTP 501, RPP-Code 2307 "Unimplemented object service" (core §16.1.6
allows 404 or 501 for an endpoint the server does not implement; table 10 gives 2307 for 501 and an object service).
The body is a Problem Detail whose detail names the object and the profile. Under the default profiles this only
shows on the RRI server's `/hosts` (the rri profile has no host) once a profile can be selected; with the default
selected, the RRI server's `/hosts` today answers by the backend (UNIMPLEMENTED_COMMAND, 501, 2101) and, as the rri
default has no host, the guard turns that into 2307. Q4.
W2 Profile read of an unknown name: 404, 2303 (object does not exist).
W3 Profile read content: json §8.8 example shape; `baseProfile` is a reference with `@type` and `name`; `defaultProfile`
true for the one default only.
W4 No new request or response headers in this issue (`RPP-Profile` is #163).
W5 Discovery changes, deliberately: EPP now lists `profiles` [base, epp] (was the epp urn only) and `extensions` with the
epp-compatibility Extension Object (was absent); RRI lists `profiles` [base, rri] (was `[]`, so absent or empty) and
the same extension as before. `objects` unchanged. The discovery wire tests are updated.

## Open questions, with recommendation

Q1 base lists host, the RRI backend holds none. Recommend: the catalog restricts a profile's objects to what the backend
holds, so base on RRI reads `[domainName, contact]`, instead of failing at start. Alternative: a startup error, which
makes {base, rri} impossible as D2 wants.
Q2 Where the offered set and the default live. Recommend the `profiles` and `default_profile` leaves of
`BackendProfile` (section B), not new top-level keys.
Q3 404 and 2303 for an unknown profile name on `GET /profiles/{name}`. Recommend yes.
Q4 501 and 2307 for the out-of-profile path (W1), also replacing the backend's 2101 on RRI `/hosts`. Recommend yes.
Q5 Is the constraint extension's schema file named `.spec/epp-compatibility.schema.json` with `$id` pointing at this
repository like the RRI one (there is no IANA registry entry to point at)? Recommend yes; its `url` in discovery is then
that `$id`.
Q6 Profile YAMLs list objects and extensions explicitly and `baseProfile` is informational plus the startup checks, no
inherited merging. Recommend yes (simple, matches D1).
