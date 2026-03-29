# API Reference

## SatnogsNetworkClient

The main entry point. Creates an HTTP session and exposes resource attributes.

```python
from satnogs_network_api import SatnogsNetworkClient

# Default (public, https://network.satnogs.org)
client = SatnogsNetworkClient()

# With authentication
client = SatnogsNetworkClient(token="your-api-token")

# Custom instance
client = SatnogsNetworkClient(base_url="https://network-dev.satnogs.org")

# Context manager (auto-closes session)
with SatnogsNetworkClient() as client:
    obs = client.observations.get(12345)
```

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `observations` | `Observations` | Observation endpoint methods |
| `stations` | `Stations` | Station endpoint methods |
| `transmitters` | `Transmitters` | Transmitter endpoint methods |

### Methods

| Method | Description |
|---|---|
| `close()` | Close the underlying HTTP session |

---

## Observations

### `observations.list(**filters)`

List observations with optional filters. Returns a lazy `PageIterator[Observation]` that fetches pages on demand.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `status` | `str` | Observation status: `good`, `bad`, `unknown`, `failed`, `future` |
| `norad_cat_id` | `int` | NORAD catalog ID |
| `sat_id` | `str` | SatNOGS satellite ID |
| `transmitter_uuid` | `str` | Transmitter UUID |
| `transmitter_mode` | `str` | Transmitter mode (e.g. `AFSK`, `BPSK`, `CW`, `FM`) |
| `transmitter_type` | `str` | `Transmitter`, `Transceiver`, `Transponder` |
| `ground_station` | `int` | Ground station ID |
| `observer` | `str` | Observer username |
| `start` | `datetime` | Observations starting after this time |
| `start__lt` | `datetime` | Observations starting before this time |
| `end` | `datetime` | Observations ending after this time |
| `end__gt` | `datetime` | Observations ending after this time |
| `waterfall_status` | `bool` | `True` for signal detected, `False` for no signal |
| `observation_id` | `str` | Comma-separated observation IDs |

All parameters are optional and keyword-only.

**Examples:**

```python
from datetime import datetime
from satnogs_network_api import SatnogsNetworkClient

client = SatnogsNetworkClient()

# Good observations for the ISS
for obs in client.observations.list(status="good", norad_cat_id=25544):
    print(obs.id, obs.start, obs.transmitter_mode)

# Filter by mode and time range
for obs in client.observations.list(
    transmitter_mode="AFSK",
    start=datetime(2026, 1, 1),
    start__lt=datetime(2026, 2, 1),
):
    print(obs.id, obs.center_frequency)

# Filter by ground station with signal detection
for obs in client.observations.list(
    ground_station=123,
    waterfall_status=True,
    status="good",
):
    print(obs.id, obs.station_name)

# Get raw dicts instead of model instances
for raw in client.observations.list(status="good", norad_cat_id=25544).json():
    print(raw["id"], raw["transmitter_mode"])

# Stop early (only fetches pages as needed)
for i, obs in enumerate(client.observations.list(status="good")):
    if i >= 10:
        break
    print(obs.id)
```

### `observations.get(observation_id)`

Retrieve a single observation by ID.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `observation_id` | `int` | The observation ID (required) |

**Returns:** `Observation`

**Example:**

```python
obs = client.observations.get(12345)
print(obs.id)
print(obs.sat_id)
print(obs.status)
print(obs.transmitter_mode)
print(obs.center_frequency)
print(obs.station_lat, obs.station_lng)
print(obs.demoddata)  # list of DemodData
```

---

## Stations

### `stations.list(**filters)`

List ground stations with optional filters. Returns a lazy `PageIterator[Station]`.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `status` | `str` | Station status: `online`, `testing`, `offline` |
| `name` | `str` | Station name |
| `id` | `int` | Station ID |
| `client_version` | `str` | Client software version |

All parameters are optional and keyword-only.

**Examples:**

