# Plan: RRI REQUEST contacts as an RPP data object (#131)

Branch `feature/131-rri-request-contacts` from `main` @ 038f736. Builds on the `rri` extension of #133.

## Tasks

- [x] T1 Plan, agreed with the maintainer
- [x] T2 Spec. `docs/rri/rri-extension.md` in the structure of guidelines §9, which replaces
      `.spec/spec-rri-extension.md` (transfer and request contacts). Schema `.spec/rri-extension.schema.json` →
      version `0.2.0`, id `de.denic.rpp.rri`. Unclear points of the guidelines → `.spec/spec-issues.md`. Gap analysis
      Q2 and §3.2 settled, links fixed. `.spec/draft-wullink-rpp-extension-guidelines.clean.txt` added
- [x] T3 Schema and routing. Extension defs `ext.rri.requestContact.{create,read,update,reference}` and
      `ext.rri.domainName.{create,read,update}`. `rpp:extends` adds `generalRequest` and `abuse` to
      `domainName.create/read/update` and to `domainTransferProcess.create`, and drops them from that one's
      `contacts`. The validator validates an extension's own objects. The `/requestContacts` paths are derived from
      the `/contacts` ones when the app is built, only where the profile offers the extension
- [x] T4 Core. `RequestContact` model (id, uriTemplate, sponsor, upDate). `RequestContactGateway` port (check,
      info, create, replace), `RegistryBackend.request_contacts`, flows for create, replace and patch (read-modify-
      write). `Domain` and `DomainReplacement` get `generalRequest` and `abuse` as fields of their own, out of
      `contacts`. Profile: `objects` + `requestContact`, `domainName.contacts.labels: []`
- [x] T5 RRI adapter. CREATE, INFO, UPDATE, CHECK of type REQUEST. Contact INFO of a REQUEST handle, and request
      contact INFO of a PERSON/ORG handle → 404. The domain state reads and writes the new fields. EPP adapter: no
      request contact gateway (the paths do not exist there)
- [x] T6 RPP adapter. DTOs, mapping, handlers `requestContacts_*`. Domain mapping of `generalRequest` and `abuse`.
      PATCH of `/generalRequest` and `/abuse` reads first
- [x] T7 Tests. Unit: mapping, schema, RRI wire and adapter, profile. Integration: a group `request_contact/`
      (where the backend has the object). The 26 cases with `{gen_req:a}` and `{abuse:a}` create their REQUEST
      contacts in a first step and use the new properties. The placeholders, `TEST_RRI_REGACCn_GEN_REQ` and `_ABUSE`
      go (`.env.example`, `rri-mtest.yaml`, `test_environment.py`, `testing.project.md`)
- [x] T8 Docs. `architecture.project.md` (extension endpoints), `overview.project.md` link, `testing.project.md`
- [x] T9 Checks: `lint-imports`, unit, smoke. MTEST smoke from an allowlisted machine (or recorded as pending)
- [x] T10 Draft PR #148, waiting for the maintainer

## Findings (evidence)

1. Today `GET /contacts/{id}` of a REQUEST handle answers 501 `02102`
   (`registry_adapter/rri/commands/contact/info.py`). The domain carries the REQUEST handles as `contacts` labelled
   `generalRequest` and `abuse` (`rri.yaml`, `rri/commands/domain/common.py` `ROLES`).
2. A REQUEST contact is a handle and a URI template (RFC 6570 level 1, 8–1024 characters, http/https/mailto,
   variables `{Alabel}` and `{Ulabel}`) and nothing else. Verification blocks are refused (`63450064002`). Handles
   share one namespace with PERSON/ORG (rri-5.0-reference.md §5.1).
3. Inheritance (data-objects §2.5, `Extends`) does not fit. A derived object inherits `contactInfo` (1, a Card) and
   `status` (1+) and cannot relax them, so a REQUEST contact would carry an empty Card and a made-up status. The
   template is no URI (`{Alabel}`), so it cannot go into the Card's `links`. Adding `uriTemplate` to `contact` also
   leaves `contactInfo` required. A new object repeats only `id` and `provMetadata` (guidelines §6 item 4).
