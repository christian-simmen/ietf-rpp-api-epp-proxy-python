# fix/152-docker-config (#152)

## Tasks
- [x] Reproduce: image built from main dies with FileNotFoundError on ./config.yaml
- [~] Dockerfile: ship config.yaml where the src/config.yaml symlink points
- [ ] Verify: image starts; lint-imports, unit tests, smoke

## Findings
- `src/config.yaml -> ../config.yaml` (since #25). Dockerfile copies `./src` to `/app`, so the link points to
  `/config.yaml`, absent in the image.

## Decisions
- `COPY config.yaml /config.yaml`: the image mirrors the repo layout (`/app` = `src/`, `/` = repo root), so the
  symlink resolves and no code or link changes. A deployment still overrides with `RPP_CONFIG_FILE` or a mount.
