# Proposal for draft-ietf-rpp-data-objects: Extensions, Profiles and Presets

- Issue: #174 (this repository)
- Base: draft-ietf-rpp-data-objects-02, upstream `src/draft-ietf-rpp-data-objects.md` at commit `5867f10`
- Status: accepted by the maintainer, with the maintainer's edits. Amended after review of the core proposal: the
  schema of a preset is a Direct Access data element (R6), with C3a, C3b and the `schema` element added
- Copied: the EPP Compatibility Profile elements of this proposal are also in the new draft proposed in
  [draft-kowalik-rpp-epp-compatibility.md](draft-kowalik-rpp-epp-compatibility.md). They stay here until that draft is adopted

This proposal separates the current notion of a profile into three concepts: the extension, which adds functionality,
the profile, which constrains, and the preset, which a client signals and which names a set of extensions and profiles.
A server binds further profiles to a preset as its own policy. Each change below names the section of the draft, the
action, and the exact text, in the notation of the draft. Section numbers are those of -02 and are given for
orientation only: the title and the anchor identify the section.

Proposals for draft-ietf-rpp-core, draft-ietf-rpp-json and draft-wullink-rpp-extension-guidelines follow in separate
files and build on the terms defined here.

## Review Points

Choices made while drafting that the requirements in #174 do not settle:

- R1. The Preset and Profile Data Objects use `id` (the URN) as their Unique Identifier and `name` as a short
  human-readable name, as the Extension Object and the IANA registries already do. Today the Profile Data Object uses
  `name` for the URN.
- R2. The permitted constraints include making an operation unavailable, restricting the output of an operation, and
  requiring the server to support a value that RPP permits but does not require. Without these, several existing
  EPP Compatibility Profile constraints (the Read operation of the Restore Process Object is "not supported", the write-only restore
  report, the record types a server MUST support) would not fit a profile. The statements that map RPP to EPP
  ("corresponds to `op="report"`") stay informative text.
- R3. A server offers one version of a preset or profile at a time (the Unique Identifier is `id`, as for the
  profile today). Offering two versions side by side would need a composite identifier.
- R4. A required extension and a profile or preset referenced as a base are matched by identifier and exact version.
- R5. The `objects` element of today's Profile Data Object is not carried over to the Preset Data Object, as a preset
  is a list of extensions and can be standardised. The `objects` element of the Discovery Data Object stays as it is.
- R6. (Amended, maintainer) The schema of a preset at a server is the data element `schema` of the Preset Data Object,
  of the new Common Data Type Representation Schema, with Visibility `onDemand` and Direct Access, so that core derives
  `/presets/{id}/schema` by its Rule 3. Direct Access is allowed on any data element of cardinality `0-1` or `1`, not
  only on associations. Whether the Read operation, and with it the schema, needs authentication is server policy.
- R7. Two initial preset registrations demonstrate the concept: `urn:ietf:params:rpp:preset:base` (no extension, no
  profile) and `urn:ietf:params:rpp:preset:epp-compatible` (built on `base`, with the EPP Compatibility Profile).
- R8. A server SHOULD offer a standardised preset rather than a private one with the same extensions, to avoid
  fragmentation. (The maintainer removed the binding rules that bound profiles do not depend on the client or the
  request, that every constraint on the form of a request SHOULD be in a profile, and that a change of the bound
  profiles SHOULD be announced.)

## C1. Abstract and Introduction

Action: in the Abstract and in the first paragraph of the Introduction, replace "as well as the discovery and profile
objects that describe server capabilities" with the following.

~~~~markdown
as well as the discovery, preset, and profile objects that describe server capabilities and policies
~~~~

## C2. Conventions and Terminology (section 1.1)

Action: add the following terms after "Label Generation Ruleset (LGR)".

