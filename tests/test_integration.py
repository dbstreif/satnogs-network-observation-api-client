"""Integration tests against the live SatNOGS Network API.

Run with: make test-integration
These tests require network access to https://network.satnogs.org

Rate limits (anonymous):
  - Observations: 60 requests/hour
  - Stations: 256 requests/hour
  - Transmitters: no known limit

Tests are structured to minimize API calls by sharing fetched data
via module-scoped fixtures.
"""

import time

import pytest

from satnogs_network_api import (
    SatnogsNetworkClient,
    Observation,
    Station,
    Transmitter,
    DemodData,
    AntennaEntry,
    TransmitterStats,
)


@pytest.fixture(scope="module")
def client():
    c = SatnogsNetworkClient()
    yield c
    c.close()


@pytest.fixture(scope="module")
def good_observations(client):
    """Fetch a page of good observations once, reuse across tests."""
    results = []
    for obs in client.observations.list(status="good"):
        results.append(obs)
        if len(results) >= 5:
            break
    return results


@pytest.fixture(scope="module")
def observation_with_demoddata(client):
    """Fetch one observation that has demoddata."""
    time.sleep(2)
    for obs in client.observations.list(status="good"):
        if obs.demoddata:
            return obs
    pytest.skip("No observations with demoddata found")


@pytest.fixture(scope="module")
def cw_observation_with_demoddata(client):
    """Fetch one CW observation that has demoddata."""
    time.sleep(2)
    for obs in client.observations.list(status="good", transmitter_mode="CW"):
        if obs.demoddata:
            return obs
    pytest.skip("No CW observations with demoddata found")


@pytest.fixture(scope="module")
def stations_page(client):
    """Fetch a few stations once."""
    results = []
    for st in client.stations.list():
        results.append(st)
        if len(results) >= 5:
            break
    return results


@pytest.fixture(scope="module")
def transmitters_page(client):
    """Fetch a few transmitters once."""
    results = []
    for tx in client.transmitters.list():
        results.append(tx)
        if len(results) >= 5:
            break
    return results


# --- Observations ---


class TestObservationsList:
    def test_list_returns_observations(self, good_observations):
        assert len(good_observations) > 0
        obs = good_observations[0]
        assert isinstance(obs, Observation)
        assert obs.id is not None
        assert obs.status is not None

    def test_list_filter_norad_cat_id(self, client):
        time.sleep(2)
        for obs in client.observations.list(norad_cat_id=25544):
            assert obs.norad_cat_id == 25544
            break

    def test_list_filter_transmitter_mode(self, client):
        time.sleep(2)
        for obs in client.observations.list(transmitter_mode="FM"):
            assert obs.transmitter_mode == "FM"
            break

    def test_list_pagination_multiple_pages(self, client):
        """Verify lazy pagination fetches across at least 2 pages (>25 results)."""
        time.sleep(2)
        count = 0
        for obs in client.observations.list(status="good"):
            assert isinstance(obs, Observation)
            count += 1
            if count >= 30:
                break
        assert count == 30

    def test_list_json_mode(self, good_observations, client):
        time.sleep(2)
        for raw in client.observations.list(status="good").json():
            assert isinstance(raw, dict)
            assert "id" in raw
            assert "status" in raw
            break

    def test_list_early_termination(self, good_observations):
        obs = good_observations[0]
        assert isinstance(obs, Observation)


class TestObservationsGet:
    def test_get_by_id(self, client, good_observations):
        time.sleep(2)
        obs_id = good_observations[0].id
        result = client.observations.get(obs_id)
        assert isinstance(result, Observation)
        assert result.id == obs_id
        assert result.status is not None

    def test_get_fields_populated(self, client, good_observations):
        time.sleep(2)
        obs_id = good_observations[0].id
        result = client.observations.get(obs_id)
        assert result.start is not None
        assert result.end is not None
        assert result.ground_station is not None
        assert result.norad_cat_id is not None
        assert result.observer is not None
        assert result.transmitter_uuid is not None


# --- Stations ---


class TestStationsList:
    def test_list_returns_stations(self, stations_page):
        assert len(stations_page) > 0
        st = stations_page[0]
        assert isinstance(st, Station)
        assert st.id is not None
        assert st.name is not None

    def test_list_fields_populated(self, stations_page):
        st = stations_page[0]
        assert st.lat is not None
        assert st.lng is not None
        assert st.status is not None

    def test_list_antenna_nested(self, stations_page):
        for st in stations_page:
            if st.antenna:
                ant = st.antenna[0]
                assert isinstance(ant, AntennaEntry)
                assert ant.antenna_type is not None
                assert ant.frequency is not None
                assert ant.frequency_max is not None
                return
        pytest.skip("No stations with antennas in sample")

    def test_list_json_mode(self, client):
        for raw in client.stations.list().json():
            assert isinstance(raw, dict)
            assert "id" in raw
            assert "name" in raw
            break


class TestStationsGet:
    def test_get_by_id(self, client, stations_page):
        st_id = stations_page[0].id
        result = client.stations.get(st_id)
        assert isinstance(result, Station)
        assert result.id == st_id
        assert result.name is not None


# --- Transmitters ---


class TestTransmittersList:
    def test_list_returns_transmitters(self, transmitters_page):
        assert len(transmitters_page) > 0
        tx = transmitters_page[0]
        assert isinstance(tx, Transmitter)
        assert tx.uuid is not None

    def test_list_stats_nested(self, transmitters_page):
        for tx in transmitters_page:
            if tx.stats:
                assert isinstance(tx.stats, TransmitterStats)
                assert tx.stats.total_count is not None
                return
        pytest.skip("No transmitters with stats in sample")

    def test_list_json_mode(self, client):
        for raw in client.transmitters.list().json():
            assert isinstance(raw, dict)
            assert "uuid" in raw
            assert "stats" in raw
            break


class TestTransmittersGet:
    def test_get_by_uuid(self, client, transmitters_page):
        tx_uuid = transmitters_page[0].uuid
        result = client.transmitters.get(tx_uuid)
        assert isinstance(result, Transmitter)
        assert result.uuid == tx_uuid


# --- DemodData ---


class TestDemodDataDownload:
    def test_download_returns_bytes(self, observation_with_demoddata):
        frame = observation_with_demoddata.demoddata[0]
        raw = frame.download()
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_download_with_session(self, client, observation_with_demoddata):
        frame = observation_with_demoddata.demoddata[0]
        raw = frame.download(session=client._session)
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_display_payload_hex(self, observation_with_demoddata):
        frame = observation_with_demoddata.demoddata[0]
        hex_str = frame.display_payload_hex()
        assert isinstance(hex_str, str)
        assert len(hex_str) > 0
        parts = hex_str.split(" ")
        for part in parts[:10]:
            assert len(part) == 2
            int(part, 16)

    def test_display_payload_utf8(self, observation_with_demoddata):
        frame = observation_with_demoddata.demoddata[0]
        result = frame.display_payload_utf8()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_cw_demoddata_is_text(self, cw_observation_with_demoddata):
        frame = cw_observation_with_demoddata.demoddata[0]
        text = frame.display_payload_utf8()
        assert isinstance(text, str)
        assert len(text) > 0
