%%%
title = "Habitable rocky planets profile Demo for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Habitable rocky planets profile Demo"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "demo"]
TocDepth = 4
date = 2026-11-17

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-habitable-rocky-planets-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo profile of the RESTful Provisioning Protocol (RPP). Builds on the rocky planets and habitable atmospheres profiles, and requires the radius of a planet. It serves as a test bed for profiles that constrain an extension.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the profile, what it constrains, and its motivation.

The profile combines the rocky planets and the habitable atmospheres profiles, and adds that the radius of a planet is required. It shows a profile that builds on several profiles: its constraints are those of both bases and its own, each stated once.

The profile follows the Profile Specification Format of [@!I-D.wullink-rpp-extension-guidelines]. It only constrains: it defines no data element, operation, result code, header field, or endpoint. A request that breaks a constraint of the profile is refused with the result code 02308 and the Problem Detail field `profile` [@!I-D.ietf-rpp-core], and a request that does not conform to the preset is refused with 400 as without the profile.

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

The terms Profile, Preset, Applicable Profiles, and Profile Binding are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Profile Schema, Constraints Mapper (`rpp:constraints`), Preset Schema, and Effective Schema are used as defined in [@!I-D.ietf-rpp-json]. The planets extension is `org.example.rpp.extension.planets`.

# Profile Overview {#overview}

| Field | Value |
| ----- | ----- |
| Name | Habitable rocky planets profile |
| Identifier | `org.example.rpp.profile.habitable-rocky-planets` |
| Version | 1.0 |
| RPP version | 1.0 |
| Required extensions | `org.example.rpp.extension.planets` 1.0 |
| Base profiles | `org.example.rpp.profile.rocky-planets` 1.0, `org.example.rpp.profile.habitable-atmospheres` 1.0 |
| Profile Schema `$id` | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/habitable-rocky-planets-profile.schema.json> |
| Specification | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/docs/demo/habitable-rocky-planets-profile.md> |
Table: Profile Overview

The preset that applies the profile MUST contain every extension the profile requires, directly or through its base profiles [@!I-D.ietf-rpp-data-objects].

# Constrained Data Objects {#constrained-data-objects}

## Planet Data Object {#planet}

* Identifier: planet

### Data Elements

* Radius
  * Identifier: radius
  * Constraints:
    * Cardinality is constrained to `1`: the data element is required in a create and a full update, and a partial update MUST NOT remove it.

The constraints of the base profiles apply as well: the type is `rocky` ([rocky-planets](rocky-planets-profile.md)), and the atmosphere is required with a pressure between 0.5 and 2 bar ([habitable-atmospheres](habitable-atmospheres-profile.md)).

### Operations

None.

# Constrained Process Objects {#constrained-process-objects}

None.

# Server Requirements {#server-requirements}

None.

# JSON Schema {#json-schema}

The Profile Schema of the profile, in the file `.spec/habitable-rocky-planets-profile.schema.json`. The profile constrains the definitions `planet.create` and `planet.update` of the planets extension. The planet atmosphere extension is required through the base profile `habitable-atmospheres`, so the profile does not list it.

<!-- profile-schema -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/habitable-rocky-planets-profile.schema.json",
  "rpp:profile": {
    "id": "org.example.rpp.profile.habitable-rocky-planets",
    "version": "1.0"
  },
  "rpp:constraints": {
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/planet.create": "#/$defs/profile.habitableRocky.radius",
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/planet.update": "#/$defs/profile.habitableRocky.radius"
  },
  "$defs": {
    "profile.habitableRocky.radius": {
      "required": [
        "radius"
      ]
    }
  }
}
```

# Constraints Not Expressed in JSON Schema {#constraints-not-expressed}

None.

# Examples {#examples}

Each example that is valid is valid with and without the profile. Each example that violates the profile is valid under a preset that contains the required extensions and not the profile, and is refused with 02308 under the preset that applies the profile. This section is non-normative.

Example planet create request of a rocky planet with a radius and an atmosphere of 1 bar:

<!-- example valid planet.create -->
```json
{
    "@type": "planet",
    "id": "kepler-22b",
    "type": "rocky",
    "radius": 15290,
    "authInfo": {
        "@type": "authInfo",
        "method": "authinfo",
        "authdata": "s3cr3t"
    },
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": 1.0
    }
}
```

Example planet create request without a radius:

<!-- example violates planet.create -->
```json
{
    "@type": "planet",
    "id": "kepler-22b",
    "type": "rocky",
    "authInfo": {
        "@type": "authInfo",
        "method": "authinfo",
        "authdata": "s3cr3t"
    },
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": 1.0
    }
}
```

Example planet create request of a gas giant, which the base profile `rocky-planets` refuses:

<!-- example violates planet.create -->
```json
{
    "@type": "planet",
    "id": "kepler-22b",
    "type": "gas-giant",
    "radius": 15290,
    "authInfo": {
        "@type": "authInfo",
        "method": "authinfo",
        "authdata": "s3cr3t"
    },
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": 1.0
    }
}
```

Example planet update request without a radius:

<!-- example violates planet.update -->
```json
{
    "@type": "planet",
    "type": "rocky",
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": 1.0
    }
}
```

A partial update with the operation `remove` at `/radius` is refused with this profile.


# IANA Considerations {#iana}

This document has no IANA actions. The profile is a private profile, and its identifier is formed by reverse domain name notation under the domain `example.org`, which is reserved for documentation [@RFC2606]. It is not registered in the RPP Profiles registry.

# Security Considerations {#security}

A profile constrains and cannot relax a constraint of the specifications it constrains. A server enforces the constraints on every request, whether or not the client validated the request against the Preset Schema.

{removeInRFC="true"}
{toc="exclude"}
# Changes History

{toc="exclude"}
{numbered="false"}
## 1.0

* initial version #179
