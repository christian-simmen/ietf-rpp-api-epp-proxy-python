%%%
title = "Planets Demo Extension for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Planets Demo Extension"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "extension", "demo"]
TocDepth = 4
date = 2026-11-16

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-planets-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo extension of the RESTful Provisioning Protocol (RPP). The extension defines the Planet and Satellite Data Objects, which have no counterpart in a domain name registry. A server that implements only this extension is a test bed for features of the protocol that do not depend on the data objects of a registry, such as discovery, extensions, transfers and messages.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the extension, the specifications it builds upon, and the reasons for the extension points it uses.

The RESTful Provisioning Protocol (RPP) is defined by [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], and [@!I-D.ietf-rpp-json]. This document extends these base specifications with two Data Objects that serve as a demonstration. It follows the extension specification format of [@!I-D.wullink-rpp-extension-guidelines, section 9].

A Planet is a resource that a client provisions and that another client can obtain by a transfer, as a domain name. A Satellite belongs to one Planet, as a subordinate host belongs to its superordinate domain name, and moves with it in a transfer. Neither object carries data of a natural person.

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

Terms of the RPP data model, such as Data Object, Component Object, Process Object, data element, cardinality, mutability, Visibility, Direct Access, Identifier, Unique Identifier, Reference, Owner Data Object, and This Object, are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Extension Mapper (`rpp:extends`) and Effective Schema are used as defined in [@!I-D.ietf-rpp-json].

## Choice of Extension Points {#choice}

This section is non-normative.

The Planet and Satellite are new Data Objects [@!I-D.wullink-rpp-extension-guidelines, section 5.1], as no base Data Object describes them. The transfer of a Planet uses the Transfer Process Object of [@!I-D.ietf-rpp-data-objects] without additions, so the extension defines no Process Object. The Satellites of a Planet are a data element of the Planet with Direct Access, so that a client reads a Satellite in the context of its Planet without a new endpoint rule.

# Extension Overview {#overview}

This section identifies the extension.

| Field                | Value                                                                                         |
| -------------------- | --------------------------------------------------------------------------------------------- |
| Name                 | RPP Planets                                                                                   |
| Identifier           | `org.example.rpp.extension.planets`                                                           |
| Version              | 1.0                                                                                           |
| RPP version          | [@!I-D.ietf-rpp-core], [@!I-D.ietf-rpp-data-objects], [@!I-D.ietf-rpp-json]                   |
| Schema `$id`         | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json> |
| Changed base objects | None                                                                                          |
| New objects          | `planet`, `planetAvailability`, `satellite`, `satelliteAvailability`                          |
Table: Extension Overview

# External Data Types {#external-data-types}

None.

# Result Codes {#result-codes}

None. The extension uses the result codes of [@!I-D.ietf-rpp-core, section 18].

# Problem Details {#problem-details}

None.

# HTTP Headers {#http-headers}

None. The Object Authorisation of a transfer request is conveyed in the `RPP-Authorization` header field [@!I-D.ietf-rpp-core, section 6.1], as for any transfer request.

# Discovery Document {#discovery}

This section states the additions of the extension to the Discovery document.

