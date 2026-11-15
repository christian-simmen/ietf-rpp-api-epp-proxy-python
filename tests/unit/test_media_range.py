"""The media ranges of Accept and the media type of Content-Type, as core §14.3 reads them."""
from decimal import Decimal

import pytest

from rpp.http import media_range
from rpp.http.media_range_error import MediaRangeError

URN = "urn:ietf:params:rpp:profile:base"


def one(value):
    [item] = media_range.parse_accept([value])
    return item


def test_a_quoted_and_a_token_value_are_the_same():
    assert one(f'application/rpp+json; profile="{URN}"; profile-version="1.0"').profile() == (URN, Decimal("1.0"))
    assert one("application/rpp+json; profile=de.denic.rpp.profile.rri; profile-version=1.0").profile() \
        == ("de.denic.rpp.profile.rri", Decimal("1.0"))


def test_names_are_not_case_sensitive_and_a_quoted_pair_is_unescaped():
    assert one('Application/RPP+json; PROFILE="a\\"b"; Profile-Version=1.0').profile() == ('a"b', Decimal("1.0"))


def test_the_weight_ends_the_media_type_parameters_and_commas_in_quotes_do_not_split():
    items = media_range.parse_accept(['application/rpp+json; profile="a,b"; profile-version=1.0; q=0.5; x=1, */*;q=0'])

    assert [item.kind for item in items] == ["application/rpp+json", "*/*"]
    assert items[0].quality == Decimal("0.5") and items[1].quality == 0
    assert items[0].profile() == ("a,b", Decimal("1.0"))


def test_a_range_without_the_parameters_names_no_profile():
    assert one("application/rpp+json").profile() is None
    assert one("application/rpp+json").quality == 1


def test_field_lines_are_joined():
    assert [item.kind for item in media_range.parse_accept(["text/html", " , application/*;q=0.1"])] \
        == ["text/html", "application/*"]


@pytest.mark.parametrize("value", ["application/rpp+json; profile=x", "application/rpp+json; profile-version=1.0"])
def test_a_profile_without_its_version_or_the_reverse_is_a_missing_parameter(value):
    with pytest.raises(MediaRangeError) as error:
        one(value).profile()

    assert error.value.code.value[0] == "2003"


@pytest.mark.parametrize("value", [
    "application/rpp+json; profile=x; profile-version=1",        # the ABNF requires a point
    "application/rpp+json; profile=x; profile-version=1.0.0",
    "application/rpp+json; profile=x; profile-version=a",
])
def test_a_version_that_is_not_digits_point_digits_is_a_syntax_error(value):
    with pytest.raises(MediaRangeError) as error:
        one(value).profile()

    assert error.value.code.value[0] == "2005"


@pytest.mark.parametrize("value", [
    "application",                                   # no subtype
    "application/rpp+json; profile",                 # no value
    'application/rpp+json; profile="x',              # not closed
    "application/rpp+json; profile=a:b",             # a colon is no token character
    "application/rpp+json; q=1.5",
    "application/rpp+json; q=0.1234",
    "application/rpp+json; q=a",
    "application/rpp+json; profile=a; profile=b",    # twice
    "application/rpp+json; profile-version=1.0; profile-version=1.1",
])
def test_a_value_that_does_not_parse_is_a_syntax_error(value):
    with pytest.raises(MediaRangeError) as error:
        one(value)

    assert error.value.code.value[0] == "2005"


def test_a_content_type_has_no_weight():
    item = media_range.parse_media_type("application/rpp+json; q=0.5; charset=utf-8")

    assert item.quality == 1 and item.parameter("q") == "0.5"
