%%%
title = "RESTful Provisioning Protocol (RPP) EPP Compatibility Profile"
abbrev = "RPP EPP Compatibility Profile"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "EPP", "provisioning", "registry", "profile"]
TocDepth = 4
date = 2026-11-15

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-epp-compatibility-00"
stream = "IETF"
status = "standard"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"
  [author.address]
  email = "pawel.kowalik@denic.de"
  uri = "https://denic.de/"

[[author]]
initials="M."
surname="Wullink"
fullname="Maarten Wullink"
organization = "SIDN Labs"
  [author.address]
  email = "maarten.wullink@sidn.nl"
  uri = "https://sidn.nl/"

%%%

.# Abstract

This document defines the EPP Compatibility Profile of the RESTful Provisioning Protocol (RPP). The profile constrains RPP to what the Extensible Provisioning Protocol (EPP) can represent, so that a server can provision a repository through RPP and EPP concurrently. This document also defines the EPP compatible preset, which combines RPP without extensions with this profile.

{mainmatter}

# Introduction

RPP is designed to coexist with the Extensible Provisioning Protocol (EPP) [@!RFC5730], often operating in parallel against a common backend provisioning system. A server in such a mixed environment can only accept what both protocols can represent.

This document defines the EPP Compatibility Profile, a profile as defined in [@!I-D.ietf-rpp-data-objects]. The profile constrains the data objects and operations of [@!I-D.ietf-rpp-data-objects], the endpoints of [@!I-D.ietf-rpp-core] and the JSON representation of [@!I-D.ietf-rpp-json]. It does not add functionality. It follows the profile specification format of [@!I-D.wullink-rpp-extension-guidelines].

A server that provisions a repository through RPP and EPP concurrently MUST include the EPP Compatibility Profile in the applicable profiles of every preset it offers, through the preset definition or through a profile binding [@!I-D.ietf-rpp-data-objects].