```python
# All online stations
for station in client.stations.list(status="online"):
    print(station.id, station.name, station.lat, station.lng)

# Raw dicts
for raw in client.stations.list(status="online").json():
    print(raw["name"])
```

### `stations.get(station_id)`

Retrieve a single station by ID.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `station_id` | `int` | The station ID (required) |

**Returns:** `Station`

**Example:**

```python
station = client.stations.get(123)
print(station.name)
print(station.lat, station.lng, station.alt)
print(station.status)
print(station.antennas)
```

---

## Transmitters

### `transmitters.list()`

List all transmitters with observation statistics. Returns a lazy `PageIterator[Transmitter]`.

**Example:**

```python
for tx in client.transmitters.list():
    print(tx.uuid, tx.description, tx.mode, tx.downlink_low)
    print(f"  Success rate: {tx.success_rate}")

# Raw dicts
for raw in client.transmitters.list().json():
    print(raw["uuid"], raw["description"])
```

### `transmitters.get(uuid)`

Retrieve a single transmitter by UUID.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `uuid` | `str` | The transmitter UUID (required) |

**Returns:** `Transmitter`

**Example:**

```python
tx = client.transmitters.get("abcd-1234-efgh-5678")
print(tx.description)
print(tx.mode)
print(tx.downlink_low, tx.downlink_high)
print(tx.total_observations, tx.success_rate)
```

---

## PageIterator

All `.list()` methods return a `PageIterator`. It fetches pages lazily (25 items per page) as you iterate.

### Methods

| Method | Returns | Description |
|---|---|---|
| `__iter__()` | `PageIterator[T]` | Iterate yielding model instances |
| `__next__()` | `T` | Get next model instance |
| `.json()` | `PageIterator` | Returns a new iterator that yields raw dicts |

**Examples:**

```python
# Typed iteration (default)
for obs in client.observations.list(status="good"):
    print(obs.id, obs.transmitter_mode)  # Observation instance

# Raw dict iteration
for raw in client.observations.list(status="good").json():
    print(raw["id"], raw["transmitter_mode"])  # plain dict

# Early termination (efficient - stops fetching pages)
iterator = client.observations.list(status="good")
first = next(iterator)
print(first.id)
```

---

## Models

All models are Pydantic `BaseModel` subclasses with `.to_dict()` and `.to_json()` methods.

### Observation

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Observation ID |
| `start` | `datetime` | Observation start time |
| `end` | `datetime` | Observation end time |
| `ground_station` | `int` | Ground station ID |
| `sat_id` | `str` | SatNOGS satellite ID |
| `norad_cat_id` | `int` | NORAD catalog ID |
| `status` | `str` | Observation status |
| `transmitter_uuid` | `str` | Transmitter UUID |
| `transmitter_description` | `str` | Transmitter description |
| `transmitter_type` | `str` | Transmitter type |
| `transmitter_mode` | `str` | Transmitter mode |
| `transmitter_baud` | `float` | Baud rate |
| `transmitter_uplink_low` | `int` | Uplink low frequency (Hz) |
| `transmitter_uplink_high` | `int` | Uplink high frequency (Hz) |
| `transmitter_downlink_low` | `int` | Downlink low frequency (Hz) |
| `transmitter_downlink_high` | `int` | Downlink high frequency (Hz) |
| `center_frequency` | `int` | Center frequency (Hz) |
| `station_name` | `str` | Station name |
| `station_lat` | `float` | Station latitude |
| `station_lng` | `float` | Station longitude |
| `station_alt` | `int` | Station altitude (m) |
| `waterfall` | `str` | Waterfall image URL |
| `waterfall_status` | `bool` | Signal detected |
| `payload` | `str` | Audio payload URL |
| `archived` | `bool` | Whether archived |
| `archive_url` | `str` | Archive.org URL |
| `demoddata` | `list[DemodData]` | Demodulated data frames |
| `author` | `str` | Observer username |
| `rise_azimuth` | `float` | Rise azimuth (degrees) |
| `max_altitude` | `float` | Max altitude (degrees) |
| `set_azimuth` | `float` | Set azimuth (degrees) |

