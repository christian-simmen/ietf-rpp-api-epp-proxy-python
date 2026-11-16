#!/bin/sh
# Copies the generated contract from the draft set into the application.
SPEC_FOLDER=.spec/auto

cp -v $SPEC_FOLDER/openapi3/openapi.yaml ./src/rpp/openapi.yaml
cp -v $SPEC_FOLDER/json-schema/rpp.schema.normalized.json ./src/rpp/schema/schemas/
cp -v .spec/draft-ietf-rpp-data-objects.yaml ./src/rpp/schema/schemas/
# The RPP extensions of the proxy (json §7), described in docs/rri/rri-extension.md.
cp -v .spec/rri-extension.schema.json ./src/rpp/schema/schemas/extensions/
# The Profile Schema of the EPP Compatibility Profile, from draft-kowalik-rpp-epp-compatibility.
cp -v .spec/epp-compatibility-profile.schema.json ./src/rpp/schema/schemas/profiles/epp-compatibility.schema.json
# The demo extension of the SQLite backend, described in docs/demo/planets-extension.md.
cp -v .spec/planets-extension.schema.json ./src/extensions/planets/rpp/schema/
