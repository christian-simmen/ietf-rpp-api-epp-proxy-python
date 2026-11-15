# Plan: profile signalling with the RPP-Profile header (#163)

Branch `feature/163-profile-header`, stacked on `feature/162-profiles` (PR #165, merges first). The PR targets `main`
and says so. #164 (media type parameters) stacks on this branch.
Status: plan, waiting for the orchestrator's approval.

## Tasks

- [~] T1 Plan approved
- [ ] T2 `rpp/http/profile_header.py`: parse and format the SF Dictionary of core §14.2 (see Decisions D3)
- [ ] T3 `ProfileResolver.resolve(scope)` reads the header; `rpp_profile_signalling` in `Settings`, `compose`, `create_app`
- [ ] T4 `ProfileMiddleware`: profile parameters in Accept/Content-Type are a 400; the `RPP-Profile` response header
- [ ] T5 Unit tests (parser, resolver, wire: every response kind)
- [ ] T6 Integration runner: `profile:` of the environment and of a case or step, sent in the configured method
- [ ] T7 Environment yamls (`profile: epp`, `profile: rri`), configs (`rpp_profile_signalling: header`)
- [ ] T8 Mixed cases 1 to 3 of the issue
- [ ] T9 Docs (architecture.project.md, testing.project.md, README config) and `.spec/spec-issues.md`
- [ ] T10 Checks, draft PR

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

## Proposals (waiting for an answer)

See the report of the plan checkpoint.

## Open questions

(see above)
