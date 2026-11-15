import pytest

from settings.load_settings import load_settings


def write(tmp_path, extra=""):
    path = tmp_path / "c.yaml"
    path.write_text("rpp_epp_host: h\n" + extra)
    return str(path)


def test_the_signalling_is_the_header_without_the_key(tmp_path):
    assert load_settings(write(tmp_path)).profile_signalling == "header"


def test_the_header_can_be_named(tmp_path):
    assert load_settings(write(tmp_path, "rpp_profile_signalling: header\n")).profile_signalling == "header"


@pytest.mark.parametrize("value", ["media-type", "cookie"])
def test_a_method_that_is_not_implemented_or_unknown_stops_the_server(tmp_path, value):
    with pytest.raises(ValueError, match="rpp_profile_signalling"):
        load_settings(write(tmp_path, f"rpp_profile_signalling: {value}\n"))


@pytest.mark.parametrize("config", ["config.yaml", "config.rri-mtest.yaml"])
def test_the_configs_of_the_test_environments_use_the_header(config):
    assert load_settings(config).profile_signalling == "header"
