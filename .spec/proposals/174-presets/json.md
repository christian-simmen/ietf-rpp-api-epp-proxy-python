# Proposal for draft-ietf-rpp-json: Extension and Profile Schemas, Preset Schema

- Issue: #174 (this repository)
- Base: draft-ietf-rpp-json-01, upstream `src/draft-ietf-rpp-json.md` at commit `07068fc`
- Builds on: [data-objects.md](data-objects.md) and [core.md](core.md) (accepted)
- Status: accepted by the maintainer. Corrected while drafting the guidelines proposal: the Preset Schema also composes
  in place an extension sub-schema that a profile narrows (C6, Preset Schema)
- Copied: the EPP Compatibility Profile elements of this proposal are also in the new draft proposed in
  [epp-compatibility.md](epp-compatibility.md). They stay here until that draft is adopted

This proposal defines the JSON side of the separation of extensions, profiles and presets. An extension schema only
adds, a profile schema only narrows, and the schema of a preset at a server composes both in one self-contained JSON
Schema document, served as the Representation Schema of the Preset Data Object. The EPP Compatibility Profile gets a
profile schema for the constraints that JSON Schema can express. Each change below names the section of the draft, the
action, and the exact text. Section numbers are those of -01 and are given for orientation only: the title and the
anchor identify the section.

## Review Points

Choices made while drafting that the requirements in #174 and the accepted proposals do not settle:

- RJ1. The Representation Schema in JSON is one self-contained JSON Schema 2020-12 document, media type
  `application/schema+json`, whose `$id` is the URL of the `schema` sub-resource of the preset, with an `rpp:preset`
  member naming the preset and its version.
- RJ2. In the preset schema, a definition that extensions extend or profiles narrow keeps the key of the base
  definition, and its value is the `allOf` of the base definition and the sub-schemas. Only this makes a nested `$ref`
  (for example from `restoreProcess.create` to `restoreReport.create`) reach the composed definition. This replaces
  the current recommendation to give effective sub-schemas the prefix `effective.` and their own keys.
- RJ3. A profile has its own JSON Schema document, with the member `rpp:profile` (identifier and version) and the
  mapping `rpp:narrows`, analogous to `rpp:extends`. A schema document never contains both `rpp:extends` and
  `rpp:narrows`, so a specification that defines an extension and a profile defines two schema documents.
