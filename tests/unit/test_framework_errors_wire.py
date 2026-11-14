import pytest

from rpp.http.app import create_app
from tests.helper.profiles import EPP_PROFILE

MEDIA_TYPE = "application/rpp+json"
RPP_ERROR = "urn:ietf:params:rpp:error"
HEADERS = {"Accept": MEDIA_TYPE, "RPP-Cltrid": "fw-err-1"}


class NoSessions:
    def session(self, username, password):
        raise AssertionError("an error of the framework needs no session")


@pytest.fixture(scope="module")
def client():
    return create_app(NoSessions(), EPP_PROFILE).test_client()


def assert_rpp_error(response, status):
    assert response.status_code == status
    assert response.headers["Content-Type"].startswith("application/problem+json")
    body = response.json()
    assert body["type"] == RPP_ERROR
    assert body["status"] == status
    assert body["errors"][0]["result"] == "02001"
    assert response.headers["RPP-Code"] == "02001"
    assert response.headers["RPP-Svtrid"]
    assert response.headers["RPP-Cltrid"] == "fw-err-1"


def allowed(response):
    return {m.strip() for m in response.headers["Allow"].split(",")}


def test_wrong_method_on_discovery_is_an_rpp_error_with_allow(client):
    response = client.post("/.well-known/rpp", headers=HEADERS)

    assert_rpp_error(response, 405)
    assert allowed(response) == {"GET", "HEAD"}
    assert response.json()["title"] == "Method Not Allowed"


def test_wrong_method_on_messages_is_an_rpp_error_with_allow(client):
    response = client.put("/messages", headers=HEADERS)

    assert_rpp_error(response, 405)
    assert allowed(response) == {"POST"}


def test_unknown_path_is_an_rpp_error(client):
    response = client.get("/nonexistent", headers=HEADERS)

    assert_rpp_error(response, 404)
    assert response.json()["title"] == "Not Found"


def test_problem_exception_is_still_rendered_by_its_own_handler(client):
    response = client.delete("/domainNames/any.example", headers=HEADERS)

    assert response.status_code == 401
    assert response.headers["RPP-Code"] == "02200"
    assert response.json()["type"] == RPP_ERROR
    assert response.json()["errors"][0]["result"] == "02200"
