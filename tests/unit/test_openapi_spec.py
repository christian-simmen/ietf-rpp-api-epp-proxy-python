from types import SimpleNamespace

import yaml

from core.session.session_pool import SessionPool
from tests.helper.profiles import EPP_PROFILE
from rpp.http.app import create_app, OPENAPI_SPEC, parsed_spec


def build_app():
    return create_app(SessionPool(lambda username, password: None), EPP_PROFILE)


def test_apps_share_one_parse_of_the_spec():
    """#112: parsing the OpenAPI document for every app made the unit tests slow."""
    before = parsed_spec.cache_info()
    build_app()
    build_app()
    after = parsed_spec.cache_info()
    assert after.hits + after.misses - before.hits - before.misses == 2
    assert after.misses <= 1


def test_building_an_app_leaves_the_shared_spec_as_parsed():
    """connexion fills in defaults and resolves references in the spec it is given."""
    build_app()
    with OPENAPI_SPEC.open("rb") as spec:
        assert parsed_spec() == yaml.safe_load(spec)


def test_the_app_serves_the_spec():
    response = build_app().test_client().get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["paths"].keys() == parsed_spec()["paths"].keys()
    assert {"/presets/{id}", "/presets/{id}/schema", "/profiles/{id}"} <= response.json()["paths"].keys()


def test_the_spec_served_stays_the_same_after_a_validated_response():
    """#193: connexion's response validation wrote `components` into the inline response schema of discovery, and
    `/openapi.json` answered 500 from then on."""
    settings = SimpleNamespace(rpp_base_url="https://rpp.example/rpp", rpp_tlds=["example"],
                               rpp_environment_name="rpp.example", rpp_environment_status="test")
    client = create_app(SessionPool(lambda username, password: None), EPP_PROFILE,
                        discovery_settings=settings).test_client()
    json_before, yaml_before = client.get("/openapi.json"), client.get("/openapi.yaml")
    assert client.get("/.well-known/rpp", headers={"RPP-Cltrid": "spec-1"}).status_code == 200
    json_after, yaml_after = client.get("/openapi.json"), client.get("/openapi.yaml")
    assert json_after.status_code == yaml_after.status_code == 200
    assert json_after.content == json_before.content
    assert yaml_after.content == yaml_before.content
