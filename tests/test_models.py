"""Tests for pydantic models."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from satnogs_network_api.models import (
    AntennaEntry,
    DemodData,
    Observation,
    Station,
    Transmitter,
    TransmitterStats,
)

from tests.conftest import SAMPLE_OBSERVATION, SAMPLE_STATION, SAMPLE_TRANSMITTER


class TestObservation:
    def test_parse_full(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert obs.id == 13687665
        assert obs.norad_cat_id == 25544
        assert obs.status == "good"
        assert obs.transmitter_mode == "SSTV"
        assert obs.transmitter_downlink_low == 145800000
        assert obs.ground_station == 4680
        assert obs.station_lat == 36.717165
        assert obs.observer == "majesat"
        assert obs.sat_id == "XSKZ-5603-1870-9019-3066"
        assert obs.transmitter == "qW5N27QuSrN2JMasbNiUhR"
        assert obs.transmitter_uuid == "qW5N27QuSrN2JMasbNiUhR"
        assert obs.observation_frequency == 145800000

    def test_parse_datetime(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert isinstance(obs.start, datetime)
        assert isinstance(obs.end, datetime)
        assert isinstance(obs.transmitter_updated, datetime)

    def test_vetted_fields(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert obs.vetted_status == "good"
        assert obs.vetted_user is None

    def test_waterfall_status_is_string(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert obs.waterfall_status == "unknown"
        assert isinstance(obs.waterfall_status, str)

    def test_transmitter_status_is_string(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert obs.transmitter_status == "active"
        assert isinstance(obs.transmitter_status, str)

    def test_demoddata_nested(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert len(obs.demoddata) == 1
        assert "data.png" in obs.demoddata[0].payload_demod

    def test_tle_fields(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert obs.tle0 == "ISS"
        assert obs.tle1.startswith("1 25544U")
        assert obs.tle_source == "CalPoly"

    def test_to_dict(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        d = obs.to_dict()
        assert d["id"] == 13687665
        assert isinstance(d, dict)

    def test_to_json(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        j = obs.to_json()
        assert "13687665" in j

    def test_optional_fields_default_none(self):
        obs = Observation.model_validate({"id": 1})
        assert obs.transmitter_mode is None
        assert obs.center_frequency is None
        assert obs.demoddata is None
        assert obs.observer is None


class TestDemodData:
    def test_parse(self):
        dd = DemodData.model_validate(SAMPLE_OBSERVATION["demoddata"][0])
        assert "data.png" in dd.payload_demod

    def test_parse_minimal(self):
        dd = DemodData.model_validate({})
        assert dd.payload_demod is None

    def test_download(self):
        dd = DemodData.model_validate(SAMPLE_OBSERVATION["demoddata"][0])
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.content = b"\xDE\xAD\xC0\xDE"
        mock_resp.raise_for_status.return_value = None
        mock_session.get.return_value = mock_resp

        result = dd.download(session=mock_session)
        assert result == b"\xDE\xAD\xC0\xDE"
        mock_session.get.assert_called_once_with(dd.payload_demod)

    def test_download_no_url_raises(self):
        dd = DemodData.model_validate({})
        with pytest.raises(ValueError, match="No payload_demod URL"):
            dd.download()

    def test_download_no_session(self):
        dd = DemodData.model_validate(SAMPLE_OBSERVATION["demoddata"][0])
        mock_resp = MagicMock()
        mock_resp.content = b"\x01\x02"
        mock_resp.raise_for_status.return_value = None
        with patch("satnogs_network_api.models._requests.get", return_value=mock_resp) as mock_get:
            result = dd.download()
            assert result == b"\x01\x02"
            mock_get.assert_called_once_with(dd.payload_demod)

    def test_display_payload_hex(self):
        dd = DemodData.model_validate(SAMPLE_OBSERVATION["demoddata"][0])
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.content = b"\xDE\xAD\xC0\xDE"
        mock_resp.raise_for_status.return_value = None
        mock_session.get.return_value = mock_resp

        result = dd.display_payload_hex(session=mock_session)
        assert result == "DE AD C0 DE"

    def test_display_payload_utf8_success(self):
        dd = DemodData.model_validate(SAMPLE_OBSERVATION["demoddata"][0])
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.content = b"Hello, World!"
        mock_resp.raise_for_status.return_value = None
        mock_session.get.return_value = mock_resp

        result = dd.display_payload_utf8(session=mock_session)
        assert result == "Hello, World!"

    def test_display_payload_utf8_fallback_to_hex(self):
        dd = DemodData.model_validate(SAMPLE_OBSERVATION["demoddata"][0])
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.content = b"\xDE\xAD\xC0\xDE"
        mock_resp.raise_for_status.return_value = None
        mock_session.get.return_value = mock_resp

        result = dd.display_payload_utf8(session=mock_session)
        assert result == "DE AD C0 DE"


class TestStation:
    def test_parse_full(self):
        st = Station.model_validate(SAMPLE_STATION)
        assert st.id == 26
        assert st.name == "SV1IYO/A"
        assert st.lat == 38.395
        assert st.status == "Online"
        assert st.observations == 33526
        assert st.altitude == 145
        assert st.min_horizon == 15
        assert st.qthlocator == "KM08vj"
        assert st.success_rate == 76
        assert st.owner == "acinonyx"

    def test_antenna_nested(self):
        st = Station.model_validate(SAMPLE_STATION)
        assert len(st.antenna) == 1
        ant = st.antenna[0]
        assert isinstance(ant, AntennaEntry)
        assert ant.antenna_type == "turnstile"
        assert ant.frequency == 135000000
        assert ant.frequency_max == 148000000
        assert ant.band == "VHF"

    def test_to_dict(self):
        st = Station.model_validate(SAMPLE_STATION)
        d = st.to_dict()
        assert d["name"] == "SV1IYO/A"

    def test_optional_fields_default_none(self):
        st = Station.model_validate({"id": 1})
        assert st.name is None
        assert st.antenna is None
        assert st.owner is None


class TestTransmitter:
    def test_parse_full(self):
        tx = Transmitter.model_validate(SAMPLE_TRANSMITTER)
        assert tx.uuid == "MZgyEeYrdJsLnHCt3je6Ed"
        assert tx.stats is not None
        assert isinstance(tx.stats, TransmitterStats)

    def test_stats_fields(self):
        tx = Transmitter.model_validate(SAMPLE_TRANSMITTER)
        assert tx.stats.total_count == 6
        assert tx.stats.good_count == 0
        assert tx.stats.bad_count == 6
        assert tx.stats.success_rate == 0
        assert tx.stats.bad_rate == 100

    def test_to_dict(self):
        tx = Transmitter.model_validate(SAMPLE_TRANSMITTER)
        d = tx.to_dict()
        assert d["uuid"] == "MZgyEeYrdJsLnHCt3je6Ed"
        assert d["stats"]["total_count"] == 6

    def test_optional_fields_default_none(self):
        tx = Transmitter.model_validate({"uuid": "test"})
        assert tx.stats is None
