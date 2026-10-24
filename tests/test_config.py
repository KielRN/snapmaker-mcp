import pytest

from snapmaker_u1_mcp.config import Settings


def test_local_config_env_override_and_secrets_never_enter_repr(monkeypatch, tmp_path):
    config = tmp_path / "config.json"
    config.write_text('{"printer_url":"http://printer.invalid","timeout_seconds":2}')
    monkeypatch.setenv("U1_CONFIG_FILE", str(config))
    monkeypatch.setenv("U1_PRINTER_URL", "http://override.invalid:7125")
    monkeypatch.setenv("U1_API_KEY", "PRIVATE-KEY")
    settings = Settings.from_env()
    assert settings.printer_url == "http://override.invalid:7125"
    assert settings.timeout_seconds == 2
    assert settings.api_key == "PRIVATE-KEY"
    assert "PRIVATE-KEY" not in repr(settings)
    assert "override.invalid" not in repr(settings)


@pytest.mark.parametrize(
    "body",
    ["[]", '{"unknown":"SECRET"}', '{"printer_url":"SECRET"}', "{broken", '{"api_key":"SECRET"}'],
)
def test_invalid_local_config_does_not_echo_values(monkeypatch, tmp_path, body):
    config = tmp_path / "SECRET.json"
    config.write_text(body)
    monkeypatch.setenv("U1_CONFIG_FILE", str(config))
    monkeypatch.delenv("U1_PRINTER_URL", raising=False)
    with pytest.raises(ValueError) as error:
        Settings.from_env()
    assert "SECRET" not in str(error.value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout_seconds": 0},
        {"timeout_seconds": float("nan")},
        {"timeout_seconds": True},
        {"max_bytes": 1},
        {"api_key": "abc\nsecret"},
    ],
)
def test_invalid_limits_and_headers_fail_before_network(kwargs):
    with pytest.raises(ValueError):
        Settings(printer_url="http://printer.invalid", **kwargs)