- RJ4. The narrowing rule in JSON terms: composition with `allOf` can only shrink the set of valid instances, except
  that a property declared in any branch counts as evaluated (#undeclared-properties). A profile sub-schema therefore
  MUST NOT declare a property that its target definition does not declare. An extension sub-schema MUST NOT declare a
  property of its base definition and MUST NOT list in `required` a property it does not declare.
- RJ5. To choose between 400 and 02308, a server validates a request first against the preset schema without its
  applicable profiles, and then against the preset schema. A failure in the second step only is a broken profile
  constraint, attributed to the profile whose sub-schema failed.
- RJ6. The `reference` view of the Preset and Profile Data Objects contains `version` besides `@type` and `id`,
  because data-objects requires the version in every reference to a preset or profile.
- RJ7. The entries of `presets` in the Discovery Data Object use the `read` view of the Preset Data Object, with
  `extensions`, `profiles` and `boundProfiles` required (as empty arrays when empty), as data-objects requires them.
- RJ8. A new IANA registry "RPP JSON Schema Profiles" mirrors the "RPP JSON Schema Extensions" registry, with the same
  TODO about merging it into the data-objects registries.
- RJ9. The EPP Compatibility Profile schema covers three constraints as examples: the restore report (`restoreTime`
  and exactly two `statements`), `repositoryId` in the Provisioning Metadata Object, and the contact labels `admin`,
  `billing` and `tech` of a domain name. The others stay prose in data-objects.

## C1. Terminology (section 2)

Action: replace the entry "EPP Compatibility Profile" with the following entries.

~~~~markdown
Extension, Profile, Preset, Applicable Profiles, EPP Compatibility Profile, Representation Schema - As defined in [@!I-D.ietf-rpp-data-objects].

Extension Schema - The JSON Schema document of an extension, see (#extension-framework).

Profile Schema - The JSON Schema document of a profile, see (#profile-schema).

Preset Schema - The Representation Schema of a preset at a server in JSON, see (#preset-schema).
~~~~

## C2. RPP Profiles and Validation (in "JSON Schema Composition Rules")

Action: replace the subsection with the following.

~~~~markdown
### Profiles and Validation {#profiles-validation}

A profile narrows RPP and its required extensions [@!I-D.ietf-rpp-data-objects]. The constraints of a profile that JSON Schema can express are expressed in its Profile Schema (#profile-schema). The other constraints are stated in the profile specification, and implementations enforce them in addition to the Preset Schema.

A server validates a request under a preset in two steps, so that it can tell a request that does not conform to the preset from a request that breaks a constraint of an applicable profile:

1. The server validates the request against the Preset Schema composed without the applicable profiles. A request that fails this step does not conform to the preset, and the server rejects it as defined in [@!I-D.ietf-rpp-core] for content that does not conform.
2. The server validates the request against the Preset Schema, and checks the constraints of the applicable profiles that the Profile Schemas do not express. A request that fails only this step breaks a constraint of an applicable profile, and the server rejects it with the result code that [@!I-D.ietf-rpp-core] defines for this case.

The profile of a constraint that a request breaks in the second step is the profile whose Profile Schema contributed the failing sub-schema, or whose specification states the constraint.

A client MAY validate a request against the Preset Schema before sending it. A server enforces the constraints regardless.
~~~~

## C3. Provisioning Metadata Object and Restore Report Object (in "Component Objects Schemas")

Action: in the list of constraints that cannot be expressed in JSON Schema of the Provisioning Metadata Object, remove
the entry "In the EPP Compatibility Profile, `repositoryId` MUST be provided." In the corresponding list of the Restore
Report Object, remove the two entries starting with "In the EPP Compatibility Profile". After each of the two lists,
add the following sentence.

~~~~markdown
The constraints of the EPP Compatibility Profile on this object are expressed in the EPP Compatibility Profile Schema (#epp-compatibility-profile-schema).
~~~~

## C4. Discovery Data Object (Read)

Action: in the Read response schema, replace the property `profiles` with the properties `presets` and `profiles`
below.

~~~~markdown
        "presets": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/preset.read",
            "required": ["extensions", "profiles", "boundProfiles"]
          },
          "minItems": 1,
          "readOnly": true
        },
        "profiles": {
          "type": "array",
          "items": { "$ref": "#/$defs/profile.reference" },
          "readOnly": true
        },
~~~~

Action: add `"presets"` to the `required` array of `discovery.read`, and add the following entries to the list of
constraints that cannot be expressed in JSON Schema.

~~~~markdown
- Exactly one entry of `presets` MUST have `defaultPreset` set to `true`.
- `extensions` MUST contain every extension of every entry of `presets`, and `profiles` every profile that is applicable to an entry of `presets`.
~~~~

## C5. Profile Data Object

Action: replace the section "Profile Data Object", including its subsections, with the two sections below.

~~~~markdown
## Preset Data Object

The Preset Data Object represents a preset offered by the server. All data elements are read-only, and the only supported operation is Read. The data element `schema` has the Visibility `onDemand`, and is therefore not listed under `required` in the read view. As a Direct Access sub-resource, its value is the Preset Schema (#preset-schema), represented in the media type `application/schema+json`. When the client requests it with the Include Elements parameter, the value is embedded as a JSON object.

The following constraints cannot be expressed in JSON Schema and MUST be enforced by implementations:

- `id` of a standardised preset MUST use the form `urn:ietf:params:rpp:preset:{name}`. The `id` of a private preset MUST be globally unique, and the use of reverse domain name notation is RECOMMENDED.
- `extensions` and `profiles` MUST NOT contain an identifier more than once, and `boundProfiles` MUST NOT contain a profile that `profiles` contains.
- `basePresets` MUST NOT reference the preset itself, directly or indirectly.
- Exactly one preset offered by the server MUST have `defaultPreset` set to `true`.

### Read

Read response schema (read-only properties):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$ref": "#/$defs/preset.read",
  "$defs": {
    "preset.read": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "preset", "readOnly": true },
        "id": { "type": "string", "readOnly": true },
        "name": { "type": "string", "readOnly": true },
        "description": { "type": "string", "readOnly": true },
        "version": { "type": "string", "readOnly": true },
        "rppVersion": { "type": "string", "readOnly": true },
        "url": { "type": "string", "format": "uri", "readOnly": true },
        "basePresets": {
          "type": "array",
          "items": { "$ref": "#/$defs/preset.reference" },
          "readOnly": true
        },
        "extensions": {
          "type": "array",
          "items": { "$ref": "#/$defs/extension.read" },
          "readOnly": true
        },
        "profiles": {
          "type": "array",
          "items": { "$ref": "#/$defs/profile.reference" },
          "readOnly": true
        },
        "boundProfiles": {
          "type": "array",
          "items": { "$ref": "#/$defs/profile.reference" },
          "readOnly": true
        },
        "defaultPreset": { "type": "boolean", "readOnly": true },
        "schema": { "type": "object", "readOnly": true }
      },
      "required": [
        "@type",
        "id",
        "name",
        "description",
        "version",
        "rppVersion",
        "defaultPreset"
      ]
    }
  }
}
```

### Reference

Reference schema. Besides the Unique Identifier, it contains the version, which [@!I-D.ietf-rpp-data-objects] requires in every reference to a preset:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$ref": "#/$defs/preset.reference",
  "$defs": {
    "preset.reference": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "preset" },
        "id": { "type": "string", "readOnly": true },
        "version": { "type": "string", "readOnly": true }
      },
      "required": ["@type", "id", "version"]
    }
  }
}
```

## Profile Data Object

The Profile Data Object represents a profile that is applicable to at least one preset offered by the server. All data elements are read-only, and the only supported operation is Read.

The following constraints cannot be expressed in JSON Schema and MUST be enforced by implementations:

- `id` of a standardised profile MUST use the form `urn:ietf:params:rpp:profile:{name}`. The `id` of a private profile MUST be globally unique, and the use of reverse domain name notation is RECOMMENDED.
- `requiredExtensions` MUST NOT contain an extension identifier more than once.
- `baseProfiles` MUST NOT reference the profile itself, directly or indirectly.

### Read

Read response schema (read-only properties):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$ref": "#/$defs/profile.read",
  "$defs": {
    "profile.read": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "profile", "readOnly": true },
        "id": { "type": "string", "readOnly": true },
        "name": { "type": "string", "readOnly": true },
        "description": { "type": "string", "readOnly": true },
        "version": { "type": "string", "readOnly": true },
        "rppVersion": { "type": "string", "readOnly": true },
        "url": { "type": "string", "format": "uri", "readOnly": true },
        "baseProfiles": {
          "type": "array",
          "items": { "$ref": "#/$defs/profile.reference" },
          "readOnly": true
        },
        "requiredExtensions": {
          "type": "array",
          "items": { "$ref": "#/$defs/extension.read" },
          "readOnly": true
        }
      },
      "required": [
        "@type",
        "id",
        "name",
        "description",
        "version",
        "rppVersion",
        "url"
      ]
    }
  }
}
```

### Reference

Reference schema. Besides the Unique Identifier, it contains the version, which [@!I-D.ietf-rpp-data-objects] requires in every reference to a profile:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$ref": "#/$defs/profile.reference",
  "$defs": {
    "profile.reference": {
      "type": "object",
      "properties": {
        "@type": { "type": "string", "const": "profile" },
        "id": { "type": "string", "readOnly": true },
        "version": { "type": "string", "readOnly": true }
      },
      "required": ["@type", "id", "version"]
    }
  }
}
```
~~~~

