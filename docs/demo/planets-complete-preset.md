%%%
title = "Complete planets preset Demo for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Complete planets preset Demo"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "demo"]
TocDepth = 4
date = 2026-11-17

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-planets-complete-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo preset of the RESTful Provisioning Protocol (RPP). Builds on the planets with atmospheres and the planets with orbits presets.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the preset and the clients and servers it is intended for.

The preset is for clients that use both the atmosphere of a planet and the orbit of a satellite. It builds on the presets `planets-atmosphere` and `planets-orbits`, and shows a preset with several bases: its extensions are the union of those of its bases, and the planets extension, which both reach, is in it once.

The preset follows the Preset Specification Format of [@!I-D.wullink-rpp-extension-guidelines].

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

The terms Profile, Preset, Applicable Profiles, and Profile Binding are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Profile Schema, Constraints Mapper (`rpp:constraints`), Preset Schema, and Effective Schema are used as defined in [@!I-D.ietf-rpp-json]. The planets extension is `org.example.rpp.extension.planets`.

# Preset Overview {#overview}

| Field | Value |
| ----- | ----- |
| Name | Complete planets preset |
| Identifier | `org.example.rpp.preset.planets-complete` |
| Version | 1.0 |
| RPP version | 1.0 |
| Extensions | None |
| Profiles | None |
| Base presets | `org.example.rpp.preset.planets-atmosphere` 1.0, `org.example.rpp.preset.planets-orbits` 1.0 |
| Specification | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/docs/demo/planets-complete-preset.md> |
Table: Preset Overview

The extensions of the preset are those of its base presets, each once.

A client signals the preset with each request, as defined in [@!I-D.ietf-rpp-core]:

```http-message
RPP-Preset: preset=org.example.rpp.preset.planets-complete;version=1.0
```

# IANA Considerations {#iana}

This document has no IANA actions. The preset is a private preset, and its identifier is formed by reverse domain name notation under the domain `example.org`, which is reserved for documentation [@RFC2606]. It is not registered in the RPP Presets registry.

# Security Considerations {#security}

The preset adds no functionality and no constraints of its own. The security considerations of its extensions and profiles apply.

{removeInRFC="true"}
{toc="exclude"}
# Changes History

{toc="exclude"}
{numbered="false"}
## 1.0

* initial version #179
