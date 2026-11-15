# RPP Profile Schemas extension

A proxy extension (extension guidelines §9) that lets a client fetch the schema a profile enforces.

| | |
|---|---|
| Id | `urn:ietf:params:rpp:extension:profile-schemas` |
| Name, version | RPP Profile Schemas, 1.0 |
| Schema | [.spec/profile-schemas.schema.json](../.spec/profile-schemas.schema.json) |
| Extends | `discovery.read`, with the member `profileSchemas` |
| Scope | server-wide: every offered profile has an effective schema, so the extension is in no profile |

## Discovery

`profileSchemas` is an array with one `{profile, version, url}` per offered profile: the profile's name and version, and
the URL of its effective schema, `rpp_base_url` plus `/profiles/<name>/schema` (the name URL-encoded as one path
segment). The Discovery `extensions` member lists the extension.

## The schema

`GET /profiles/{name}/schema` answers the effective schema of an offered profile as `application/schema+json`, without
authentication (as discovery); a name the server does not offer is a 404 with `02303`. The document is a JSON Schema
2020-12 with `$id` the URL above. Its `$defs` hold the definitions of the drafts and those of the profile's extensions.
A definition an extension extends (`domainName.create` for `de.denic.rpp.rri`) is the `allOf` of the base definition and
the extension's, which is what the proxy validates a request with (json §7.2), so what is published is what is enforced.
The members a profile does not have are absent: a body with an rri member is valid under the rri profile's schema and
not under base's.
