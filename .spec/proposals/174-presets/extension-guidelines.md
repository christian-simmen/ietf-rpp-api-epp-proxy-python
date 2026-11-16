# Proposal for draft-wullink-rpp-extension-guidelines: Profiles and Presets

- Issue: #174 (this repository)
- Base: draft-wullink-rpp-extension-guidelines-00, upstream `SIDN/ietf-rpp-extension-guidelines`,
  `src/draft-wullink-rpp-extension-guidelines.md` at commit `cbd3142`
- Builds on: [data-objects.md](data-objects.md), [core.md](core.md) and [json.md](json.md) (accepted)
- Status: accepted by the maintainer, with the Example Preset appendix (C15) and C13 aligned with it

This proposal brings the guidelines in line with the separation of extensions, profiles and presets. Extensions only
add, a requirement that only constrains becomes a profile, and the guidelines get a specification format for profiles
and a short one for presets, each with an example appendix. Each change below names the section of the draft, the
action, and the exact text. Section numbers are those of -00 and are given for orientation only: the title and the
anchor identify the section.

## Review Points

Choices made while drafting that the requirements in #174 and the accepted proposals do not settle:

- RG1. The Discovery extension point no longer answers the use of an unlisted extension with 02103 (Unimplemented
  extension). A request that uses an extension outside its signalled preset is a 400, as core RC4 decided. The
  restriction of an extension to specific clients becomes a restriction of a preset.
- RG2. The Profile Specification Format lists the constrained objects in the data element notation of data-objects, with
  only the attributes the profile constrains, each of which MUST be stricter than the attribute it constrains. Each
  constraint needs an example that is valid under the preset without the profile and invalid with it.
- RG3. A specification that defines an extension and a profile follows the extension format and adds a top-level
  section "Profile" with the sections of the profile format. IANA, Security, Privacy and Internationalization
  Considerations are shared. The profile has its own Profile Schema (json RJ3).
- RG4. A short Preset Specification Format is included, as the RPP Presets registry asks for a specification URL.
- RG5. A profile defines no result codes, header fields, query parameters, Problem Detail fields, Discovery properties
  or registries. These add functionality and belong to an extension.
- RG6. The "Composition and Validation" example of the Example Extension appendix shows the in-place composition of the
  Preset Schema (json RJ2) instead of the `effective.` prefix. A new appendix "Example Profile" constrains the example
  extension, and a new appendix "Example Preset" bundles the example extension and the example profile on top of the
  base preset.
- RG7. The IANA Registrations table names data-objects as the home of the RPP Extensions registry, where the registry
  is now defined, instead of core.

## C1. Abstract

Action: replace the Abstract with the following.

~~~~markdown
The RESTful Provisioning Protocol (RPP) defines a base set of data objects, component objects, and operations for provisioning objects. This document defines guidelines and a normative mechanism for extension specifications that add data elements, associations, operations, result codes, or other functionality, without modifying the base specifications itself. It also defines the format of profile specifications, which constrain the base specifications and extensions, and of preset specifications, which name a set of extensions and profiles.
~~~~

## C2. Introduction (section 1)

Action: in the second paragraph, replace "could require ad-hoc, per-combination schema and code to be written for
every deployment profile" with "could require ad-hoc, per-combination schema and code to be written for every
combination of extensions that a deployment offers".

