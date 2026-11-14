# Plan: HTTP errors of the framework rendered as RPP errors (#101)

Branch `fix/101-405-problem`, from `main`. Follow-up #98 is stacked on this branch and not done here.

## Tasks

- [x] T1 `problem.py`: `handle_http_exception` converts `starlette.exceptions.HTTPException` into a `ProblemException`
      and renders it with `handle_rpp_error` (one rendering path, architecture rule 5)
- [x] T2 `app.py`: `app.add_error_handler(HTTPException, handle_http_exception)` next to the ProblemException one
- [x] T3 Unit wire tests: 405 on two paths (Allow kept), unknown-path 404; type, `errors[0].result`, RPP-Code,
      RPP-Svtrid, RPP-Cltrid echo
- [~] T4 Checks: lint-imports, `pytest -n 4 tests/unit`, smoke `RPP_TEST_ENV=epp-docker pytest -n 8 -m smoke tests/integration`
      (MTEST pending, no allowlisted machine)

      Added at approval: a test that a ProblemException path is unchanged (401, 02200); Allow compared as a set.

## Findings (evidence)

1. 405 comes from Starlette routing (`Route.handle` raises `HTTPException` with an `Allow` header). An unknown path
   gives a werkzeug NotFound that ends up as a Starlette `HTTPException(404)`.
2. Connexion 3.2.0 `ExceptionMiddleware.http_exception` renders both as `about:blank` with no RPP-Code, RPP-Svtrid,
   RPP-Cltrid and no `errors`.
3. Reproduce: `POST /.well-known/rpp` gives 405 `allow: GET, HEAD`; `PUT /messages` gives 405 `allow: POST`;
   `GET /nonexistent` gives 404.

## Decisions (maintainer, via orchestrator)

1. Scope includes the unknown-path 404.
2. One error handler for `starlette.exceptions.HTTPException` registered in `create_app`, converting to the rendering
   of `handle_rpp_error`: type `urn:ietf:params:rpp:error`, `errors` with `result`, status kept, headers of the
   exception (`Allow`) kept, RPP-Code, RPP-Svtrid, RPP-Cltrid echoed. Title from the HTTP status phrase.
3. RPP-Code from the existing `_default_result`, no new mapping: 405 and 404 give 02001.
4. Deliberate wire change: status codes unchanged; headers and body type change (about:blank to the RPP error type,
   RPP headers and `errors` added). Stated in the commit message.
5. #98 will raise `HTTPException(404)` from a guard middleware and rely on this handler. Not implemented here.

## Check results

lint-imports 15 kept; unit 2187 passed; smoke with `RPP_TEST_ENV=epp-docker` 34 passed, 38 skipped.
DENIC MTEST smoke: pending (no allowlisted machine).

## Review round 1

Fixes: spec issue "Result code of an HTTP-level error" in `.spec/spec-issues.md` (no code change); the 405 and 404
tests assert the reason; the ProblemException test now uses a registry error (404/02303, title "Object does not
exist") and fails when the ProblemException handler registration is removed (mutation checked); one clause in
`architecture.project.md`. `detail` is `null` in the body (Connexion `problem` always emits it), so the tests assert
`is None`, not absence. Checks re-run: lint-imports 15 kept, unit 2187 passed, smoke 34 passed, 38 skipped.

## Open questions

None.
