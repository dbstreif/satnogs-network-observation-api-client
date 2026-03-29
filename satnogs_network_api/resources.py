"""API resource classes for SatNOGS Network endpoints."""

from datetime import datetime
from typing import Any, Dict, Optional, Union

import requests

from satnogs_network_api.models import Observation, Station, Transmitter
from satnogs_network_api.pagination import PageIterator


def _format_param(value: Any) -> Any:
    """Format parameter values for the API."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(value, bool):
        return str(value).lower()
    return value


def _build_params(**kwargs: Any) -> Dict[str, Any]:
    """Build query params dict, dropping None values."""
    return {k: _format_param(v) for k, v in kwargs.items() if v is not None}


class Observations:
    """SatNOGS Network Observations API.

    Provides read-only access to satellite observations.
    """

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self._session = session
        self._base_url = f"{base_url}/api/observations/"

    def list(
        self,
        *,
        status: Optional[str] = None,
        norad_cat_id: Optional[int] = None,
        sat_id: Optional[str] = None,
        transmitter_uuid: Optional[str] = None,
        transmitter_mode: Optional[str] = None,
        transmitter_type: Optional[str] = None,
        ground_station: Optional[int] = None,
        observer: Optional[str] = None,
        start: Optional[datetime] = None,
        start__lt: Optional[datetime] = None,
        end: Optional[datetime] = None,
        end__gt: Optional[datetime] = None,
        waterfall_status: Optional[bool] = None,
        observation_id: Optional[str] = None,
    ) -> PageIterator[Observation]:
        """List observations with optional filters.

        Args:
            status: Filter by status (good, bad, unknown, failed, future).
            norad_cat_id: Filter by NORAD catalog ID.
            sat_id: Filter by SatNOGS satellite ID.
            transmitter_uuid: Filter by transmitter UUID.
            transmitter_mode: Filter by transmitter mode (e.g. AFSK, BPSK, CW).
            transmitter_type: Filter by transmitter type (Transmitter, Transceiver, Transponder).
            ground_station: Filter by ground station ID.
            observer: Filter by observer username.
            start: Filter observations starting after this datetime.
            start__lt: Filter observations starting before this datetime.
            end: Filter observations ending after this datetime.
            end__gt: Filter observations ending after this datetime.
            waterfall_status: Filter by signal detection (True=with signal).
            observation_id: Comma-separated observation IDs.

        Returns:
            PageIterator yielding Observation instances.
        """
        params = _build_params(
            status=status,
            norad_cat_id=norad_cat_id,
            sat_id=sat_id,
            transmitter_uuid=transmitter_uuid,
            transmitter_mode=transmitter_mode,
            transmitter_type=transmitter_type,
            ground_station=ground_station,
            observer=observer,
            start=start,
            start__lt=start__lt,
            end=end,
            end__gt=end__gt,
            waterfall_status=waterfall_status,
            observation_id=observation_id,
        )
        return PageIterator(
            session=self._session,
            url=self._base_url,
            params=params,
            model=Observation,
        )

    def get(self, observation_id: int) -> Observation:
        """Retrieve a single observation by ID.

        Args:
            observation_id: The observation ID.

        Returns:
            An Observation instance.
        """
        url = f"{self._base_url}{observation_id}/"
        response = self._session.get(url)
        response.raise_for_status()
        return Observation.model_validate(response.json())


class Stations:
    """SatNOGS Network Stations API.

    Provides read-only access to ground stations.
    """

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self._session = session
        self._base_url = f"{base_url}/api/stations/"

    def list(
        self,
        *,
        status: Optional[str] = None,
        name: Optional[str] = None,
        id: Optional[int] = None,
        client_version: Optional[str] = None,
    ) -> PageIterator[Station]:
        """List ground stations with optional filters.

        Args:
            status: Filter by station status (online, testing, offline).
            name: Filter by station name.
            id: Filter by station ID.
            client_version: Filter by client version.

        Returns:
            PageIterator yielding Station instances.
        """
        params = _build_params(
            status=status,
            name=name,
            id=id,
            client_version=client_version,
        )
        return PageIterator(
            session=self._session,
            url=self._base_url,
            params=params,
            model=Station,
        )

    def get(self, station_id: int) -> Station:
        """Retrieve a single station by ID.

        Args:
            station_id: The station ID.

        Returns:
            A Station instance.
        """
        url = f"{self._base_url}{station_id}/"
        response = self._session.get(url)
        response.raise_for_status()
        return Station.model_validate(response.json())


class Transmitters:
    """SatNOGS Network Transmitters API.

    Provides read-only access to transmitter data with statistics.
    """

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self._session = session
        self._base_url = f"{base_url}/api/transmitters/"

    def list(self) -> PageIterator[Transmitter]:
        """List all transmitters with statistics.

        Returns:
            PageIterator yielding Transmitter instances.
        """
        return PageIterator(
            session=self._session,
            url=self._base_url,
            params={},
            model=Transmitter,
        )

    def get(self, uuid: str) -> Transmitter:
        """Retrieve a single transmitter by UUID.

        Args:
            uuid: The transmitter UUID.

        Returns:
            A Transmitter instance.
        """
        url = f"{self._base_url}{uuid}/"
        response = self._session.get(url)
        response.raise_for_status()
        return Transmitter.model_validate(response.json())