## C6. Extension Framework (section 7)

Action: replace the first paragraph ("Extensions MUST employ an additive schema composition method, ...") with the
following. The TODO about extending enumerations that follows it stays.

~~~~markdown
An extension adds functionality and does not narrow RPP or another extension [@!I-D.ietf-rpp-data-objects]. Extension Schemas therefore employ an additive schema composition method, allowing new optional or required properties to be added to an existing base object schema. A sub-schema of an Extension Schema MUST NOT:

- declare under `properties` a property that the base definition declares,
- list under `required` a property that the sub-schema does not declare, or
- use a keyword that constrains the base object as a whole, such as `maxProperties`, `not`, `if`, `dependentRequired` or `dependentSchemas`, other than for properties the sub-schema declares.

An Extension Schema MUST NOT contain the `rpp:narrows` member (#profile-schema).
~~~~

Action: replace the section "Effective Schema" with the following.

~~~~markdown
## Effective Schema

The effective schema of a base definition under a preset at a server is the composition, using the `allOf` keyword, of the base definition, the sub-schemas that the Extension Schemas of the extensions of the preset map to it with `rpp:extends`, and the sub-schemas that the Profile Schemas of the applicable profiles map to it with `rpp:narrows` (#profile-schema). A validator uses it to determine whether an object conforms to the combined constraints. The server uses the `rpp:extends` and `rpp:narrows` members to resolve the mapping between the base definition and the sub-schemas.

Extension sub-schemas only add properties, and profile sub-schemas only narrow the properties that the base definition and the extension sub-schemas declare. The composition with `allOf` therefore keeps every property of the base definition and of the extensions, and narrows the set of valid instances by the constraints of the profiles.

The following is an example of an Extension Schema, which adds new properties to both the domain and contact base objects:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://rpp.example/schemas/extension1.json",

  "rpp:extends": {
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/domainName.create":
      "#/$defs/ext.domain",

    "urn:ietf:params:rpp:schema:json-1.0#/$defs/contact.create":
      "#/$defs/ext.contact"
  },

  "$defs": {
    "ext.domain": {
      "type": "object",
      "properties": {
        "foo": { "type": "string" },
        "bar": { "type": "boolean" }
      },
      "required": ["foo"]
    },

    "ext.contact": {
      "type": "object",
      "properties": {
        "fooContact": { "type": "string" }
      }
    }
  }
}
```

The Preset Schema (#preset-schema) contains the effective schema of every definition.
~~~~

Action: add the following sections at the end of the section "Extension Framework", renaming the section to
"Extension and Profile Framework" while keeping its anchor `{#extension-framework}`.

~~~~markdown
## Profile Schema {#profile-schema}

A profile expresses the constraints that JSON Schema can express in a Profile Schema, a JSON Schema document whose sub-schemas narrow definitions of RPP and of the extensions that the profile requires. A profile has at most one Profile Schema.

A Profile Schema MUST have a top-level `$id`, and MUST contain the member `rpp:profile`, whose value is an object with the members `id` and `version`, holding the identifier and the version of the profile. A Profile Schema MUST NOT contain the member `rpp:extends`. A specification that defines an extension and a profile defines an Extension Schema and a Profile Schema.

A Profile Schema MUST map every sub-schema to the definitions it narrows, using the member `rpp:narrows`. Its keys are the absolute URIs of the narrowed definitions, of RPP or of an Extension Schema of a required extension. Its values are the JSON Pointers of the sub-schemas in the Profile Schema. More than one key MAY map to the same sub-schema.

A sub-schema of a Profile Schema only narrows. It MAY use any JSON Schema keyword that constrains the properties that the narrowed definition declares, for example `required`, `minItems`, `maxItems`, `enum`, `const`, `pattern`, `maxLength`, or the schema `false` for a property that the profile forbids. A sub-schema of a Profile Schema MUST NOT declare under `properties`, at any depth, a property that the narrowed definition does not declare at that depth. A property declared in any branch of an `allOf` is evaluated (#undeclared-properties), so such a property would be accepted and add functionality.

It is RECOMMENDED to use the prefix "profile." for every sub-schema of a Profile Schema, for example `#/$defs/profile.restoreReport`.

A profile whose base profiles have Profile Schemas does not repeat their sub-schemas. The applicable profiles of a preset include the base profiles, so their Profile Schemas take part in the effective schema.

## Preset Schema {#preset-schema}

The Representation Schema [@!I-D.ietf-rpp-data-objects] in JSON is the Preset Schema: a JSON Schema 2020-12 document that describes the messages of RPP and of the extensions of a preset, narrowed by the applicable profiles of the preset at the server. Its media type is `application/schema+json`. The server serves it as the Direct Access sub-resource `schema` of the Preset Data Object.

The Preset Schema MUST be self-contained: it MUST NOT reference a schema outside the document. It is constructed as follows:

- Its `$id` is the URL of the `schema` sub-resource of the preset at the server.
- It contains the member `rpp:preset`, whose value is an object with the members `id` and `version`, holding the identifier and the version of the preset.
- Its `$defs` contains every definition of RPP under the key of the definition.
- The value of a definition that an extension extends or a profile narrows is its effective schema: an `allOf` of the base definition, embedded in place, and the references to the extension and profile sub-schemas, in that order.
- Its `$defs` contains the sub-schemas of the Extension Schemas of the extensions of the preset and of the Profile Schemas of the applicable profiles, under their keys.
- The value of a sub-schema of an Extension Schema that a profile narrows is the `allOf` of the sub-schema, embedded in place, and the references to the profile sub-schemas.

A nested reference to a definition, for example from the `create` view of a Process Object to the `create` view of a Component Object, therefore resolves to its effective schema.

A Preset Schema does not carry the `unevaluatedProperties` keywords of (#undeclared-properties). A validator adds them before validation, as for any other RPP schema.

Example of the definition `restoreReport.create` in the Preset Schema of a preset whose applicable profiles include the EPP Compatibility Profile:

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

## EPP Compatibility Profile Schema {#epp-compatibility-profile-schema}

The following Profile Schema expresses constraints of the EPP Compatibility Profile [@!I-D.ietf-rpp-data-objects] that JSON Schema can express. The other constraints of the profile are stated in [@!I-D.ietf-rpp-data-objects] and enforced by implementations.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:ietf:params:rpp:schema:profile:epp-compatibility-1.0",
  "rpp:profile": {
    "id": "urn:ietf:params:rpp:profile:epp-compatibility",
    "version": "1.0"
  },
  "rpp:narrows": {
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/restoreReport.create":
      "#/$defs/profile.restoreReport",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/provMetadata.read":
      "#/$defs/profile.provMetadata",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/domainName.create":
      "#/$defs/profile.domainNameContacts",
    "urn:ietf:params:rpp:schema:json-1.0#/$defs/domainName.read":
      "#/$defs/profile.domainNameContacts"
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
    }
  }
}
```
~~~~

## C7. Examples: Discovery and Profile

Action: in the example discovery read response, replace the member `profiles` with the following.

~~~~markdown
    "presets": [
        {
            "@type": "preset",
            "id": "urn:ietf:params:rpp:preset:epp-compatible",
            "name": "EPP compatible preset",
            "description": "RPP without extensions, narrowed by the EPP Compatibility Profile",
            "version": "1.0",
            "rppVersion": "1.0",
            "basePresets": [
                {
                    "@type": "preset",
                    "id": "urn:ietf:params:rpp:preset:base",
                    "version": "1.0"
                }
            ],
            "extensions": [],
            "profiles": [
                {
                    "@type": "profile",
                    "id": "urn:ietf:params:rpp:profile:epp-compatibility",
                    "version": "1.0"
                }
            ],
            "boundProfiles": [
                {
                    "@type": "profile",
                    "id": "org.example.rpp.profile.registry-policy",
                    "version": "1.0"
                }
            ],
            "defaultPreset": true
        }
    ],
    "profiles": [
        {
            "@type": "profile",
            "id": "urn:ietf:params:rpp:profile:epp-compatibility",
            "version": "1.0"
        },
        {
            "@type": "profile",
            "id": "org.example.rpp.profile.registry-policy",
            "version": "1.0"
        }
    ],
~~~~

Action: replace the section "Profile" of the Examples with the following.

~~~~markdown
## Preset

### Read

There is no request message for the preset read operation.

Example preset read response:

```json
{
    "@type": "preset",
    "id": "urn:ietf:params:rpp:preset:epp-compatible",
    "name": "EPP compatible preset",
    "description": "RPP without extensions, narrowed by the EPP Compatibility Profile",
    "version": "1.0",
    "rppVersion": "1.0",
    "url": "https://www.iana.org/assignments/rpp-presets/epp-compatible",
    "basePresets": [
        {
            "@type": "preset",
            "id": "urn:ietf:params:rpp:preset:base",
            "version": "1.0"
        }
    ],
    "extensions": [],
    "profiles": [
        {
            "@type": "profile",
            "id": "urn:ietf:params:rpp:profile:epp-compatibility",
            "version": "1.0"
        }
    ],
    "boundProfiles": [
        {
            "@type": "profile",
            "id": "org.example.rpp.profile.registry-policy",
            "version": "1.0"
        }
    ],
    "defaultPreset": true
}
```

The schema of the preset is read from the sub-resource `/presets/urn:ietf:params:rpp:preset:epp-compatible/schema` with the media type `application/schema+json`, see (#preset-schema).

## Profile

### Read

There is no request message for the profile read operation.

Example read response for a profile of a server that builds on the EPP Compatibility Profile:

```json
{
    "@type": "profile",
    "id": "org.example.rpp.profile.registry-policy",
    "name": "Registry policy",
    "description": "Constraints of the registry on top of the EPP Compatibility Profile",
    "version": "1.0",
    "rppVersion": "1.0",
    "url": "https://registry.example/rpp/profiles/registry-policy",
    "baseProfiles": [
        {
            "@type": "profile",
            "id": "urn:ietf:params:rpp:profile:epp-compatibility",
            "version": "1.0"
        }
    ],
    "requiredExtensions": []
}
```
~~~~

## C8. IANA Considerations

Action: in the registration of the media type "application/rpp+json", replace the line "Optional parameters: profile,
version" with the following.

~~~~markdown
Optional parameters: preset, preset-version, version
~~~~

Action: add the following section after "RPP JSON Schema Extensions Registry".

~~~~markdown
## RPP JSON Schema Profiles Registry

The IANA is requested to create a new registry for RPP JSON Schema profiles. This registry will be used to register the Profile Schemas (#profile-schema) of standardised profiles.

```text
Name of the registry: RPP JSON Schema Profiles
Registry group: RESTful Provisioning Protocol (RPP)
Registration procedure: Expert Review
```

Fields to be registered:

- `name`: The name of the profile, for example "EPP Compatibility Profile".
- `id`: The unique `$id` URI of the Profile Schema, for example "urn:ietf:params:rpp:schema:profile:epp-compatibility-1.0".
- `profile`: The identifier of the profile in the RPP Profiles registry, for example "urn:ietf:params:rpp:profile:epp-compatibility".
- `version`: The version of the profile, for example "1.0".
- `RFC`: The RFC number for the profile specification, for example "RFC 1234".
- `description`: A human-readable description of the profile and its intended use.

Initial registrations:

- `name`: EPP Compatibility Profile
- `id`: urn:ietf:params:rpp:schema:profile:epp-compatibility-1.0
- `profile`: urn:ietf:params:rpp:profile:epp-compatibility
- `version`: 1.0
- `RFC`: This document
- `description`: The constraints of the EPP Compatibility Profile that JSON Schema can express, (#epp-compatibility-profile-schema).

**TODO** consider whether this registry is necessary or if it should be merged with the RPP Profiles registry defined in [@!I-D.ietf-rpp-data-objects], as for the RPP JSON Schema Extensions registry.
~~~~

## C9. Change History

Action: add the following entries to the subsection of the next revision.

~~~~markdown
- Restricted Extension Schemas to additions, and added Profile Schemas with `rpp:profile` and `rpp:narrows` in (#profile-schema)
- Added the Preset Schema in (#preset-schema), composing effective schemas in place under the keys of the base definitions
- Added the two-step validation of (#profiles-validation) that separates non-conforming requests from broken profile constraints
- Added the EPP Compatibility Profile Schema in (#epp-compatibility-profile-schema)
- Replaced the Profile Data Object schemas by schemas of the Preset and Profile Data Objects, and the `profiles` of the Discovery Data Object by `presets` and `profiles`
- Replaced the `profile` parameter of the media type by `preset` and `preset-version`, and added the RPP JSON Schema Profiles registry
~~~~
