# Swagger UI

The files of `swagger-ui-dist` 5.17.14 (npm, Apache-2.0, `LICENSE` and `NOTICE`), integrity
`sha512-CVbSfaLpstV65OnSjbXfVd6Sta3q3F7Cj/yYuvHMp1P90LztOLs6PfUnKEVAeiIVQt9u2SaPwv0LiH/OyMjHRw==`, without the source maps and
the ES bundles. `index.j2` is the template of `swagger_ui_bundle` 1.1.0, which Connexion renders with the URL of the OpenAPI
document. The proxy serves its OpenAPI document as 3.1, which Swagger UI renders from 5.0; `swagger_ui_bundle` ships 4.15.5 (#204).
To update: replace the files by those of a newer `swagger-ui-dist` and the version and integrity above.
