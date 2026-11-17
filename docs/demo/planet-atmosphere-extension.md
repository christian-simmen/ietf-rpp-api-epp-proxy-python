%%%
title = "Planet Atmosphere Demo Extension for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Planet Atmosphere Demo Extension"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "extension", "demo"]
TocDepth = 4
date = 2026-11-17

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-planet-atmosphere-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo extension of the RESTful Provisioning Protocol (RPP). The extension adds the atmosphere of a planet to the Planet Data Object of the planets demo extension. It serves as a test bed for extensions that add members to the data object of another extension.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the extension, the specifications it builds upon, and the reasons for the extension point it uses.

The RESTful Provisioning Protocol (RPP) is defined by [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], and [@!I-D.ietf-rpp-json]. This document follows the extension specification format of [@!I-D.wullink-rpp-extension-guidelines, section 9]. It builds on the planets demo extension ([planets-extension.md](planets-extension.md)), which defines the Planet Data Object, and adds one data element to it. A planet has at most one atmosphere, which a client sets, changes, and removes as a whole.

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

Terms of the RPP data model, such as Data Object, Component Object, data element, cardinality, mutability, and Visibility, are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Extension Mapper (`rpp:extends`), Extension Schema, Preset Schema, and Effective Schema are used as defined in [@!I-D.ietf-rpp-json]. The planets extension is the extension `org.example.rpp.extension.planets`.

## Choice of Extension Points {#choice}

This section is non-normative.

