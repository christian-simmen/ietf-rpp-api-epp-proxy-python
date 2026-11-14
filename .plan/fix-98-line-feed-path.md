# Plan: a path with a line feed is a 404 Problem, not a 500 (#98)

Branch `fix/98-line-feed-path`, stacked on `fix/101-405-problem` (draft PR #150, issue #101, not merged). The PR
targets `main`; its description says it is stacked on #150 and that #150 merges first.

## Tasks

- [~] T1 `src/rpp/http/middleware/line_feed_path_middleware.py`: `LineFeedPathMiddleware`, one class per file,
      re-exported per the package convention (`middleware/__init__.py` is empty today: check the convention before
      adding an export)
- [ ] T2 `app.py`: `app.add_middleware(LineFeedPathMiddleware, position=MiddlewarePosition.BEFORE_ROUTING)`
- [ ] T3 Unit wire tests: GET and DELETE `/messages/a%0Ab`, GET `/hosts/a%0Ab`: 404, type, `errors[0].result` 02001,
      RPP-Code, RPP-Svtrid, RPP-Cltrid echo; `%0D`/`%09` not caught by the guard; Swagger UI paths unaffected
- [ ] T4 Docs: `architecture.project.md` middleware paragraph; `.spec/spec-issues.md` entry "Result code of an
      HTTP-level error" gets a line for the line-feed path
- [ ] T5 Checks: lint-imports, `pytest -n 4 tests/unit`, smoke `RPP_TEST_ENV=epp-docker pytest -n 8 -m smoke tests/integration`
      (MTEST pending, no allowlisted machine)

## Findings (evidence)

1. Root cause as verified by the orchestrator (connexion 3.2.0, starlette 0.46.1): the API Mount compiles to
   `^(?P<path>.*)$`, `.` does not match `\n`, so the request falls through to Flask and Connexion's decorator raises
   `RuntimeError: Working outside of operation context`: 500 `about:blank`, no RPP headers.
2. Connexion's stack order (ConnexionMiddleware): ServerError, Exception, Swagger UI, Routing, Security,
   validation... `BEFORE_ROUTING` sits after ExceptionMiddleware (so an `HTTPException` raised there goes through the
   #101 handler) and before SecurityMiddleware (so no 401 first) and before `BodyBufferingMiddleware`
   (`BEFORE_VALIDATION`), so the body of a refused request is never read.
3. `/nonexistent` today without credentials answers 404 (existing test `test_unknown_path_is_an_rpp_error` uses a
   client whose session pool fails on any use and sends no credentials). The guard matches that.

## Decisions (maintainer, via orchestrator)

1. A path containing a line feed answers 404 as a Problem Detail, as any path the API does not have. RPP-Code 02001
   via `_default_result`, consistent with #101. The spec-issues entry gets a line saying so.
2. Only the line feed is refused. Other control characters keep their behaviour.
3. Mechanism: one ASGI guard middleware at `BEFORE_ROUTING` raising `HTTPException(404)` when `"\n"` is in
   `scope["path"]`; the #101 handler renders it. (Confirmed below in the plan report, see open questions.)
4. Deliberate wire change, 500 to 404 Problem; stated in the commit message.

## Check results

(pending)

## Open questions

None. Note: the guard checks `scope["path"]` (decoded), http scope only (websocket and lifespan pass).
