%%%
title = "Profile Schemas Extension for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Profile Schemas Extension"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "registry", "extension", "profile", "JSON Schema"]
TocDepth = 4
date = 2026-11-15

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-profile-schemas-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines an extension of the RESTful Provisioning Protocol (RPP) that lets a server publish the Effective Schema of each profile it offers. The extension adds the `profileSchemas` data element to the Discovery Data Object and defines the operation that reads the Effective Schema of a profile.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the extension, the specifications it builds upon, and the reasons for the extension points it uses.

The RESTful Provisioning Protocol (RPP) is defined by [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], and [@!I-D.ietf-rpp-json]. A server offers one or more profiles [@!I-D.ietf-rpp-core, section 12.4], and each profile supports a set of extensions. The base specifications give the JSON Schema of the base objects and of each extension as separate documents, and require a deployment to combine them for the extensions of a profile and to inject `"unevaluatedProperties": false` before validation [@!I-D.ietf-rpp-json, section 4.9.1] [@!I-D.wullink-rpp-extension-guidelines, section 8.6]. They define no way for a client to obtain the result, so a client cannot validate a request against what the server enforces without repeating the composition. This document follows the extension specification format of [@!I-D.wullink-rpp-extension-guidelines, section 9].

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

Terms of the RPP data model are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Extension Mapper (`rpp:extends`) and Effective Schema are used as defined in [@!I-D.ietf-rpp-json].

## Choice of Extension Points {#choice}

This section is non-normative.

The extension changes the Discovery Data Object, because a new Discovery property comes from an extension [@!I-D.wullink-rpp-extension-guidelines, section 5.13], and defines no new Data Object. The Effective Schema is a document of a profile and not a data object of the registry, so it has an operation of its own below the Profile Data Object's path, `/profiles/{name}/schema`, and no Data Object. The extension is server-wide: every offered profile has an Effective Schema, so no profile lists the extension.

# Extension Overview {#overview}

This section identifies the extension.

| Field                | Value                                                                                         |
| -------------------- | --------------------------------------------------------------------------------------------- |
| Name                 | RPP Profile Schemas                                                                           |
| Identifier           | `urn:ietf:params:rpp:extension:profile-schemas`                                               |
| Version              | 1.0                                                                                           |
| RPP version          | [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], [@!I-D.ietf-rpp-json]                   |
| Schema `$id`         | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/profile-schemas.schema.json> |
| Changed base objects | `discovery`                                                                                   |
| New objects          | None                                                                                          |
Table: Extension Overview

# External Data Types {#external-data-types}

None.

# Result Codes {#result-codes}

None. The extension uses the result codes of [@!I-D.ietf-rpp-core, section 18]. A name that the server does not offer is `02303` (object does not exist).

# Problem Details {#problem-details}

None.

# HTTP Headers {#http-headers}

None.

# Discovery Document {#discovery}

This section states the additions of the extension to the Discovery document.

