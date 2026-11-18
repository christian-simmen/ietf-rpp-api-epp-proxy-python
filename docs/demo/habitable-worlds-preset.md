%%%
title = "Habitable worlds preset Demo for the RESTful Provisioning Protocol (RPP)"
abbrev = "RPP Habitable worlds preset Demo"
area = "Applications and Real-Time"
workgroup = "Network Working Group"
submissiontype = "IETF"
keyword = ["RPP", "provisioning", "demo"]
TocDepth = 4
date = 2026-11-17

[seriesInfo]
name = "Internet-Draft"
value = "draft-kowalik-rpp-habitable-worlds-demo-00"
stream = "IETF"
status = "informational"

[[author]]
initials="P."
surname="Kowalik"
fullname="Pawel Kowalik"
organization = "DENIC"

%%%

.# Abstract

This document defines a private demo preset of the RESTful Provisioning Protocol (RPP). Builds on the planets with atmospheres and the catalogued planets presets, and applies the habitable rocky planets profile.

{mainmatter}

# Introduction {#introduction}

This section states the purpose of the preset and the clients and servers it is intended for.

The preset is for clients of a server that holds habitable rocky planets with catalogued satellites. It builds on the presets `planets-atmosphere` and `catalogued-planets`, and applies the profile [habitable-rocky-planets](habitable-rocky-planets-profile.md). The profile `rocky-planets` is reached through the base preset and through the profile, and applies once.

The preset follows the Preset Specification Format of [@!I-D.wullink-rpp-extension-guidelines].

## Conventions and Terminology {#terminology}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when, and only when, they appear in all capitals, as shown here.

The terms Profile, Preset, Applicable Profiles, and Profile Binding are used as defined in [@!I-D.ietf-rpp-data-objects]. The terms Profile Schema, Constraints Mapper (`rpp:constraints`), Preset Schema, and Effective Schema are used as defined in [@!I-D.ietf-rpp-json]. The planets extension is `org.example.rpp.extension.planets`.

# Preset Overview {#overview}

| Field | Value |
| ----- | ----- |
| Name | Habitable worlds preset |
| Identifier | `org.example.rpp.preset.habitable-worlds` |
| Version | 1.0 |
| RPP version | 1.0 |
| Extensions | None |
| Profiles | `org.example.rpp.profile.habitable-rocky-planets` 1.0 |
| Base presets | `org.example.rpp.preset.planets-atmosphere` 1.0, `org.example.rpp.preset.catalogued-planets` 1.0 |
| Specification | <https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/docs/demo/habitable-worlds-preset.md> |
Table: Preset Overview

The extensions of the preset are those of its base presets, which contain every extension the profile requires, directly or through its base profiles.

A client signals the preset with each request, as defined in [@!I-D.ietf-rpp-core]:

```http-message
RPP-Preset: preset=org.example.rpp.preset.habitable-worlds;version=1.0
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
