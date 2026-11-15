"""The effective schema of each profile: built once with the app, published at /profiles/{name}/schema, listed in
discovery, and the same as what the proxy validates with (json §7.2)."""
from urllib.parse import quote

import jsonschema
import pytest
from jsonschema import Draft202012Validator

from core.session.session_pool import SessionPool
from rpp.http.app import create_app
from rpp.schema import effective_schema
from rpp.schema import profile_schemas as profile_schemas_module
from rpp.schema import validator
from rpp.schema.extensions import SERVER_EXTENSIONS
from rpp.schema.profiles import PROFILES
from tests.helper.epp_backends import epp_backends
from tests.helper.fake_epp_client import FakeEppClient
from tests.helper.fake_rri_client import FakeRriClient, rri_backends
from tests.helper.profiles import EPP_PROFILE, RRI_PROFILE
from tests.unit.test_profiles_wire import BASE, EPP, RRI, epp_client, rri_client
from tests.unit.test_rri_wire import DISCOVERY, HEADERS

PUBLIC = {"Accept": "application/rpp+json", "RPP-Cltrid": "cl-1"}   # no Authorization: like discovery
SCHEMA = {"Accept": "application/schema+json"}                          # a schema fetch: no RPP-Cltrid, no profile
BASE_URL = DISCOVERY.rpp_base_url


def url_of(name):
    return f"{BASE_URL}/profiles/{quote(name, safe='')}/schema"


def schema_of(client, name):
    response = client.get(f"/profiles/{quote(name, safe='')}/schema", headers=SCHEMA)
    assert response.status_code == 200, response.text
    return response


@pytest.mark.parametrize("client_of, names", [(epp_client, [BASE, EPP]), (rri_client, [BASE, RRI])])
def test_discovery_lists_the_url_of_the_schema_of_each_offered_profile(client_of, names):
    document = client_of().get("/.well-known/rpp", headers=PUBLIC).json()

    assert document["profileSchemas"] == [{"profile": name, "version": "1.0", "url": url_of(name)} for name in names]
    assert document["profiles"] == names
    assert document["extensions"][-1]["id"] == SERVER_EXTENSIONS[0]    # server-wide, in no profile