### DemodData

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Demod data ID |
| `observation` | `int` | Parent observation ID |
| `payload_demod` | `str` | URL to demodulated data file |
| `is_image` | `bool` | Whether the frame is an image |

#### `demoddata.download(session=None)`

Download the raw demodulated data as bytes.

| Parameter | Type | Description |
|---|---|---|
| `session` | `requests.Session` | Optional session (uses the client's session for auth, or a plain GET if omitted) |

**Returns:** `bytes`

**Example:**

```python
obs = client.observations.get(12345)
for frame in obs.demoddata:
    raw_bytes = frame.download(session=client._session)
    print(len(raw_bytes), "bytes")
```

#### `demoddata.display_payload_hex(session=None)`

Download and return the frame as a pretty hex string (e.g. `DE AD C0 DE`).

| Parameter | Type | Description |
|---|---|---|
| `session` | `requests.Session` | Optional session |

**Returns:** `str`

**Example:**

```python
obs = client.observations.get(12345)
for frame in obs.demoddata:
    print(frame.display_payload_hex(session=client._session))
    # Output: DE AD BE EF 01 02 03 ...
```

#### `demoddata.display_payload_utf8(session=None)`

Download and return the frame decoded as UTF-8. Falls back to pretty hex if UTF-8 decoding fails.

| Parameter | Type | Description |
|---|---|---|
| `session` | `requests.Session` | Optional session |

**Returns:** `str`

**Example:**

```python
obs = client.observations.get(12345)
for frame in obs.demoddata:
    text = frame.display_payload_utf8(session=client._session)
    print(text)
    # Output: readable text if UTF-8, or "DE AD C0 DE" hex fallback
```

### Station

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Station ID |
| `name` | `str` | Station name |
| `lat` | `float` | Latitude |
| `lng` | `float` | Longitude |
| `alt` | `int` | Altitude (m) |
| `status` | `str` | Station status |
| `client_version` | `str` | Client software version |
| `last_seen` | `datetime` | Last heartbeat time |
| `created` | `datetime` | Station creation time |
| `is_available` | `bool` | Whether available for scheduling |
| `testing` | `bool` | Whether in testing mode |
| `description` | `str` | Station description |
| `antennas` | `list[Antenna]` | Antenna configurations |
| `observations` | `int` | Total observation count |
| `target_utilization` | `int` | Target utilization percentage |
| `qthlocator` | `str` | QTH Maidenhead locator |

### Transmitter

| Field | Type | Description |
|---|---|---|
| `uuid` | `str` | Transmitter UUID |
| `description` | `str` | Description |
| `alive` | `bool` | Whether active |
| `type` | `str` | Transmitter type |
| `uplink_low` | `int` | Uplink low frequency (Hz) |
| `uplink_high` | `int` | Uplink high frequency (Hz) |
| `downlink_low` | `int` | Downlink low frequency (Hz) |
| `downlink_high` | `int` | Downlink high frequency (Hz) |
| `mode` | `str` | Transmission mode |
| `baud` | `float` | Baud rate |
| `sat_id` | `str` | Satellite ID |
| `norad_cat_id` | `int` | NORAD catalog ID |
| `status` | `str` | Transmitter status |
| `service` | `str` | Service category |
| `total_observations` | `int` | Total observations |
| `good_observations` | `int` | Good observations |
| `bad_observations` | `int` | Bad observations |
| `success_rate` | `float` | Success rate percentage |

### Antenna

| Field | Type | Description |
|---|---|---|
| `antenna_type` | `str` | Antenna type identifier |
| `antenna_type_name` | `str` | Antenna type name |
| `frequency_ranges` | `list[FrequencyRange]` | Supported frequency ranges |

### FrequencyRange

| Field | Type | Description |
|---|---|---|
| `min_frequency` | `int` | Minimum frequency (Hz) |
| `max_frequency` | `int` | Maximum frequency (Hz) |
