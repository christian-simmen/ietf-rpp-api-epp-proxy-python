%%%
title = "Satellite Orbit Demo Extension for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Satellite Orbit Demo Extension"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "extension", "demo"]
TocDepth = 4
date = 2026-11-17

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-satellite-orbit-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo extension of the RESTful Provisioning Protocol (RPP). The extension adds the orbit of a satellite to the Satellite Data Object of the planets demo extension. It serves as a test bed for extensions that add members to the data object of another extension.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the extension, the specifications it builds upon, and the reasons for the extension point it uses.

The RESTful Provisioning Protocol (RPP) is defined by [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], and [@!I-D.ietf-rpp-json]. This document follows the extension specification format of [@!I-D.wullink-rpp-extension-guidelines, section 9]. It builds on the planets demo extension ([planets-extension.md](planets-extension.md)), which defines the Satellite Data Object, and adds one data element to it. A satellite has at most one orbit, which a client sets, changes, and removes as a whole.

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

Terms of the RPP data model, such as Data Object, Component Object, data element, cardinality, mutability, and Visibility, are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Extension Mapper (`rpp:extends`), Extension Schema, Preset Schema, and Effective Schema are used as defined in [@!I-D.ietf-rpp-json]. The planets extension is the extension `org.example.rpp.extension.planets`.

## Choice of Extension Points {#choice}

This section is non-normative.

The extension adds a data element to the Satellite Data Object of the planets extension, as [@!I-D.wullink-rpp-extension-guidelines, section 5.1] describes for a change of an existing Data Object. It defines no Data Object, operation, result code, header field, or endpoint of its own. It adds no constraint to the Satellite: the bounds below are those of the new data element only, and a requirement that constrains the Satellite is a profile (see [@!I-D.wullink-rpp-extension-guidelines, section 6], and [rocky-planets](rocky-planets-profile.md) for an example of a profile of the planets extension).

# Extension Overview {#overview}

This section identifies the extension.

| Field                | Value |
| -------------------- | ----- |
| Name                 | RPP Satellite Orbit |
| Identifier           | `org.example.rpp.extension.satellite-orbit` |
| Version              | 1.0 |
| RPP version          | [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], [@!I-D.ietf-rpp-json] |
| Schema `$id`         | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/satellite-orbit-extension.schema.json> |
| Changed base objects | Satellite of `org.example.rpp.extension.planets` |
| New objects          | None |
Table: Extension Overview

A server that offers a preset with this extension MUST offer the planets extension in the same preset. The extension adds members to the definitions `satellite.create`, `satellite.read`, and `satellite.update` of the planets extension, so a preset that has it without the planets extension is invalid.

# External Data Types {#external-data-types}

None.

# Result Codes {#result-codes}

None. The extension uses the result codes of [@!I-D.ietf-rpp-core, section 18]. A value that breaks a bound of the data element is a request that does not conform to the preset (400, `02001`), see [@!I-D.ietf-rpp-core, section 18.1].

# Problem Details {#problem-details}

None.

# HTTP Headers {#http-headers}

None.

# Discovery Document {#discovery}

