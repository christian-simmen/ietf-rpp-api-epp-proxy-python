# Plan: fix #193, /openapi.json answers 500 after the first discovery request

## Tasks

- [~] Snapshot middleware: a `SwaggerUIMiddleware` that serves a clone of the spec taken at startup
- [ ] `create_app` uses it in place of connexion's `SwaggerUIMiddleware`
- [ ] Unit test: after discovery, `/openapi.json` and `/openapi.yaml` answer 200 and the same document as before
- [ ] Checks: lint-imports, unit tests, smoke suite

## Findings

- Reproduced on `main` at 8fc9097: `/openapi.json` 200, `GET /.well-known/rpp` 200, `/openapi.json` 500.
- `OpenAPIOperation.with_definitions` (connexion/operations/openapi.py:136) writes `components` into the inline
  response schema of the live spec. `SwaggerUIAPI._spec_for_prefix` calls `with_base_path` → `clone`, which
  re-validates that spec: `components` is not allowed there, `InvalidSpecification`.
- All connexion middlewares get the same `Specification` object.

## Decisions

- Maintainer chose the snapshot middleware over a route of our own (`serve_spec: False`): `/openapi.json`,
  `/openapi.yaml`, `/ui` and the base-path rewriting stay connexion's code, the document is the same as today's first
  answer.
- Mutex of #178 taken over on the maintainer's word; local changes on `main` left in place, never staged.

## Open questions

None.
