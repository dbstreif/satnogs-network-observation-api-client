"""Tests for pydantic models."""

from datetime import datetime

from satnogs_network_api.models import (
    Antenna,
    DemodData,
    FrequencyRange,
    Observation,
    Station,
    Transmitter,
)

from tests.conftest import SAMPLE_OBSERVATION, SAMPLE_STATION, SAMPLE_TRANSMITTER


class TestObservation:
    def test_parse_full(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert obs.id == 1001
        assert obs.norad_cat_id == 25544
        assert obs.status == "good"
        assert obs.transmitter_mode == "AFSK"
        assert obs.center_frequency == 437000000
        assert obs.ground_station == 42
        assert obs.station_lat == 40.0
        assert obs.author == "testuser"

    def test_parse_datetime(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert isinstance(obs.start, datetime)
        assert isinstance(obs.end, datetime)

    def test_demoddata_nested(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        assert len(obs.demoddata) == 1
        assert obs.demoddata[0].id == 500
        assert obs.demoddata[0].is_image is False

    def test_to_dict(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        d = obs.to_dict()
        assert d["id"] == 1001
        assert isinstance(d, dict)

    def test_to_json(self):
        obs = Observation.model_validate(SAMPLE_OBSERVATION)
        j = obs.to_json()
        assert '"id": 1001' in j or '"id":1001' in j

    def test_optional_fields_default_none(self):
        obs = Observation.model_validate({"id": 1})
        assert obs.transmitter_mode is None
        assert obs.center_frequency is None
        assert obs.demoddata is None


class TestDemodData:
    def test_parse(self):
        dd = DemodData.model_validate(SAMPLE_OBSERVATION["demoddata"][0])
        assert dd.id == 500
        assert dd.observation == 1001
        assert dd.is_image is False
        assert "demod.raw" in dd.payload_demod


class TestStation:
    def test_parse_full(self):
        st = Station.model_validate(SAMPLE_STATION)
        assert st.id == 42
        assert st.name == "Test Station"
        assert st.lat == 40.0
        assert st.status == "online"
        assert st.observations == 1500

    def test_antennas_nested(self):
        st = Station.model_validate(SAMPLE_STATION)
        assert len(st.antennas) == 1
        ant = st.antennas[0]
        assert isinstance(ant, Antenna)
        assert ant.antenna_type == "yagi"
        assert len(ant.frequency_ranges) == 1
        assert isinstance(ant.frequency_ranges[0], FrequencyRange)
        assert ant.frequency_ranges[0].min_frequency == 430000000

    def test_to_dict(self):
        st = Station.model_validate(SAMPLE_STATION)
        d = st.to_dict()
        assert d["name"] == "Test Station"

    def test_optional_fields_default_none(self):
        st = Station.model_validate({"id": 1})
        assert st.name is None
        assert st.antennas is None


class TestTransmitter:
    def test_parse_full(self):
        tx = Transmitter.model_validate(SAMPLE_TRANSMITTER)
        assert tx.uuid == "abc123"
        assert tx.mode == "AFSK"
        assert tx.downlink_low == 437000000
        assert tx.norad_cat_id == 25544
        assert tx.success_rate == 80.0
        assert tx.total_observations == 500

    def test_to_dict(self):
        tx = Transmitter.model_validate(SAMPLE_TRANSMITTER)
        d = tx.to_dict()
        assert d["uuid"] == "abc123"

    def test_optional_fields_default_none(self):
        tx = Transmitter.model_validate({"uuid": "test"})
        assert tx.mode is None
        assert tx.success_rate is None
