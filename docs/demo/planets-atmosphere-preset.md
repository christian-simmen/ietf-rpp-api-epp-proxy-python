%%%
title = "Planets with atmospheres preset Demo for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Planets with atmospheres preset Demo"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "demo"]
TocDepth = 4
date = 2026-11-17

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-planets-atmosphere-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo preset of the RESTful Provisioning Protocol (RPP). The planets preset with the atmosphere of a planet.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the preset and the clients and servers it is intended for.

The preset is for clients that read and set the atmosphere of a planet. It adds the planet atmosphere extension ([planet-atmosphere-extension.md](planet-atmosphere-extension.md)) to the planets preset.

The preset follows the Preset Specification Format of [@!I-D.wullink-rpp-extension-guidelines].

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

The terms Profile, Preset, Applicable Profiles, and Profile Binding are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Profile Schema, Constraints Mapper (`rpp:constraints`), Preset Schema, and Effective Schema are used as defined in [@!I-D.ietf-rpp-json]. The planets extension is `org.example.rpp.extension.planets`.

# Preset Overview {#overview}

| Field | Value |
| ----- | ----- |
| Name | Planets with atmospheres preset |
| Identifier | `org.example.rpp.preset.planets-atmosphere` |
| Version | 1.0 |
| RPP version | 1.0 |
| Extensions | `org.example.rpp.extension.planet-atmosphere` 1.0 |
| Profiles | None |
| Base presets | `org.example.rpp.preset.planets` 1.0 |
| Specification | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/docs/demo/planets-atmosphere-preset.md> |
Table: Preset Overview

A client signals the preset with each request, as defined in [@!I-D.ietf-rpp-core]:

```http-message
RPP-Preset: preset=org.example.rpp.preset.planets-atmosphere;version=1.0
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
