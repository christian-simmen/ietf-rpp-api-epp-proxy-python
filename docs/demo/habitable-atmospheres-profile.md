%%%
title = "Habitable atmospheres profile Demo for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Habitable atmospheres profile Demo"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "demo"]
TocDepth = 4
date = 2026-11-17

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-habitable-atmospheres-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo profile of the RESTful Provisioning Protocol (RPP). Requires an atmosphere on a planet, with a pressure between 0.5 and 2 bar. It serves as a test bed for profiles that constrain an extension.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the profile, what it constrains, and its motivation.

The planet atmosphere extension makes the atmosphere of a planet optional and accepts any pressure of 0 or greater. The profile limits a registry to planets that have an atmosphere of a pressure that holds liquid water.

The profile follows the Profile Specification Format of [@!I-D.wullink-rpp-extension-guidelines]. It only constrains: it defines no data element, operation, result code, header field, or endpoint. A request that breaks a constraint of the profile is refused with the result code 02308 and the Problem Detail field `profile` [@!I-D.ietf-rpp-core], and a request that does not conform to the preset is refused with 400 as without the profile.

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

The terms Profile, Preset, Applicable Profiles, and Profile Binding are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Profile Schema, Constraints Mapper (`rpp:constraints`), Preset Schema, and Effective Schema are used as defined in [@!I-D.ietf-rpp-json]. The planets extension is `org.example.rpp.extension.planets`.

# Profile Overview {#overview}

| Field | Value |
| ----- | ----- |
| Name | Habitable atmospheres profile |
| Identifier | `org.example.rpp.profile.habitable-atmospheres` |
| Version | 1.0 |
| RPP version | 1.0 |
| Required extensions | `org.example.rpp.extension.planets` 1.0, `org.example.rpp.extension.planet-atmosphere` 1.0 |
| Base profiles | None |
| Profile Schema `$id` | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/habitable-atmospheres-profile.schema.json> |
| Specification | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/docs/demo/habitable-atmospheres-profile.md> |
Table: Profile Overview

The preset that applies the profile MUST contain every extension the profile requires, directly or through its base profiles [@!I-D.ietf-rpp-data-objects].

# Constrained Data Objects {#constrained-data-objects}

## Planet Data Object {#planet}

* Identifier: planet

### Data Elements

* Atmosphere
  * Identifier: atmosphere
  * Constraints:
    * Cardinality is constrained to `1`: the data element is required in a create and a full update, and a partial update MUST NOT remove it.

### Operations

None. The constraint applies to the input of the Create and Update operations.

## Atmosphere Component Object {#atmosphere}

* Identifier: atmosphere

### Data Elements

* Atmosphere Pressure
  * Identifier: pressure
  * Constraints:
    * The value MUST be between 0.5 and 2 bar.


# Constrained Process Objects {#constrained-process-objects}

None.

# Server Requirements {#server-requirements}

None.

# JSON Schema {#json-schema}

The Profile Schema of the profile, in the file `.spec/habitable-atmospheres-profile.schema.json`. The profile constrains the definitions `planet.create` and `planet.update` of the planets extension (the data element is required) and the definition `atmosphere` of the planet atmosphere extension (the pressure).

<!-- profile-schema -->
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/habitable-atmospheres-profile.schema.json",
  "rpp:profile": {
    "id": "org.example.rpp.profile.habitable-atmospheres",
    "version": "1.0"
  },
  "rpp:constraints": {
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/planet.create": "#/$defs/profile.habitable.atmosphere",
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/planet.update": "#/$defs/profile.habitable.atmosphere",
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planet-atmosphere-extension.schema.json#/$defs/atmosphere": "#/$defs/profile.habitable.pressure"
  },
  "$defs": {
    "profile.habitable.atmosphere": {
      "required": [
        "atmosphere"
      ]
    },
    "profile.habitable.pressure": {
      "properties": {
        "pressure": {
          "minimum": 0.5,
          "maximum": 2
        }
      }
    }
  }
}
```

# Constraints Not Expressed in JSON Schema {#constraints-not-expressed}

None.

# Examples {#examples}

Each example that is valid is valid with and without the profile. Each example that violates the profile is valid under a preset that contains the required extensions and not the profile, and is refused with 02308 under the preset that applies the profile. This section is non-normative.

Example planet create request with an atmosphere of 1 bar:

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

Example planet create request without an atmosphere:

<!-- example violates planet.create -->
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
    }
}
```

Example planet create request with an atmosphere of 5 bar:

<!-- example violates planet.create -->
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
        "pressure": 5
    }
}
```

Example planet update request without an atmosphere:

<!-- example violates planet.update -->
```json
{
    "@type": "planet",
    "type": "rocky"
}
```

A partial update with the operation `remove` at `/atmosphere` is refused with the profile, because the profile requires the data element in every case. A partial update with the operation `replace` at `/atmosphere` and a pressure of 5 is refused alike.


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
