# Plan: presets, profiles and extensions (#174)

Branch `feature/174-presets` from `main` (`f370121`). The requirements and acceptance criteria are in #174.

## Tasks

- [x] T0 Agent docs for specification writing (`docs/agents/specification.md`, `specification.project.md`), imported
      from the data-objects `Agents.md` (`2438b83`), linked from `Agents.md`, `requirements.md` and
      `architecture.project.md`
- [x] T1 Proposal for draft-ietf-rpp-data-objects: concepts, Preset and Profile Data Objects, Discovery, IANA, the EPP
      Compatibility Profile as a profile (`.spec/proposals/174-presets/data-objects.md`)
- [x] T2 Proposal for draft-ietf-rpp-core: `RPP-Preset`, `preset`/`preset-version`, versioning, 02308
- [x] T3 Proposal for draft-ietf-rpp-json: additive-only Extension Framework, profile schema composition, Profiles and
      Validation, the JSON Schema part of the EPP Compatibility Profile
- [x] T4 Proposal for draft-wullink-rpp-extension-guidelines: specification formats for profiles
      and presets, with an example profile (Appendix B) and an example preset (Appendix C)
- [~] T4a (draft written, in review) Proposal for a new draft, the RPP EPP Compatibility Profile, with the EPP
      elements copied from data-objects, core and json (`.spec/proposals/174-presets/draft-kowalik-rpp-epp-compatibility.md`, renamed
      and edited by the maintainer)
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

- D1 (maintainer) Extension adds only, profile constrains only (required, cardinality, enum subset, forbidden field), in
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
- D10 (maintainer) The data-objects proposal is accepted with R1-R7 as drafted. The maintainer removed three rules of
  Profile Binding: that bound profiles do not depend on the client or the request, that a server SHOULD state every
  constraint on the form of a request in a profile, and that it SHOULD announce a change of its bound profiles.
- D12 (maintainer) The schema of a preset is the Direct Access data element `schema` of the Preset Data Object
  (Common Data Type Representation Schema, Visibility onDemand). Direct Access is allowed on any data element of
  cardinality 0-1 or 1. Authentication of the Read operation, and so of the schema, is server policy. A value not
  wrapped in an RPP message is served in its native media type, so media type signalling cannot carry its preset.
  This amends the accepted data-objects proposal (R6) and replaces RC3 of the core proposal.
- D13 (maintainer) The core proposal is accepted with RC1-RC7 as drafted.
- D14 (maintainer) The json proposal is accepted with RJ1-RJ9 as drafted.
- D15 (maintainer) The EPP Compatibility Profile gets its own draft. Its constraints, Profile Schema and registrations
  are copied into it and stay in data-objects, core and json for now.
- D16 (maintainer) The Profile Schema of the EPP Compatibility Profile also constrains the JSContact Card of
  `contact.create`, `contact.read` and `contact.update`: name, address with locality and at most three street lines,
  email, US-ASCII internationalised form, one localisation, the telephone format, and `authInfo` on create. New
  constraint: one email, at most one voice and one fax number (RFC 5733). Map entries are constrained through
  `additionalProperties`, `required` and `propertyNames`, so no property is declared that the Card does not declare.
- D17 (maintainer) The EPP Compatibility Profile constrains a localization entry with JSContact patch semantics: no
  `emails`, a localized `name` with `full`, a localized organization with `name`, a localized address complete
  (`countryCode`, locality, at most three street lines). The base definition of the entry is requested upstream in
  SIDN/ietf-rpp-jscontact-profile#36, together with moving the Card schema from json to the JSContact profile draft.
- D18 (maintainer) The guidelines proposal is accepted with RG1-RG7 as drafted, plus the Example Preset appendix
  (Appendix C) and the composition example of the Example Extension aligned with it.
- D11 (maintainer) The agent docs for specification writing go to `main` in their own PR,
  `docs/specification-agent-docs`. This branch is stacked on it.

## Corrections

- C1 The accepted json proposal did not say how the Preset Schema composes an extension sub-schema that a profile
  constrains (the case of the Example Profile of the guidelines). Added as a bullet of its Preset Schema section.

## Open questions

- `.vscode/settings.json` and `config.rri-mtest.yaml.local` were changed on `main` before the branch. They are the
  maintainer's and are left unstaged.
- The EPP Compatibility Profile draft awaits the maintainer's review.