A server that supports the extension lists it in the `extensions` of its Discovery document with the values of (#overview). The extension is not part of a profile: the server lists it next to the extensions of its profiles.

# Updated Data Objects {#updated-data-objects}

This section defines the data elements that the extension adds to existing Data Objects.

## Discovery Data Object {#discovery-object}

### Data Elements {#discovery-data-elements}

| Element Identifier | Element Name    | Card. | Mutability | Data Type                  | Description                                                              |
| ------------------ | --------------- | ----- | ---------- | -------------------------- | ------------------------------------------------------------------------ |
| profileSchemas     | Profile Schemas | 1+    | read-only  | List of Profile Schema     | Where the Effective Schema of each profile the server offers is published. |
Table: Data elements added to the Discovery Data Object

The Profile Schema component object has the following data elements:

| Element Identifier | Element Name | Card. | Mutability | Data Type | Description                                                                 |
| ------------------ | ------------ | ----- | ---------- | --------- | --------------------------------------------------------------------------- |
| profile            | Profile      | 1     | read-only  | String    | The name of the profile, as listed in the `profiles` of the Discovery document. |
| version            | Version      | 1     | read-only  | String    | The version of the profile.                                                 |
| url                | URL          | 1     | read-only  | String    | The URL of the Effective Schema of the profile, see (#schema-operation).    |
Table: Profile Schema component object

The list has one entry for each profile in the `profiles` of the Discovery document. The `url` is the base URL of the server, as in the `baseUrl` of its Discovery version, followed by the path of (#endpoints) with the name of the profile encoded as one path segment [@!RFC3986].

### Operations {#discovery-operations}

None. The Read operation of the Discovery Data Object is unchanged.

# New Data Objects {#new-data-objects}

None.

# Updated Process Objects {#updated-process-objects}

None.

# New Process Objects {#new-process-objects}

None.

# Endpoints {#endpoints}

This section lists the endpoint of the extension. This section is non-normative.

| Operation                         | HTTP Method | URL path                  |
| --------------------------------- | ----------- | ------------------------- |
| Profile Schema: read              | GET         | /profiles/{name}/schema   |
Table: Endpoint of the extension

## Schema Operation {#schema-operation}

Request: GET /profiles/{name}/schema

Request message: None

Response message: the Effective Schema of the profile, a JSON Schema document [@!JSON-SCHEMA] with the media type `application/schema+json`.

The operation needs no authentication and no registry command, as the Discovery operation. It reads a document and is not an RPP operation: the profile of the request is not selected, so `RPP-Profile` and the media type parameters of the request are ignored and the response names no profile, and `RPP-Cltrid` is optional, so that a generic JSON Schema client that resolves the `$id` of the schema can fetch it. A client sends `Accept` with `application/schema+json`, `application/json`, `application/*` or `*/*`, or none; any other `Accept` is a 406 with the result code `02004`. The response has `Vary: Accept`.

| Case                                    | HTTP status | RPP result code |
| --------------------------------------- | ----------- | --------------- |
| the profile is offered                  | 200         | 01000           |
| the server does not offer the name      | 404         | 02303           |
Table: Results of the schema operation

The Effective Schema of a profile is the combined schema of [@!I-D.wullink-rpp-extension-guidelines, section 8.6] for the extensions of the profile: its `$defs` hold the definitions of the base specifications and those of the extensions of the profile. Each definition that an extension extends is the `allOf` of the base definition and the definition of every extension of the profile, composed through the Extension Mapper of that extension. `"unevaluatedProperties": false` is injected at every object-schema node, except a node that has `unevaluatedProperties` or `additionalProperties` already, and, for a composed definition, on the node that holds the `allOf` and not in its branches, so that the members an extension adds are evaluated. The document has the `$id` of the URL of the Profile Schema. A server MUST validate requests with the schema it publishes.

# JSON Schema {#json-schema}

This section defines the JSON representation of the updated object, following the rules of [@!I-D.ietf-rpp-json, section 4] and the Extension Framework of [@!I-D.ietf-rpp-json, section 7].

The extension defines one JSON Schema document, <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/profile-schemas.schema.json>. Every definition of the extension has the prefix `ext.profileSchemas.`.

## Extension Mapping {#extension-mapping}

```json
{
  "rpp:extends": {
    "#/$defs/discovery.read": "#/$defs/ext.profileSchemas.discovery.read"
  }
}
```

The schema document states the Name, Identifier, and Version of (#overview) in the property `rpp:extension`:

```json
{
  "rpp:extension": {
    "name": "RPP Profile Schemas",
    "id": "urn:ietf:params:rpp:extension:profile-schemas",
    "version": "1.0"
  }
}
```

## Discovery Data Object {#json-discovery}

<!-- definition ext.profileSchemas.discovery.read -->
```json
{
  "$defs": {
    "ext.profileSchemas.discovery.read": {
      "type": "object",
      "properties": {
        "profileSchemas": {
          "type": "array",
          "items": { "$ref": "#/$defs/ext.profileSchemas.profileSchema" },
          "minItems": 1,
          "readOnly": true
        }
      },
      "required": ["profileSchemas"]
    }
  }
}
```

<!-- definition ext.profileSchemas.profileSchema -->
```json
{
  "$defs": {
    "ext.profileSchemas.profileSchema": {
      "type": "object",
      "properties": {
        "profile": { "type": "string" },
        "version": { "type": "string" },
        "url": { "type": "string", "format": "uri" }
      },
      "required": ["profile", "version", "url"]
    }
  }
}
```

The schema document of the extension MUST NOT contain `unevaluatedProperties` or `additionalProperties` set to false, see [@!I-D.wullink-rpp-extension-guidelines, section 8.6].

# Examples {#examples}

Example Discovery document of a server that offers the base profile and the profile of the DENIC RRI extension:

<!-- example valid discovery.read -->
```json
{
  "@type": "discovery",
  "versions": [{ "@type": "discoveryVersion", "version": "1.0", "baseUrl": "https://rpp.example" }],
  "environment": { "@type": "discoveryEnvironment", "name": "rpp.example", "status": "production" },
  "tlds": ["de"],
  "objects": ["domainName", "contact", "requestContact"],
  "datetime": "2026-11-15T12:00:00Z",
  "profiles": ["urn:ietf:params:rpp:profile:base", "de.denic.rpp.profile.rri"],
  "extensions": [
    { "@type": "extension", "name": "DENIC RRI", "id": "de.denic.rpp.rri", "version": "0.2.0", "url": "https://example.org/rri-extension.schema.json" },
    { "@type": "extension", "name": "RPP Profile Schemas", "id": "urn:ietf:params:rpp:extension:profile-schemas", "version": "1.0", "url": "https://example.org/profile-schemas.schema.json" }
  ],
  "profileSchemas": [
    { "profile": "urn:ietf:params:rpp:profile:base", "version": "1.0",
      "url": "https://rpp.example/profiles/urn%3Aietf%3Aparams%3Arpp%3Aprofile%3Abase/schema" },
    { "profile": "de.denic.rpp.profile.rri", "version": "1.0",
      "url": "https://rpp.example/profiles/de.denic.rpp.profile.rri/schema" }
  ]
}
```

Example request of the Effective Schema of the profile of the DENIC RRI extension, and the start of its response:

```
GET /profiles/de.denic.rpp.profile.rri/schema HTTP/1.1
Host: rpp.example
Accept: application/schema+json

HTTP/1.1 200 OK
Content-Type: application/schema+json
RPP-Code: 01000
```

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://rpp.example/profiles/de.denic.rpp.profile.rri/schema",
  "$defs": {
    "domainName.create": {
      "allOf": [
        { "type": "object", "properties": { "@type": { "const": "domainName" } } },
        { "$ref": "#/$defs/ext.rri.domainName.create" }
      ],
      "unevaluatedProperties": false
    }
  }
}
```

The `$defs` of the example are shortened to one definition, and the base definition inside the `allOf` to its first member: the node that holds the `allOf` has the injection and its branches have none, so the members of the base definition and of the extension are all evaluated.

## Invalid Examples {#examples-invalid}

Example Discovery document of a server that supports the extension, without `profileSchemas`:

<!-- example invalid discovery.read -->
```json
{
  "@type": "discovery",
  "versions": [{ "@type": "discoveryVersion", "version": "1.0", "baseUrl": "https://rpp.example" }],
  "environment": { "@type": "discoveryEnvironment", "name": "rpp.example", "status": "production" },
  "tlds": ["de"],
  "objects": ["domainName"],
  "datetime": "2026-11-15T12:00:00Z"
}
```

Example Discovery document with a Profile Schema without a URL:

<!-- example invalid discovery.read -->
```json
{
  "@type": "discovery",
  "versions": [{ "@type": "discoveryVersion", "version": "1.0", "baseUrl": "https://rpp.example" }],
  "environment": { "@type": "discoveryEnvironment", "name": "rpp.example", "status": "production" },
  "tlds": ["de"],
  "objects": ["domainName"],
  "datetime": "2026-11-15T12:00:00Z",
  "profileSchemas": [{ "profile": "urn:ietf:params:rpp:profile:base", "version": "1.0" }]
}
```

Example Discovery document with an empty `profileSchemas`:

<!-- example invalid discovery.read -->
```json
{
  "@type": "discovery",
  "versions": [{ "@type": "discoveryVersion", "version": "1.0", "baseUrl": "https://rpp.example" }],
  "environment": { "@type": "discoveryEnvironment", "name": "rpp.example", "status": "production" },
  "tlds": ["de"],
  "objects": ["domainName"],
  "datetime": "2026-11-15T12:00:00Z",
  "profileSchemas": []
}
```

A request for the schema of a profile that the server does not offer is answered with 404 and `RPP-Code: 02303`. A member that the Effective Schema of a profile does not declare, such as `generalRequest` in a Domain Name create request under the base profile, is invalid under that schema, and valid under the schema of the profile of the DENIC RRI extension.

# IANA Considerations {#iana}

This document has no IANA actions. The Identifier of the extension is a URN below the RPP URN sub-namespace [@!I-D.wullink-rpp-extension-guidelines, section 7], as the extension of the EPP Compatibility profile. For a standardised version of the extension, the following entries would be registered.

Extension: RPP Profile Schemas, `urn:ietf:params:rpp:extension:profile-schemas`, version 1.0, with the `$id` of (#overview) and the changed base object `discovery`.

Object: discovery (additions)

Data Elements

| Element Identifier | Element Name    | Card. | Mutability | Data Type              | Description                                                                |
| ------------------ | --------------- | ----- | ---------- | ---------------------- | -------------------------------------------------------------------------- |
| profileSchemas     | Profile Schemas | 1+    | read-only  | List of Profile Schema | Where the Effective Schema of each profile the server offers is published. |

# Security Considerations {#security}

The operation needs no authentication, as the Discovery operation, because the Effective Schema is the same for every client and holds no registry data: it states what the server enforces for a profile. It does state which extensions and which data elements a server supports, as the Profile Data Object does. A server that does not want to publish them SHOULD NOT implement the extension.

The Effective Schema is large (about 50 kilobytes for the profiles of the implementation) and built once, when the server starts, so a request costs no composition. A server SHOULD apply the rate limits it applies to the Discovery operation, and MAY allow caching of the response, as it only changes with the configuration of the server.

A client MUST NOT take the schema from a URL that the Discovery document of another server states: the URL is under the base URL of the server that states it.

# Privacy Considerations {#privacy}

None. The document holds no personal data.

# Internationalisation Considerations {#i18n}

None. The name of a profile is encoded as one path segment [@!RFC3986].

{removeInRFC="true"}
{toc="exclude"}
# Changes History

{toc="exclude"}
{numbered="false"}
## 1.0

* initial version: the Discovery member `profileSchemas` and the operation `GET /profiles/{name}/schema` (#164)

{backmatter}

# What the Proxy Does Where the Drafts Are Silent {#proxy}

This appendix states the decisions of the implementation where the base specifications say nothing. They are collected in the specification issues of the implementation (`.spec/spec-issues.md`, "Effective schemas of a profile").

* The drafts define no way to obtain the Effective Schema of a profile. The extension is the proxy's, and the Identifier is in the RPP URN sub-namespace by analogy with the extension of the EPP Compatibility profile.
* The schema is built once per worker when the application starts, from the same `$defs` that the validators of the profile use, so what is published is what is enforced. The bundle of the base specifications references no definition that an extension extends from another definition, so composing in place changes no other definition.
* The injection of `"unevaluatedProperties": false` follows [@!I-D.ietf-rpp-json, section 4.9.1]: object-schema nodes have it, nodes with `additionalProperties` or `unevaluatedProperties` do not get it, and the conditions `if` and `not` are not entered.
* A member no schema of the profile declares is refused with 400 `02001` and the detail "Undeclared property", also one that only another profile declares (an rri member under the base profile) and one nested in an object of an extension. The status of a contact or a host has no `due` member [@!I-D.ietf-rpp-json, section 6.2.3], so it is refused the same way.
* The schema is not an RPP media type and the operation is not part of profile signalling: [@!I-D.ietf-rpp-core, section 13] and 14 are not applied to it. The `Accept` must allow `application/schema+json` (406 otherwise), the request profile is not selected and no `RPP-Profile` is sent, in either signalling method. [@!I-D.ietf-rpp-core, section 6.1] asks for `RPP-Cltrid` on every request; the proxy relaxes that for this operation only, which is echoed when sent.
* Without a base URL that discovery would state (https, no userinfo, query or fragment) a document has no `$id`, and the Discovery document is the 500 it is without that URL.