This document also defines the EPP compatible preset (#epp-compatible-preset), a standardised preset for clients that work with such servers.

A> TODO: The constraints of this document are also stated in [@!I-D.ietf-rpp-data-objects], [@!I-D.ietf-rpp-json] and [@!I-D.ietf-rpp-core], marked "In EPP Compatibility Profile". They are to be removed from those documents, which will then refer to this one.

## Conventions and Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

The terms Extension, Profile, Preset, Profile Binding, Applicable Profiles, Data Object, Component Object, Process Object, data element, cardinality and the other terms of the data model are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Profile Schema and Preset Schema are used as defined in [@!I-D.ietf-rpp-json].

EPP Compatibility Profile
: The profile defined in this document.

# Profile Overview {#profile-overview}

| Field | Value |
|---|---|
| Name | EPP Compatibility Profile |
| Identifier | urn:ietf:params:rpp:profile:epp-compatibility |
| Version | 1.0 |
| RPP version | 1.0 |
| Required extensions | None |
| Base profiles | None |
| Profile Schema `$id` | urn:ietf:params:rpp:schema:profile:epp-compatibility-1.0 |

# Constrained Primitive Data Types

## Timestamp {#timestamp}

* Constraints:
  * Upper case "T" and "Z" characters MUST be used. An example of a timestamp is `2025-10-27T09:42:51Z`.

# Constrained Data Objects

## Provisioning Metadata Object

* Identifier: provMetadata

### Data Elements

* Repository ID
  * Identifier: repositoryId
  * Cardinality: 1
  * Constraints:
    * This data element MUST be provided.

### Operations

None.

## Authorisation Information Object {#authorisation-information-object}

* Identifier: authInfo

### Data Elements

* Method
  * Identifier: method
  * Constraints:
    * This value MUST be set to `authinfo` if standard password-based authorisation is used.

### Operations

None.

## Restore Report Object

* Identifier: restoreReport

### Data Elements

* Restore Time
  * Identifier: restoreTime
  * Cardinality: 1
  * Constraints:
    * This element MUST be present as defined in [@!RFC3915].
* Statements
  * Identifier: statements
  * Cardinality: 2
  * Constraints:
    * Exactly two statements MUST be present as defined in [@!RFC3915].

### Operations

None.

## Domain Name Data Object

* Identifier: domainName

### Data Elements

* Contacts
  * Identifier: contacts
  * Label Constraints:
    * The value MUST be one of: "admin", "billing", or "tech".

### Operations

None.

## Contact Data Object {#contact-data-object}

* Identifier: contact

### Data Elements

* Contact Information
  * Identifier: contactInfo
  * Constraints:
    * At most one internationalised and one localised form of the contact information are provided. The internationalised form MUST be represented in a subset of UTF-8 that can be represented in the 7-bit US-ASCII character set, while the localised form MAY be represented in unrestricted UTF-8.
    * A postal address consists of up to three street lines, a city, an OPTIONAL state or province, an OPTIONAL postal code, and a country code that is a two-character identifier as specified in ISO 3166-1.
    * Telephone numbers MUST begin with a plus sign ("+"), followed by a country code defined in ITU-T E.164, followed by a dot ("."), followed by a sequence of digits, and MAY note an extension. Email addresses MUST conform to the syntax defined in [@!RFC5322].
    * In the JSON representation [@!I-D.ietf-rpp-json], `card.name.full` MUST be provided.
    * In the JSON representation, `card.addresses.addr` MUST be provided, containing at least `countryCode` and a `"locality"` kind component.
    * In the JSON representation, `card.emails.email.address` MUST be provided.
    * In the JSON representation, a localization MUST NOT contain `emails`. A localized `name` MUST contain `full`, a localized organization MUST contain `name`, and a localized address MUST contain `countryCode`, a `"locality"` kind component and at most three `"name"` kind components. A member that a localization leaves out takes the value of the internationalised form, as in JSContact.
    * At most one email address, at most one voice telephone number and at most one facsimile telephone number are provided, as defined in [@!RFC5733]. In the JSON representation, the `emails` map contains only the key `email`, and the `phones` map contains only the keys `voice` and `fax`.

### Operations

#### Create Operation

The following data elements MUST be provided:

* Handle ID (`id`)
* At least one Contact Information entry (`contactInfo`) containing a Name (`name`) and an Address (`addr`) with City (`city`) and Country Code (`cc`)
* Email (`email`)
* Authorisation Information (`authInfo`)

## Host Data Object {#host-data-object}

* Identifier: host

### Data Elements

* DNS Data
  * Identifier: dns
  * Constraints:
    * The record entries MUST be limited to A and AAAA entries for IPv4 and IPv6 glue records respectively.
    * IPv4 addresses MUST conform to [@!RFC0791] and IPv6 addresses MUST conform to [@!RFC4291]. A server MAY reject IP addresses that have not been allocated for public use by IANA.

### Operations

#### Create Operation

IP addresses are REQUIRED only as needed to produce DNS glue records. If the host name exists in a namespace for which the server is authoritative and is subordinate to an existing domain, IP addresses SHOULD be provided. If the host name is external to the server's namespace, IP addresses are not required by the DNS and MAY be omitted.

## Message Data Object {#message-data-object}

* Identifier: message

### Data Elements

None.

### Operations

#### Retrieve

The following limitations apply to the retrieval of messages, as defined in the section "Messages" of [@!I-D.ietf-rpp-core]:

* The RPP server always returns the oldest message in the EPP poll queue.
* Multiple sequential requests from the same client return the same message until the message is acknowledged.
* The `type` query parameter is ignored. The server always returns the oldest message in the EPP poll queue, regardless of its type.
* When multiple readers are used, each reader independently receives the oldest message in the EPP poll queue. Consequently, multiple readers may receive the same message, possibly multiple times, until that message is acknowledged.
* The messages remain in the `queued` state.

# Constrained Process Objects {#constrained-process-objects}

## Transfer Process Object {#transfer-process-object}

* Identifier: transfer

### Data Elements

None.

### Operations

#### Reject

* Input Data Elements:
  * Reason
    * Identifier: reason
    * Cardinality: 0
    * Constraints: This data element MUST NOT be used.

## Domain Transfer Process Object

* Identifier: domainTransfer

### Data Elements

* Transfer Period
  * Identifier: transferPeriod
  * Constraints:
    * Transfer Period cannot be read from the Transfer Process Object. The server does not return it in the output of any operation.

### Operations

None.

## Restore Process Object

* Identifier: restore

### Data Elements

* Restore Report
  * Identifier: restoreReport
  * Constraints:
    * The restore report is write-only: the server does not return it in the output of any operation, because [@!RFC3915] provides no means to retrieve a submitted report.

### Operations

#### Read (Restore Query)

This operation is not supported.

# Server Requirements {#server-requirements}

## DNS Resource Record Object

* The following record types MUST be supported, as defined in [@!RFC5732]: `ns`, `a`, and `aaaa`.
* With the DNSSEC Extension [@RFC5910], the following record types MUST additionally be supported: `ds` and `dnskey`.

### RDATA Structures {#rdata-structures}

The following RDATA structures MUST be supported, as defined in [@!RFC5732]:

* For NS records ([@!RFC1035], Section 3.3.11): `nsdname` (the fully qualified domain name of the nameserver).
* For A records ([@!RFC1035], Section 3.4.1): `address` (the IPv4 address in dotted-decimal notation).
* For AAAA records ([@RFC3596], Section 2.2): `address` (the IPv6 address in text representation as defined in [@!RFC5952]).

With the DNSSEC Extension ([@RFC5910]), the following RDATA structures MUST additionally be supported:

* For DS records ([@RFC4034], Section 5): `keyTag` (key tag value), `algorithm` (algorithm number), `digestType` (digest algorithm type), and `digest` (digest value).
* For DNSKEY records ([@RFC4034], Section 2): `flags` (flags field value), `protocol` (protocol field value), `algorithm` (algorithm number), and `publicKey` (encoded public key value).

A> TBC: Optional keyData inside dsData (RFC 5910 Section 4.1): In the DS Data Interface, a DS record MAY optionally contain a nested keyData element used for server-side validation of the DS hash. This document does not describe this pattern - a client submitting a DS record with accompanying DNSKEY for validation.

## DNS Data Object

* With the DNSSEC Extension [@RFC5910], records of type DS and DNSKEY MUST be supported in addition to NS, A, and AAAA. A server MUST support either DS or DNSKEY or both. If provided with only DNSKEY, a server MUST calculate the DS record.

## Domain Name Data Object

* A server MUST support NS, A, and AAAA record types for delegation in the DNS Data (`dns`), and with the DNSSEC Extension [@RFC5910] a server MUST additionally support DS and/or DNSKEY record types.

# JSON Schema {#epp-compatibility-profile-schema}

The following Profile Schema [@!I-D.ietf-rpp-json] expresses the constraints of the EPP Compatibility Profile that JSON Schema can express.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:ietf:params:rpp:schema:profile:epp-compatibility-1.0",
  "rpp:profile": {
    "id": "urn:ietf:params:rpp:profile:epp-compatibility",
    "version": "1.0"
  },
  "rpp:constraints": {
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/restoreReport.create":
      "#/$defs/profile.restoreReport",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/provMetadata.read":
      "#/$defs/profile.provMetadata",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/domainName.create":
      "#/$defs/profile.domainNameContacts",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/domainName.read":
      "#/$defs/profile.domainNameContacts",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/contact.create":
      "#/$defs/profile.contactCreate",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/contact.read":
      "#/$defs/profile.contact",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/contact.update":
      "#/$defs/profile.contact"
  },
  "$defs": {
    "profile.restoreReport": {
      "properties": {
        "statements": { "minItems": 2 }
      },
      "required": ["restoreTime"]
    },
    "profile.provMetadata": {
      "required": ["repositoryId"]
    },
    "profile.domainNameContacts": {
      "properties": {
        "contacts": {
          "items": {
            "properties": {
              "label": { "enum": ["admin", "billing", "tech"] }
            }
          }
        }
      }
    },
    "profile.contactCreate": {
      "$ref": "#/$defs/profile.contact",
      "required": ["authInfo"]
    },
    "profile.contact": {
      "properties": {
        "contactInfo": { "$ref": "#/$defs/profile.card" }
      }
    },
    "profile.card": {
      "required": ["name", "addresses", "emails"],
      "properties": {
        "name": {
          "required": ["full"],
          "properties": {
            "full": { "$ref": "#/$defs/profile.ascii" }
          }
        },
        "organizations": {
          "additionalProperties": {
            "properties": {
              "name": { "$ref": "#/$defs/profile.ascii" }
            }
          }
        },
        "addresses": {
          "required": ["addr"],
          "additionalProperties": {
            "$ref": "#/$defs/profile.address",
            "properties": {
              "components": {
                "items": {
                  "properties": {
                    "value": { "$ref": "#/$defs/profile.ascii" }
                  }
                }
              }
            }
          }
        },
        "emails": {
          "required": ["email"],
          "propertyNames": { "const": "email" },
          "additionalProperties": {
            "properties": {
              "address": { "$ref": "#/$defs/profile.ascii" }
            }
          }
        },
        "phones": {
          "propertyNames": { "enum": ["voice", "fax"] },
          "additionalProperties": {
            "properties": {
              "number": {
                "pattern": "^tel:\\+[0-9]{1,3}\\.[0-9]{1,14}(;ext=[0-9]+)?$"
              }
            }
          }
        },
        "localizations": {
          "maxProperties": 1,
          "additionalProperties": {
            "properties": {
              "name": { "required": ["full"] },
              "organizations": {
                "additionalProperties": { "required": ["name"] }
              },
              "addresses": {
                "additionalProperties": { "$ref": "#/$defs/profile.address" }
              },
              "emails": false
            }
          }
        }
      }
    },
    "profile.address": {
      "required": ["countryCode", "components"],
      "properties": {
        "components": {
          "allOf": [
            {
              "contains": {
                "properties": { "kind": { "const": "locality" } }
              },
              "minContains": 1
            },
            {
              "contains": {
                "properties": { "kind": { "const": "name" } }
              },
              "minContains": 0,
              "maxContains": 3
            }
          ]
        }
      }
    },
    "profile.ascii": {
      "pattern": "^[\\x20-\\x7E]*$"
    }
  }
}
```

The Profile Schema constrains every entry of a map of the JSContact Card through `additionalProperties`, and names the keys of a map only in `required` and `propertyNames`. The pattern `profile.ascii` restricts the internationalised form to printable US-ASCII characters. The localised form, in `localizations`, is not restricted to US-ASCII.

A> The constraints on a localization entry assume that the base Card schema declares the members of a localization. Today [@!I-D.ietf-rpp-json] declares `localizations` as an object without members. The definition of the localization entry is requested in https://github.com/SIDN/ietf-rpp-jscontact-profile/issues/36.

# Constraints Not Expressed in JSON Schema

The following constraints are not expressed in the Profile Schema and MUST be enforced by implementations:

* The upper-case "T" and "Z" of a Timestamp, see (#timestamp).
* The `method` of the Authorisation Information Object for password-based authorisation, see (#authorisation-information-object).
* The syntax of email addresses defined in [@!RFC5322], the country code of a telephone number defined in ITU-T E.164, and the country code of a postal address specified in ISO 3166-1, see (#contact-data-object).
* The constraints on the DNS Data of the Host Data Object and the IP addresses of its Create operation, see (#host-data-object).
* The limitations of the retrieval of messages, see (#message-data-object).
* The forbidden `reason` of the Reject operation of the Transfer Process Object, see (#transfer-process-object).
* The output restrictions of the Domain Transfer Process Object and the Restore Process Object, and the unavailable Read operation of the Restore Process Object, see (#constrained-process-objects).
* The Server Requirements, see (#server-requirements).

# Examples

The following Restore Report Object in a Create request is valid under a preset without the EPP Compatibility Profile, and invalid with the profile, because it contains one statement only:

```json
{
  "@type": "restoreReport",
  "preData": "Pre-delete registration data",
  "postData": "Post-restore registration data",
  "deleteTime": "2025-10-01T10:00:00Z",
  "restoreTime": "2025-10-20T10:00:00Z",
  "statements": [
    "The information in this report is true to the best of the client's knowledge."
  ]
}
```

A server rejects it with the result code that [@!I-D.ietf-rpp-core] defines for a broken profile constraint:

```json
{
  "type": "urn:ietf:params:rpp:error",
  "title": "RPP Error",
  "errors": [{
    "type": "https://rpp.example/problems/profile-constraint",
    "result": "02308",
    "paths": ["$.report.statements"],
    "reason": "Exactly two statements are required",
    "profile": "urn:ietf:params:rpp:profile:epp-compatibility"
  }]
}
```

The following Provisioning Metadata Object in a Read response is valid without the profile, and invalid with the profile, because `repositoryId` is missing:

```json
{
  "@type": "provMetadata",
  "spClientId": "ClientX",
  "crClientId": "ClientX",
  "crDate": "2025-10-27T09:42:51Z"
}
```

The following Domain Name Data Object in a Create request is valid without the profile, and invalid with the profile, because the contact label `reseller` is not one of "admin", "billing" or "tech":

```json
{
  "@type": "domainName",
  "name": "example.example",
  "contacts": [
    {
      "label": "reseller",
      "object": { "@type": "contact", "id": "C-1234" }
    }
  ]
}
```

The same request with the label `admin` is valid with the profile.

The following Contact Data Object in a Create request is valid with the profile:

```json
{
  "@type": "contact",
  "id": "JD-1234",
  "contactInfo": {
    "@type": "Card",
    "version": "2.0",
    "name": { "full": "John Doe" },
    "addresses": {
      "addr": {
        "components": [
          { "kind": "name", "value": "123 Example Dr., Suite 100" },
          { "kind": "locality", "value": "Dulles" },
          { "kind": "region", "value": "VA" },
          { "kind": "postcode", "value": "20166-6503" }
        ],
        "countryCode": "US"
      }
    },
    "phones": {
      "voice": { "number": "tel:+1.7035555555" }
    },
    "emails": {
      "email": { "address": "jdoe@example.example" }
    }
  },
  "authInfo": {
    "@type": "authInfo",
    "method": "authinfo",
    "authdata": "2fooBAR"
  }
}
```

The same request is valid without the profile, and invalid with the profile, in each of the following cases: `emails` contains a second entry `email-1`, `name` is missing, the address has no `locality` component, the name contains a character outside US-ASCII such as `"J\u00f6rg Doe"`, the telephone number is `tel:+1-703-555-5555`, `authInfo` is missing, `localizations` contains a second language, a localization contains `emails`, or a localized address has no `locality` component.

A> TODO: examples for the constraints that are not expressed in JSON Schema.

# EPP Compatible Preset {#epp-compatible-preset}

This section follows the preset specification format of [@!I-D.wullink-rpp-extension-guidelines].

## Introduction

The EPP compatible preset is a preset as defined in [@!I-D.ietf-rpp-data-objects], for clients of servers that provision a repository through RPP and EPP concurrently. It contains no extensions, and its applicable profiles include the EPP Compatibility Profile. A server that offers the preset can bind further profiles to it [@!I-D.ietf-rpp-data-objects].

## Preset Overview

| Field | Value |
|---|---|
| Name | EPP compatible preset |
| Identifier | urn:ietf:params:rpp:preset:epp-compatible |
| Version | 1.0 |
| RPP version | 1.0 |
| Extensions | None |
| Profiles | urn:ietf:params:rpp:profile:epp-compatibility 1.0 |
| Base presets | urn:ietf:params:rpp:preset:base 1.0 |

The EPP Compatibility Profile requires no extensions.

A client signals the preset with each request, as defined in [@!I-D.ietf-rpp-core]:

```http-message
RPP-Preset: preset=urn:ietf:params:rpp:preset:epp-compatible;version=1.0
```

## Preset Schema

The Preset Schema of the preset at a server contains, for each definition that the EPP Compatibility Profile constrains, the base definition embedded in place and the reference to the sub-schema of the Profile Schema (#epp-compatibility-profile-schema) that constrains it [@!I-D.ietf-rpp-json].

Example of the definition `restoreReport.create` in the Preset Schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://rpp.example/rpp/presets/urn:ietf:params:rpp:preset:epp-compatible/schema",
  "rpp:preset": {
    "id": "urn:ietf:params:rpp:preset:epp-compatible",
    "version": "1.0"
  },
  "$defs": {
    "restoreReport.create": {
      "allOf": [
        {
          "type": "object",
          "properties": {
            "@type": { "type": "string", "const": "restoreReport" },
            "preData": { "type": "string" },
            "postData": { "type": "string" },
            "deleteTime": { "type": "string", "format": "date-time" },
            "restoreTime": { "type": "string", "format": "date-time" },
            "restoreReason": { "type": "string" },
            "statements": {
              "type": "array",
              "items": { "type": "string" },
              "minItems": 1,
              "maxItems": 2
            },
            "other": { "type": "string" }
          },
          "required": ["@type", "statements"]
        },
        { "$ref": "#/$defs/profile.restoreReport" }
      ]
    },
    "profile.restoreReport": {
      "properties": {
        "statements": { "minItems": 2 }
      },
      "required": ["restoreTime"]
    }
  }
}
```

