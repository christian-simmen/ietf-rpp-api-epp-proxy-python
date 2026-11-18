# Plan: #207 deployment config templates use the profile settings renamed to presets

Branch `fix/207-deploy-preset-settings` from `main` (661ca57). The local changes to `.vscode/settings.json`,
`deploy/ansible/ansible.cfg` and the untracked `config.rri-mtest.yaml.local` are carried, never committed. The branch mutex
of #204 (PR #206, ready for review, nothing in progress) was taken over by the maintainer's request.

## Findings (evidence)

- F1 The running containers stop at startup: `ValueError: backend profile: unknown default_profile, profiles; missing
  none` (`BackendProfile.from_layers`). #178 renamed `profiles` / `default_profile` to `presets` / `default_preset`;
  `config.yaml`, `config.rri-mtest.yaml` and `config.demo.yaml` have the new names, the three templates in
  `deploy/ansible/inventory/example/configs/` the old ones.
- F2 `load_settings` ignores keys it does not know: `rpp_profile_signalling` (renamed `rpp_preset_signalling`) is dropped
  without an error, and `rri-mtest` would run with `header` instead of `media-type`.
- F3 No test renders the templates, and no process rule asks a change of configuration keys to update them.

## Decisions (maintainer, 2026-11-18)

- D1 The templates take the keys and values of the configuration each is made from: `epp` from `config.yaml` (`base`,
  `epp-compatible`), `rri-mtest` from `config.rri-mtest.yaml` (`base`, `rri`), `sqlite-demo` from `config.demo.yaml`
  (`base`, `planets`). The maintainer's `.deploy/configs/` copies get the same changes in place (not in git).
- D2 A unit test renders each template, checks that it states no key its repository configuration lacks, that the
  signalling and backend profile layers are the same, and composes the app from it.
- D3 Process rule: a change to configuration keys updates every configuration that uses them, the deployment templates
  included. The principle in process.md, the files in process.project.md.

## Tasks

- [x] T0 Issue #207, plan
- [~] T1 Test first: the templates rendered and loaded (fails on `main`)
- [ ] T2 Templates: keys, values and comments
- [ ] T3 `.deploy/configs/` copies (local)
- [ ] T4 Process rule (process.md, process.project.md)
- [ ] T5 Checks: lint-imports, unit, smoke; ansible-lint and syntax check in `deploy/ansible`

## Open questions

## Corrections

## Check results
