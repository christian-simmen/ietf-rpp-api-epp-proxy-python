# Plan: presets, profiles and extensions (#174)

Branch `feature/174-presets` from `main` (`f370121`). The requirements and acceptance criteria are in #174.

## Tasks

- [x] T0 Agent docs for specification writing (`docs/agents/specification.md`, `specification.project.md`), imported
      from the data-objects `Agents.md` (`2438b83`), linked from `Agents.md`, `requirements.md` and
      `architecture.project.md`
- [~] T1 Proposal for draft-ietf-rpp-data-objects: concepts, Preset and Profile Data Objects, Discovery, IANA, the EPP
      Compatibility Profile as a profile (`.spec/proposals/174-presets/data-objects.md`)
- [ ] T2 Proposal for draft-ietf-rpp-core: `RPP-Preset`, `preset`/`preset-version`, versioning, 02308
- [ ] T3 Proposal for draft-ietf-rpp-json: additive-only Extension Framework, profile schema composition, Profiles and
      Validation, the JSON Schema part of the EPP Compatibility Profile
- [ ] T4 Proposal for draft-wullink-rpp-extension-guidelines: a specification format for profiles
- [ ] T5 Link the approved proposals from #174
- [ ] T6 Implementation plan for the proxy (tasks added here once T1-T4 are approved)

## Findings (evidence)

1. data-objects §2.3.2: extensions may add data elements, and "MUST NOT alter the semantics or constraints of existing
   core data elements", which allows an extension to make its own members required.
2. data-objects §4 Profiles and the Profile Data Object: a profile is a bundle of objects and extensions with versions,
   a `baseProfile` of depth 1 that may override, and a `defaultProfile` flag. This is the preset of #174.
3. data-objects §2.8: the EPP Compatibility Profile is a set of constraints only. This is the profile of #174.
4. core §12.3, §12.4 and §14: the client selects the extensions through the profile, signalled by `RPP-Profile` or the
   media type parameters `profile` and `profile-version`.
5. json Extension Framework: the example extension adds `"required": ["foo"]`. json "RPP Profiles and Validation":
   profile constraints are enforced beyond JSON Schema.
6. The proxy models EPP Compatibility as an extension that adds nothing (`.spec/epp-compatibility.schema.json`), and its
   configured profiles `base` and `epp` are presets in the sense of #174.

## Decisions

- D1 (maintainer) Extension adds only, profile narrows only (required, cardinality, enum subset, forbidden field), in
  JSON Schema where possible and prose otherwise. Distinct identifiers even in one document.
- D2 (maintainer) The client signals only the preset. Profiles reach a request through the preset definition and the
  server's binding, which is static and published.
- D3 (maintainer) Profile requirements on extensions are transitive.
- D4 (maintainer) Presets can be standardised and can include profiles. A server binds further profiles outside the
  definitions. Discovery shows both kinds separately.
- D5 (maintainer) No extension per request.
- D6 (maintainer) Multiple inheritance for presets and profiles, as a union without overriding. Cycles and two
  versions of one extension are invalid.
- D7 (maintainer) A broken profile constraint is 02308 (422), JSON Schema or not. A broken preset schema stays 400.
- D8 (maintainer) Wire names `RPP-Preset`, `preset`/`preset-version`, `/presets/{id}`, `/presets/{id}/schema`,
  `/profiles/{id}`. No backward compatibility in the proxy.
- D9 (maintainer) The proposals are files under `.spec/proposals/174-presets/`, one per draft, reviewed one at a time.

## Corrections

## Open questions

- `.vscode/settings.json` and `config.rri-mtest.yaml.local` were changed on `main` before the branch. They are the
  maintainer's and are left unstaged.