## IANA Considerations

The registration of the preset is requested in (#iana-preset-registration).

## Security Considerations

The preset adds no functionality and no constraints of its own. The security considerations of the EPP Compatibility Profile apply, see (#security-considerations).

# Correspondence with EPP {#epp-mapping}

This section is informative. It states how RPP constructs that the EPP Compatibility Profile constrains correspond to EPP constructs.

* Restore Process Object, data element `restoreReport`: providing this element in the Create operation corresponds to `op="report"`, omitting it corresponds to `op="request"`, and providing it in the Update operation corresponds to `op="report"` as defined in [@!RFC3915].
* Restore Process Object, Create operation (Restore Request): corresponds to `op="request"` (without report) or a combined `op="request"` followed immediately by `op="report"` as defined in [@!RFC3915].
* Restore Process Object, Update operation (Restore Report): corresponds to `op="report"` as defined in [@!RFC3915].
* Host Data Object, Read operation: host objects do not carry authorisation information and there is no distinction based on client identity as described in [@!RFC5732, section 3.1.2].

# IANA Considerations

## RPP Profiles Registry

The IANA is requested to register the following profile in the RPP Profiles registry defined in [@!I-D.ietf-rpp-data-objects]:

- `name`: EPP Compatibility Profile
- `id`: urn:ietf:params:rpp:profile:epp-compatibility
- `version`: 1.0
- `requiredExtensions`: (None)
- `baseProfiles`: (None)
- `url`: This document, (#profile-overview)
- `description`: Constrains RPP to what EPP can represent, for a server that provisions a repository through RPP and EPP concurrently.

## RPP JSON Schema Profiles Registry

The IANA is requested to register the following Profile Schema in the RPP JSON Schema Profiles registry defined in [@!I-D.ietf-rpp-json]:

- `name`: EPP Compatibility Profile
- `id`: urn:ietf:params:rpp:schema:profile:epp-compatibility-1.0
- `profile`: urn:ietf:params:rpp:profile:epp-compatibility
- `version`: 1.0
- `RFC`: This document
- `description`: The constraints of the EPP Compatibility Profile that JSON Schema can express, (#epp-compatibility-profile-schema).

## RPP Presets Registry {#iana-preset-registration}

The IANA is requested to register the following preset in the RPP Presets registry defined in [@!I-D.ietf-rpp-data-objects]:

- `name`: EPP compatible preset
- `id`: urn:ietf:params:rpp:preset:epp-compatible
- `version`: 1.0
- `extensions`: (None)
- `profiles`: urn:ietf:params:rpp:profile:epp-compatibility 1.0
- `basePresets`: urn:ietf:params:rpp:preset:base 1.0
- `url`: This document, (#epp-compatible-preset)
- `description`: RPP without extensions, constrained by the EPP Compatibility Profile.

A> The registrations above are also requested by [@!I-D.ietf-rpp-data-objects] and [@!I-D.ietf-rpp-json] until the constraints are removed from them.

# Security Considerations {#security-considerations}

The EPP Compatibility Profile only constrains RPP. It does not weaken the authentication and authorisation that [@!I-D.ietf-rpp-core] and [@!I-D.ietf-rpp-data-objects] require. A server enforces the constraints of the profile on every request, whether or not the client has validated the request against the Preset Schema.

# Privacy Considerations

The profile requires a contact to carry a name, an address and an email address, as EPP [@!RFC5733] does.

{backmatter}

# Changes History {#changes-history removeInRFC="true"}

## draft-kowalik-rpp-epp-compatibility-00

* Initial version, with the constraints marked "In EPP Compatibility Profile" in draft-ietf-rpp-data-objects-02, draft-ietf-rpp-json-01 and draft-ietf-rpp-core, the EPP Compatibility Profile Schema, and the EPP compatible preset.