@pytest.mark.parametrize("client_of, names", [(epp_client, [BASE, EPP]), (rri_client, [BASE, RRI])])
def test_each_listed_schema_is_fetched_without_authentication_and_is_a_valid_2020_12_schema(client_of, names):
    client = client_of()
    for name in names:
        response = schema_of(client, name)
        document = response.json()

        assert response.headers["Content-Type"] == "application/schema+json"
        assert response.headers["RPP-Code"] == "01000"
        assert document["$id"] == url_of(name)
        assert document["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(document)


@pytest.mark.parametrize("name", ["nope", RRI])
def test_a_name_the_server_does_not_offer_is_a_404(name):
    response = epp_client().get(f"/profiles/{quote(name, safe='')}/schema", headers=SCHEMA)

    assert response.status_code == 404 and response.headers["RPP-Code"] == "02303"
    assert response.headers["Content-Type"] == "application/problem+json"


def media_client():
    sessions = SessionPool(epp_backends(lambda username, password: FakeEppClient(username, password)))
    return create_app(sessions, EPP_PROFILE, discovery_settings=DISCOVERY, signalling="media-type").test_client()


@pytest.mark.parametrize("client_of", [epp_client, media_client], ids=["header", "media-type"])
class TestTheSchemaIsADocumentOutsideProfileSignalling:
    def fetch(self, client_of, headers):
        return client_of().get(f"/profiles/{BASE}/schema", headers=headers)

    @pytest.mark.parametrize("accept", ["application/schema+json", "application/json", "application/*", "*/*",
                                        "text/html, application/json;q=0.5", 'application/schema+json; profile="x"'])
    def test_an_accept_that_allows_the_document_is_answered(self, client_of, accept):
        response = self.fetch(client_of, {"Accept": accept})

        assert response.status_code == 200 and response.headers["Content-Type"] == "application/schema+json"
        assert response.headers["Vary"] == "Accept"

    def test_no_accept_is_any(self, client_of):
        response = client_of().get(f"/profiles/{BASE}/schema", headers={"Accept": ""})

        assert response.status_code == 200

    @pytest.mark.parametrize("accept", ["text/html", "application/rpp+json", "application/xml, application/schema+json;q=0",
                                        "application/schema+json;q=0, */*"])
    def test_an_accept_that_does_not_allow_it_is_a_406_problem_detail(self, client_of, accept):
        response = self.fetch(client_of, {"Accept": accept})

        assert response.status_code == 406 and response.headers["RPP-Code"] == "02004"
        assert response.headers["Content-Type"] == "application/problem+json"
        assert "RPP-Profile" not in response.headers

    def test_rpp_cltrid_is_optional_and_echoed_when_sent(self, client_of):
        assert "RPP-Cltrid" not in self.fetch(client_of, SCHEMA).headers
        assert self.fetch(client_of, {**SCHEMA, "RPP-Cltrid": "cl-9"}).headers["RPP-Cltrid"] == "cl-9"

    @pytest.mark.parametrize("headers", [
        {"RPP-Profile": "garbage"},                                          # no refusal, and nothing selected
        {"RPP-Profile": f"profile={RRI};version=9.9"},
        {"Content-Type": 'application/rpp+json; profile="nope"; profile-version="9.9"'},
        {"Accept": 'application/schema+json; profile="nope"; profile-version="9.9"'},
    ])
    def test_profile_headers_and_parameters_are_ignored(self, client_of, headers):
        response = self.fetch(client_of, {**SCHEMA, **headers})

        assert response.status_code == 200
        assert "RPP-Profile" not in response.headers
        assert response.headers["Content-Type"] == "application/schema+json"      # no profile parameters
        assert response.json()["$id"] == url_of(BASE)

    def test_a_name_not_offered_is_a_404_with_no_profile_either(self, client_of):
        response = client_of().get("/profiles/nope/schema", headers=SCHEMA)

        assert response.status_code == 404 and "RPP-Profile" not in response.headers


def test_a_profile_has_the_definitions_of_its_extensions_and_no_others():
    base, rri = (schema_of(rri_client(), name).json()["$defs"] for name in (BASE, RRI))

    assert "ext.rri.requestContact.create" in rri and "ext.rri.requestContact.create" not in base
    assert set(base) < set(rri)
    # an extended definition is the allOf of the base definition and the extension's
    assert "allOf" not in base["domainName.create"] and len(rri["domainName.create"]["allOf"]) == 2
    assert rri["domainName.create"]["allOf"][1] == {"$ref": "#/$defs/ext.rri.domainName.create"}


# Bodies and the definition each is checked as: the proxy and the published schema must agree on every one.
SAMPLES = [
    ("domainName.create", {"@type": "domainName", "name": "foo.de"}),
    ("domainName.create", {"@type": "domainName"}),
    ("domainName.create", {"@type": "domainName", "name": 1}),
    ("domainName.create", {"@type": "domainName", "name": "foo.de",
                           "generalRequest": {"@type": "requestContact", "id": "X-1"}}),
    # a malformed member of the extension: refused where the profile has the extension, an undeclared member without it
    ("domainName.create", {"@type": "domainName", "name": "foo.de", "generalRequest": {"@type": "requestContact"}}),
    ("domainName.update", {"@type": "domainName", "abuse": {"@type": "requestContact"}}),
    ("domainTransferProcess.create", {"@type": "domainNameTransferProcess"}),
    ("contact.create", {"@type": "contact", "id": "X-1"}),
    ("requestContact.create", {"@type": "requestContact", "id": "X-1"}),
    ("requestContact.create", {"@type": "requestContact", "id": "X-1", "uriTemplate": "https://e.example/{Alabel}"}),
    ("discovery.read", {"@type": "discovery"}),
    # undeclared members (json §4.9.1): at the top level, nested in a referenced object, in an object of the extension, and
    # in an object the extension defines
    ("domainName.create", {"@type": "domainName", "name": "foo.de", "bogus": 1}),
    ("domainName.create", {"@type": "domainName", "name": "foo.de", "registrant": {"@type": "contact", "id": "X-1", "bogus": 1}}),
    ("domainName.create", {"@type": "domainName", "name": "foo.de",
                           "generalRequest": {"@type": "requestContact", "id": "X-1", "bogus": 1}}),
    ("domainName.create", {"@type": "domainName", "name": "foo.de", "dns": {"@type": "dnsData", "bogus": 1}}),
    ("requestContact.create", {"@type": "requestContact", "id": "X-1", "uriTemplate": "https://e.example/{Alabel}", "bogus": 1}),
    ("contact.create", {"@type": "contact", "id": "X-1", "contactInfo": {"@type": "Card", "version": "2.0", "bogus": 1}}),
    ("domainTransferProcess.create", {"@type": "domainTransferProcess", "bogus": 1}),
    # an undeclared member in an item of an array
    ("domainName.create", {"@type": "domainName", "name": "foo.de",
                           "nameservers": [{"@type": "host", "hostName": "ns1.example", "bogus": 1}]}),
    ("domainName.create", {"@type": "domainName", "name": "foo.de",
                           "contacts": [{"label": "admin", "object": {"@type": "contact", "id": "X-1"}, "bogus": 1}]}),
]


def published_validity(document, name, body):
    """Whether the published schema accepts `body` as definition `name` (an extension's own object has the name of the
    definition it is in the document)."""
    defs = document["$defs"]
    target = name if name in defs else next((d for d in defs if d.startswith("ext.") and d.endswith("." + name)), None)
    if target is None:
        return None     # the profile has no such definition
    return Draft202012Validator({"$ref": f"#/$defs/{target}", "$defs": defs}).is_valid(body)


def enforced_validity(name, body, extensions):
    if (name, tuple(extensions)) not in validator._effective:
        validator.build_effective(extensions)
    try:
        validator.validate_schema(name, body, extensions)
        return True
    except (jsonschema.ValidationError, ValueError):     # an undeclared member is a ValueError (json §4.9.1)
        return False


@pytest.mark.parametrize("key", ["base", "epp", "rri"])
@pytest.mark.parametrize("name, body", SAMPLES, ids=[f"{n}-{i}" for i, (n, _) in enumerate(SAMPLES)])
def test_the_published_schema_accepts_and_refuses_what_the_proxy_does(key, name, body):
    profile = PROFILES[key]
    client = rri_client() if key == "rri" else epp_client()
    if key == "base":
        client = epp_client()
    document = schema_of(client, profile.name).json()
    published = published_validity(document, name, body)

    if published is None:
        assert name in validator.own_definitions() or name == "requestContact.create"
        return
    assert published == enforced_validity(name, body, profile.extensions), (key, name, body)


def test_an_rri_member_is_refused_where_the_profile_lacks_the_extension_and_accepted_where_it_has_it():
    body = {"@type": "domainName", "name": "foo.de", "generalRequest": {"@type": "requestContact", "id": "X-1"}}
    base = schema_of(rri_client(), BASE).json()
    rri = schema_of(rri_client(), RRI).json()

    assert published_validity(base, "domainName.create", body) is False      # undeclared under base (json §4.9.1)
    assert published_validity(rri, "domainName.create", body) is True
    malformed = {**body, "generalRequest": {"@type": "requestContact"}}
    assert published_validity(base, "domainName.create", malformed) is False
    assert published_validity(rri, "domainName.create", malformed) is False  # the member lacks its id


def test_a_member_nobody_declares_is_refused_under_every_profile_even_inside_the_extension():
    for name in (BASE, RRI):
        document = schema_of(rri_client(), name).json()
        for body in ({"@type": "domainName", "name": "foo.de", "bogus": 1},
                     {"@type": "domainName", "name": "foo.de", "registrant": {"@type": "contact", "id": "X-1", "bogus": 1}}):
            assert published_validity(document, "domainName.create", body) is False
    rri = schema_of(rri_client(), RRI).json()
    inside = {"@type": "domainName", "name": "foo.de", "generalRequest": {"@type": "requestContact", "id": "X-1", "bogus": 1}}
    assert published_validity(rri, "domainName.create", inside) is False


def test_the_validators_are_built_on_the_published_definitions():
    for key in ("base", "rri"):
        profile = PROFILES[key]
        published = schema_of(rri_client(), profile.name).json()["$defs"]

        assert effective_schema.effective_definitions((*profile.extensions, *SERVER_EXTENSIONS)) == published
        assert (("domainName.create", (*profile.extensions, *SERVER_EXTENSIONS)) in validator._effective)


@pytest.mark.parametrize("client_of, names", [(epp_client, [BASE, EPP]), (rri_client, [BASE, RRI])])
def test_the_published_schema_accepts_the_discovery_document_of_the_server(client_of, names):
    client = client_of()
    discovery = client.get("/.well-known/rpp", headers=PUBLIC).json()
    for name in names:
        defs = schema_of(client, name).json()["$defs"]
        schema = Draft202012Validator({"$ref": "#/$defs/discovery.read", "$defs": defs})

        assert list(schema.iter_errors(discovery)) == [], name


def test_an_undeclared_member_is_the_error_a_mapper_turns_into_a_400():
    with pytest.raises(ValueError, match="Undeclared property: 'bogus'"):
        validator.validate_schema("domainName.create", {"@type": "domainName", "name": "foo.de", "bogus": 1})


def count_composed(monkeypatch):
    calls = []
    original = validator._compose

    def counting(name, extensions):
        calls.append((name, extensions))
        return original(name, extensions)

    monkeypatch.setattr(validator, "_compose", counting)
    return calls


def test_the_schemas_are_built_once_per_profile_with_the_app_and_never_per_request(monkeypatch):
    monkeypatch.setattr(validator, "LAZY_BUILD", False)     # the app builds all it needs, a request builds nothing
    monkeypatch.setattr(validator, "_effective", {})
    monkeypatch.setattr(effective_schema, "_effective", {})
    composed = count_composed(monkeypatch)
    documents = []
    original = profile_schemas_module.ProfileSchemas._document
    monkeypatch.setattr(profile_schemas_module.ProfileSchemas, "_document",
                        staticmethod(lambda *args: documents.append(args[0].key) or original(*args)))

    sessions = SessionPool(rri_backends(lambda username, password: FakeRriClient(username, password, replies=[])))
    client = create_app(sessions, RRI_PROFILE, discovery_settings=DISCOVERY).test_client()

    # one document per offered profile, and the validators of every definition for each distinct extension tuple
    assert documents == ["base", "rri"]
    assert len(composed) == len(validator._names()) * 4            # (), rri, the server's own, rri and the server's
    built = len(composed)

    for _ in range(3):
        client.get("/.well-known/rpp", headers=PUBLIC)
        client.get(f"/profiles/{RRI}/schema", headers=PUBLIC)
        client.get(f"/profiles/{RRI}", headers=PUBLIC)
        client.post("/domainNames", json={"@type": "domainName", "name": "foo.de"},
                    headers={**HEADERS, "Content-Type": "application/rpp+json"})
        client.get("/domainNames/foo.de", headers=HEADERS)
        for response in (
                client.post("/requestContacts", json={"@type": "requestContact", "id": "DENIC-1000022-GR",
                                                      "uriTemplate": "https://e.example/{Alabel}"},
                            headers={**HEADERS, "Content-Type": "application/rpp+json"}),
                client.put("/requestContacts/DENIC-1000022-GR", json={"@type": "requestContact",
                                                                     "uriTemplate": "https://e.example/{Alabel}"},
                           headers={**HEADERS, "Content-Type": "application/rpp+json"}),
                client.get("/requestContacts/DENIC-1000022-GR/availability", headers=HEADERS)):
            assert "No schema" not in response.text         # nothing was built, or looked up unbuilt, for the request

    assert len(composed) == built and documents == ["base", "rri"]


def test_a_second_app_of_the_same_profiles_reuses_the_validators(monkeypatch):
    epp_client()
    composed = count_composed(monkeypatch)

    epp_client()

    assert composed == []


def test_without_a_configured_base_url_a_document_has_no_id():
    sessions = SessionPool(epp_backends(lambda username, password: FakeEppClient(username, password)))
    client = create_app(sessions, EPP_PROFILE).test_client()
    document = client.get(f"/profiles/{BASE}/schema", headers=PUBLIC).json()

    assert "$id" not in document


@pytest.mark.parametrize("body", [
    {"@type": "domainName", "name": "foo.de", "nameservers": [{"@type": "host", "hostName": "ns1.example", "bogus": 1}]},
    {"@type": "domainName", "name": "foo.de", "contacts": [{"label": "admin", "object": {"@type": "contact", "id": "X-1"}, "bogus": 1}]},
])
@pytest.mark.parametrize("key", ["base", "epp", "rri"])
def test_an_undeclared_member_in_an_array_item_is_refused_under_every_profile(key, body):
    profile = PROFILES[key]
    client = rri_client() if key == "rri" else epp_client()
    document = schema_of(client, profile.name).json()

    assert published_validity(document, "domainName.create", body) is False
    with pytest.raises(ValueError, match="Undeclared property: 'bogus'"):
        validator.validate_schema("domainName.create", body, profile.extensions)


def test_an_unbuilt_schema_is_an_error_where_the_app_is_not_lazy(monkeypatch):
    monkeypatch.setattr(validator, "LAZY_BUILD", False)

    with pytest.raises(validator.SchemaNotBuilt):
        validator.effective_validator("domainName.create", ("no.such.extension",))
    # what no profile of the app has: an extension's own object under a tuple without the extension
    with pytest.raises(validator.SchemaNotBuilt):
        validator.effective_validator("requestContact.create", ())


def https_settings(url):
    from types import SimpleNamespace
    return SimpleNamespace(rpp_base_url=url, rpp_tlds=["de"], rpp_environment_name="test", rpp_environment_status="test")


@pytest.mark.parametrize("url", ["https://user:secret@rpp.example", "https://rpp.example/?token=1", "https://rpp.example/#x",
                                 "http://rpp.example", "https://", "https://rpp.example/a b", "rpp.example"])
def test_a_base_url_discovery_would_refuse_is_published_in_no_id(url):
    sessions = SessionPool(epp_backends(lambda username, password: FakeEppClient(username, password)))
    client = create_app(sessions, EPP_PROFILE, discovery_settings=https_settings(url)).test_client()
    document = client.get(f"/profiles/{BASE}/schema", headers=SCHEMA)

    assert document.status_code == 200 and "$id" not in document.json()
    assert "secret" not in document.text and "token" not in document.text
    assert client.get("/.well-known/rpp", headers=PUBLIC).status_code == 500
