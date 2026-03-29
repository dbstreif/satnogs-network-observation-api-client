"""Pydantic models for SatNOGS Network API responses."""

import codecs
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests as _requests
from pydantic import BaseModel, ConfigDict, Field


def _decode_pretty_hex(binary_data: bytes) -> str:
    """Return binary data as hex dump: ``DE AD C0 DE``."""
    data = codecs.encode(binary_data, "hex").decode("ascii").upper()
    return " ".join(data[i : i + 2] for i in range(0, len(data), 2))


class DemodData(BaseModel):
    """Demodulated data frame from an observation."""

    payload_demod: Optional[str] = Field(None, description="URL to demodulated data file")

    def download(self, session: Optional[_requests.Session] = None) -> bytes:
        """Download the raw demodulated data as bytes.

        Args:
            session: Optional requests session. If not provided, a plain
                GET request is made.

        Returns:
            Raw bytes of the demodulated frame.

        Raises:
            ValueError: If no payload_demod URL is available.
            requests.HTTPError: If the download fails.
        """
        if not self.payload_demod:
            raise ValueError("No payload_demod URL available for this frame")
        if session:
            resp = session.get(self.payload_demod)
        else:
            resp = _requests.get(self.payload_demod)
        resp.raise_for_status()
        return resp.content

    def display_payload_hex(
        self, session: Optional[_requests.Session] = None
    ) -> str:
        """Download and return the frame as a pretty hex string.

        Returns format: ``DE AD C0 DE``

        Args:
            session: Optional requests session.

        Returns:
            Space-separated uppercase hex representation of the frame.
        """
        return _decode_pretty_hex(self.download(session))

    def display_payload_utf8(
        self, session: Optional[_requests.Session] = None
    ) -> str:
        """Download and return the frame decoded as UTF-8.

        Falls back to pretty hex if UTF-8 decoding fails.

        Args:
            session: Optional requests session.

        Returns:
            UTF-8 decoded string, or hex dump on decode failure.
        """
        payload = self.download(session)
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError:
            return _decode_pretty_hex(payload)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()


class Observation(BaseModel):
    """A satellite observation from the SatNOGS Network."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    ground_station: Optional[int] = None
    transmitter: Optional[str] = Field(None, description="Short transmitter UUID")
    transmitter_uuid: Optional[str] = None
    transmitter_description: Optional[str] = None
    transmitter_type: Optional[str] = None
    transmitter_uplink_low: Optional[int] = None
    transmitter_uplink_high: Optional[int] = None
    transmitter_uplink_drift: Optional[int] = None
    transmitter_downlink_low: Optional[int] = None
    transmitter_downlink_high: Optional[int] = None
    transmitter_downlink_drift: Optional[int] = None
    transmitter_mode: Optional[str] = None
    transmitter_invert: Optional[bool] = None
    transmitter_baud: Optional[float] = None
    transmitter_updated: Optional[datetime] = None
    transmitter_status: Optional[str] = None
    transmitter_unconfirmed: Optional[bool] = None
    center_frequency: Optional[int] = None
    observation_frequency: Optional[int] = None
    sat_id: Optional[str] = None
    norad_cat_id: Optional[int] = None
    tle0: Optional[str] = None
    tle1: Optional[str] = None
    tle2: Optional[str] = None
    tle_source: Optional[str] = None
    observer: Optional[str] = None
    client_version: Optional[str] = None
    client_metadata: Optional[str] = None
    status: Optional[str] = None
    vetted_status: Optional[str] = None
    vetted_user: Optional[int] = None
    vetted_datetime: Optional[datetime] = None
    waterfall: Optional[str] = None
    waterfall_status: Optional[str] = None
    waterfall_status_datetime: Optional[datetime] = None
    waterfall_status_user: Optional[int] = None
    payload: Optional[str] = None
    station_name: Optional[str] = None
    station_lat: Optional[float] = None
    station_lng: Optional[float] = None
    station_alt: Optional[int] = None
    rise_azimuth: Optional[float] = None
    max_altitude: Optional[float] = None
    set_azimuth: Optional[float] = None
    archived: Optional[bool] = None
    archive_url: Optional[str] = None
    demoddata: Optional[List[DemodData]] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()


class AntennaEntry(BaseModel):
    """Station antenna entry from the API."""

    frequency: Optional[int] = Field(None, description="Min frequency (Hz)")
    frequency_max: Optional[int] = Field(None, description="Max frequency (Hz)")
    band: Optional[str] = None
    antenna_type: Optional[str] = None
    antenna_type_name: Optional[str] = None


class Station(BaseModel):
    """A SatNOGS ground station."""

    id: int
    name: Optional[str] = None
    altitude: Optional[int] = None
    min_horizon: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    qthlocator: Optional[str] = None
    antenna: Optional[List[AntennaEntry]] = None
    created: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    status: Optional[str] = None
    observations: Optional[int] = None
    future_observations: Optional[int] = None
    description: Optional[str] = None
    client_version: Optional[str] = None
    target_utilization: Optional[int] = None
    image: Optional[str] = None
    success_rate: Optional[float] = None
    owner: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()


class TransmitterStats(BaseModel):
    """Transmitter observation statistics."""

    total_count: Optional[int] = None
    unknown_count: Optional[int] = None
    future_count: Optional[int] = None
    good_count: Optional[int] = None
    bad_count: Optional[int] = None
    unknown_rate: Optional[float] = None
    future_rate: Optional[float] = None
    success_rate: Optional[float] = None
    bad_rate: Optional[float] = None


class Transmitter(BaseModel):
    """A satellite transmitter with statistics."""

    uuid: str
    stats: Optional[TransmitterStats] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()
