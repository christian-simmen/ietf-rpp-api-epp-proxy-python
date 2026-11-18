# Specification writing

Project-agnostic rules for writing protocol specifications in the IETF house style: an Internet-Draft, an extension
specification, or a proposed change to a draft. Which documents exist, which drafts they follow, the authoring syntax
and the data model notation are in [specification.project.md](specification.project.md).

These rules are imported from the agent guide of the RPP data objects draft (the source and the imported revision are
in the project file). A rule that should change is changed here, not worked around.

## Working agreement

- **Requirements first.** A concept nobody has specified yet goes through [requirements.md](requirements.md) before
  any specification text is written.
- **Propose, then edit.** Before changing a specification, present the target section (title and anchor), the exact
  text to add, change or remove, and why it belongs there. Apply nothing until the user approves both the text and the
  location. Revise and present again if the user asks for changes.
- **Rule conflicts need confirmation, not silent overrides.** If a request would break or bend a rule in this file,
  stop and ask whether the exception is one-off or the rule should change. If the rule changes, update its text in
  the same session.
- **Never restore removed content.** Text the user edited or removed by hand is authoritative. Re-read the region
  before an edit so a replacement block does not bring deleted text back. If an edit would reintroduce it, stop and
  ask.
- **Bulk structural edits are scripted.** The same structural transformation repeated across many places (a table to
  a definition list, re-quoting every literal) is done by a throwaway script, not by many hand edits. The script
  transforms structure only and never rewrites prose. Snapshot the file first, then diff: the prefix and tail are
  byte-identical, only the intended markup changed, no prose word changed, and every anchor is kept. Delete the
  script and the snapshot afterwards and never commit them.

## Normative language (BCP 14)

- Use MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL
  only in their RFC 2119 sense and only in capitals. In lower case they are ordinary words.
- Include the BCP 14 boilerplate exactly once, citing both RFC 2119 and RFC 8174 with the "when, and only when, they
  appear in all capitals" sentence.
- Every key word places a requirement on a **specific actor** for a **specific, testable behaviour**. "The server MUST
  reject the request" is testable. "The system MUST be secure" is not: rewrite it.
- Do not stack key words ("MUST ... REQUIRED to"). Do not use one where present tense states a fact ("the field
  *contains* a timestamp").
- Use the key words sparingly, only where interoperability or the limitation of harm needs them, never for emphasis.
  Plain declarative prose is often the better normative statement (IESG statement on BCP 14 key words,
  <https://www.ietf.org/about/groups/iesg/statements/clarifying-use-bcp14/>).
- **Justify every SHOULD and RECOMMENDED**: say what an implementation weighs before deviating. Without a legitimate
  reason to deviate it is a MUST. Without interoperability or harm implications it is a MAY or no key word.
- For backward compatibility, make the rationale explicit: "New implementations MUST use $NEW. Implementations SHOULD
  accept $OLD for compatibility with existing deployments."
- No key words in the Abstract, IANA Considerations, examples, figures, captions, or appendices (a large normative
  table in an appendix is the only exception).

## Specify, don't describe

- Write declarative, present-tense requirements, not narrative or marketing prose.
- Name the conformance target (client, server, sender, receiver) in each requirement.
- Specify **both sides**: what a sender produces and what a receiver accepts, including how a receiver handles values
  it does not recognise (forward compatibility, must-ignore rules).
- State **error handling** and the behaviour on malformed or unexpected input explicitly. These are the requirements
  most often left implicit and most needed for interoperability.
- Give the **wire format precisely**: character encoding, case sensitivity, length limits, defaults and units. Prefer
  explicit enumerations and ranges to open-ended adjectives.

## Terminology

- Define each term once and use it consistently. Never introduce a synonym for a defined term.
- Reuse the terms of the specifications the document builds on, cite their source, and do not redefine them.
- Expand every acronym on first use, in the body and in any title. RFC 7322 exempts a short list of well-known
  abbreviations (TCP, IP, HTTP and others).

## Structure

- Follow the RFC 7322 ordering: Abstract, Introduction, Conventions and Terminology, the body, IANA Considerations,
  Security Considerations, then the references in the back matter.
- The **Abstract** stands alone: no citations and no key words.
- **IANA Considerations** is required. List every registry action precisely, use `TBD1`, `TBD2`, ... for values IANA
  assigns, and never leave a bare TODO. A document with no actions says so.
- **Security Considerations** is required and substantive, following BCP 72 (RFC 3552).
- **Privacy Considerations** is included when the protocol collects, exposes or correlates person-linkable data
  (RFC 6973). If it does not apply, say so and why.
- Lead each major section with one sentence stating its purpose.
- Keep rationale, history and explanation in places marked non-normative. Mark examples as non-normative.
- **State each requirement once** and cross-reference it with an anchor. Duplicated normative text drifts.
- Keep anchors stable. Never rename or drop one silently during a restructure: other sections and external readers
  link to it.
- Classify each reference deliberately as normative or informative. A reference a MUST depends on is normative.

## Tone and mechanics

- Neutral and precise. Avoid hype and hedging ("simply", "just", "obviously").
- Distinguish "i.e." (that is) from "e.g." (for example).
- One requirement per sentence where practical, so that a conformance checklist can be built from the text.
- Never join sentences with a semicolon. Write separate sentences.
- **ASCII only** (RFC 7997), except in internationalised domain names in examples and in person names, which get an
  ASCII equivalent where RFC 7997 recommends one. Use `--` or a reworded sentence for dashes, straight quotes, `...`
  for an ellipsis and `->` for arrows. Check with `grep -nP '[^\x00-\x7F]' <file>`.
- Use the reserved example domains and addresses (RFC 2606, RFC 5737), never real ones.
- Wrap bare URIs in angle brackets (`<https://example.com/>`).
- Title case for the document title and section titles.
- Inline code for identifiers, literal tokens and type names. Examples use the proper type representation (strings in
  quotes). Constraints are specific and testable.
- Editorial markers: `TBC:` (to be confirmed), `TBD:` (to be determined), `TODO:` (action required).
- When in doubt: RFC 7322 (style guide), RFC 2119 and RFC 8174 with the IESG BCP 14 statement, and
  <https://authors.ietf.org/>. Run idnits before a submission.

## Changes History

Every edit to a specification adds an entry to its Changes History section, in the subsection of the revision being
written:

- One concise line per change, in lower case, with the issue number as `#NN` where there is one.
- Describe what changed, not why (the issue has the why).
- Group related changes. If an entry already covers the same change or issue, merge into it instead of adding a
  bullet.

## Consistency checks

After a structural change (adding, removing or refactoring an object or data element, or any change affecting several
sections), check every definition against every place that restates it, such as the IANA registry tables, the schema
and the examples:

- Every element of a definition appears in the restatement and vice versa.
- Identifiers, cardinality, mutability and data types are identical.
- No field that belongs to a shared component remains duplicated in an object.

Fix what is inconsistent and report what was checked.

## Checklist

Before an edit to a specification is complete:

- [ ] The user approved the text and its location.
- [ ] Every definition carries all attributes the project's notation requires.
- [ ] Constraints are clear and testable.
- [ ] Key words in capitals, used sparingly, each SHOULD justified.
- [ ] References formatted and classified as normative or informative.
- [ ] Anchors kept, cross-references resolve.
- [ ] No non-ASCII characters outside IDN examples and person names. No trailing whitespace.
- [ ] Terminology matches existing usage. Spelling follows the project's convention consistently.
- [ ] Consistency check done for a structural change.
- [ ] Changes History entry added.
