# Proposal for draft-ietf-rpp-core: Preset Signalling

- Issue: #174 (this repository)
- Base: draft-ietf-rpp-core-01, upstream `src/draft-ietf-rpp-core.md` at commit `7467c9e`
- Builds on: [data-objects.md](data-objects.md) (accepted, amended with the `schema` element of the Preset Data Object)
- Status: accepted by the maintainer
- Copied: the EPP Compatibility Profile elements of this proposal are also in the new draft proposed in
  [epp-compatibility.md](epp-compatibility.md). They stay here until that draft is adopted

This proposal replaces profile signalling by preset signalling. A client signals a preset, which states the extensions
it uses. The server applies the applicable profiles of the preset, which the client never signals. A request that
breaks a profile constraint is refused with 02308. Each change below names the section of the draft, the action, and
the exact text. Section numbers are those of -01 and are given for orientation only: the title and the anchor identify
the section.

## Review Points

Choices made while drafting that the requirements in #174 and the data-objects proposal do not settle:

- RC1. A request without a preset signal is processed under the default preset in both signalling methods. Today the
  header method says the client MUST send `RPP-Profile`, while the media type method falls back to the default profile.
- RC2. The error object of a Problem Detail gets a `profile` field with the identifier of the profile whose constraint
  the request breaks (SHOULD), so that a client can find the constraint in the profile specification.
- RC3. (Amended, maintainer) The schema of a preset is the Direct Access data element `schema` of the Preset Data
  Object, so Rule 3 derives `/presets/{id}/schema`, and it needs authentication unless the server's policy allows
  the Read operation without it (data-objects R6). Rule 3 covers Direct Access on data elements that are not
  associations.
- RC4. A request that uses an extension the signalled preset does not contain is content that does not conform to the
  preset, 400 (Bad Request) as for any other non-conforming content. No new result code.
- RC5. The anchors `#profile-signalling` and `#profiles` become `#preset-signalling` and `#presets`. The references to
  them, including the two in the Change History of -01, are updated.
- RC6. A request for an operation that an applicable profile makes unavailable is refused with 02308 as well, and not
  with 02101 (Unimplemented command), because the server implements the operation and refuses it by policy.
- RC7. (Maintainer) A value that is not wrapped in an RPP message, such as a Representation Schema addressed as a
  Direct Access sub-resource, is served in its native media type. Such a request has no RPP media type to carry preset
  parameters, so with media type signalling the server applies the default preset. This is a further reason for
  header field signalling, added to the rationale.

## C1. Terminology (section 2)

Action: add the following terms after "RPP media type".

~~~~markdown
Extension, Profile, Preset, Profile Binding, Applicable Profiles - As defined in [@!I-D.ietf-rpp-data-objects].
~~~~

## C2. Request Header Fields (section 6.1)

Action: in the first sentence replace "`RPP-Profile`" with "`RPP-Preset`", and replace the bullet `RPP-Profile` with
the following.

