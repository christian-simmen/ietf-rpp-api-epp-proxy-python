import logging

from core.session.session_pool import SessionPool
from rpp.http.app import create_app
from tests.helper.epp_backends import epp_backends
from tests.helper.fake_epp_client import FakeEppClient
from tests.helper.profiles import EPP_PROFILE

HEADERS = {"Accept": "application/rpp+json", "RPP-Cltrid": "cl-1"}


def client():
    return create_app(SessionPool(epp_backends(FakeEppClient)), EPP_PROFILE).test_client()


def test_building_the_app_logs_no_missing_bearer_function(caplog):
    with caplog.at_level(logging.WARNING, logger="connexion"):
        client().get("/.well-known/rpp", headers=HEADERS)

    assert not [record for record in caplog.records if "x-bearerInfoFunc" in record.getMessage()]


def test_a_bearer_token_is_not_accepted():
    response = client().delete("/domainNames/any.example", headers={**HEADERS, "Authorization": "Bearer abc.def"})

    assert response.status_code == 401
