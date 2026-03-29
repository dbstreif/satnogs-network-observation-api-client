"""Tests for SatnogsNetworkClient."""

from unittest.mock import patch, MagicMock

from satnogs_network_api import SatnogsNetworkClient
from satnogs_network_api.resources import Observations, Stations, Transmitters


class TestClientInit:
    def test_default_base_url(self, client):
        assert client._base_url == "https://network.satnogs.org"

    def test_custom_base_url(self):
        with patch("satnogs_network_api.client.requests.Session") as mock_cls:
            mock_cls.return_value = MagicMock(headers={})
            c = SatnogsNetworkClient(base_url="https://custom.example.com/")
            assert c._base_url == "https://custom.example.com"

    def test_trailing_slash_stripped(self):
        with patch("satnogs_network_api.client.requests.Session") as mock_cls:
            mock_cls.return_value = MagicMock(headers={})
            c = SatnogsNetworkClient(base_url="https://example.com///")
            assert c._base_url == "https://example.com"

    def test_token_sets_auth_header(self):
        with patch("satnogs_network_api.client.requests.Session") as mock_cls:
            headers = {}
            mock_session = MagicMock()
            mock_session.headers = headers
            mock_cls.return_value = mock_session
            SatnogsNetworkClient(token="mytoken123")
            assert headers["Authorization"] == "Token mytoken123"

    def test_no_token_no_auth_header(self, client):
        assert "Authorization" not in client._mock_session.headers

    def test_accept_json_header(self, client):
        assert client._mock_session.headers["Accept"] == "application/json"

    def test_exposes_resources(self, client):
        assert isinstance(client.observations, Observations)
        assert isinstance(client.stations, Stations)
        assert isinstance(client.transmitters, Transmitters)


class TestClientContextManager:
    def test_context_manager_closes_session(self):
        with patch("satnogs_network_api.client.requests.Session") as mock_cls:
            mock_session = MagicMock(headers={})
            mock_cls.return_value = mock_session
            with SatnogsNetworkClient() as c:
                pass
            mock_session.close.assert_called_once()

    def test_close_method(self, client):
        client.close()
        client._mock_session.close.assert_called_once()
