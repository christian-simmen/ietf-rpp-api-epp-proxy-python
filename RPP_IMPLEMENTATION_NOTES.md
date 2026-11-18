## Special handling behavior

- server changing caps of the domain name/host name -> make comparisons case-insensitive
- server changing order of entries in lists (contacts, IPs) -> list shall be treated unordered
- servers actually enforce unique clTRID
- test EPP server answers 2400 if clTRID is duplicated

## RPP design notes

- Presets, profiles and extensions (#174, #178): the proxy implements the accepted proposals in `.spec/proposals/174-presets/`.
  Not implemented: core RC6, a request for an operation that an applicable profile makes unavailable is 02308. No profile
  of the proxy makes an operation unavailable in its Profile Schema (the EPP Compatibility Profile does so in prose, and the
  proxy keeps today's 501 or the backend's error for the prose constraints). Where the proxy diverges from a proposal, or the
  proposals are silent, it is in [.spec/spec-issues.md](.spec/spec-issues.md#presets-profiles-and-extensions).

- client/server transaction ids with incomplete/invalid requests? yes/no?
- take a look into Retry-After header (to indicate temp errors)
- BODY missing on GET/DELETE"

  - https://github.com/swagger-api/swagger-ui/issues/2136#issuecomment-1055839700
  - https://github.com/spec-first/connexion/issues/1689
- see https://datatracker.ietf.org/doc/html/draft-gould-carney-regext-registry

  - full object update with UPDATE (check host and domain)
  - INFO with morphing answers (list or detail or even something else)
- Requirement: contact shall have clear contact type (and only one name field?)
- RPP-Code-Text ???

### Status codes

[x] domain not free (EPP 2302): 409
[x] domain not existing (EPP 2303): 404
[x] all other client-side errors: 400
[x] all server side errors: 500
