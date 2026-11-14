# docs/readme-docker-epp

## Tasks
- [~] README: set up the local EPP test server (EPP-server-docker), run the proxy against it from source and in docker
- [ ] Draft PR (docs only: the test steps are skipped)

## Findings
- EPP-server-docker README: setup and run profiles, registrars foo/bar (FO-) and baz/qux (BZ-), TLS on 743 inside,
  7043 on the host.
- config.yaml names `epp-server:743` on the compose network `epptest_epp_net`, so the compose project is `epptest`.
- Run from `src/`, `./config.yaml` is the symlink and `./config.local.yaml` is not looked for at the root:
  `RPP_CONFIG_FILE=../config.yaml` makes the root config.local.yaml apply.
- Verified: image on `epptest_epp_net`, `HEAD /domainNames/x.example/availability` answers 200 (EPP 1000).