~~~~markdown
- `RPP-Preset`: The client uses this header field to indicate the preset of the request, see (#preset-signalling).
~~~~

## C3. Response Header Fields (section 6.2)

Action: in the first sentence replace "`RPP-Profile`" with "`RPP-Preset`", and replace the bullet `RPP-Profile` with
the following.

~~~~markdown
- `RPP-Preset`: The server uses this header field to indicate the preset under which it processed the request, see (#preset-signalling).
~~~~

## C4. Versioning (section 12)

Action: in the list of elements with versioning support, replace the bullet "Profiles" with the two bullets below.

~~~~markdown
- Presets: RPP presets MUST include the version of the RPP API they are compatible with.
- Profiles: RPP profiles MUST include the version of the RPP API they are compatible with.
~~~~

Action: in subsection "Extensions" (section 12.3), replace the last sentence ("The set of extensions required by the
client MUST be signalled by the client by using the correct `profile`, see (#profiles).") with the following.

~~~~markdown
The client signals the set of extensions it uses with a preset that contains them, see (#presets).
~~~~

Action: replace subsection "Profiles" (section 12.4) with the following.

~~~~markdown
## Presets {#presets}

The RPP server MUST provide the presets it offers, with their versions, and their applicable profiles, with their versions, in the RPP Discovery response, as defined in [@!I-D.ietf-rpp-data-objects]. The client uses this information to determine which presets the server offers and which constraints apply to each of them. A request that signals a preset MUST include the version of the preset. The server MUST reject a request that signals a preset or a preset version that the server does not offer, as defined in (#preset-signalling).

A client does not signal profiles. The applicable profiles of a preset are determined by the preset definition and by the profile bindings of the server.
~~~~

## C5. Media Types (section 13)

Action: in the first paragraph, replace the last sentence with the following.

~~~~markdown
Every RPP media type MUST support the `preset` and `preset-version` parameters defined in (#media-type-signalling), so that preset signalling is identical for all representations.
~~~~

Action: in "Responses", replace "whose content depends on the negotiated media type or profile" with "whose content
depends on the negotiated media type or preset".

Action: add the following subsection at the end of the section.

~~~~markdown
## Native Media Types {#native-media-types}

A Direct Access sub-resource of a data element that is not an association (see Rule 3 in (#endpoints)) has as its content the value of the data element, for example a Representation Schema [@!I-D.ietf-rpp-data-objects]. Such a value is not wrapped in an RPP message. It is represented in its native media type, which the specification of its data type defines, and not in an RPP media type. The following rules apply to a request for such a sub-resource, in place of the rules for requests and responses above:

- The client MUST list the native media type, or a media range that includes it, in the `Accept` header field. The media ranges in the `Accept` header field do not need to identify an RPP media type.
- The request has no content, and the client does not send a `Content-Type` header field.
- If the `Accept` header field does not allow the native media type, the server MUST reject the request with HTTP status code 406 (Not Acceptable).
- The server MUST indicate the native media type in the `Content-Type` header field of a successful response.
- A Problem Detail response uses the `application/problem+json` media type, as for any other request.

Such a request cannot signal a preset with media type parameters, see (#media-type-signalling).
~~~~

## C6. Profile Signalling (section 14)

Action: replace the section, including its subsections, with the following.

~~~~markdown
# Preset Signalling {#preset-signalling}

This section defines how a client signals the preset of a request and how a server indicates the preset of a response. This document describes two distinct methods for signalling the preset used in an RPP request or response. The first method uses a dedicated HTTP header field, the second method uses media type parameters. The two methods MUST NOT be used simultaneously in a single request or response. If both methods are used in a single request, the server MUST return an HTTP error response and include a Problem Detail response in the content.

The preset determines the extensions that a request and its response use, and the applicable profiles whose constraints apply to them, as defined in [@!I-D.ietf-rpp-data-objects]. A client signals only the preset. A client does not signal extensions or profiles.

## Rationale for Header Field Signalling {#signalling-rationale}

This section is not normative. Signalling the preset using a dedicated HTTP header field is preferable to signalling it using media type parameters, for the following reasons:

- Protocol level versus content level: the preset, and the RPP version it implies, determines how the whole HTTP message is interpreted, including URL paths, query parameters, and HTTP header fields, which can all evolve over time and need agreement between client and server. A media type only describes the format of the content. Signalling at the protocol level, in a header field, fits this scope better than signalling in a property of the content.
- Independence of the representation format: media type parameters have to be mandated for, and implemented identically in, every RPP media type registered for every representation format. A header field is independent of the representation format, so a new representation format does not need to define any preset signalling and the preset signalling does not need to be changed when the media type handling changes.
- Messages without content: `Content-Type` is only meaningful for a message that has content. Requests such as GET and DELETE, and responses without content, would otherwise have to carry a `Content-Type` header field only to signal the preset. A header field defined by RPP can be present in every request and response.
- Separation of concerns: with a dedicated header field, media types are used only to negotiate the data format of the content, and the preset is negotiated independently of it.
- Values in their native media type: a value that is not wrapped in an RPP message, such as the schema of a preset, is served in its native media type (#native-media-types), which has no preset parameters. A header field signals the preset of such a request as of any other.

A> TODO: the working group has not yet decided on the signalling method to use, the two methods are both described until that decision is made.

## Header Signalling

The client uses the `RPP-Preset` header field to indicate the preset of the request. The value of this header field is a Dictionary as defined in [@!RFC9651, Section 3.2]. The Dictionary MUST contain a `preset` member whose value uniquely identifies a preset, for example `urn:ietf:params:rpp:preset:epp-compatible`, and this member MUST carry a `version` parameter indicating the version of the preset. If the server does not offer the indicated preset or version, the server MUST return an HTTP error response and include a Problem Detail response in the content. If a request does not include the `RPP-Preset` header field, the server MUST apply the default preset advertised in the RPP Discovery document (see (#discoverability)).

The server MUST include the `RPP-Preset` header field, with the identifier and the version of the preset it applied, in every response to a request that it processed under a preset, and MUST list `RPP-Preset` in the `Vary` header field [@!HTTP, Section 12.5.5] of that response.

The ABNF for the `RPP-Preset` header field value is as follows:

```abnf
preset-header = "preset" "=" preset-name ";" OWS "version" "=" version
preset-name   = token
version       = 1*DIGIT "." 1*DIGIT
```

Example:

```http-message
GET /domainNames/foo.example HTTP/1.1
Host: rpp.example
Authorization: Bearer <token>
Accept: application/rpp+json
RPP-Preset: preset=urn:ietf:params:rpp:preset:epp-compatible;version=1.0
RPP-Cltrid: ABC-12345

```

## Media Type Signalling {#media-type-signalling}

An RPP client and an RPP server select the preset that applies to a message using the media type parameters defined in this section, on top of the `Content-Type` and `Accept` header field handling defined in (#media-types). The presets offered by an RPP server are announced in the RPP Discovery document (see (#discoverability)).

The media type parameters are defined as follows:

- `preset`: The value of this parameter MUST uniquely identify the preset, for example `urn:ietf:params:rpp:preset:epp-compatible`.
- `preset-version`: The value of this parameter MUST indicate the version of the preset.

The ABNF for the media type parameters is as follows:

```abnf
preset-parameter = "preset" "=" preset-name ";" OWS "preset-version" "=" version
preset-name      = token
version          = 1*DIGIT "." 1*DIGIT
```

Requests:

- Each media range in the `Accept` header field of a request MUST include the `preset` and `preset-version` parameters of a preset the client is able to process in the response. The client MAY list more than one preset and MAY use quality values to indicate preference.
- The media type in the `Content-Type` header field of a request with content MUST include the `preset` and `preset-version` parameters of the preset that the content conforms to.
- The preset indicated in the `Content-Type` header field MUST also be listed in the `Accept` header field of the same request.

Server processing:

- The RPP server MUST determine the preset of request content only from the `Content-Type` header field and MUST NOT infer it from the content, and MUST process the content according to that preset.
- If the server does not offer the indicated preset or preset version, the server MUST reject the request with HTTP status code 415 (Unsupported Media Type).
- The RPP server MUST select the preset for the response from the `Accept` header field using proactive negotiation as described in [@!HTTP, Section 12.5.1]. If the server offers none of the listed presets, the server MUST reject the request with HTTP status code 406 (Not Acceptable).
- If the preset in the `Content-Type` header field is not listed in the `Accept` header field, the server MUST reject the request with HTTP status code 400 (Bad Request).
- If a request does not include preset parameters, the server MUST apply the default preset advertised in the RPP Discovery document (see (#discoverability)). This includes a request for a value in its native media type (#native-media-types), which cannot include them.
- The extensions of the requested preset may include additional HTTP header fields or query parameters that the server needs to understand and process correctly.
- In all rejection cases above, the server MUST include the `RPP-Code` header field and a Problem Detail response as described in (#problem-detail).

Responses:

- The media type in the `Content-Type` header field of a successful response that contains content MUST include the `preset` and `preset-version` parameters of the preset the server applied, and that preset MUST be one listed in the `Accept` header field of the request.
- Problem Detail responses do not carry preset parameters.

Client processing:

- The RPP client MUST determine the preset of response content only from the `Content-Type` header field and MUST interpret the content according to that preset.
- If that preset or preset version was not listed in the `Accept` header field of the request, the client MUST NOT process the content as an RPP response and MUST treat the response as a protocol error.
- The extensions of the requested preset may include additional HTTP header fields or query parameters that the client needs to understand and process correctly.

Example of a request and the corresponding response header fields, using `application/rpp+json` for illustration:

```http-message
GET /domainNames/foo.example HTTP/1.1
Host: rpp.example
Authorization: Bearer <token>
Accept: application/rpp+json; preset="urn:ietf:params:rpp:preset:epp-compatible"; preset-version="1.0"
RPP-Cltrid: ABC-12345

HTTP/1.1 200 OK
Content-Type: application/rpp+json; preset="urn:ietf:params:rpp:preset:epp-compatible"; preset-version="1.0"
Vary: Accept
RPP-Svtrid: XYZ-12345
RPP-Cltrid: ABC-12345
RPP-Code: 01000

```

## Extensions and Profiles of a Request {#preset-processing}

A request uses only the extensions of its preset. A server MUST reject a request that uses a data element, operation, header field or query parameter of an extension that the preset does not contain. The server rejects it with HTTP status code 400 (Bad Request), as content that does not conform to the preset.

A server MUST enforce the constraints of the applicable profiles of the preset on every request. A server that rejects a request because it breaks a constraint of an applicable profile MUST use the RPP result code 02308 (Data management policy violation) and HTTP status code 422 (Unprocessable Content). This applies to every constraint of an applicable profile, whether or not the schema of the representation expresses it, and to an operation that an applicable profile makes unavailable. Each error object of the Problem Detail response for such a rejection SHOULD contain a `profile` field, whose value is the identifier of the profile that states the constraint. A client uses this field to find the constraint in the profile specification. A server can omit the field when it cannot attribute the rejection to a single profile.

A request that conforms to the preset but breaks a constraint that RPP or an extension of the preset defines is rejected as defined for that constraint, and not with 02308.

Example of a Problem Detail response for a restore report with one statement, under a preset whose applicable profiles include the EPP Compatibility Profile:

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
~~~~

## C7. Endpoints: Rule 3 (section 16.1.3)

Action: add the anchor `{#endpoints}` to the heading "Endpoints". Add the following paragraph after the paragraph
starting with "If the Direct Access element's cardinality is
greater than 1", and add the row below to the table of resulting paths.

~~~~markdown
If the Direct Access element is not an association, its cardinality is 0-1 or 1 [@!I-D.ietf-rpp-data-objects], and the path segment is derived as for such a cardinality. The sub-resource is the value of the data element. It supports only the HTTP GET method, which reads the value, and its content is represented in its native media type, see (#native-media-types).
~~~~

~~~~markdown
| `/presets/{id}` | `schema` | 1 | `/presets/{id}/schema` |
~~~~

## C8. Endpoints (section 16)

Action: in the table of "Rule 1: Collection Path Segment", add the following row after the row `profile`.

~~~~markdown
| `preset` | `presets` | `/presets` |
~~~~

Action: in the table of "Derived Endpoint Reference", replace the row "Profile: read" with the following rows.

~~~~markdown
| Preset: read | `GET` | `/presets/{id}` |
| Preset: read (schema) | `GET` | `/presets/{id}/schema` |
| Profile: read | `GET` | `/profiles/{id}` |
~~~~

## C9. Problem Detail Responses for Errors (section 9)

Action: after the description of the field `reason` of the error object, add the following.

~~~~markdown
`profile`
: (optional, string) The identifier of the profile whose constraint the request breaks, see (#preset-processing).
~~~~

## C10. Security Considerations

Action: in the third paragraph, replace "infers the data format or profile of a message from its content" with
"infers the data format or preset of a message from its content".

## C11. Change History

Action: in the subsection "Version ietf-rpp-core-00 to ietf-rpp-core-01", replace "(#profile-signalling)" with
"(#preset-signalling)" in the two entries that reference it. Add the following entries to the subsection of the next
revision.

~~~~markdown
- Replaced profile signalling by preset signalling: the `RPP-Preset` header field and the `preset` and `preset-version` media type parameters in (#preset-signalling)
- Applied the default preset when a request signals no preset, in both signalling methods
- Added (#preset-processing): extensions outside the preset are rejected, and a broken profile constraint is rejected with 02308 and the Problem Detail field `profile`
- Extended Rule 3 to Direct Access data elements that are not associations, and added (#native-media-types) for their values
- Added the Preset endpoints, including the schema of a preset, and changed the Profile endpoint to `/profiles/{id}` in the Derived Endpoint Reference
~~~~
