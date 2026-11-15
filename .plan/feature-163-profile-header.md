# Plan: profile signalling with the RPP-Profile header (#163)

Branch `feature/163-profile-header`, stacked on `feature/162-profiles` (PR #165, merges first). The PR targets `main`
and says so. #164 (media type parameters) stacks on this branch.
Status: approved, implemented, checks running.

## Tasks

- [x] T1 Plan approved
- [x] T2 `rpp/http/profile_header.py`: parse and format the SF Dictionary of core §14.2 (see Decisions D3)
- [x] T3 `ProfileResolver.resolve(scope)` reads the header; `rpp_profile_signalling` in `Settings`, `compose`, `create_app`
- [x] T4 `ProfileMiddleware`: profile parameters in Accept/Content-Type are a 400; the `RPP-Profile` response header
- [x] T5 Unit tests (parser, resolver, wire: every response kind)
- [x] T6 Integration runner: `profile:` of the environment and of a case or step, sent in the configured method
- [x] T7 Environment yamls (`profile: epp`, `profile: rri`), configs (`rpp_profile_signalling: header`)
- [x] T8 Mixed cases 1 to 3 of the issue
- [x] T9 Docs (architecture.project.md, testing.project.md, README config) and `.spec/spec-issues.md`
- [x] T10 Checks, draft PR

## Findings (evidence)

1. `ProfileMiddleware` runs at BEFORE_VALIDATION, after security, and resolves the profile for every http scope, also
   an unrouted path; it refuses (501 02307) only routed operations (`profile_middleware.py`).
2. A `ProblemException` raised below the connexion ExceptionMiddleware is rendered by `handle_rpp_error` with the
   `send` of that outer middleware, so a `send` wrapper in `ProfileMiddleware` does not see Problem Details. They need
   the header added in `handle_rpp_error`, from the selected profile in `connexion_context`.
3. A 401 is produced by the security middleware before the profile middleware: no profile is selected for it.
4. `.spec/auto/openapi3/openapi.yaml` and `src/rpp/openapi.yaml` already declare `RPP-Profile` (string) on responses.
5. `profile.profiles` is a profile fact (keys offered), so cases select `{"profile.profiles": {"contains": "rri"}}`.
6. No SF library is installed; `http-sfv` 0.9.9 exists on PyPI.
7. core §12.4: an unsupported version MUST be rejected "and MUST return an RPP Client error code" (2xxx).
   §14.2: unsupported profile or version: "an HTTP error response" and a Problem Detail, no status named.

## Decisions (given by the orchestrator)

- D1 `rpp_profile_signalling: header | media-type` per server. This issue implements `header`; `media-type` is #164.
  `config.yaml` and `config.rri-mtest.yaml` use `header` (the latter until #164 switches it).
- D2 Header is an SF Dictionary (RFC 9651): `profile=<token>;version=<decimal>`. Malformed: 400. The Decimal problem
  (1.1 and 1.10 collide) goes in `.spec/spec-issues.md`.
- D3 Unknown profile, unknown version, or not offered by this server: 400, Problem Detail, RPP client error code.
  Without the header the default profile applies. Both gaps recorded in `.spec/spec-issues.md`.
- D4 On a header-mode server, profile parameters in Accept or Content-Type: 400.
- D5 Response `RPP-Profile` names the applied profile and version on every response where a profile was selected;
  absent when the profile itself was refused.
- D6 Integration tests as in the issue; select by profile facts, never by backend name; mind the MTEST limits.

## Decisions (answers of the orchestrator to the plan)

- D7 SF parsing is `http-sfv` 0.9.9, pinned in requirements.txt. Verified in its source: it has the RFC 9651 Date and
  Display String types, so it implements RFC 9651. After parsing: `profile` is a Token, `version` a Decimal; an Integer
  (`version=1`) is 400 `02005`.
- D8 Default `header` when `rpp_profile_signalling` is absent.
- D9 Codes, all 400: `02005` (malformed, wrong type, header twice), `02003` (no profile member or version), `02004`
  (profile or version unknown or not offered), `02001` (profile parameters in Accept/Content-Type). Extra members and
  parameters are ignored; recorded as a gap. Decimal comparison (1.10 is 1.1), recorded.
- D10 Only routed operations select a profile. `RPP-Profile` on every response after selection (also discovery,
  `/profiles/*`, Problem Details), absent on a 401, an unrouted path and the profile's own refusal. Discovery is not
  lenient.
- D11 Mixed case 2 on `profile.profiles contains rri`; cases 1 and 3 are `smoke`, case 2 is not.
- D12 The base profile is named `urn:ietf:params:rpp:profile:base` (maintainer, via the orchestrator). Done on
  `feature/162-profiles` (PR #165), checks run there, and this branch rebased onto it.

## Results

On the commit before this note (no edits during the runs):
- `PYTHONPATH=src lint-imports`: 15 kept, 0 broken.
- `pytest -n 4 tests/unit`: 2258 passed.
- `pytest -n 4 -m smoke tests/integration` (epp-docker and rri-mtest, run from this machine): 64 passed, 12 skipped
  (hosts on RRI, requestContact and the rri transfer on EPP).
- `profile_signalling/` (all three cases) also passed on both environments.
- The #165 rename commit: lint-imports, 2212 unit, smoke 60 passed and 12 skipped; noted in the description of #165.

## Open questions

None.