A server that supports the extension lists it in the `extensions` of its Discovery document with the values of (#overview), in each preset that contains it. It lists no object in `objects`.

# Updated Data Objects {#updated-data-objects}

This section defines the data element that the extension adds to the Satellite Data Object of the planets extension.

## Satellite Data Object {#satellite}

### Data Elements {#satellite-data-elements}

* Orbit
  * Identifier: orbit
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: Orbit Component Object (below)
  * Description: The orbit of the satellite around its planet.
  * Constraints:
    * A partial update changes the element as a whole: the path of an operation is `/orbit`, a path below it is rejected.
    * A full update that omits the element removes it, under a preset that contains this extension. A full update under a preset that does not contain the extension leaves it as it is.

The Orbit Component Object has these data elements:

* Semi-major Axis
  * Identifier: semiMajorAxis
  * Cardinality: 1
  * Mutability: read-write
  * Data Type: Decimal
  * Description: The semi-major axis of the orbit in kilometres.
  * Constraints:
    * The value MUST be greater than 0.
* Eccentricity
  * Identifier: eccentricity
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: Decimal
  * Description: The eccentricity of the orbit.
  * Constraints:
    * The value MUST be 0 or greater and less than 1.
* Inclination
  * Identifier: inclination
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: Decimal
  * Description: The inclination of the orbit in degrees.
  * Constraints:
    * The value MUST be between 0 and 180.

### Operations {#satellite-operations}

The extension adds no operation. The element is part of the input of the Create and Update operations and of the output of the Read operation of the Satellite. The Update operation of the Satellite takes the element in a full update, and in a partial update with the operations `add`, `replace`, and `remove` at the path `/orbit`.

# New Data Objects {#new-data-objects}

None.

# Updated Process Objects {#updated-process-objects}

None.

# New Process Objects {#new-process-objects}

None.

# Endpoints {#endpoints}

None. The element is carried by the endpoints of the Satellite Data Object of the planets extension.

# JSON Schema {#json-schema}

This section defines the JSON representation of the data element, following the rules of [@!I-D.ietf-rpp-json, section 4] and the Extension Framework of [@!I-D.ietf-rpp-json, section 7].

The extension defines one JSON Schema document, <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/satellite-orbit-extension.schema.json>. The definitions of the extension that are composed with a definition of the planets extension are named `ext.orbit.<definition>`. A definition of the extension MUST NOT have the name of a base definition or of a definition of another extension.

## Extension Mapping {#extension-mapping}

The extension maps each of its sub-schemas to the definition of the planets extension that it extends. The key is the `$id` of the schema of the planets extension and the pointer of the definition, as a Profile Schema names a definition of an extension:

```json
{
  "rpp:extends": {
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/satellite.create": "#/$defs/ext.orbit.satellite.create",
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/satellite.read": "#/$defs/ext.orbit.satellite.read",
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/satellite.update": "#/$defs/ext.orbit.satellite.update"
  }
}
```

The schema document states the Name, Identifier, and Version of (#overview) in the property `rpp:extension`:

```json
{
  "rpp:extension": {
    "name": "RPP Satellite Orbit",
    "id": "org.example.rpp.extension.satellite-orbit",
    "version": "1.0",
    "objects": []
  }
}
```

## Definitions {#json-definitions}

The definition of the data element, and the sub-schemas that add it to the Satellite. A sub-schema declares no member that the Satellite declares, and requires no member but its own, as [@!I-D.ietf-rpp-json, section 7] requires of an extension:

<!-- definition orbit -->
```json
{
  "$defs": {
    "orbit": {
      "type": "object",
      "properties": {
        "@type": {
          "type": "string",
          "const": "orbit"
        },
        "semiMajorAxis": {
          "type": "number",
          "exclusiveMinimum": 0
        },
        "eccentricity": {
          "type": "number",
          "minimum": 0,
          "exclusiveMaximum": 1
        },
        "inclination": {
          "type": "number",
          "minimum": 0,
          "maximum": 180
        }
      },
      "required": [
        "@type",
        "semiMajorAxis"
      ]
    }
  }
}
```
<!-- definition ext.orbit.satellite.create -->
```json
{
  "$defs": {
    "ext.orbit.satellite.create": {
      "type": "object",
      "properties": {
        "orbit": {
          "$ref": "#/$defs/orbit"
        }
      }
    }
  }
}
```
<!-- definition ext.orbit.satellite.read -->
```json
{
  "$defs": {
    "ext.orbit.satellite.read": {
      "type": "object",
      "properties": {
        "orbit": {
          "$ref": "#/$defs/orbit"
        }
      }
    }
  }
}
```
<!-- definition ext.orbit.satellite.update -->
```json
{
  "$defs": {
    "ext.orbit.satellite.update": {
      "type": "object",
      "properties": {
        "orbit": {
          "$ref": "#/$defs/orbit"
        }
      }
    }
  }
}
```

# Examples {#examples}

Each valid example validates against the Effective Schema [@!I-D.ietf-rpp-json, section 7.2] of a server that supports the planets extension and this extension, and each invalid example fails it. This section is non-normative.

## Satellite {#examples-satellite}

Example satellite create request with an orbit:

<!-- example valid satellite.create -->
```json
{
    "@type": "satellite",
    "id": "phobos-i",
    "planet": {
        "@type": "planet",
        "id": "mars"
    },
    "orbitalPeriod": 0.32,
    "orbit": {
        "@type": "orbit",
        "semiMajorAxis": 9376,
        "eccentricity": 0.015,
        "inclination": 1.1
    }
}
```

Example satellite read response:

<!-- example valid satellite.read -->
```json
{
    "@type": "satellite",
    "id": "phobos-i",
    "planet": {
        "@type": "planet",
        "id": "mars"
    },
    "orbitalPeriod": 0.32,
    "provMetadata": {
        "@type": "provMetadata",
        "spClientId": "ClientX",
        "crClientId": "ClientX",
        "crDate": "2026-11-17T12:00:00Z"
    },
    "orbit": {
        "@type": "orbit",
        "semiMajorAxis": 9376
    }
}
```

Example satellite update request that sets the orbit:

<!-- example valid satellite.update -->
```json
{
    "@type": "satellite",
    "orbit": {
        "@type": "orbit",
        "semiMajorAxis": 9376,
        "inclination": 2
    }
}
```

Example partial update that replaces the orbit, and one that removes it:

```json
[
    {
        "op": "replace",
        "path": "/orbit",
        "value": {
            "@type": "orbit",
            "semiMajorAxis": 9400
        }
    }
]
```

```json
[
    {
        "op": "remove",
        "path": "/orbit"
    }
]
```

## Invalid Examples {#examples-invalid}

Example satellite create request with a semi-major axis of 0:

<!-- example invalid satellite.create -->
```json
{
    "@type": "satellite",
    "id": "phobos-i",
    "planet": {
        "@type": "planet",
        "id": "mars"
    },
    "orbit": {
        "@type": "orbit",
        "semiMajorAxis": 0
    }
}
```

Example satellite update request with an eccentricity of 1:

<!-- example invalid satellite.update -->
```json
{
    "@type": "satellite",
    "orbit": {
        "@type": "orbit",
        "semiMajorAxis": 1,
        "eccentricity": 1
    }
}
```

Example satellite update request with an inclination above 180 degrees:

<!-- example invalid satellite.update -->
```json
{
    "@type": "satellite",
    "orbit": {
        "@type": "orbit",
        "semiMajorAxis": 1,
        "inclination": 181
    }
}
```

# IANA Considerations {#iana}

This document has no IANA actions. The extension is a private extension [@!I-D.wullink-rpp-extension-guidelines, section 10], and its Identifier is formed by reverse domain name notation [@!I-D.wullink-rpp-extension-guidelines, section 7] under the domain `example.org`, which is reserved for documentation [@RFC2606].

# Security Considerations {#security}

The extension inherits the authentication and authorisation services of the base specifications [@!I-D.wullink-rpp-extension-guidelines, section 12]. Only the sponsoring client changes a satellite, and with it the element. A server MUST NOT include the element in a response under a preset that does not contain the extension [@!I-D.wullink-rpp-extension-guidelines, section 5.13].

# Privacy Considerations {#privacy}

The element holds no personal data.

# Internationalisation Considerations {#i18n}

None.

{removeInRFC="true"}
{toc="exclude"}
# Changes History

{toc="exclude"}
{numbered="false"}
## 1.0

* initial version: the orbit data element of the Satellite #179