4. Core §16.1.1 `plural()`: the collection of `requestContact` is `/requestContacts`.
5. The OpenAPI document is generated from the drafts (`copy_models.sh`). Its response schemas are the base ones
   (`gen.domainName.read`), which do not forbid more members.
6. 26 integration case files use `{gen_req:a}` / `{abuse:a}`.

## Decisions

- D1 (maintainer) A new data object `requestContact` (variant A), not one derived from `contact`.
- D2 (maintainer) The extension id is reverse-domain, `de.denic.rpp.rri`; member names stay short
  (`requestContact`, `generalRequest`, `abuse`, `uriTemplate`).
- D3 (maintainer) The extension spec moves to `docs/rri/rri-extension.md`; the schema stays in `.spec/`.
- D4 (maintainer) Operations: create, read, update (PUT and PATCH), availability. Delete answers 501 (`02101`).
- D5 `GET /contacts/{id}` of a REQUEST handle answers 404, it is not a contact (was 501). Likewise
  `/requestContacts/{id}` of a PERSON/ORG handle.
- D6 `domainName.generalRequest` and `domainName.abuse`: 0-1, read-write, Aggregation[requestContact]. On RRI
  `contacts` keeps only further holders (`registrant`). A label `generalRequest` or `abuse` in `contacts` answers
  501 (`02102`) as `admin` does.
- D7 Wire changes, deliberate: discovery lists the extension as `de.denic.rpp.rri` version `0.2.0`; an RRI domain
  read shows the REQUEST contacts as properties, not in `contacts`; the transfer extension takes them the same way.
- D8 The proxy checks only the length of a template (schema). DENIC checks the rest (`83000000005`) → 400.

## Corrections

- C1 (T4) The core does not get fields of its own for the two roles. `Domain.contacts` and
  `DomainReplacement.contacts` already carry a reference per role, which `domain_difference`, `domain_application`
  and the RRI domain state compare and write. The roles `generalRequest` and `abuse` stay there, and the separation
  is in the RPP representation: `rpp/mapping/domain/domain_request_contacts.py` maps the members an offered
  extension adds to and from those roles, and `contacts` no longer shows them. Changing the core would touch the EPP
  adapter and both model conversions for no difference on the wire.
- C2 (T3) The extension states the objects it defines in `rpp:extension.objects`; the validator takes their
  definitions by the name without `ext.rri.` (`requestContact.create`). The OpenAPI schemas of the derived paths are
  plain objects, the mappers validate with the extension's schema.

- C3 (T7, maintainer review) A domain needs no request contact on RRI (ref §5.2: 0-1 each; a create without them
  passes on MTEST). The profile states it as `domainName.generalRequest` and `domainName.abuse`, `min_count` 0 and
  `max_count` 1 (0 and 0 on EPP). The cases that work alike on both backends no longer create or send request
  contacts; only `domain_transfer_ext/`, `domain_update/test37` and `limits_domain/test20` do, selected on
  `max_count` at least 1, and `request_contact/` on the object. `limits_domain/test20` lost its skip (it creates two
  handles now) and is pinned to 400 `02001`.

## Checks (2026-11-14)

- `lint-imports`: 15 contracts kept. Unit: 2168 passed.
- Smoke, both environments, MTEST from this machine: 60 passed, 12 skipped. `draft_discovery/test1` now expects
  `requestContact` in the objects of RRI.
- The 28 changed case files and `request_contact/` on both environments: all passed or skipped by their selectors
  (the RRI branches of the cases that need `admin` or hosts were skipped there before too). MTEST answers 403
  (`02201`) to another RegAcc's request contact (`request_contact/test7`) and 400 (`02005`) to an `ftp` template.

- After C3: `lint-imports` kept, unit 2170 passed, smoke 60 passed and 12 skipped on both, the changed cases and
  `request_contact/` 45 passed and 27 skipped by their selectors.

## Open questions

- `.env` still holds `TEST_RRI_REGACCn_GEN_REQ` and `_ABUSE`, which nothing reads now; the maintainer removes them.
