"""The media ranges of Accept and the media type of Content-Type, as core §14.3 reads them."""
from decimal import Decimal

import pytest

from rpp.http import media_range
from rpp.http.media_range_error import MediaRangeError

URN = "urn:ietf:params:rpp:preset:base"


def one(value):
    [item] = media_range.parse_accept([value])
    return item


def test_a_quoted_and_a_token_value_are_the_same():
    assert one(f'application/rpp+json; preset="{URN}"; preset-version="1.0"').preset() == (URN, Decimal("1.0"))
    assert one("application/rpp+json; preset=de.denic.rpp.preset.rri; preset-version=1.0").preset() \
        == ("de.denic.rpp.preset.rri", Decimal("1.0"))


def test_names_are_not_case_sensitive_and_a_quoted_pair_is_unescaped():
    assert one('Application/RPP+json; PRESET="a\\"b"; Preset-Version=1.0').preset() == ('a"b', Decimal("1.0"))


def test_the_weight_ends_the_media_type_parameters_and_commas_in_quotes_do_not_split():
    items = media_range.parse_accept(['application/rpp+json; preset="a,b"; preset-version=1.0; q=0.5; x=1, */*;q=0'])

    assert [item.kind for item in items] == ["application/rpp+json", "*/*"]
    assert items[0].quality == Decimal("0.5") and items[1].quality == 0
    assert items[0].preset() == ("a,b", Decimal("1.0"))


def test_a_range_without_the_parameters_names_no_profile():
    assert one("application/rpp+json").preset() is None
    assert one("application/rpp+json").quality == 1


def test_field_lines_are_joined():
    assert [item.kind for item in media_range.parse_accept(["text/html", " , application/*;q=0.1"])] \
        == ["text/html", "application/*"]


@pytest.mark.parametrize("value", ["application/rpp+json; preset=x", "application/rpp+json; preset-version=1.0"])
def test_a_profile_without_its_version_or_the_reverse_is_a_missing_parameter(value):
    with pytest.raises(MediaRangeError) as error:
        one(value).preset()

    assert error.value.code.value[0] == "2003"


@pytest.mark.parametrize("value", [
    "application/rpp+json; preset=x; preset-version=1",        # the ABNF requires a point
    "application/rpp+json; preset=x; preset-version=1.0.0",
    "application/rpp+json; preset=x; preset-version=a",
])
def test_a_version_that_is_not_digits_point_digits_is_a_syntax_error(value):
    with pytest.raises(MediaRangeError) as error:
        one(value).preset()

    assert error.value.code.value[0] == "2005"


@pytest.mark.parametrize("value", [
    "application",                                   # no subtype
    "application/rpp+json; preset",                 # no value
    'application/rpp+json; preset="x',              # not closed
    "application/rpp+json; preset=a:b",             # a colon is no token character
    "application/rpp+json; q=1.5",
    "application/rpp+json; q=0.1234",
    "application/rpp+json; q=a",
    "application/rpp+json; preset=a; preset=b",    # twice
    "application/rpp+json; preset-version=1.0; preset-version=1.1",
])
def test_a_value_that_does_not_parse_is_a_syntax_error(value):
    with pytest.raises(MediaRangeError) as error:
        one(value)

    assert error.value.code.value[0] == "2005"


def test_a_content_type_has_no_weight():
    item = media_range.parse_media_type("application/rpp+json; q=0.5; charset=utf-8")

    assert item.quality == 1 and item.parameter("q") == "0.5"


def test_a_range_of_another_media_type_only_has_to_split():
    items = media_range.parse_accept(["application/ld+json; preset=a; preset=b; q=x, application/rpp+json"])

    assert [item.kind for item in items] == ["application/ld+json", "application/rpp+json"]


def test_a_quote_that_is_not_closed_in_another_media_type_is_still_refused():
    with pytest.raises(MediaRangeError) as error:
        media_range.parse_accept(['text/html; x="a, application/rpp+json'])

    assert error.value.code.value[0] == "2005"


def test_an_empty_accept_has_no_ranges():
    assert media_range.parse_accept([""]) == [] == media_range.parse_accept([])