Action: add the following paragraph after the third paragraph ("This document identifies the set of extension
points ...").

~~~~markdown
An extension adds functionality and does not constrain the base specifications or other extensions [@!I-D.ietf-rpp-data-objects]. A requirement that only constrains, for example the policy of a registry, is specified as a profile, see (#profiles). A client uses extensions and is subject to profiles through a preset that it signals with each request, see (#presets). This document defines the format of profile and preset specifications alongside the format of extension specifications.
~~~~

## C3. Terminology (section 2)

Action: replace the entry "Discovery document" with the following, and add the entries below after "Effective Schema".

~~~~markdown
Discovery document - The JSON document, published by an RPP server at a well-known location, that describes the capabilities of the server, including the presets it offers and their extensions and profiles, as defined in [@!I-D.ietf-rpp-data-objects].
~~~~

~~~~markdown
Extension, Profile, Preset, Profile Binding, Applicable Profiles - As defined in [@!I-D.ietf-rpp-data-objects].

Extension Schema, Profile Schema, Preset Schema - As defined in [@!I-D.ietf-rpp-json].

Constraints Mapper (`rpp:constraints`) - The property of a Profile Schema that maps the reference of a definition to the local definition in the Profile Schema that constrains it, as defined in [@!I-D.ietf-rpp-json].
~~~~

## C4. Restrictions on Extensions (section 4)

Action: add the following paragraph.

~~~~markdown
An extension MUST NOT constrain the base specifications or another extension, as defined in [@!I-D.ietf-rpp-data-objects]. A requirement to constrain is specified as a profile, see (#profiles).
~~~~

## C5. RPP Extension Points: Discovery (section 5.13)

Action: replace the first two paragraphs of the subsection with the following. The third paragraph stays.

~~~~markdown
A server MUST publish every extension of every preset it offers in the `extensions` list of its RPP Discovery document, as defined in [@!I-D.ietf-rpp-data-objects]. Each entry MUST contain the `name`, `id`, `version` and `url` of the extension, using the name, identifier and version defined in the Extension Overview section of the extension specification.

A client uses an extension by signalling a preset that contains it, as defined in [@!I-D.ietf-rpp-core]. A client MUST NOT use an extension that the signalled preset does not contain. A server MUST reject a request that uses such an extension as defined in [@!I-D.ietf-rpp-core], and MUST NOT include data of an extension that the preset does not contain in its responses. A server MAY restrict the use of a preset to specific clients, based on the identity and the authorisations of the client. The Discovery document is available without authentication, so a client can find presets listed that it is not authorised to use. A server MUST reject a request from an unauthorised client under such a preset with an authorisation error.
~~~~

## C6. Selecting an Extension Point (section 6)

Action: add the following paragraph before the first paragraph.

~~~~markdown
Before choosing an extension point, a designer determines whether the requirement adds functionality or only constrains what the base specifications and extensions permit. A requirement that only constrains is specified as a profile and not as an extension, see (#profiles). A requirement that has both parts is specified as an extension and a profile, with distinct identifiers.
~~~~

Action: in the paragraph starting with "Before defining an extension", replace "the IANA RPP Extensions registry, the
RPP Data Object Registry" with "the IANA RPP Extensions, RPP Profiles and RPP Presets registries, the RPP Data Object
Registry".

## C7. Identifying Extensions (section 7)

Action: add the following bullet at the end of the list.

~~~~markdown
* The identifier of an extension MUST NOT be used as the identifier of a profile or a preset, also when one specification defines the extension and the profile.
~~~~

## C8. JSON Schema: Consumer Implementation and Validation (sections 8.4 and 8.6)

Action: in "Consumer Implementation", replace the first sentence of the second paragraph ("A consumer learns at
runtime which extensions a given server supports ...") with the following.

~~~~markdown
A consumer learns at runtime which presets a given server offers, and which extensions and applicable profiles each of them has, from that server's RPP Discovery response, as defined in [@!I-D.ietf-rpp-data-objects], and uses the extensions of the preset it signals.
~~~~

Action: replace the first paragraph of "Validation" with the following.

~~~~markdown
A deployment that offers a preset MUST build its Preset Schema, as defined in [@!I-D.ietf-rpp-json]: for every definition that an extension of the preset extends or an applicable profile constrains, the effective schema composes the base definition, the `allOf` branch contributed by every extension of the preset, and the `allOf` branch contributed by every applicable profile. A server validates a request in the two steps defined in [@!I-D.ietf-rpp-json], so that it can tell a request that does not conform to the preset from a request that breaks a constraint of an applicable profile.
~~~~

Action: in the second paragraph of "Validation", replace "the combined, per-deployment schema" with "the Preset
Schema" and "any individual base or extension specification" with "any individual base, extension or profile
specification".

## C9. Extension Specification Format (section 9)

Action: add the following paragraph after the paragraph starting with "The extension specification MUST define
exactly one JSON Schema document".

~~~~markdown
A specification that defines an extension and a profile adds, after the section "Examples" of the extension, a top-level section "Profile", whose subsections are the sections 1 to 8 of the Profile Specification Format (#profile-format). The sections IANA Considerations, Security Considerations, Privacy Considerations and Internationalization Considerations are shared. The profile has its own Profile Schema, which is not part of the JSON Schema document of the extension.
~~~~

## C10. Profiles, Profile Specification Format, Presets (new sections)

Action: add the following sections after "Extension Specification Format".

~~~~markdown
# Profiles {#profiles}

A profile constrains the base specifications and the extensions it requires, as defined in [@!I-D.ietf-rpp-data-objects], and does not add functionality. This section gives guidelines for profile specifications.

A profile is the right mechanism for a requirement that limits what a client can send or what a server returns, without adding anything to it, for example the policy of a registry or the requirements of an environment such as the EPP Compatibility Profile [@!I-D.ietf-rpp-data-objects]. A profile does not define result codes, HTTP header fields, query parameters, Problem Detail fields, Discovery document properties or registries. These add functionality and are defined by an extension.

A profile is identified as an extension is, see (#identifying-extensions), with the URN form `urn:ietf:params:rpp:profile:<name>` for a standardised profile and the RPP Profiles registry. The identifier of a profile MUST NOT be used as the identifier of an extension or a preset.

A profile that constrains a definition of an extension MUST require that extension. A profile MAY build on other profiles. Before defining a profile, a designer SHOULD check the IANA RPP Profiles registry for a profile that states the same constraints, and SHOULD build on it instead of restating its constraints, so that the constraints are stated once.

A profile expresses the constraints that JSON Schema can express in a Profile Schema, using the Constraints Mapper (`rpp:constraints`), as defined in [@!I-D.ietf-rpp-json]. A Profile Schema MUST have a top-level `$id`, MUST NOT contain `unevaluatedProperties` or `additionalProperties` set to `false`, see (#validation), and MUST NOT be split over multiple documents.

## Profile Specification Format {#profile-format}

A profile specification SHOULD follow the structure defined in this section, so that all profile specifications are uniform and can be read, reviewed and processed in the same way.

A profile specification contains the following sections, in this order:

1. Introduction: the purpose of the profile, the base specifications and extensions that it constrains, and its motivation.
2. Profile Overview: the name, the identifier, the version, the minimum RPP version that the profile constrains, the required extensions with their versions, the base profiles with their versions, and the `$id` of the Profile Schema.
3. Constrained Data Objects: the data objects and component objects of the base specifications and of the required extensions that the profile constrains.
   1. Data Elements: the data elements that the profile constrains in each object.
   2. Operations: the operations of each object that the profile makes unavailable, and the input data elements, parameters and outputs that it constrains.
4. Constrained Process Objects: the process objects that the profile constrains.
   1. Data Elements: the data elements that the profile constrains in each process object.
   2. Operations: the operations of each process object that the profile makes unavailable, and the input data elements, parameters and outputs that it constrains.
5. Server Requirements: the values and behaviours that RPP or an extension permits, but does not require, and that the profile requires a server to support.
6. JSON Schema: the Profile Schema.
7. Constraints Not Expressed in JSON Schema: every constraint of the profile that the Profile Schema does not express, with a reference to the section that states it.
8. Examples: valid and invalid examples for the constraints of the profile.
9. IANA Considerations: the registration of the profile in the RPP Profiles registry and of its Profile Schema in the RPP JSON Schema Profiles registry, as described in (#iana-registries).
10. Security Considerations.
11. Privacy Considerations (optional).

A data element that is listed in a Data Elements section is identified by its name and identifier, and lists only the attributes defined in [@!I-D.ietf-rpp-data-objects] that the profile constrains, with their constrained values. A constrained attribute MUST be stricter than the attribute of the base specification or extension. For example, a Cardinality of `0-1` can be constrained to `1` or to `0`, and a Constraints attribute adds constraints to the existing ones.

A profile specification that follows this structure MUST include every section that is not marked as optional. A section that does not apply to the profile MUST contain the text "None".

The specification MUST include, for each constraint of the profile, at least one JSON example that is valid against the Preset Schema of a preset that contains the required extensions without the profile, and invalid with the profile. Every example of a valid instance MUST validate successfully against the Preset Schema with the profile.

## Presets {#presets}

A preset names a set of extensions and profiles that a client signals with each request, as defined in [@!I-D.ietf-rpp-data-objects]. A preset is identified as an extension is, see (#identifying-extensions), with the URN form `urn:ietf:params:rpp:preset:<name>` for a standardised preset and the RPP Presets registry. The identifier of a preset MUST NOT be used as the identifier of an extension or a profile.

Before defining a preset, a designer SHOULD check the IANA RPP Presets registry for a preset with the same extensions, and SHOULD use it. A server expresses its own constraints by binding profiles to a standardised preset [@!I-D.ietf-rpp-data-objects], so a new preset is not needed for them.

A preset specification SHOULD contain the following sections, in this order:

1. Introduction: the purpose of the preset and the clients and servers it is intended for.
2. Preset Overview: the name, the identifier, the version, the minimum RPP version, the extensions with their versions, the profiles with their versions, and the base presets with their versions.
3. IANA Considerations: the registration of the preset in the RPP Presets registry.
4. Security Considerations.

The extensions of a preset MUST contain every extension that its profiles require, directly or through their base profiles.
~~~~

## C11. IANA Registrations (section 10)

Action: in the first row of the table, replace "[@!I-D.ietf-rpp-core]" with "[@!I-D.ietf-rpp-data-objects]", and add
the following rows after the row "RPP Extensions".

~~~~markdown
| RPP Profiles | [@!I-D.ietf-rpp-data-objects] | Expert Review | defines a standardised profile, with its name, identifier, version, required extensions, base profiles and specification URL |
| RPP Presets | [@!I-D.ietf-rpp-data-objects] | Expert Review | defines a standardised preset, with its name, identifier, version, extensions, profiles, base presets and specification URL |
| RPP JSON Schema Profiles | [@!I-D.ietf-rpp-json] | Expert Review | defines a standardised profile with a Profile Schema |
~~~~

Action: add the following bullets after the first bullet of the list "The registrations are used as follows".

~~~~markdown
* A standardised profile MUST be registered in the RPP Profiles registry, and its Profile Schema in the RPP JSON Schema Profiles registry.
* A standardised preset MUST be registered in the RPP Presets registry.
~~~~

## C12. Security Considerations (section 12)

Action: replace the last paragraph with the following, and add the paragraph below it.

~~~~markdown
A server MUST apply authentication and authorisation to the data elements, operations and other elements that an extension adds, in the same way as for the elements of the base specifications. A server MUST reject undeclared properties, as described in (#validation), and MUST reject the use of an extension that the signalled preset does not contain, as described in the Discovery document extension point.
~~~~

~~~~markdown
A profile constrains, and cannot remove a security service or relax a constraint of the specifications it constrains. A profile can add constraints that serve security, for example a stricter pattern for a value. A server enforces the constraints of the applicable profiles on every request, whether or not the client validated the request against the Preset Schema [@!I-D.ietf-rpp-data-objects].
~~~~

## C13. Example Extension (Appendix A): Composition and Validation

Action: replace the text and the example of the subsection "Composition and Validation" with the following.

~~~~markdown
For a deployment that offers the example preset (#preset-example), the Preset Schema contains the effective schema of `domainName.create` under the key of the base definition, so that every reference to it resolves to the composed definition [@!I-D.ietf-rpp-json]. The base definition and the sub-schema of the example extension are embedded in place, and the sub-schema of the extension is composed with the sub-schema of the example profile (#profile-example) that constrains it. The base definition is abbreviated here:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://rpp.example/rpp/presets/urn:ietf:params:rpp:preset:example-preset/schema",
  "rpp:preset": {
    "id": "urn:ietf:params:rpp:preset:example-preset",
    "version": "1.0"
  },
  "$defs": {
    "domainName.create": {
      "allOf": [
        {
          "type": "object",
          "properties": {
            "@type": { "type": "string", "const": "domainName" },
            "name": { "type": "string" }
          },
          "required": ["@type", "name"]
        },
        { "$ref": "#/$defs/ext.domainName.create" }
      ]
    },
    "ext.domainName.create": {
      "allOf": [
        {
          "type": "object",
          "properties": {
            "extProperty1": { "type": "string", "minLength": 1, "maxLength": 64 }
          },
          "required": ["extProperty1"]
        },
        { "$ref": "#/$defs/profile.extProperty1" }
      ]
    },
    "profile.extProperty1": {
      "properties": {
        "extProperty1": { "pattern": "^[a-z]{1,16}$" }
      }
    }
  }
}
```
~~~~

## C14. Example Profile (new Appendix B)

Action: add the following appendix after "Example Extension".

~~~~markdown
# Example Profile {#profile-example}

This appendix is informative. It shows a profile specification that follows the structure defined in "Profile Specification Format". The example profile constrains the property `extProperty1` of the example extension (#extension-example) to at most 16 lower-case letters, and is therefore a profile that requires an extension.

## Introduction

This document provides an example of a profile specification, following the guidelines defined in [@I-D.wullink-rpp-extension-guidelines]. The example constrains a data element that an extension defines.

## Profile Overview

| Field | Value |
|---|---|
| Name | RPP Example Profile |
| Identifier | urn:ietf:params:rpp:profile:example-profile |
| Version | 1.0 |
| RPP version | 1.0 |
| Required extensions | urn:ietf:params:rpp:extension:example-ext-property 1.0 |
| Base profiles | None |
| Profile Schema `$id` | https://rpp.example/schemas/profile-example.json |

## Constrained Data Objects

### Domain Name Data Object

* Identifier: domainName

#### Data Elements

* Extension Property 1
  * Identifier: extProperty1
  * Constraints:
    * The value MUST consist of 1 to 16 lower-case letters `a` to `z`.

#### Operations

None.

## Constrained Process Objects

None.

## Server Requirements

None.

## JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://rpp.example/schemas/profile-example.json",
  "rpp:profile": {
    "id": "urn:ietf:params:rpp:profile:example-profile",
    "version": "1.0"
  },
  "rpp:constraints": {
    "https://rpp.example/schemas/ext-domain-extproperty1.json#/$defs/ext.domainName.create":
      "#/$defs/profile.extProperty1"
  },
  "$defs": {
    "profile.extProperty1": {
      "properties": {
        "extProperty1": { "pattern": "^[a-z]{1,16}$" }
      }
    }
  }
}
```

## Constraints Not Expressed in JSON Schema

None.

## Examples

The following instance is valid with and without the profile:

```json
{
  "@type": "domainName",
  "name": "example.example",
  "extProperty1": "somevalue"
}
```

The following instance is valid under a preset with the example extension and without the profile, and invalid with the profile, because `extProperty1` contains characters other than lower-case letters. A server rejects it with the result code that [@!I-D.ietf-rpp-core] defines for a broken profile constraint:

```json
{
  "@type": "domainName",
  "name": "example.example",
  "extProperty1": "Some Value"
}
```

## IANA Considerations

**TODO:**

## Security Considerations

**TODO:**
~~~~

## C15. Example Preset (new Appendix C)

Action: add the following appendix after "Example Profile".

~~~~markdown
# Example Preset {#preset-example}

This appendix is informative. It shows a preset specification that follows the structure defined in "Presets". The example preset contains the example extension (#extension-example) and the example profile (#profile-example), and builds on the base preset defined in [@!I-D.ietf-rpp-data-objects].

## Introduction

This document provides an example of a preset specification, following the guidelines defined in [@I-D.wullink-rpp-extension-guidelines]. The example preset is intended for clients that use the example extension with servers that apply the example profile. A server that offers the preset can bind further profiles to it [@!I-D.ietf-rpp-data-objects].

## Preset Overview

| Field | Value |
|---|---|
| Name | RPP Example Preset |
| Identifier | urn:ietf:params:rpp:preset:example-preset |
| Version | 1.0 |
| RPP version | 1.0 |
| Extensions | urn:ietf:params:rpp:extension:example-ext-property 1.0 |
| Profiles | urn:ietf:params:rpp:profile:example-profile 1.0 |
| Base presets | urn:ietf:params:rpp:preset:base 1.0 |

The example profile requires the example extension, which the preset contains.

A client signals the preset with each request, as defined in [@!I-D.ietf-rpp-core]:

```http-message
RPP-Preset: preset=urn:ietf:params:rpp:preset:example-preset;version=1.0
```

## IANA Considerations

A registration of the preset in the RPP Presets registry [@!I-D.ietf-rpp-data-objects] contains the following fields:

- `name`: RPP Example Preset
- `id`: urn:ietf:params:rpp:preset:example-preset
- `version`: 1.0
- `extensions`: urn:ietf:params:rpp:extension:example-ext-property 1.0
- `profiles`: urn:ietf:params:rpp:profile:example-profile 1.0
- `basePresets`: urn:ietf:params:rpp:preset:base 1.0
- `url`: This document, (#preset-example)
- `description`: RPP with the example extension, constrained by the example profile.

## Security Considerations

The preset adds no functionality and no constraints of its own. The security considerations of the example extension and of the example profile apply.
~~~~

## C16. Change History (section 15)

Action: replace "**TODO**" with the following.

~~~~markdown
* added profiles and presets: extensions do not constrain, a constraining requirement is a profile, and a client uses extensions through a preset
* replaced the rejection with 02103 of an unlisted extension by the rejection of an extension outside the signalled preset, as defined in rpp-core
* added the Profile Specification Format and a Preset Specification Format
* aligned Validation and the Example Extension with the Preset Schema of rpp-json
* added an example profile and an example preset
* added the RPP Profiles, RPP Presets and RPP JSON Schema Profiles registries to the IANA Registrations table
~~~~