~~~~markdown
Extension
: A specification that adds functionality to RPP, as defined in (#extensions).

Profile
: A specification that constrains what RPP and a set of extensions permit, as defined in (#profiles).

Preset
: A named and versioned set of extensions and profiles that a client signals with a request, as defined in (#presets).

Profile Binding
: The association of a profile with a preset that a server makes in addition to the profiles of the preset definition, as defined in (#profile-binding).

Applicable Profiles
: The profiles whose constraints apply to a request under a preset at a server, as defined in (#applicable-profiles).
~~~~

## C3. Extensibility (section 2.3)

Action: add the anchor `{#extensibility}` to the heading "Extensibility", and replace its last paragraph ("When an
extension adds data elements, input data elements, or parameters to a core object or operation, these additions MUST
NOT alter the semantics or constraints of existing core data elements.") with the following.

~~~~markdown
Extensions are additive. An extension MUST NOT constrain RPP or another extension. In particular, for a data element, input data element or parameter that the extension does not define, an extension MUST NOT:

* raise the lower bound or lower the upper bound of its cardinality,
* restrict its permitted values, or
* alter its semantics.

An extension MAY define any cardinality and constraints for the data elements, input data elements and parameters it defines itself, including making them required. Constraining is the purpose of a profile, see (#profiles).
~~~~

## C3a. Data Element Semantics (section 2.4)

Action: replace the paragraph starting with "The Direct Access flag is applicable only to a data element whose Data
Type is an association" with the following.

~~~~markdown
The Direct Access flag is applicable to a data element whose Data Type is an association (Aggregation, Composition, Labelled Aggregation, Dictionary Aggregation, Labelled Composition, or Dictionary Composition) with a Data Object, Component Object, or Process Object, of any cardinality. Where such a data element has a cardinality greater than `1`, the associated object type MUST define a Unique Identifier, so that an individual associated object can be addressed unambiguously among the collection.

The Direct Access flag is also applicable to a data element of any other Data Type with a cardinality of `0-1` or `1`. The sub-resource of such a data element is the value of the data element.
~~~~

## C3b. Common Data Types (section 6)

Action: add the following subsection after "Phone Number".

~~~~markdown
## Representation Schema {#representation-schema}

A Representation Schema is a schema that describes the messages of RPP in one representation, in the schema language that the representation specification defines. Its content is not defined by this document. Each representation specification defines the schema language, how the schema of a preset combines the schemas of RPP, of the extensions of the preset and of its applicable profiles (#applicable-profiles), and the media type of a Representation Schema value, for example [@!I-D.ietf-rpp-json].
~~~~

## C4. EPP Compatibility Profile (section 2.8)

Action: replace the section with the following.

~~~~markdown
## EPP Compatibility Profile {#epp-compatibility-profile}

RPP is designed to coexist with the Extensible Provisioning Protocol (EPP), often operating in parallel against a common backend provisioning system. A server in such a mixed environment can only accept what both protocols can represent.

This document defines the EPP Compatibility Profile, a profile as defined in (#profiles), with the following attributes:

* Name: EPP Compatibility Profile
* Identifier: `urn:ietf:params:rpp:profile:epp-compatibility`
* Version: `1.0`
* Required Extensions: (None)
* Base Profiles: (None)

The constraints of the profile are the constraints marked "In EPP Compatibility Profile" throughout this document. Each of them constrains RPP in one of the ways listed in (#profiles). Text marked "In EPP Compatibility Profile" that maps an RPP construct to an EPP construct is informative. [@!I-D.ietf-rpp-json] defines how the constraints are expressed in JSON Schema.

A server that provisions a repository through RPP and EPP concurrently MUST include the EPP Compatibility Profile in the applicable profiles (#applicable-profiles) of every preset it offers, through the preset definition or through a profile binding.
~~~~

## C5. Profiles (section 4)

Action: replace the section "Profiles", including its subsection "Inheritance", with the following.

~~~~markdown
# Extensions, Profiles and Presets {#extensions-profiles-presets}

This section defines how extensions, profiles and presets describe the functionality and the constraints that apply to an RPP request.

An extension adds functionality. A profile constrains what RPP and its extensions permit. A preset names a set of extensions and profiles, so that a client and a server agree on both with a single identifier. Because a client signals a preset and not a list of extensions, the number of combinations of extensions that a server serves, and therefore the number of schemas that describe its messages, is bounded by the number of presets it offers.

## Extensions {#extensions}

An extension adds functionality to RPP using the extension points defined in (#extensibility), and does not constrain RPP or another extension. An extension is identified by a unique identifier. The identifier of a standardised extension is registered in the RPP Extension Registry (#iana-extension-registry).

A client does not select an extension on its own. A client uses an extension by signalling a preset that contains it, see (#presets).

## Profiles {#profiles}

A profile constrains the set of requests, responses and server behaviours that RPP and a set of extensions permit. A profile expresses the policy of a server, or the requirements of the environment in which a server operates, such as the EPP Compatibility Profile (#epp-compatibility-profile).

A profile constrains only in the following ways:

1. Raising the lower bound of the cardinality of a data element, input data element or parameter, which makes an optional element required.
2. Lowering the upper bound of the cardinality of a data element, input data element or parameter. An upper bound of zero forbids the element.
3. Restricting the permitted values of a data element, input data element or parameter, for example to a subset of the values of an enumeration, to a pattern, to a maximum length, or to a range.
4. Making an operation unavailable.
5. Restricting the output of an operation, for example by never returning a data element.
6. Requiring the server to support a value or a behaviour that RPP or an extension permits but does not require, for example a DNS record type.

A profile MUST NOT add functionality. In particular, a profile MUST NOT define a data object, data element, association, operation, process, input data element, parameter or value that RPP and the extensions the profile requires do not define, and MUST NOT relax a constraint of RPP or of an extension.

A profile specification states each constraint normatively. Where a representation can express a constraint in its schema language, the representation specification defines how a profile expresses it, see [@!I-D.ietf-rpp-json]. A constraint that the schema language cannot express is stated in prose, or by reference to the normative text that defines it.

A profile MAY require extensions. A profile that constrains a data element, operation or value that an extension defines MUST require that extension. A required extension is identified by its identifier and version.

A profile MAY build on one or more base profiles, see (#preset-profile-inheritance).

A profile is identified by a unique identifier. The identifier of a standardised profile uses the RPP URN namespace, in the form `urn:ietf:params:rpp:profile:{name}`, and is registered in the RPP Profile Registry (#iana-profile-registry). The identifier of a private profile MUST be globally unique. The use of reverse domain name notation is RECOMMENDED for private profile identifiers, as it is for private extension identifiers.

An extension and a profile are distinct even when one specification defines both. Such a specification assigns each its own identifier. An identifier MUST NOT denote more than one of an extension, a profile and a preset.

## Presets {#presets}

A preset is a named and versioned set of extensions and profiles. Its extensions state the functionality a client uses. Its profiles state the constraints that the preset definition includes.

A client signals a preset with every request, as defined in [@!I-D.ietf-rpp-core]. A client does not signal extensions or profiles. A request uses only the extensions of the signalled preset. A client MUST NOT use the functionality of an extension that the signalled preset does not contain, and a server MUST refuse a request that does.

A preset definition consists of an identifier, a name, a version, the extensions it contains, the profiles it includes, and its base presets (#preset-profile-inheritance). A preset MUST contain every extension that its profiles require, directly or through their base profiles.

A preset can be standardised, so that many servers offer the same preset and a client implements it once. The identifier of a standardised preset uses the RPP URN namespace, in the form `urn:ietf:params:rpp:preset:{name}`, and is registered in the RPP Preset Registry (#iana-preset-registry). The identifier of a private preset MUST be globally unique. The use of reverse domain name notation is RECOMMENDED for private preset identifiers.

A server designates exactly one of the presets it offers as its default preset. The default preset applies to a request that signals no preset.

A server that offers a set of extensions for which a standardised preset exists SHOULD offer that preset, and express its own constraints through profile bindings (#profile-binding), instead of defining a private preset with the same extensions. A private preset with the same extensions as a standardised preset makes a client support two identifiers for one set of messages, and fragments the protocol. A server can have a reason to deviate, for example when it offers a version of an extension that the standardised preset does not contain.

## Profile Binding {#profile-binding}

A server MAY bind profiles to a preset it offers, in addition to the profiles of the preset definition. A binding is not part of the definition of the preset or of the profile. The same preset can have different bound profiles at different servers.

The following rules apply to a profile binding:

* A server MUST NOT bind a profile to a preset that does not contain every extension the profile requires, directly or through its base profiles.
* A server publishes the bound profiles of each preset it offers in the Preset Data Object (#preset-data-object) and in the Discovery Data Object.

## Inheritance of Presets and Profiles {#preset-profile-inheritance}

A preset MAY build on one or more base presets. A profile MAY build on one or more base profiles. Inheritance is a union without overriding, so that a preset or a profile is flattened by collecting the contents of its bases:

* The extensions of a preset are its own extensions and the extensions of all its base presets, directly or indirectly.
* The profiles of a preset are its own profiles and the profiles of all its base presets, directly or indirectly.
* The constraints of a profile are its own constraints and the constraints of all its base profiles, directly or indirectly. A profile adds constraints to those of its base profiles, and does not remove or relax any of them.
* The required extensions of a profile are its own required extensions and those of all its base profiles, directly or indirectly.
* An extension, profile, preset or constraint that is reached through more than one base counts once.

A base preset or base profile is referenced by its identifier and version. A preset or profile MUST NOT build on itself, directly or indirectly. A preset whose flattened extensions contain one extension in two versions is invalid. A profile whose flattened required extensions contain one extension in two versions is invalid. A server MUST NOT offer an invalid preset and MUST NOT apply an invalid profile.

The constraints of several profiles combine as a conjunction. A combination of constraints that no value satisfies makes the element concerned unusable, but does not make the profile invalid.

## Applicable Profiles {#applicable-profiles}

The applicable profiles of a preset at a server are the profiles of the preset, the profiles the server binds to it, and the base profiles of all of these, directly or indirectly. A request under a preset is subject to the constraints of all its applicable profiles.

A server MUST enforce the constraints of the applicable profiles on every request, whether or not the client validated the request in advance. A server that refuses a request because it breaks a constraint of an applicable profile uses the result code that [@!I-D.ietf-rpp-core] defines for this case.

A profile only constrains. Every request that a server accepts under a preset is therefore valid under RPP and the extensions of the preset without any profile, and a client that implements a preset can be used with every server that offers it. The servers differ only in the constraints of their applicable profiles, which each server publishes. The representation specification defines how the schema of a preset at a server combines the schemas of RPP, of the extensions and of the applicable profiles, see [@!I-D.ietf-rpp-json].
~~~~

## C6. Extension Object (section 8.x, Discovery)

Action: replace the Description of the data element Version (`version`) of the Extension Object with the following.

~~~~markdown
    * Description: The version of the extension, for example "1.0".
~~~~

## C7. Discovery Data Object

Action: replace the data elements Extensions (`extensions`) and Profiles (`profiles`) with the following, and add
"presets" to the list in the Description of the object ("such as the supported versions, TLDs, extensions, presets,
profiles, ...").

~~~~markdown
* Extensions
  * Identifier: extensions
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Extension Object
  * Description: The extensions of the presets the server offers.
  * Constraints:
    * The server MUST include every extension of every preset it offers, with its version.
    * The server MUST NOT include an extension with the same identifier and version more than once.

* Presets
  * Identifier: presets
  * Cardinality: 1+
  * Mutability: read-only
  * Data Type: Aggregation[Preset Data Object]
  * Description: The presets the server offers.
  * Constraints:
    * Each entry MUST include the data elements Identifier (`id`), Version (`version`), Extensions (`extensions`), Profiles (`profiles`), Bound Profiles (`boundProfiles`) and Default Preset (`defaultPreset`) of the preset.
    * Exactly one entry MUST have the Default Preset (`defaultPreset`) value `true`.

* Profiles
  * Identifier: profiles
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Aggregation[Profile Data Object]
  * Description: The profiles that are applicable to at least one preset the server offers.
  * Constraints:
    * Each entry MUST include the data elements Identifier (`id`) and Version (`version`) of the profile.
    * The server MUST include every applicable profile (#applicable-profiles) of every preset it offers.
~~~~

## C8. Profile Data Object (section 15)

Action: replace the section "Profile Data Object" with the two sections below.

~~~~markdown
# Preset Data Object {#preset-data-object}

## Object Description

* Name: Preset Data Object
* Identifier: preset
* Unique Identifier: id
* Description: A Preset Data Object represents a preset (#presets) offered by the server: the extensions a client uses when it signals the preset, the profiles of the preset definition, and the profiles the server binds to it. The object is flattened: its extensions and profiles include those of its base presets.

## Data Elements

The following data elements are defined for the Preset Data Object. All data elements are managed by the server.

* Identifier
  * Identifier: id
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: The unique identifier of the preset, for example `urn:ietf:params:rpp:preset:epp-compatible`.
  * Constraints:
    * The identifier of a standardised preset MUST use the form `urn:ietf:params:rpp:preset:{name}` and MUST be registered in the RPP Preset Registry.
    * The identifier of a private preset MUST be globally unique. The use of reverse domain name notation is RECOMMENDED.

* Name
  * Identifier: name
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: A short human-readable name of the preset, for example "EPP compatible preset".
  * Constraints: (None)

* Description
  * Identifier: description
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: A human-readable description of the preset and its intended use.
  * Constraints: (None)

* Version
  * Identifier: version
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: The version of the preset, for example "1.0".
  * Constraints: A preset definition whose extensions, their versions, its profiles or its base presets change MUST have a new version.

* RPP Version
  * Identifier: rppVersion
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: The minimum version of RPP that the preset requires.
  * Constraints: (None)

* URL
  * Identifier: url
  * Cardinality: 0-1
  * Mutability: read-only
  * Data Type: URL
  * Description: The location of the preset specification.
  * Constraints:
    * For a standardised preset, the value MUST be the URL of the preset in the IANA registry.
    * For a private preset, the value, if present, MUST be the URL of the preset specification, which MUST be accessible to the client.

* Base Presets
  * Identifier: basePresets
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Aggregation[Preset Data Object]
  * Description: The presets this preset builds on, see (#preset-profile-inheritance).
  * Constraints:
    * Each entry MUST include the data elements Identifier (`id`) and Version (`version`) of the base preset.
    * A preset MUST NOT build on itself, directly or indirectly.

* Extensions
  * Identifier: extensions
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Extension Object
  * Description: The extensions of the preset, including the extensions of its base presets.
  * Constraints:
    * The value MUST NOT contain an extension identifier more than once.
    * The server MUST support every extension of the preset in the listed version.

* Profiles
  * Identifier: profiles
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Aggregation[Profile Data Object]
  * Description: The profiles of the preset definition, including the profiles of its base presets.
  * Constraints:
    * Each entry MUST include the data elements Identifier (`id`) and Version (`version`) of the profile.
    * The value MUST NOT contain a profile identifier more than once.

* Bound Profiles
  * Identifier: boundProfiles
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Aggregation[Profile Data Object]
  * Description: The profiles the server binds to the preset (#profile-binding).
  * Constraints:
    * Each entry MUST include the data elements Identifier (`id`) and Version (`version`) of the profile.
    * The value MUST NOT contain a profile that the Profiles (`profiles`) data element contains.
    * The preset MUST contain every extension that a bound profile requires, directly or through its base profiles.

* Default Preset
  * Identifier: defaultPreset
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: Boolean
  * Description: Indicates whether the preset is the default preset of the server, which applies to a request that signals no preset.
  * Constraints: Exactly one preset offered by the server MUST have the value `true`.

* Schema
  * Identifier: schema
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: Representation Schema
  * Visibility: onDemand
  * Direct Access: true
  * Description: The schema of the preset at the server, which combines the schemas of RPP and of the extensions of the preset, constrained by its applicable profiles (#applicable-profiles), see (#representation-schema).
  * Constraints: The schema MUST reflect the profiles that the Profiles (`profiles`) and Bound Profiles (`boundProfiles`) data elements state.

## Operations

### Read Operation

* Identifier: read

The Read operation allows a client to retrieve the Preset Data Object identified by its identifier, and its Direct Access data element Schema (`schema`). It is the only operation supported for this object.

* Input: (None)

* Authorisation:
  * Any authenticated client is authorised to perform this operation.
  * A server MAY, by its policy, also allow this operation without authentication, for example to publish the schemas of its presets.

# Profile Data Object {#profile-data-object}

## Object Description

* Name: Profile Data Object
* Identifier: profile
* Unique Identifier: id
* Description: A Profile Data Object represents a profile (#profiles) that is applicable to at least one preset offered by the server. The object is flattened: its required extensions include those of its base profiles.

## Data Elements

The following data elements are defined for the Profile Data Object. All data elements are managed by the server.

* Identifier
  * Identifier: id
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: The unique identifier of the profile, for example `urn:ietf:params:rpp:profile:epp-compatibility`.
  * Constraints:
    * The identifier of a standardised profile MUST use the form `urn:ietf:params:rpp:profile:{name}` and MUST be registered in the RPP Profile Registry.
    * The identifier of a private profile MUST be globally unique. The use of reverse domain name notation is RECOMMENDED.

* Name
  * Identifier: name
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: A short human-readable name of the profile, for example "EPP Compatibility Profile".
  * Constraints: (None)

* Description
  * Identifier: description
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: A human-readable description of the profile and its intended use.
  * Constraints: (None)

* Version
  * Identifier: version
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: The version of the profile, for example "1.0".
  * Constraints: A profile whose constraints, required extensions or base profiles change MUST have a new version.

* RPP Version
  * Identifier: rppVersion
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: String
  * Description: The minimum version of RPP that the profile constrains.
  * Constraints: (None)

* URL
  * Identifier: url
  * Cardinality: 1
  * Mutability: read-only
  * Data Type: URL
  * Description: The location of the profile specification, which states the constraints of the profile.
  * Constraints:
    * For a standardised profile, the value MUST be the URL of the profile in the IANA registry.
    * For a private profile, the value MUST be the URL of the profile specification, which MUST be accessible to the client.

* Base Profiles
  * Identifier: baseProfiles
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Aggregation[Profile Data Object]
  * Description: The profiles this profile builds on, see (#preset-profile-inheritance).
  * Constraints:
    * Each entry MUST include the data elements Identifier (`id`) and Version (`version`) of the base profile.
    * A profile MUST NOT build on itself, directly or indirectly.

* Required Extensions
  * Identifier: requiredExtensions
  * Cardinality: 0+
  * Mutability: read-only
  * Data Type: Extension Object
  * Description: The extensions the profile requires, including those its base profiles require.
  * Constraints: The value MUST NOT contain an extension identifier more than once.

## Operations

### Read Operation

* Identifier: read

The Read operation allows a client to retrieve the Profile Data Object identified by its identifier. It is the only operation supported for this object.

* Input: (None)

* Authorisation:
  * Any authenticated client is authorised to perform this operation.
~~~~

## C9. IANA Considerations: RPP Data Object Registry, Initial Registrations

Action: replace the registration of the object `profile` with the two registrations below, replace the Description of
the `version` row of the object `extension`, and replace the rows `extensions` and `profiles` of the object
`discovery`, adding the row `presets` after `extensions`.

~~~~markdown
Object: preset

Object Name: Preset Data Object

Object Type: Resource

Description: Represents a preset offered by the server: a named and versioned set of extensions and profiles that a client signals with a request.

Reference: [This-ID]

Data Elements
| Identifier     | Name           | Card. | Mutability | Data Type                        | Description                                                                 |
|----------------|----------------|-------|------------|----------------------------------|-----------------------------------------------------------------------------|
| id             | Identifier     | 1     | read-only  | String                           | The unique identifier of the preset.                                        |
| name           | Name           | 1     | read-only  | String                           | A short human-readable name of the preset.                                  |
| description    | Description    | 1     | read-only  | String                           | A human-readable description of the preset and its intended use.            |
| version        | Version        | 1     | read-only  | String                           | The version of the preset.                                                  |
| rppVersion     | RPP Version    | 1     | read-only  | String                           | The minimum version of RPP that the preset requires.                        |
| url            | URL            | 0-1   | read-only  | URL                              | The location of the preset specification.                                   |
| basePresets    | Base Presets   | 0+    | read-only  | Aggregation [Preset Data Object] | The presets this preset builds on.                                          |
| extensions     | Extensions     | 0+    | read-only  | Extension Object                 | The extensions of the preset, including those of its base presets.          |
| profiles       | Profiles       | 0+    | read-only  | Aggregation [Profile Data Object]| The profiles of the preset definition, including those of its base presets. |
| boundProfiles  | Bound Profiles | 0+    | read-only  | Aggregation [Profile Data Object]| The profiles the server binds to the preset.                                |
| defaultPreset  | Default Preset | 1     | read-only  | Boolean                          | Indicates whether this preset is the default preset of the server.          |
| schema         | Schema         | 1     | read-only  | Representation Schema            | The schema of the preset at the server.                                     |

Operations

Operation: Read

Operation Identifier: read

Description: Retrieves the Preset Data Object identified by its identifier.

Input Data Elements: (None)

Parameters: (None)

Object: profile

Object Name: Profile Data Object

Object Type: Resource

Description: Represents a profile, which constrains what RPP and a set of extensions permit, applicable to at least one preset offered by the server.

Reference: [This-ID]

Data Elements
| Identifier         | Name                | Card. | Mutability | Data Type                         | Description                                                                 |
|--------------------|---------------------|-------|------------|-----------------------------------|-----------------------------------------------------------------------------|
| id                 | Identifier          | 1     | read-only  | String                            | The unique identifier of the profile.                                       |
| name               | Name                | 1     | read-only  | String                            | A short human-readable name of the profile.                                 |
| description        | Description         | 1     | read-only  | String                            | A human-readable description of the profile and its intended use.           |
| version            | Version             | 1     | read-only  | String                            | The version of the profile.                                                 |
| rppVersion         | RPP Version         | 1     | read-only  | String                            | The minimum version of RPP that the profile constrains.                        |
| url                | URL                 | 1     | read-only  | URL                               | The location of the profile specification.                                  |
| baseProfiles       | Base Profiles       | 0+    | read-only  | Aggregation [Profile Data Object] | The profiles this profile builds on.                                        |
| requiredExtensions | Required Extensions | 0+    | read-only  | Extension Object                  | The extensions the profile requires, including those of its base profiles.  |

Operations

Operation: Read

Operation Identifier: read

Description: Retrieves the Profile Data Object identified by its identifier.

Input Data Elements: (None)

Parameters: (None)
~~~~

Row of the object `extension`:

~~~~markdown
| version | Version | 1 | read-only | String | The version of the extension. |
~~~~

Rows of the object `discovery`:

~~~~markdown
| extensions | Extensions | 0+ | read-only | Extension Object | The extensions of the presets the server offers. |
| presets | Presets | 1+ | read-only | Aggregation [Preset Data Object] | The presets the server offers. |
| profiles | Profiles | 0+ | read-only | Aggregation [Profile Data Object] | The profiles applicable to at least one preset the server offers. |
~~~~

## C10. IANA Considerations: URN Sub-namespace for RPP

Action: replace the line starting with "TODO: add filled in template" with the following.

~~~~markdown
TODO: add filled in template. The sub-namespace holds the identifiers of standardised extensions (`urn:ietf:params:rpp:extension:{name}`), profiles (`urn:ietf:params:rpp:profile:{name}`) and presets (`urn:ietf:params:rpp:preset:{name}`).
~~~~

## C11. IANA Considerations: RPP Extension Registry

Action: add the anchor `{#iana-extension-registry}` to the heading, replace the first paragraph, and add the field
`id` and the final paragraph below.

~~~~markdown
The IANA is requested to create a new registry for RPP extensions. This registry will be used to register standardised extensions to the RPP protocol. An extension adds functionality to RPP, for example additional resource types, additional operations or additional authentication methods, and does not constrain RPP or another extension, see (#extensions).
~~~~

~~~~markdown
- `id`: The unique URN identifier of the extension, for example "urn:ietf:params:rpp:extension:rpp-example".
~~~~

~~~~markdown
The designated expert verifies that the extension does not constrain RPP or another extension, and that its identifier is not registered in the RPP Profile Registry or the RPP Preset Registry.
~~~~

## C12. IANA Considerations: RPP Profile Registry and RPP Preset Registry

Action: replace the section "RPP Profile Registry" with the two sections below.

~~~~markdown
## RPP Profile Registry {#iana-profile-registry}

The IANA is requested to create a new registry for RPP profiles. This registry will be used to register standardised profiles, which constrain what RPP and a set of extensions permit, see (#profiles). An example is the EPP Compatibility Profile, which constrains RPP to what the Extensible Provisioning Protocol (EPP) [@!RFC5730] can represent.

```text
Name of the registry: RPP Profiles
Registry group: RESTful Provisioning Protocol (RPP)
Registration procedure: Expert Review
```

Fields to be registered:

- `name`: The name of the profile, for example "EPP Compatibility Profile".
- `id`: The unique URN identifier of the profile, for example "urn:ietf:params:rpp:profile:epp-compatibility".
- `version`: The version of the profile, for example "1.0".
- `requiredExtensions`: The identifiers and versions of the extensions the profile requires, or "(None)".
- `baseProfiles`: The identifiers and versions of the profiles the profile builds on, or "(None)".
- `url`: The URL for the profile specification.
- `description`: A human-readable description of the profile and its intended use.

The designated expert verifies that the profile only constrains, in the ways listed in (#profiles), that every extension it constrains is a required extension, that it does not build on itself directly or indirectly, and that its identifier is not registered in the RPP Extension Registry or the RPP Preset Registry.

Initial registrations:

- `name`: EPP Compatibility Profile
- `id`: urn:ietf:params:rpp:profile:epp-compatibility
- `version`: 1.0
- `requiredExtensions`: (None)
- `baseProfiles`: (None)
- `url`: This document, (#epp-compatibility-profile)
- `description`: Constrains RPP to what EPP can represent, for a server that provisions a repository through RPP and EPP concurrently.

## RPP Preset Registry {#iana-preset-registry}

The IANA is requested to create a new registry for RPP presets. This registry will be used to register standardised presets, which name a set of extensions and profiles that a client signals with a request, see (#presets).

```text
Name of the registry: RPP Presets
Registry group: RESTful Provisioning Protocol (RPP)
Registration procedure: Expert Review
```

Fields to be registered:

- `name`: The name of the preset, for example "EPP compatible preset".
- `id`: The unique URN identifier of the preset, for example "urn:ietf:params:rpp:preset:epp-compatible".
- `version`: The version of the preset, for example "1.0".
- `extensions`: The identifiers and versions of the extensions of the preset, or "(None)".
- `profiles`: The identifiers and versions of the profiles of the preset, or "(None)".
- `basePresets`: The identifiers and versions of the presets the preset builds on, or "(None)".
- `url`: The URL for the preset specification.
- `description`: A human-readable description of the preset and its intended use.

The designated expert verifies that the preset contains every extension that its profiles require, that its flattened extensions do not contain one extension in two versions, that it does not build on itself directly or indirectly, and that its identifier is not registered in the RPP Extension Registry or the RPP Profile Registry.

Initial registrations:

- `name`: Base preset
- `id`: urn:ietf:params:rpp:preset:base
- `version`: 1.0
- `extensions`: (None)
- `profiles`: (None)
- `basePresets`: (None)
- `url`: This document, (#presets)
- `description`: RPP without extensions and without profiles.

- `name`: EPP compatible preset
- `id`: urn:ietf:params:rpp:preset:epp-compatible
- `version`: 1.0
- `extensions`: (None)
- `profiles`: urn:ietf:params:rpp:profile:epp-compatibility 1.0
- `basePresets`: urn:ietf:params:rpp:preset:base 1.0
- `url`: This document, (#presets)
- `description`: RPP without extensions, constrained by the EPP Compatibility Profile.
~~~~

## C13. Changes History

Action: add the following entries to the subsection of the next revision.

~~~~markdown
* separated extensions, which add functionality, from profiles, which constrain, and added presets, which a client signals and which name a set of extensions and profiles
* added profile binding by the server and multiple inheritance of presets and profiles
* added the Preset Data Object, redefined the Profile Data Object, and replaced the profiles of the Discovery Data Object by presets and profiles
* added the Representation Schema common data type and the schema of a preset, and allowed Direct Access on data elements of cardinality 0-1 or 1 of any data type
* restated the EPP Compatibility Profile as a registered profile
* added the RPP Preset Registry and the `id` field of the RPP Extension Registry, and redefined the RPP Profile Registry
~~~~
