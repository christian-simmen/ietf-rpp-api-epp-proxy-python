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

- [~] 1. Bearer: a handler in `security_map` that skips the scheme without a warning (TDD; behaviour unchanged).
- [ ] 2. uvicorn 0.34.0 → 0.54.0; `UVICORN_TIMEOUT_WORKER_HEALTHCHECK=60` in the image.
- [ ] 3. Dockerfile healthcheck: `--start-period=180s --start-interval=5s`.
- [ ] 4. Role: `compose up --wait` per instance in turn, then one `up --remove-orphans` of all.
- [ ] 5. Docs: deploy/README.md, docs/agents where they describe these.
- [ ] 6. Local inventory `.deploy` (ignored): `rpp_proxy_workers: 1`.
- [ ] 7. Checks: lint-imports, unit, smoke, ansible-lint, syntax check, image build.

## Decisions

- Staggering covers deployments only; after a reboot the daemon starts every container. Tasks 2 and 3 cover that.

## Open questions

None.
