"""Shared test fixtures."""

import json
from unittest.mock import MagicMock, patch

import pytest

from satnogs_network_api import SatnogsNetworkClient


SAMPLE_OBSERVATION = {
    "id": 1001,
    "start": "2026-03-01T12:00:00Z",
    "end": "2026-03-01T12:10:00Z",
    "ground_station": 42,
    "sat_id": "XXXX-YYYY-ZZZZ",
    "norad_cat_id": 25544,
    "status": "good",
    "transmitter_uuid": "abc123",
    "transmitter_description": "UHF 9k6 AFSK Telemetry",
    "transmitter_type": "Transmitter",
    "transmitter_mode": "AFSK",
    "transmitter_downlink_low": 437000000,
    "transmitter_downlink_high": None,
    "transmitter_baud": 9600.0,
    "center_frequency": 437000000,
    "station_name": "Test Station",
    "station_lat": 40.0,
    "station_lng": -74.0,
    "station_alt": 50,
    "waterfall": "https://network.satnogs.org/media/waterfall.png",
    "waterfall_status": True,
    "payload": "https://network.satnogs.org/media/audio.ogg",
    "archived": False,
    "author": "testuser",
    "demoddata": [
        {
            "id": 500,
            "observation": 1001,
            "payload_demod": "https://network.satnogs.org/media/demod.raw",
            "is_image": False,
        }
    ],
}

SAMPLE_STATION = {
    "id": 42,
    "name": "Test Station",
    "lat": 40.0,
    "lng": -74.0,
    "alt": 50,
    "status": "online",
    "client_version": "1.8.1",
    "last_seen": "2026-03-29T10:00:00Z",
    "created": "2020-01-01T00:00:00Z",
    "is_available": True,
    "testing": False,
    "description": "A test ground station",
    "observations": 1500,
    "target_utilization": 80,
    "antennas": [
        {
            "antenna_type": "yagi",
            "antenna_type_name": "Yagi",
            "frequency_ranges": [
                {"min_frequency": 430000000, "max_frequency": 440000000}
            ],
        }
    ],
}

SAMPLE_TRANSMITTER = {
    "uuid": "abc123",
    "description": "UHF 9k6 AFSK Telemetry",
    "alive": True,
    "type": "Transmitter",
    "downlink_low": 437000000,
    "downlink_high": None,
    "mode": "AFSK",
    "mode_id": 1,
    "baud": 9600.0,
    "sat_id": "XXXX-YYYY-ZZZZ",
    "norad_cat_id": 25544,
    "status": "active",
    "updated": "2026-03-01T00:00:00Z",
    "total_observations": 500,
    "good_observations": 400,
    "bad_observations": 50,
    "unknown_observations": 50,
    "future_observations": 0,
    "success_rate": 80.0,
}


def make_paginated_response(results, next_url=None):
    """Build a paginated API response dict."""
    return {"next": next_url, "previous": None, "results": results}


def mock_response(data, status_code=200):
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = data
    resp.raise_for_status.return_value = None
    return resp


@pytest.fixture
def client():
    """Return a SatnogsNetworkClient with a mocked session."""
    with patch("satnogs_network_api.client.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session
        c = SatnogsNetworkClient()
        c._mock_session = mock_session
        yield c
