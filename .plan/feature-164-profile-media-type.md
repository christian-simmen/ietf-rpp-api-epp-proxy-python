# Plan: profile signalling with media type parameters (#164)

Branch `feature/164-profile-media-type`, stacked on `feature/163-profile-header` (#166), itself on
`feature/162-profiles` (#165). The PR targets `main`; merge order #165, #166, this one. Core §14.3 with §13.

## Tasks

- [x] T0 Plan approved by the orchestrator
- [x] T1 `rpp/http/media_range.py`: parse `Accept` and `Content-Type` (quoted and token values, q, wildcards)
- [x] T2 `ProfileSelection` (content profile, response profile); `HeaderProfileSignalling` (today's `ProfileResolver`,
      unchanged behaviour) and `MediaTypeProfileSignalling`, each with `resolve(scope)` and the response side
- [x] T3 Middleware, context and `handle_rpp_error` use the selection and the signalling; handlers render with the
      response profile and parse with the request profile
- [x] T4 Settings accept `media-type`; `create_app` and `main` pass it; `config.rri-mtest.yaml` switches
- [x] T5 Unit tests (parser, resolver, wire: 415, 406, 400, defaults, response Content-Type, Vary, no RPP-Profile)
- [x] T6 Runner: Accept and Content-Type carry the profile; runner unit tests
- [x] T7 Integration cases: 415, 406, 400, both methods, differing profiles
- [x] T8 Docs: architecture.project.md, testing.project.md, README, config comments, spec-issues.md
- [~] T9 Checks (lint-imports, unit, smoke on epp-docker and rri-mtest), draft PR

## Findings (evidence)

1. Today `ProfileResolver(profiles, signalling)` raises `ValueError` for anything but `header`, and `resolve(scope)`
   returns one `RppProfile`; `ProfileMiddleware` stores it as `rpp_profile` in the connexion context, and `context.py`
   (`selected_profile`, `request_profile`) hands it to every handler, for parsing and for rendering alike.
2. Handlers use `request_profile()` for the mappers (parse and check) and for `model_to_rpp(..., extensions)`
   (render): `domain_handlers.py` lines 28 and 99, plus the contact handlers.
3. Connexion already answers a `Content-Type` that is not `application/rpp+json` with 415 `02001`, and accepts
   parameters on it (probed). Nothing reads `Accept`: `text/html`, `application/xml` and `*/*` all answer 200 as
   `application/rpp+json` (header mode and no-profile media type negotiation of §13 are out of scope, see below).
4. `RPP_MEDIA_TYPE` is set in `headers.py`, `discovery.py` and `profiles.py` as a constant `Content-Type`.
5. The step `status` of a case may be a list (`assert_response`), so one case can expect 400 or 406.
6. `tchar` (RFC 9110 §5.6.2) has no `:`, so a profile URN cannot be a token; §14.3 says `profile-name = token` and
   its own example quotes the URN.

## Design

### Seam

`rpp/http/profile_selection.py`: `ProfileSelection(content: RppProfile | None, response: RppProfile)` with
`request` = `content or response`. Header mode: both are the named profile.

`ProfileResolver` becomes one class per method, same two-method interface, one file each:
`HeaderProfileSignalling` (the current code, moved, behaviour unchanged) and `MediaTypeProfileSignalling`.
- `resolve(scope) -> ProfileSelection`, raising `ProblemException`.
- `announce(send, selection)`: wraps `send` so the response shows the profile (header: `RPP-Profile` + `Vary`;
  media type: `Content-Type` parameters on a 2xx RPP response + `Vary: Accept`).
- `problem_headers(selection, headers)`: what `handle_rpp_error` adds (header: `RPP-Profile`, `Vary`; media type:
  `Vary: Accept`, no parameters).
`profile_signalling.py` maps the config value to the class. The middleware and `handle_rpp_error` call these and
no longer know a header name.

### Which profile governs what (proposal)

- Content profile (request with content): the mappers and schema validation, the extensions allowed in the body, the
  patch application, the backend command.
- Response profile: rendering (`model_to_rpp` extensions, the discovery and profile documents) and the response
  Content-Type.
- Request without content (GET, DELETE, HEAD): the response profile governs everything (there is no content profile).
- Object availability (501 `02307`): the object must be in the request profile (`content or response`) and in the
  response profile; the refusal names the profile that lacks it.
- Handlers: `request_profile()` (BackendProfile of `selection.request`, used for parsing and checking) and a new
  `response_profile()` (for rendering). Same in header mode, where they are equal.

### Parsing (`media_range.py`)

- `Accept`: all field lines joined, split at commas and `;` outside quoted strings (the splitter of `profile_header.py`
  moves here). A range is `type/subtype`, parameters, `q` (0 to 1, at most 3 decimals, the first `q` parameter ends
  the media type parameters, RFC 9110 §12.5.1). Parameter names are case-insensitive, values are a token or a
  quoted-string (unescaped) and equal either way. A duplicated `profile` or `profile-version` in one range, a bad `q`
  or a range that does not parse: 400 `02005`.
- `profile` without `profile-version`, or the reverse: 400 `02003` (core §12.4: a request using a profile MUST include
  its version). A version that is not `1*DIGIT "." 1*DIGIT`: 400 `02005`.
- Only `application/rpp+json` is an RPP media type here; other ranges are ignored for the profile. Header-mode
  refusal of profile parameters stays on `application/rpp+*`.

### Selection of the response profile from Accept

- No `Accept` header, or no profile parameters anywhere: the default profile.
- Each offered profile gets the `q` of the most specific range that matches it: exact range with its profile (3),
  `application/rpp+json` without parameters = the default profile only (2), `application/*` (1), `*/*` (0). A
  wildcard matches every offered profile. `q=0` excludes. This is RFC 9110 §12.5.1 precedence.
- Highest `q` wins. Tie: the content profile if it is among the tied ones, else the first in Accept order, else (a
  wildcard) the default.
- Nothing left (unknown profile or version, `q=0`, or no RPP range, e.g. `text/html`): 406.

### Content-Type

- Parameters on `application/rpp+json` are the content profile. An unsupported profile or version: 415.
- No parameters: the default profile when the request has content (content-length or transfer-encoding), else no
  content profile (a GET that sends a bare `Content-Type`, as §13 asks, has no content to be under a profile). Parameters
  are checked even without content.
- The content profile must be one the Accept selection lists with `q>0` (a wildcard lists all): otherwise 400.
- Content-Type that is not the RPP type stays connexion's 415 `02001`.

### Wire decisions (proposal)

| Rejection | Status | RPP code |
|---|---|---|
| unsupported profile or version in Content-Type | 415 | `02004` parameter value range error (as header mode for the same fault) |
| no supported profile in Accept | 406 | `02004` |
| Content-Type profile not listed in Accept | 400 | `02001` command syntax error |
| `RPP-Profile` request header on a media-type server | 400 | `02001` (header mode answers the same for the parameters) |
| missing `profile` or `profile-version` | 400 | `02003` |
| malformed value (version, q, duplicate, syntax) | 400 | `02005` |

Table 9 of core §18 maps none of these to a status, so the status is the one §13 and §14.3 give and the code is the
RPP one of the same fault in header mode.

Versions: `Decimal(profile.version) == Decimal(value)`, as header mode (1.10 is 1.1). The ABNF requires a point, so `1`
is a syntax error, as in header mode.

Response (media-type mode): a 2xx whose `Content-Type` is `application/rpp+json` gets
`application/rpp+json; profile="<name>"; profile-version="1.0"` (the response profile). Problem Details have none. No
`RPP-Profile` header (§14: the methods MUST NOT both be used in a response). `Vary` lists `Accept` on every response
of a routed operation, Problem Details included (they can be a 406). A refusal before the selection (415, 406, 400)
has no profile.

### Runner

`profile_headers` becomes the profile named in the request's headers: header mode adds `RPP-Profile`; media-type mode
rewrites a plain `application/rpp+json` in the step's `Accept`, and in `Content-Type` when the request has a body
(`json`/`data`), to `application/rpp+json; profile="<name>"; profile-version="1.0"`; adds `Accept` if the step has none. A
value that already carries a `profile` parameter stays (the step sends what it wants).

## Decisions

Approved by the orchestrator: the plan as written (structure, wire table, Decimal versions, quoted and token values, q and wildcard precedence, tie-break). Answers: (1) test3 expects `"status": [400, 406]`, 02004 and absent RPP-Profile exact, with a comment in the case; (2) bare range = default only, wildcards = all; (3) parse under the content profile, answer under Accept's preference; (4) `Vary: Accept` on every response of a routed operation. Further: header mode byte-identical on the wire, #163 unit tests green without edits but for the resolver rename; media-type 415/406/400 cases in profile_signalling/ selected by a fact (the runner exposes `rpp_profile_signalling` as `env.profile_signalling`); the spec-issues entries. Filed out of scope: #167 Accept not negotiated, #168 Content-Type on bodiless requests, #169 nosniff, #170 415 code 02001; mention in the PR. Decided before: config.rri-mtest.yaml `media-type`, config.yaml `header`; runner
format; the normative rejections of §14.3; `RPP-Profile` on a media-type server is 400 `02001`; no `RPP-Profile`
response header in media-type mode, with the tension with §6.2 recorded in spec-issues.)

## Open questions

1. test3 expects 400 for a profile the server does not offer, which §14.3 makes 406 (GET) in media-type mode. Recommend
   `"status": [400, 406]` there (the code `02004` and no `RPP-Profile` stay exact); test1 and test2 stay unchanged.
2. Bare `application/rpp+json` in Accept = default profile only, and wildcards = every profile (recommend). The
   alternative, bare = every profile, makes the §14.3 sentence "no parameters: default" untrue for Accept.
3. Differing profiles (content epp, Accept lists base and epp, base preferred): answer under base, parse under epp
   (recommend; the §14.3 reading). The alternative, answering in the content profile whenever it is listed, ignores
   Accept's `q`.
4. Vary: Accept on Problem Details too (recommend).

## Specification issues to add (.spec/spec-issues.md, "Profile signalling with media type parameters")

`profile-name = token` cannot hold a URN, §14.3's own example quotes it; no RPP codes for 415, 406, 400; §6.2
(`RPP-Profile` MUST in every response) against §14 (never both methods in one response); what a bare media range or a
wildcard in Accept means; no tie-break between equal `q`; the Content-Type profile of a request without content;
content and response profile may differ, and what a profile means for the object path or query parameters then;
a media range's parameters are not in the ABNF as separate parameters (`;` OWS joins them).

## Issues to file (out of scope; orchestrator files)

- `Accept` is not negotiated: header mode answers 200 `application/rpp+json` to `text/html`; no 406 without profiles
  (§13). Also no `Accept` header is accepted, where §13 says the client MUST send one.
- `Content-Type` is not required on a request without content (§13).
- `X-Content-Type-Options: nosniff` (§13 SHOULD) is never sent.
- A non-RPP `Content-Type` is 415 `02001` from connexion: the code is a choice nobody made.

## Check results

(pending)

## Implementation notes

- Wildcard tie: a wildcard stands for every offered profile at one position, so the default of the server is the one
  it means (`*/*` from curl answers the default, not the first offered profile).
- Mixed cases of #163 cannot pass byte-unchanged in media-type mode: test1 and test2 assert the `RPP-Profile` response
  header, which this mode does not send. Their expectations are now selects on `env.profile_signalling`: the header method
  keeps today's expectation, the media-type method expects the header absent and (success with content) the
  `Content-Type` with the parameters. test3: `[400, 406]` and a comment, as approved.
- #163 unit tests edited mechanically only: the resolver class rename and the `ProfileSelection` it now returns
  (`test_profiles_wire.py` `Selecting`, `test_profile_header_wire.py` `with_profile_header` -> `announce`), and
  `test_settings_signalling.py`, which asserted `media-type` is refused.
- New cases: test4 (415), test5 (406), test6 (400), test7 (both methods, both modes), test8 (content base, response
  under the server's profile); 4 to 6 and 8 `when env.profile_signalling` is `media-type`.

## Check results of the first implementation (commit 8d1ae7f)

lint-imports 15 kept; unit 2342 passed; smoke (epp-docker and rri-mtest) 70 passed, 16 skipped. This used the runner
that injected the profile; it is replaced, see below.

## Decisions of the maintainer after the plan (supersede the runner design above)

- The runner injects nothing: no `RPP-Profile`, `Accept` or `Content-Type` is added or rewritten, no per-case or step
  `"profile"` override. Every request states them with the placeholders `{rpp:profile}`, `{rpp:accept}`,
  `{rpp:content-type}`, resolved from the environment's `profile:` and its config's `rpp_profile_signalling`.
  `{rpp:profile}` resolves to "omit" in media-type mode. Done on #166 (`feature/163-profile-header`) first, then this
  branch is rebased on it.
- `Content-Type` is on every request, bodiless ones included (core §13).
- Two case sets, `profile_signalling_header/` (on #166) and `profile_signalling_media_type/` (here), literal values,
  activated by a case-level `when` on the new fact `env.profile_signalling`, read from the config.
- The request profile comes only from Content-Type, for every request, with or without a body; Content-Type without
  parameters, or absent, is the default profile. It alone governs routing, validation, mappers and the backend command.
  Accept governs only the response profile (rendering, response Content-Type, 406). The content profile must be listed in
  Accept for every request, else 400. The object check (501 `02307`) uses the request profile only. Rendering of an
  object the response profile lacks: it is rendered with the extensions of the response profile, which for a domain are
  none of the request profile's; the object itself is rendered, so nothing is lost but extension members.
  (Proposal: an object the response profile does not hold cannot be told apart from one it does, since the profiles
  list objects for the endpoints; the response cannot show the members it does not declare, so they are left out.)
- spec-issues: §14.3 speaks of "request content", §13 requires Content-Type even without content, so the proxy takes the
  request profile from Content-Type always.

Confirmed by the orchestrator: where the response profile lacks something the request profile has, render with the response profile's extensions, leaving out the request profile's extension members; recorded in spec-issues as a gap. #164 is not rebased until the findings of #166's review round 3 are in.

## Step 3 (after #166 round 3)

- #164 rebuilt on `feature/163-profile-header` (d933566): the server side re-applied, the old runner and cases dropped.
- The request profile is read from Content-Type only, for every request (absent or bare: default); `ProfileSelection`
  is now `request` and `response`; the 501 `02307` check uses the request profile; the request profile must be listed in
  Accept for every request (400 `02001`), also for a GET.
- Cases: `profile_signalling_media_type/` test1 to test9 (literal headers, `when env.profile_signalling` media-type);
  `profile_signalling_header/test4` (both methods) added; `profile_signalling_header/test2` (rri-only refusals) removed,
  since no environment runs RRI with the header method and the harness refuses a case no environment runs. Its content is
  `profile_signalling_media_type/test2`; the header method on RRI stays covered by `test_profile_header_wire.py`.
