"""Shared test fixtures."""

from unittest.mock import MagicMock, patch

import pytest

from satnogs_network_api import SatnogsNetworkClient


SAMPLE_OBSERVATION = {
    "id": 13687665,
    "start": "2026-03-29T19:08:44Z",
    "end": "2026-03-29T19:17:16Z",
    "ground_station": 4680,
    "transmitter": "qW5N27QuSrN2JMasbNiUhR",
    "norad_cat_id": 25544,
    "payload": "https://network-satnogs.freetls.fastly.net/media/data_obs/2026/3/29/19/13687665/satnogs_13687665.ogg",
    "waterfall": "https://s3.eu-central-1.wasabisys.com/satnogs-network/data_obs/2026/3/29/19/13687665/waterfall.png",
    "demoddata": [
        {
            "payload_demod": "https://s3.eu-central-1.wasabisys.com/satnogs-network/data_obs/2026/3/29/19/13687665/data.png",
        }
    ],
    "station_name": "MAJESAT",
    "station_lat": 36.717165,
    "station_lng": -4.464836,
    "station_alt": 95,
    "vetted_status": "good",
    "vetted_user": None,
    "vetted_datetime": None,
    "archived": False,
    "archive_url": None,
    "client_version": "1.8.1",
    "client_metadata": "{}",
    "status": "good",
    "waterfall_status": "unknown",
    "waterfall_status_user": None,
    "waterfall_status_datetime": None,
    "rise_azimuth": 317.0,
    "set_azimuth": 118.0,
    "max_altitude": 50.0,
    "transmitter_uuid": "qW5N27QuSrN2JMasbNiUhR",
    "transmitter_description": "Mode V Imaging",
    "transmitter_type": "Transmitter",
    "transmitter_uplink_low": None,
    "transmitter_uplink_high": None,
    "transmitter_uplink_drift": None,
    "transmitter_downlink_low": 145800000,
    "transmitter_downlink_high": None,
    "transmitter_downlink_drift": None,
    "transmitter_mode": "SSTV",
    "transmitter_invert": False,
    "transmitter_baud": 0.0,
    "transmitter_updated": "2025-10-02T07:54:48.115415Z",
    "transmitter_status": "active",
    "transmitter_unconfirmed": False,
    "tle0": "ISS",
    "tle1": "1 25544U 98067A   26088.13267411  .00012260  00000-0  23326-3 0  9999",
    "tle2": "2 25544  51.6344 336.2407 0006215 245.2164 114.8178 15.48624340559341",
    "tle_source": "CalPoly",
    "center_frequency": None,
    "observer": "majesat",
    "observation_frequency": 145800000,
    "sat_id": "XSKZ-5603-1870-9019-3066",
}

SAMPLE_STATION = {
    "id": 26,
    "name": "SV1IYO/A",
    "altitude": 145,
    "min_horizon": 15,
    "lat": 38.395,
    "lng": 21.828,
    "qthlocator": "KM08vj",
    "antenna": [
        {
            "frequency": 135000000,
            "frequency_max": 148000000,
            "band": "VHF",
            "antenna_type": "turnstile",
            "antenna_type_name": "Turnstile",
        }
    ],
    "created": "2017-10-11T21:19:49Z",
    "last_seen": "2026-03-29T21:15:34Z",
    "status": "Online",
    "observations": 33526,
    "future_observations": 0,
    "description": "",
    "client_version": "2.1.1",
    "target_utilization": 100,
    "image": "https://network-satnogs.freetls.fastly.net/media/ground_stations/station.jpg",
    "success_rate": 76,
    "owner": "acinonyx",
}

SAMPLE_TRANSMITTER = {
    "uuid": "MZgyEeYrdJsLnHCt3je6Ed",
    "stats": {
        "total_count": 6,
        "unknown_count": 0,
        "future_count": 0,
        "good_count": 0,
        "bad_count": 6,
        "unknown_rate": 0,
        "future_rate": 0,
        "success_rate": 0,
        "bad_rate": 100,
    },
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
    resp.headers = {}
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
