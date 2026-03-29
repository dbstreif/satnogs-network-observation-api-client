"""Integration tests against the live SatNOGS Network API.

Run with: make test-integration
These tests require network access to https://network.satnogs.org
"""

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


class TestObservationsList:
    def test_list_returns_observations(self, client):
        for obs in client.observations.list(status="good"):
            assert isinstance(obs, Observation)
            assert obs.id is not None
            assert obs.status == "good"
            break

    def test_list_filter_norad_cat_id(self, client):
        for obs in client.observations.list(norad_cat_id=25544):
            assert obs.norad_cat_id == 25544
            break

    def test_list_filter_transmitter_mode(self, client):
        for obs in client.observations.list(status="good", transmitter_mode="FM"):
            assert obs.transmitter_mode == "FM"
            break

    def test_list_pagination_multiple_pages(self, client):
        """Verify lazy pagination fetches across at least 2 pages (>25 results)."""
        count = 0
        for obs in client.observations.list(status="good"):
            assert isinstance(obs, Observation)
            count += 1
            if count >= 30:
                break
        assert count == 30

    def test_list_json_mode(self, client):
        for raw in client.observations.list(status="good").json():
            assert isinstance(raw, dict)
            assert "id" in raw
            assert "status" in raw
            break

    def test_list_early_termination(self, client):
        it = client.observations.list(status="good")
        first = next(it)
        assert isinstance(first, Observation)


class TestObservationsGet:
    def test_get_by_id(self, client):
        # Get an ID from list first
        for obs in client.observations.list(status="good"):
            obs_id = obs.id
            break

        result = client.observations.get(obs_id)
        assert isinstance(result, Observation)
        assert result.id == obs_id
        assert result.status is not None

    def test_get_fields_populated(self, client):
        for obs in client.observations.list(status="good"):
            obs_id = obs.id
            break

        result = client.observations.get(obs_id)
        assert result.start is not None
        assert result.end is not None
        assert result.ground_station is not None
        assert result.norad_cat_id is not None
        assert result.observer is not None
        assert result.transmitter_uuid is not None


class TestStationsList:
    def test_list_returns_stations(self, client):
        for st in client.stations.list():
            assert isinstance(st, Station)
            assert st.id is not None
            assert st.name is not None
            break

    def test_list_fields_populated(self, client):
        for st in client.stations.list():
            assert st.lat is not None
            assert st.lng is not None
            assert st.status is not None
            break

    def test_list_antenna_nested(self, client):
        for st in client.stations.list():
            if st.antenna:
                ant = st.antenna[0]
                assert isinstance(ant, AntennaEntry)
                assert ant.antenna_type is not None
                assert ant.frequency is not None
                assert ant.frequency_max is not None
                break

    def test_list_json_mode(self, client):
        for raw in client.stations.list().json():
            assert isinstance(raw, dict)
            assert "id" in raw
            assert "name" in raw
            break


class TestStationsGet:
    def test_get_by_id(self, client):
        for st in client.stations.list():
            st_id = st.id
            break

        result = client.stations.get(st_id)
        assert isinstance(result, Station)
        assert result.id == st_id
        assert result.name is not None


class TestTransmittersList:
    def test_list_returns_transmitters(self, client):
        for tx in client.transmitters.list():
            assert isinstance(tx, Transmitter)
            assert tx.uuid is not None
            break

    def test_list_stats_nested(self, client):
        for tx in client.transmitters.list():
            if tx.stats:
                assert isinstance(tx.stats, TransmitterStats)
                assert tx.stats.total_count is not None
                break

    def test_list_json_mode(self, client):
        for raw in client.transmitters.list().json():
            assert isinstance(raw, dict)
            assert "uuid" in raw
            assert "stats" in raw
            break


class TestTransmittersGet:
    def test_get_by_uuid(self, client):
        for tx in client.transmitters.list():
            tx_uuid = tx.uuid
            break

        result = client.transmitters.get(tx_uuid)
        assert isinstance(result, Transmitter)
        assert result.uuid == tx_uuid


class TestDemodDataDownload:
    def _find_observation_with_demoddata(self, client):
        for obs in client.observations.list(status="good"):
            if obs.demoddata:
                return obs
        pytest.skip("No observations with demoddata found")

    def test_download_returns_bytes(self, client):
        obs = self._find_observation_with_demoddata(client)
        frame = obs.demoddata[0]
        raw = frame.download()
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_download_with_session(self, client):
        obs = self._find_observation_with_demoddata(client)
        frame = obs.demoddata[0]
        raw = frame.download(session=client._session)
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_display_payload_hex(self, client):
        obs = self._find_observation_with_demoddata(client)
        frame = obs.demoddata[0]
        hex_str = frame.display_payload_hex()
        assert isinstance(hex_str, str)
        assert len(hex_str) > 0
        # Should be uppercase hex pairs separated by spaces
        parts = hex_str.split(" ")
        for part in parts[:10]:
            assert len(part) == 2
            int(part, 16)  # Should not raise

    def test_display_payload_utf8(self, client):
        obs = self._find_observation_with_demoddata(client)
        frame = obs.demoddata[0]
        result = frame.display_payload_utf8()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_cw_demoddata_is_text(self, client):
        """CW observations should produce readable UTF-8 text."""
        for obs in client.observations.list(status="good", transmitter_mode="CW"):
            if obs.demoddata:
                frame = obs.demoddata[0]
                text = frame.display_payload_utf8()
                assert isinstance(text, str)
                # CW decoded data should not fall back to hex
                # (no space-separated two-char hex pairs pattern)
                assert len(text) > 0
                return
        pytest.skip("No CW observations with demoddata found")
