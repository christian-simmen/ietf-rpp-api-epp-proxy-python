# The DENIC RRI extension of RPP

A private RPP extension of this proxy, for a deployment whose registry speaks DENIC RRI 5.0. It follows the structure
of [draft-wullink-rpp-extension-guidelines-00](../../.spec/draft-wullink-rpp-extension-guidelines.clean.txt) §9
(cited as "guidelines"). The base specifications are draft-ietf-rpp-core ("core"), draft-ietf-rpp-data-objects
("data-objects") and draft-ietf-rpp-json ("json") in [.spec/](../../.spec/). The RRI facts behind it are in
[rri-5.0-reference.md](rri-5.0-reference.md) ("ref"), the gaps it closes in [gap-analysis.md](gap-analysis.md). Where
the guidelines are unclear, [spec-issues.md](../../.spec/spec-issues.md#extension-guidelines) says what this
document does.

## 1. Introduction

RRI holds data that the RPP base specifications have no place for:

- **Request contacts.** A domain has, besides its 1 to 5 holders, a General Request contact and an Abuse contact.
  Both are RRI contacts of type `REQUEST`: a handle and a URI template (RFC 6570, level 1) that tells where requests
  about the domain go, such as `https://example.com/contact?domain={Alabel}` (ref §5.1, §5.2). They have no name,
  address or status, so they are no Contact Data Object (data-objects §12), whose `contactInfo` (a JSContact Card) and
  `status` are required. This extension defines them as a data object of their own, the Request Contact, and adds
  the two roles to the Domain Name Data Object as data elements of their own.
- **The data of a transfer.** RRI's only transfer, CHPROV (ref §6.18), is requested by the gaining registrar with the
  complete data of the domain: holders, request contacts and DNS data, all of them the gainer's own. The RPP transfer
  request carries none of it (gap Q3). This extension adds them to the Create operation of the Domain Transfer
  Process Object.

Why the request contact is a new data object and not one derived from the Contact Data Object (data-objects §2.5,
`Extends`): a derived object inherits every data element of its base object with its cardinality, and cannot relax
it. A Request Contact would carry an empty Card as `contactInfo` and a made-up `status`. The template cannot go into
the Card's `links` either, since `{Alabel}` makes it no URI. Adding a `uriTemplate` element to the Contact Data
Object leaves `contactInfo` required as well. The new object repeats only `id` and `provMetadata` of the Contact Data
Object (guidelines §6, item 4).

## 2. Extension Overview

| Field | Value |
|---|---|
| Name | DENIC RRI |
| Identifier | `de.denic.rpp.rri` |
| Version | 0.2.0 |
| RPP version | the drafts of `.spec/` (core -00, data-objects -01, json -00) |
| Schema `$id` | `https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/rri-extension.schema.json` |
| Changed base objects | `domainName`, `domainTransferProcess` |
| New objects | `requestContact`, `requestContactAvailability` |

Version 0.1.0 (#133) had the identifier `rri` and carried the request contacts of a transfer as `contacts` labelled
`generalRequest` and `abuse`. 0.2.0 replaces both.

## 3. External Data Types

None.

## 4. Result Codes

None. The refusals of RRI are mapped to the result codes of core §18, see the operations below.

## 5. Problem Details

None.

## 6. HTTP Headers

None. The AuthInfo of a transfer travels in `RPP-Authorization` (core §6.1), as for any transfer.

## 7. Discovery Document

None beyond the entry in `extensions`:

```json
{"@type": "extension", "name": "DENIC RRI", "id": "de.denic.rpp.rri", "version": "0.2.0",
 "url": "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/.spec/rri-extension.schema.json"}
```

A server that offers the extension also lists `requestContact` in `objects`.

## 8. Updated Data Objects

### 8.1 Domain Name Data Object

- Identifier: `domainName`

#### 8.1.1 Data Elements

The following data elements are added to the Domain Name Data Object.

- General Request Contact
  - Identifier: `generalRequest`
  - Cardinality: 0-1
  - Mutability: read-write
  - Data Type: Aggregation[Request Contact Data Object]
  - Description: The request contact that general requests about the domain go to (RRI role `generalrequest`).
  - Constraints:
    - The relation MUST correspond to a Request Contact Data Object of the sponsoring client.
- Abuse Contact
  - Identifier: `abuse`
  - Cardinality: 0-1
  - Mutability: read-write
  - Data Type: Aggregation[Request Contact Data Object]
  - Description: The request contact that reports of abuse of the domain go to (RRI role `abusecontact`).
  - Constraints:
    - The relation MUST correspond to a Request Contact Data Object of the sponsoring client.

The roles are not labels of `contacts`: a server that offers the extension refuses a `contacts` entry labelled
`generalRequest` or `abuse` with 501 (`02102`), as any label it has no role for. On RRI, `contacts` holds only the
holders after the first, labelled `registrant` (gap Q1).

The Create, Read and Update operations (data-objects §11.3) take and show the two elements as the other read-write
elements. An Update that omits one removes it (RRI deletes a role an UPDATE does not state). A partial update
addresses them as `/generalRequest` and `/abuse` (json §5.2); a `remove` of one the domain does not have is not
applicable (422, `02308`).

#### 8.1.2 Operations

None.

## 9. New Data Objects

### 9.1 Request Contact Data Object

- Name: Request Contact Data Object
- Identifier: `requestContact`
- Unique Identifier: `id`
- Description: A contact that is only a URI template: where requests about a domain go. The registry expands the
  template for a domain where it publishes it (RRI: in its web whois); a read shows it as stored.

#### 9.1.1 Data Elements

- Handle ID
  - Identifier: `id`
  - Cardinality: 1
  - Mutability: create-only
  - Data Type: Identifier
  - Description: External unique identifier of the request contact.
  - Constraints:
    - This value MUST be provided by the client.
    - On RRI, request contacts and contacts share one namespace of handles (`DENIC-<RegAccId>-<suffix>`, 9 to 32
      characters).
- Provisioning Metadata
  - Identifier: `provMetadata`
  - Cardinality: 1
  - Mutability: read-only
  - Data Type: Provisioning Metadata Object
  - Description: Standard metadata about the object's lifecycle and ownership.
  - Constraints: (None). RRI shows `spClientId` (the RegAccId of the handle) and `upDate` only.
- URI Template
  - Identifier: `uriTemplate`
  - Cardinality: 1
  - Mutability: read-write
  - Data Type: String
  - Description: An RFC 6570 URI template of where requests go, with the variables `{Alabel}` and `{Ulabel}` for
    the domain name in its A-label and U-label form.
  - Constraints:
    - The value MUST contain between 8 and 1024 characters.
    - On RRI: level 1 of RFC 6570, the schemes `http`, `https` and `mailto`, and no variables but `{Alabel}` and
      `{Ulabel}` (case-sensitive). The registry checks this; a template it refuses (`83000000005`) answers 400
      (`02005`).

The object has no status and no authorisation information.

#### 9.1.2 Operations

The uniform interface of data-objects §2.7.4. Only the sponsoring client may read, update or use a request contact;
another client's request contact is refused with 403 (`02201`).

- Availability (`availability`): whether a request contact with the given Handle ID can be created. Output: Request
  Contact Availability Object. On RRI a handle of a contact is not available either.
- Create (`create`): input `id` and `uriTemplate`. Output: the request contact. Answers 201 with `Location`.
- Read (`read`): output the request contact. A Handle ID of a contact (an RRI `PERSON` or `ORG`) is no request
  contact, 404 (`02303`); likewise a contact read of a request contact's handle.
- Update (`update`): input `uriTemplate`, as a full update (PUT) or a partial update (PATCH, json §5.2), which can
  only replace the template. An update that changes nothing sends nothing and answers 200.
- Delete (`delete`): RRI has no delete of a contact; the registry deletes unused ones itself (ref §5.1). Answers 501
  (`02101`).

### 9.2 Request Contact Availability Object

- Name: Request Contact Availability Object
- Identifier: `requestContactAvailability`
- Extends: Base Availability Object (data-objects §9.18.1)
- Description: The availability of a Handle ID for a request contact.

#### 9.2.1 Data Elements

None beyond those of the Base Availability Object.

#### 9.2.2 Operations

None.

## 10. Updated Process Objects

### 10.1 Domain Transfer Process Object

- Identifier: `domainTransferProcess`

#### 10.1.1 Data Elements

The following Input Data Elements are added to the Create operation (Transfer Request, data-objects §10.1.1.1). They
are the data of the domain as the gainer will hold it, and mean what they mean for the Create operation of the
Domain Name Data Object.

| Identifier | Cardinality | Data Type | Description |
|---|---|---|---|
| `registrant` | 1 | Aggregation[Contact Data Object] | The first holder |
| `contacts` | 0+ | Labelled Aggregation[Contact Data Object] | The further holders, labelled `registrant` |
| `generalRequest` | 0-1 | Aggregation[Request Contact Data Object] | As in §8.1 |
| `abuse` | 0-1 | Aggregation[Request Contact Data Object] | As in §8.1 |
| `dns` | 1 | DNS Data Object | `ns` records with glue, `a`, `aaaa`, `mx`, `dnskey` |

Every contact and request contact MUST be one of the gaining client. They are converted as those of a domain create,
with the same refusals: no `nameservers` (RRI has no host objects), no `ds` records, no other contact labels.

#### 10.1.2 Operations

Create (Transfer Request) is CHPROV, which moves the domain at once: 200 without `Location`, the "completed at once"
answer of core §16.1.4. The RRI reply has no transfer state, so the process is stated as the registry completed it:
`transferDir` `pull`, `trStatus` `serverApproved`, `reqClientId` and `actClientId` the gainer's RegAccId,
`requestDate` and `actionDate` the time of the reply, no `expiryDate` (an RRI domain has none). The losing
registrar learns of it from a `chprovAuthInfo` queue message, which the proxy shows as a service notice.

| Case | Answer |
|---|---|
| `registrant` or `dns` missing | 400 (`02001`), no command sent |
| no `RPP-Authorization` | 400 (`02003`), no command sent |
| the AuthInfo does not match (`63370088701`), or no AuthInfo2 exists (`56000088709`) | 401 (`02202`) |
| a contact of another registrar (`63200020603`) | 403 (`02201`) |
| the gainer already sponsors the domain (`63380063209`) | 409 (`02002`) |
| required CHPROV data missing (`53370080005`) | 400 (`02003`) |

Read (query), Delete (cancel), Approve and Reject: RRI has none, so they answer 501 (`02101`). A push transfer is 501
(`02102`), TRANSIT is not mapped (gap Q8). A transfer of a domain in its redemption period with an AuthInfo2, which
RRI allows, works as any other but is not tested: RPP has no way to request an AuthInfo2 (gap Q9). The operator
change of a DNSSEC domain (DENIC's separate document) is not described here.

## 11. New Process Objects

None.

## 12. Endpoints

Informative, derived by the rules of core §16.1 from the identifier `requestContact` (`plural()` gives
`requestContacts`):

| Operation | Method and path |
|---|---|
| Create | `POST /requestContacts` |
| Read | `GET /requestContacts/{id}` |
| Update | `PUT /requestContacts/{id}`, `PATCH /requestContacts/{id}` |
| Delete | `DELETE /requestContacts/{id}` |
| Availability | `GET /requestContacts/{id}/availability`, `HEAD /requestContacts/{id}/availability` |

The added data elements of `domainName` and `domainTransferProcess` add no endpoints: they are not Direct Access.

## 13. JSON Schema

The one schema document of the extension is [.spec/rri-extension.schema.json](../../.spec/rri-extension.schema.json).
It follows guidelines §8, except where the base drafts give it nothing to refer to
([spec-issues.md](../../.spec/spec-issues.md#extension-guidelines)):

- `rpp:extends` maps `domainName.create`, `domainName.read`, `domainName.update` and `domainTransferProcess.create`
  to the extension's definitions (`ext.rri.…`), which are composed with them by `allOf` into the Effective Schema
  (json §7.2).
- `rpp:extends` and the `$ref`s name the base definitions by their local names (`#/$defs/contact.reference`): the
  bundle of the drafts has no `$id` to refer to. The proxy adds the extension's definitions to the bundle.
- `rpp:extension` holds the name, identifier and version of §2 and the new objects. The guidelines do not say where
  a schema states them.
- The new objects are `ext.rri.requestContact.{create,read,update,reference}` and
  `ext.rri.requestContactAvailability.read`, validated under the names a base object's definitions would have
  (`requestContact.create`).

## 14. Examples

Each block below names the definition it is an instance of, and whether it is valid against the Effective Schema
of a deployment that offers the extension. [test_rri_extension_doc.py](../../tests/unit/test_rri_extension_doc.py)
validates every one.

Create a request contact:

```json valid requestContact.create
{"@type": "requestContact", "id": "DENIC-1000022-GR", "uriTemplate": "https://example.com/contact?domain={Alabel}"}
```

Read it:

```json valid requestContact.read
{"@type": "requestContact", "id": "DENIC-1000022-GR",
 "provMetadata": {"@type": "provMetadata", "spClientId": "DENIC-1000022", "upDate": "2026-11-12T00:20:20.000Z"},
 "uriTemplate": "https://example.com/contact?domain={Alabel}"}
```

Replace its template (PUT), and change it by a partial update (PATCH):

```json valid requestContact.update
{"@type": "requestContact", "uriTemplate": "mailto:abuse@example.com"}
```

```json
[{"op": "replace", "path": "/uriTemplate", "value": "https://example.com/abuse/{Ulabel}"}]
```

Its availability:

```json valid requestContactAvailability.read
{"@type": "requestContactAvailability", "available": false}
```

A domain with its request contacts, as created and read:

```json valid domainName.create
{"@type": "domainName", "name": "example.de",
 "registrant": {"@type": "contact", "id": "DENIC-1000022-HOLDER"},
 "generalRequest": {"@type": "requestContact", "id": "DENIC-1000022-GR"},
 "abuse": {"@type": "requestContact", "id": "DENIC-1000022-AB"},
 "dns": {"@type": "dnsData", "records": [
   {"@type": "dnsRecord", "name": "@", "type": "a", "rdata": {"address": "192.0.2.10"}}]}}
```

```json valid domainName.read
{"@type": "domainName", "name": "example.de",
 "provMetadata": {"@type": "provMetadata", "spClientId": "DENIC-1000022"},
 "status": [{"@type": "domainStatus", "label": "ok"}],
 "registrant": {"@type": "contact", "id": "DENIC-1000022-HOLDER"},
 "contacts": [{"label": "registrant", "object": {"@type": "contact", "id": "DENIC-1000022-HOLDER2"}}],
 "generalRequest": {"@type": "requestContact", "id": "DENIC-1000022-GR"},
 "abuse": {"@type": "requestContact", "id": "DENIC-1000022-AB"}}
```

A partial update that replaces the abuse contact and removes the general request contact:

```json
[{"op": "replace", "path": "/abuse", "value": {"@type": "requestContact", "id": "DENIC-1000022-AB2"}},
 {"op": "remove", "path": "/generalRequest"}]
```

A transfer request (`POST /domainNames/example.de/processes/transferProcesses`, with
`RPP-Authorization: authinfo value=QWJjMjM0NTY3OA==`):

```json valid domainTransferProcess.create
{"@type": "domainTransferProcess",
 "registrant": {"@type": "contact", "id": "DENIC-1000002-HOLDER"},
 "generalRequest": {"@type": "requestContact", "id": "DENIC-1000002-GENERAL"},
 "abuse": {"@type": "requestContact", "id": "DENIC-1000002-ABUSE"},
 "dns": {"@type": "dnsData", "records": [
   {"@type": "dnsRecord", "name": "@", "type": "ns", "rdata": {"nsdname": "ns1.example.com."}},
   {"@type": "dnsRecord", "name": "@", "type": "ns", "rdata": {"nsdname": "ns2.example.com."}}]}}
```

Invalid: a request contact without a template, one with a template under 8 characters, a contact where a request
contact belongs, and a transfer without its domain data.

```json invalid requestContact.create
{"@type": "requestContact", "id": "DENIC-1000022-GR"}
```

```json invalid requestContact.create
{"@type": "requestContact", "id": "DENIC-1000022-GR", "uriTemplate": "http://"}
```

```json invalid domainName.update
{"@type": "domainName", "abuse": {"@type": "contact", "id": "DENIC-1000022-HOLDER"}}
```

```json invalid domainTransferProcess.create
{"@type": "domainTransferProcess"}
```

Valid by the schema, but refused by a server that offers the extension: a role as a contact label (501, `02102`).

```json valid domainName.update
{"@type": "domainName", "contacts": [{"label": "abuse", "object": {"@type": "contact", "id": "DENIC-1000022-AB"}}]}
```

## 15. IANA Considerations

None. The extension is private (guidelines §10): it registers nothing, and its identifier is reverse-domain
(guidelines §7). Its identifiers do not conflict with registered ones.

## 16. Security Considerations

The extension inherits the authentication and authorisation of the objects it extends (guidelines §12). A request
contact is the sponsoring client's own: RRI refuses another RegAcc's request contact on every operation and on a
domain (`63200020603`, 403). The AuthInfo of a transfer is sent in plaintext to RRI, so the proxy never logs that
command. The proxy does not validate a template beyond its length; RRI test-expands it on CREATE and refuses what it
cannot expand, so a template is not a vector into the proxy.

## 17. Privacy Considerations

A request contact is published: RRI's web whois shows the expanded template of a domain's General Request and Abuse
contacts. A `mailto` template that names a natural person's mailbox makes that address public. A request contact
holds no other personal data, and RRI refuses verification data on it (`63450064002`). The proxy logs the codes of
RRI's messages only, never their texts (docs/agents/security.project.md).

## 18. Internationalization Considerations

`{Ulabel}` expands to the U-label of the domain. How RRI encodes it in the expanded URI is not documented (ref
§5.1). The template itself is ASCII by the syntax of RFC 6570.

## Appendix A. Mapping to RRI

| RPP | RRI (XML 5.0) |
|---|---|
| `requestContact` | `contact:*` of `contact:type` `REQUEST` |
| `id` | `contact:handle` |
| `uriTemplate` | `contact:uri-template` |
| `provMetadata.spClientId` | the RegAccId the handle starts with |
| `provMetadata.upDate` | `contact:changed` |
| Create / Read / Update / Availability | contact CREATE / INFO / UPDATE / CHECK |
| `domainName.generalRequest` | `domain:contact role="generalrequest"` |
| `domainName.abuse` | `domain:contact role="abusecontact"` |
| `domainTransferProcess` Create | CHPROV with the full domain data |

The proxy keeps the two roles in its core model as contact references by role, as it keeps the holders, so the RRI
domain commands write them as before; only the RPP representation holds them as data elements of their own.
