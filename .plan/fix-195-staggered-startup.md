# Plan: instances unhealthy after a redeploy (#195, #189)

Branch `fix/195-staggered-startup`, from `main` at `c6d9e63`. The maintainer accepted the approach below. The
uncommitted changes of `main` (`.vscode/settings.json`, `deploy/ansible/ansible.cfg`, `config.rri-mtest.yaml.local`)
are carried along in the working tree and never committed.

## Findings

- Host: 2 vCPU, 3.8 GB, about 190 MB free, no swap, load about 9 during the deploy.
- All three instances were recreated at once: 9 workers building the app. uvicorn 0.34 pings each worker with a fixed
  5 s timeout (`supervisors/multiprocess.py`, `ping(timeout=5)`) and kills it otherwise: 26–30 `Child process [n] died`
  per container. The healthcheck (60 s start, 3 × 30 s) went unhealthy at about 05:56:30, the workers were all up by
  about 05:57:40, and the containers were healthy afterwards.
- `--timeout-worker-healthcheck` exists from uvicorn 0.37.0; uvicorn reads options from `UVICORN_*` variables.
- "x-bearerInfoFunc missing" (#189): `BearerAuth` is in the spec, but no handler; Connexion warns and skips the scheme.

## Tasks

- [x] 1. Bearer: a handler in `security_map` that skips the scheme without a warning (TDD; behaviour unchanged).
- [x] 2. uvicorn 0.34.0 → 0.54.0 (httptools 0.6.4 → 0.9.0, its `standard` minimum); `UVICORN_TIMEOUT_WORKER_HEALTHCHECK=60` in the image.
- [x] 3. Dockerfile healthcheck: `--start-period=180s --start-interval=5s`.
- [x] 4. Role: `compose up --wait` per instance in turn, then one `up --remove-orphans` of all.
- [x] 5. Docs: deploy/README.md, architecture.project.md (Composition).
- [x] 6. Local inventory `.deploy` (ignored): `rpp_proxy_workers: 1`.
- [~] 7. Checks: lint-imports (25 kept), unit (2691 passed), smoke (94 passed, 113 skipped, epp-docker, sqlite-demo and
  rri-mtest), ansible-lint (0 failures), syntax check, image built and run: healthy after about 15 s, no
  `x-bearerInfoFunc` line, uvicorn 0.54.0. Pending: a run of the playbook against the host.

## Decisions

- Staggering covers deployments only; after a reboot the daemon starts every container. Tasks 2 and 3 cover that.

## Corrections

- The image built from this working tree answered 500: some files under `src/` are not world-readable here
  (`src/rpp/handlers/contact/__init__.py`, mode 600 in the working tree, 644 in git). Built from a copy with `a+rX`
  it is fine. The host builds from a fresh clone, so this is local only.

## Open questions

None.