A server that supports the extension lists it in the `extensions` of its Discovery document with the values of (#overview).

A server that supports the extension lists `planet` and `satellite` in the `objects` of its Discovery document.

# Updated Data Objects {#updated-data-objects}

None.

# New Data Objects {#new-data-objects}

This section defines the Data Objects and Component Objects that the extension introduces.

## Planet Data Object {#planet}

### Object Description

* Name: Planet Data Object
* Identifier: planet
* Unique Identifier: id
* Description: A Planet Data Object represents a planet that a client provisions.

### Data Elements {#planet-data-elements}

The following data elements are defined for the Planet Data Object.

* Planet ID
  * Identifier: id
  * Cardinality: 1
  * Mutability: create-only
  * Data Type: Identifier
  * Description: External unique identifier of the planet, its name.
  * Constraints:
    * This value MUST be provided by the client.
* Provisioning Metadata
  * Identifier: provMetadata
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: Provisioning Metadata Object
  * Description: Standard metadata about the object's lifecycle and ownership.
  * Constraints: (None)
* Type
  * Identifier: type
  * Cardinality: 1
  * Mutability: read-write
  * Data Type: String
  * Description: The kind of the planet.
  * Constraints:
    * The value MUST be one of `rocky`, `gas-giant`, or `ice-giant`.
* Radius
  * Identifier: radius
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: Decimal
  * Description: The mean radius of the planet in kilometres.
  * Constraints:
    * The value MUST be greater than 0.
* Mass
  * Identifier: mass
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: Decimal
  * Description: The mass of the planet in Earth masses.
  * Constraints:
    * The value MUST be greater than 0.
* Authorisation Information
  * Identifier: authInfo
  * Cardinality: 1
  * Mutability: read-write
  * Data Type: Authorisation Information Object
  * Description: The Object Authorisation that a client presents to request the transfer of the planet.
  * Constraints:
    * A server MUST show it only to the sponsoring client.
* Satellites
  * Identifier: satellite
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Aggregation[Satellite Data Object]
  * Visibility: onDemand
  * Direct Access: true
  * Description: The satellites of the planet.
  * Constraints: (None)
* Processes
  * Identifier: processes
  * Cardinality: 0-1
  * Mutability: read-only
  * Data Type: Processes Object
  * Direct Access: true
  * Description: The processes of the planet, with its transfer processes.
  * Constraints: (None)

### Operations {#planet-operations}

#### Availability Operation

* Identifier: availability

The Availability operation allows a client to determine whether a Planet resource with the given Planet ID can be created.

* Authorisation:
  * Any authenticated client is authorised to perform this operation.

* Output:
  * Object: Planet Availability Object

#### Create Operation

* Identifier: create

The Create operation allows a client to provision a new Planet resource. The operation accepts as input all create-only and read-write data elements defined for the Planet Data Object.

* Authorisation:
  * Each client is authorised to create new planet objects, becoming their sponsoring client.

* Input:
  * Object: This Object
* Output:
  * Object: This Object

#### Read Operation

* Identifier: read

The Read operation allows a client to retrieve the data elements of a Planet resource.

* Authorisation:
  * Any authenticated client is authorised to perform this operation. The Authorisation Information is shown only to the sponsoring client.

* Input:
  * Reference: This Object
* Output:
  * Object: This Object

#### Update Operation

* Identifier: update

The Update operation allows a client to modify the read-write data elements of a Planet resource. A full update that omits the Authorisation Information leaves it as it is.

* Authorisation:
  * Only the sponsoring client is authorised to perform this operation.

* Input:
  * Reference: This Object
  * Object: This Object
* Output:
  * Object: This Object

A server MUST reject an update of a planet with a pending transfer.

#### Delete Operation

* Identifier: delete

The Delete operation removes a Planet resource.

* Authorisation:
  * Only the sponsoring client is authorised to perform this operation.

* Input:
  * Reference: This Object

A server MUST reject the deletion of a planet that has satellites, or a pending transfer.

### Processes {#planet-processes}

The Planet Data Object supports the Transfer Process Object [@!I-D.ietf-rpp-data-objects] with the following rules, as the transfer of a domain name in EPP [@RFC5731]:

* Only the pull transfer is supported. A request for a push transfer is rejected.
* A client that is not the sponsoring client requests the transfer with the Object Authorisation of the planet. A server MUST reject a request without it, with an Object Authorisation that does not match, and a request of the sponsoring client.
* The transfer is pending until the sponsoring client approves or rejects it, or the requesting client cancels it. A server MUST NOT approve a pending transfer on its own after a period.
* The sponsoring client and the requesting client of the latest transfer can query it.
* On approval, the requesting client becomes the sponsoring client of the planet and of all its satellites.
* A server informs the sponsoring client of a request and of a cancellation, and the requesting client of an approval and of a rejection, with a message [@!I-D.ietf-rpp-core]. The message is a Transfer Request Message or a Transfer Outcome Message with the Object Type `planet`.

## Planet Availability Object {#planet-availability}

* Name: Planet Availability Object
* Identifier: planetAvailability
* Extends: Base Availability Object
* Description: The result of an Availability operation on a Planet Data Object.
* Data Elements: (None)

## Satellite Data Object {#satellite}

### Object Description

* Name: Satellite Data Object
* Identifier: satellite
* Unique Identifier: id
* Description: A Satellite Data Object represents a satellite of one planet.

### Data Elements {#satellite-data-elements}

The following data elements are defined for the Satellite Data Object.

* Satellite ID
  * Identifier: id
  * Cardinality: 1
  * Mutability: create-only
  * Data Type: Identifier
  * Description: External unique identifier of the satellite, its name.
  * Constraints:
    * This value MUST be provided by the client.
* Provisioning Metadata
  * Identifier: provMetadata
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: Provisioning Metadata Object
  * Description: Standard metadata about the object's lifecycle and ownership.
  * Constraints:
    * The sponsoring client of a satellite is the sponsoring client of its planet.
* Planet
  * Identifier: planet
  * Cardinality: 1
  * Mutability: create-only
  * Data Type: Aggregation[Planet Data Object]
  * Description: The planet the satellite belongs to.
  * Constraints:
    * The relation MUST correspond to a Planet Data Object of the client that creates the satellite.
* Orbital Period
  * Identifier: orbitalPeriod
  * Cardinality: 0-1
  * Mutability: read-write
  * Data Type: Decimal
  * Description: The orbital period of the satellite in days.
  * Constraints:
    * The value MUST be greater than 0.

### Operations {#satellite-operations}

The Satellite Data Object has the Availability, Create, Read, Update and Delete operations, as defined for the Planet Data Object in (#planet-operations), with the following differences:

* Create: the planet MUST exist and be sponsored by the client that creates the satellite.
* Read: any authenticated client is authorised to perform this operation.
* Update and Delete: only the sponsoring client is authorised to perform them. A server MUST reject them while the planet has a pending transfer.

### Processes

The Satellite Data Object supports no Process Objects. A satellite moves with its planet.

## Satellite Availability Object {#satellite-availability}

* Name: Satellite Availability Object
* Identifier: satelliteAvailability
* Extends: Base Availability Object
* Description: The result of an Availability operation on a Satellite Data Object.
* Data Elements: (None)

# Updated Process Objects {#updated-process-objects}

None.

# New Process Objects {#new-process-objects}

None.

# Endpoints {#endpoints}

This section lists the endpoints that result from the new Data Objects, derived by the rules of [@!I-D.ietf-rpp-core, section 16.1]. This section is non-normative.

| Operation                     | HTTP Method  | URL path                                              |
| ----------------------------- | ------------ | ----------------------------------------------------- |
| Planet: availability          | HEAD or GET  | /planets/{id}/availability                            |
| Planet: create                | POST         | /planets                                              |
| Planet: read                  | GET          | /planets/{id}                                         |
| Planet: update                | PUT or PATCH | /planets/{id}                                         |
| Planet: delete                | DELETE       | /planets/{id}                                         |
| Planet: satellite             | GET          | /planets/{id}/satellites/{satelliteId}                |
| Planet: transfer request      | POST         | /planets/{id}/processes/transferProcesses             |
| Planet: transfer query        | GET          | /planets/{id}/processes/transferProcesses/latest      |
| Planet: transfer cancel       | DELETE       | /planets/{id}/processes/transferProcesses/latest      |
| Planet: transfer approve      | POST         | /planets/{id}/processes/transferProcesses/latest/transferApprove |
| Planet: transfer reject       | POST         | /planets/{id}/processes/transferProcesses/latest/transferReject  |
| Satellite: availability       | HEAD or GET  | /satellites/{id}/availability                         |
| Satellite: create             | POST         | /satellites                                           |
| Satellite: read               | GET          | /satellites/{id}                                      |
| Satellite: update             | PUT or PATCH | /satellites/{id}                                      |
| Satellite: delete             | DELETE       | /satellites/{id}                                      |
Table: Endpoints of the Planet and Satellite Data Objects

The path `/planets/{id}/satellites/{satelliteId}` results from Rule 3 for the Direct Access data element `satellite` of cardinality 0+. A server MUST respond to it as for an object that does not exist when the satellite does not belong to the planet.

Example Planet Create request:

```http
POST /planets HTTP/1.1
Host: rpp.example
Authorization: Basic <credentials>
Accept: application/rpp+json
Content-Type: application/rpp+json
RPP-Cltrid: ABC-12345
Content-Length: 142
```

Example Planet Create response:

```http
HTTP/1.1 201 Created
Date: Mon, 16 Nov 2026 12:00:00 GMT
Content-Type: application/rpp+json
Location: https://rpp.example/rpp/planets/kepler-22b
RPP-Svtrid: XYZ-12345
RPP-Cltrid: ABC-12345
RPP-Code: 01000
```

Example Planet Transfer request with Object Authorisation:

```http
POST /planets/kepler-22b/processes/transferProcesses HTTP/1.1
Host: rpp.example
Authorization: Basic <credentials>
Accept: application/rpp+json
Content-Type: application/rpp+json
RPP-Cltrid: ABC-12346
RPP-Authorization: authinfo value=czNjcjN0
Content-Length: 30
```

Example Planet Transfer response for a pending transfer:

```http
HTTP/1.1 201 Created
Date: Mon, 16 Nov 2026 12:00:00 GMT
Content-Type: application/rpp+json
Location: https://rpp.example/rpp/planets/kepler-22b/processes/transferProcesses/latest
RPP-Svtrid: XYZ-12346
RPP-Cltrid: ABC-12346
RPP-Code: 01001
```

# JSON Schema {#json-schema}

This section defines the JSON representation of the new objects, following the rules of [@!I-D.ietf-rpp-json, section 4] and the Extension Framework of [@!I-D.ietf-rpp-json, section 7].

The extension defines one JSON Schema document, <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/planets-extension.schema.json>. Its definitions are shown below. The extension defines new Data Objects and changes no base definition, so its definitions are named after their objects and views as the base definitions are (`planet.create`), without a prefix. A definition of the extension MUST NOT have the name of a base definition.

## Extension Mapping {#extension-mapping}

The extension changes no base definition, so its Extension Mapper is empty:

```json
{
  "rpp:extends": {}
}
```

The schema document states the Name, Identifier, Version, and New Data Objects of (#overview) in the property `rpp:extension`:

```json
{
  "rpp:extension": {
    "name": "RPP Planets",
    "id": "org.example.rpp.extension.planets",
    "version": "1.0",
    "objects": ["planet", "satellite"]
  }
}
```

## Planet Data Object {#json-planet}

The type of a planet:

<!-- definition planetType -->
```json
{
  "$defs": {
    "planetType": {
      "type": "string",
      "enum": ["rocky", "gas-giant", "ice-giant"]
    }
  }
}
```

### Availability

The response of the Availability operation is the Planet Availability Object:

<!-- definition planetAvailability.read -->
```json
{
  "$defs": {
    "planetAvailability.read": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "planetAvailability", "readOnly": true },
        "available": { "type": "boolean", "readOnly": true },
        "reason": { "type": "string", "readOnly": true }
      },
      "required": ["@type", "available"]
    }
  }
}
```

### Create

Create request schema (create-only and read-write properties):

<!-- definition planet.create -->
```json
{
  "$defs": {
    "planet.create": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "planet" },
        "id": { "$ref": "#/$defs/identifier" },
        "type": { "$ref": "#/$defs/planetType" },
        "radius": { "type": "number", "exclusiveMinimum": 0 },
        "mass": { "type": "number", "exclusiveMinimum": 0 },
        "authInfo": { "$ref": "#/$defs/authInfo.create" }
      },
      "required": ["@type", "id", "type", "authInfo"]
    }
  }
}
```

### Read

Read response schema (read-write and read-only properties). The `satellite` property is shown when the request asks for it with `includeElements` [@!I-D.ietf-rpp-core]:

<!-- definition planet.read -->
```json
{
  "$defs": {
    "planet.read": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "planet", "readOnly": true },
        "id": { "$ref": "#/$defs/identifier", "readOnly": true },
        "type": { "$ref": "#/$defs/planetType" },
        "radius": { "type": "number", "exclusiveMinimum": 0 },
        "mass": { "type": "number", "exclusiveMinimum": 0 },
        "provMetadata": { "$ref": "#/$defs/provMetadata.read", "readOnly": true },
        "authInfo": { "$ref": "#/$defs/authInfo.read" },
        "satellite": {
          "type": "array",
          "items": { "$ref": "#/$defs/satellite.reference" },
          "readOnly": true
        },
        "processes": { "$ref": "#/$defs/processes.read", "readOnly": true }
      },
      "required": ["@type", "id", "type", "provMetadata"]
    }
  }
}
```

### Update

Update request schema (read-write properties):

<!-- definition planet.update -->
```json
{
  "$defs": {
    "planet.update": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "planet" },
        "type": { "$ref": "#/$defs/planetType" },
        "radius": { "type": "number", "exclusiveMinimum": 0 },
        "mass": { "type": "number", "exclusiveMinimum": 0 },
        "authInfo": { "$ref": "#/$defs/authInfo.create" }
      },
      "required": ["@type", "type"]
    }
  }
}
```

### Reference

Reference schema (identifier only):

<!-- definition planet.reference -->
```json
{
  "$defs": {
    "planet.reference": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "planet" },
        "id": { "$ref": "#/$defs/identifier" }
      },
      "required": ["@type", "id"]
    }
  }
}
```

### Transfer

The transfer of a planet uses the definitions `transferProcess.create`, `transferProcess.read` and `transferProcess.transferReject` of [@!I-D.ietf-rpp-json] without change.

## Satellite Data Object {#json-satellite}

### Availability

The response of the Availability operation is the Satellite Availability Object:

<!-- definition satelliteAvailability.read -->
```json
{
  "$defs": {
    "satelliteAvailability.read": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "satelliteAvailability", "readOnly": true },
        "available": { "type": "boolean", "readOnly": true },
        "reason": { "type": "string", "readOnly": true }
      },
      "required": ["@type", "available"]
    }
  }
}
```

### Create

Create request schema (create-only and read-write properties):

<!-- definition satellite.create -->
```json
{
  "$defs": {
    "satellite.create": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "satellite" },
        "id": { "$ref": "#/$defs/identifier" },
        "planet": { "$ref": "#/$defs/planet.reference" },
        "orbitalPeriod": { "type": "number", "exclusiveMinimum": 0 }
      },
      "required": ["@type", "id", "planet"]
    }
  }
}
```

### Read

Read response schema (read-write and read-only properties):

<!-- definition satellite.read -->
```json
{
  "$defs": {
    "satellite.read": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "satellite", "readOnly": true },
        "id": { "$ref": "#/$defs/identifier", "readOnly": true },
        "planet": { "$ref": "#/$defs/planet.reference", "readOnly": true },
        "orbitalPeriod": { "type": "number", "exclusiveMinimum": 0 },
        "provMetadata": { "$ref": "#/$defs/provMetadata.read", "readOnly": true }
      },
      "required": ["@type", "id", "planet", "provMetadata"]
    }
  }
}
```

### Update

Update request schema (read-write properties):

<!-- definition satellite.update -->
```json
{
  "$defs": {
    "satellite.update": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "satellite" },
        "orbitalPeriod": { "type": "number", "exclusiveMinimum": 0 }
      },
      "required": ["@type"]
    }
  }
}
```

### Reference

Reference schema (identifier only):

<!-- definition satellite.reference -->
```json
{
  "$defs": {
    "satellite.reference": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "satellite" },
        "id": { "$ref": "#/$defs/identifier" }
      },
      "required": ["@type", "id"]
    }
  }
}
```

# Examples {#examples}

This section contains examples of the new objects. Each valid example validates against the Effective Schema [@!I-D.ietf-rpp-json, section 7.2] of a server that supports the extension, and each invalid example fails it. This section is non-normative.

## Planet {#examples-planet}

### Availability

Example planet availability response for a planet that cannot be created:

<!-- example valid planetAvailability.read -->
```json
{
    "@type": "planetAvailability",
    "available": false,
    "reason": "In use"
}
```

### Create

Example planet create request:

<!-- example valid planet.create -->
```json
{
    "@type": "planet",
    "id": "kepler-22b",
    "type": "rocky",
    "radius": 15290,
    "mass": 9.1,
    "authInfo": { "@type": "authInfo", "method": "authinfo", "authdata": "s3cr3t" }
}
```

### Read

Example planet read response for the sponsoring client, with the satellites requested by `includeElements=satellite`:

<!-- example valid planet.read -->
```json
{
    "@type": "planet",
    "id": "kepler-22b",
    "type": "rocky",
    "radius": 15290,
    "mass": 9.1,
    "provMetadata": {
        "@type": "provMetadata",
        "spClientId": "ClientX",
        "crClientId": "ClientX",
        "crDate": "2026-11-16T12:00:00Z"
    },
    "authInfo": { "@type": "authInfo", "method": "authinfo", "authdata": "s3cr3t" },
    "satellite": [
        { "@type": "satellite", "id": "kepler-22b-i" }
    ]
}
```

### Update

Example planet full update request:

<!-- example valid planet.update -->
```json
{
    "@type": "planet",
    "type": "rocky",
    "radius": 15300
}
```

Example planet partial update request:

```json
[
  {
    "op": "replace",
    "path": "/mass",
    "value": 9.2
  }
]
```

### Transfer Request

Example planet transfer request:

<!-- example valid transferProcess.create -->
```json
{
    "@type": "transferProcess",
    "transferDir": "pull"
}
```

Example planet transfer response for a pending transfer:

<!-- example valid transferProcess.read -->
```json
{
    "@type": "transferProcess",
    "transferDir": "pull",
    "trStatus": "pending",
    "reqClientId": "ClientY",
    "requestDate": "2026-11-16T12:00:00Z",
    "actClientId": "ClientX",
    "actionDate": "2026-11-16T12:00:00Z"
}
```

## Satellite {#examples-satellite}

### Create

Example satellite create request:

<!-- example valid satellite.create -->
```json
{
    "@type": "satellite",
    "id": "kepler-22b-i",
    "planet": { "@type": "planet", "id": "kepler-22b" },
    "orbitalPeriod": 12.5
}
```

### Read

Example satellite read response:

<!-- example valid satellite.read -->
```json
{
    "@type": "satellite",
    "id": "kepler-22b-i",
    "planet": { "@type": "planet", "id": "kepler-22b" },
    "orbitalPeriod": 12.5,
    "provMetadata": { "@type": "provMetadata", "spClientId": "ClientX" }
}
```

### Update

Example satellite full update request:

<!-- example valid satellite.update -->
```json
{
    "@type": "satellite",
    "orbitalPeriod": 13
}
```

### Availability

Example satellite availability response:

<!-- example valid satelliteAvailability.read -->
```json
{
    "@type": "satelliteAvailability",
    "available": true
}
```

## Invalid Examples {#examples-invalid}

Example planet create request without a type:

<!-- example invalid planet.create -->
```json
{
    "@type": "planet",
    "id": "kepler-22b",
    "authInfo": { "@type": "authInfo", "method": "authinfo", "authdata": "s3cr3t" }
}
```

Example planet create request with a type that is not defined:

<!-- example invalid planet.create -->
```json
{
    "@type": "planet",
    "id": "kepler-22b",
    "type": "dwarf",
    "authInfo": { "@type": "authInfo", "method": "authinfo", "authdata": "s3cr3t" }
}
```

Example planet update request with a radius of 0:

<!-- example invalid planet.update -->
```json
{
    "@type": "planet",
    "type": "rocky",
    "radius": 0
}
```

Example satellite create request without its planet:

<!-- example invalid satellite.create -->
```json
{
    "@type": "satellite",
    "id": "kepler-22b-i"
}
```

Example satellite update request that changes the planet, which is create-only:

<!-- example invalid satellite.update -->
```json
{
    "@type": "satellite",
    "planet": { "@type": "planet", "id": "kepler-22c" }
}
```

# IANA Considerations {#iana}

This document has no IANA actions. The extension is a private extension [@!I-D.wullink-rpp-extension-guidelines, section 10], and its Identifier is formed by reverse domain name notation [@!I-D.wullink-rpp-extension-guidelines, section 7] under the domain `example.org`, which is reserved for documentation [@RFC2606].

# Security Considerations {#security}

The extension inherits the authentication and authorisation services of the base specifications [@!I-D.wullink-rpp-extension-guidelines, section 12]. Only the sponsoring client changes or deletes a planet or a satellite. The Authorisation Information of a planet is shown only to its sponsoring client, and a server MUST NOT record the Object Authorisation of a transfer request in logs.

# Privacy Considerations {#privacy}

The objects of the extension hold no personal data.

# Internationalisation Considerations {#i18n}

None. The identifiers of planets and satellites are strings of the Identifier type of [@!I-D.ietf-rpp-data-objects].

{removeInRFC="true"}
{toc="exclude"}
# Changes History

{toc="exclude"}
{numbered="false"}
## 1.0

* initial version: the Planet and Satellite Data Objects with availability, create, read, update, delete and the transfer of a planet #177