The extension adds a data element to the Planet Data Object of the planets extension, as [@!I-D.wullink-rpp-extension-guidelines, section 5.1] describes for a change of an existing Data Object. It defines no Data Object, operation, result code, header field, or endpoint of its own. It adds no constraint to the Planet: the bounds below are those of the new data element only, and a requirement that constrains the Planet is a profile (see [profiles](#profiles)).

# Extension Overview {#overview}

This section identifies the extension.

| Field                | Value |
| -------------------- | ----- |
| Name                 | RPP Planet Atmosphere |
| Identifier           | `org.example.rpp.extension.planet-atmosphere` |
| Version              | 1.0 |
| RPP version          | [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], [@!I-D.ietf-rpp-json] |
| Schema `$id`         | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planet-atmosphere-extension.schema.json> |
| Changed base objects | Planet of `org.example.rpp.extension.planets` |
| New objects          | None |
Table: Extension Overview

A server that offers a preset with this extension MUST offer the planets extension in the same preset. The extension adds members to the definitions `planet.create`, `planet.read`, and `planet.update` of the planets extension, so a preset that has it without the planets extension is invalid.

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

This section defines the data element that the extension adds to the Planet Data Object of the planets extension.

## Planet Data Object {#planet}

### Data Elements {#planet-data-elements}

* Atmosphere
  * Identifier: atmosphere
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: Atmosphere Component Object (below)
  * Description: The atmosphere of the planet.
  * Constraints:
    * A partial update changes the element as a whole: the path of an operation is `/atmosphere`, a path below it is rejected.
    * A full update that omits the element removes it, under a preset that contains this extension. A full update under a preset that does not contain the extension leaves it as it is.

The Atmosphere Component Object has these data elements:

* Atmosphere Pressure
  * Identifier: pressure
  * Cardinality: 1
  * Mutability: read-write
  * Data Type: Decimal
  * Description: The pressure at the surface of the planet in bar.
  * Constraints:
    * The value MUST be 0 or greater.
* Dominant Gas
  * Identifier: dominantGas
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: String
  * Description: The gas that makes up most of the atmosphere.
  * Constraints:
    * The value MUST NOT be empty.

### Operations {#planet-operations}

The extension adds no operation. The element is part of the input of the Create and Update operations and of the output of the Read operation of the Planet. The Update operation of the Planet takes the element in a full update, and in a partial update with the operations `add`, `replace`, and `remove` at the path `/atmosphere`.

# New Data Objects {#new-data-objects}

None.

# Updated Process Objects {#updated-process-objects}

None.

# New Process Objects {#new-process-objects}

None.

# Endpoints {#endpoints}

None. The element is carried by the endpoints of the Planet Data Object of the planets extension.

# JSON Schema {#json-schema}

This section defines the JSON representation of the data element, following the rules of [@!I-D.ietf-rpp-json, section 4] and the Extension Framework of [@!I-D.ietf-rpp-json, section 7].

The extension defines one JSON Schema document, <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planet-atmosphere-extension.schema.json>. The definitions of the extension that are composed with a definition of the planets extension are named `ext.atmosphere.<definition>`. A definition of the extension MUST NOT have the name of a base definition or of a definition of another extension.

## Extension Mapping {#extension-mapping}

The extension maps each of its sub-schemas to the definition of the planets extension that it extends. The key is the `$id` of the schema of the planets extension and the pointer of the definition, as a Profile Schema names a definition of an extension:

```json
{
  "rpp:extends": {
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/planet.create": "#/$defs/ext.atmosphere.planet.create",
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/planet.read": "#/$defs/ext.atmosphere.planet.read",
    "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json#/$defs/planet.update": "#/$defs/ext.atmosphere.planet.update"
  }
}
```

The schema document states the Name, Identifier, and Version of (#overview) in the property `rpp:extension`:

```json
{
  "rpp:extension": {
    "name": "RPP Planet Atmosphere",
    "id": "org.example.rpp.extension.planet-atmosphere",
    "version": "1.0",
    "objects": []
  }
}
```

## Definitions {#json-definitions}

The definition of the data element, and the sub-schemas that add it to the Planet. A sub-schema declares no member that the Planet declares, and requires no member but its own, as [@!I-D.ietf-rpp-json, section 7] requires of an extension:

<!-- definition atmosphere -->
```json
{
  "$defs": {
    "atmosphere": {
      "type": "object",
      "properties": {
        "@type": {
          "type": "string",
          "const": "atmosphere"
        },
        "pressure": {
          "type": "number",
          "minimum": 0
        },
        "dominantGas": {
          "type": "string",
          "minLength": 1
        }
      },
      "required": [
        "@type",
        "pressure"
      ]
    }
  }
}
```
<!-- definition ext.atmosphere.planet.create -->
```json
{
  "$defs": {
    "ext.atmosphere.planet.create": {
      "type": "object",
      "properties": {
        "atmosphere": {
          "$ref": "#/$defs/atmosphere"
        }
      }
    }
  }
}
```
<!-- definition ext.atmosphere.planet.read -->
```json
{
  "$defs": {
    "ext.atmosphere.planet.read": {
      "type": "object",
      "properties": {
        "atmosphere": {
          "$ref": "#/$defs/atmosphere"
        }
      }
    }
  }
}
```
<!-- definition ext.atmosphere.planet.update -->
```json
{
  "$defs": {
    "ext.atmosphere.planet.update": {
      "type": "object",
      "properties": {
        "atmosphere": {
          "$ref": "#/$defs/atmosphere"
        }
      }
    }
  }
}
```

# Examples {#examples}

Each valid example validates against the Effective Schema [@!I-D.ietf-rpp-json, section 7.2] of a server that supports the planets extension and this extension, and each invalid example fails it. This section is non-normative.

## Planet {#examples-planet}

Example planet create request with an atmosphere:

<!-- example valid planet.create -->
```json
{
    "@type": "planet",
    "id": "mars",
    "type": "rocky",
    "radius": 3389.5,
    "authInfo": {
        "@type": "authInfo",
        "method": "authinfo",
        "authdata": "s3cr3t"
    },
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": 0.006,
        "dominantGas": "co2"
    }
}
```

Example planet read response:

<!-- example valid planet.read -->
```json
{
    "@type": "planet",
    "id": "mars",
    "type": "rocky",
    "radius": 3389.5,
    "provMetadata": {
        "@type": "provMetadata",
        "spClientId": "ClientX",
        "crClientId": "ClientX",
        "crDate": "2026-11-17T12:00:00Z"
    },
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": 0.006,
        "dominantGas": "co2"
    }
}
```

Example planet update request that sets the atmosphere:

<!-- example valid planet.update -->
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

Example partial update that replaces the atmosphere, and one that removes it:

```json
[
    {
        "op": "replace",
        "path": "/atmosphere",
        "value": {
            "@type": "atmosphere",
            "pressure": 2.5
        }
    }
]
```

```json
[
    {
        "op": "remove",
        "path": "/atmosphere"
    }
]
```

## Invalid Examples {#examples-invalid}

Example planet create request with a negative pressure:

<!-- example invalid planet.create -->
```json
{
    "@type": "planet",
    "id": "mars",
    "type": "rocky",
    "authInfo": {
        "@type": "authInfo",
        "method": "authinfo",
        "authdata": "s3cr3t"
    },
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": -1
    }
}
```

Example planet update request with an atmosphere without a pressure:

<!-- example invalid planet.update -->
```json
{
    "@type": "planet",
    "type": "rocky",
    "atmosphere": {
        "@type": "atmosphere",
        "dominantGas": "co2"
    }
}
```

Example planet update request with a member the atmosphere does not declare:

<!-- example invalid planet.update -->
```json
{
    "@type": "planet",
    "type": "rocky",
    "atmosphere": {
        "@type": "atmosphere",
        "pressure": 1,
        "humidity": 3
    }
}
```

# IANA Considerations {#iana}

This document has no IANA actions. The extension is a private extension [@!I-D.wullink-rpp-extension-guidelines, section 10], and its Identifier is formed by reverse domain name notation [@!I-D.wullink-rpp-extension-guidelines, section 7] under the domain `example.org`, which is reserved for documentation [@RFC2606].

# Security Considerations {#security}

The extension inherits the authentication and authorisation services of the base specifications [@!I-D.wullink-rpp-extension-guidelines, section 12]. Only the sponsoring client changes a planet, and with it the element. A server MUST NOT include the element in a response under a preset that does not contain the extension [@!I-D.wullink-rpp-extension-guidelines, section 5.13].

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

* initial version: the atmosphere data element of the Planet #179
