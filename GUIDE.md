# Usage Guide

## Filtering Observations by Satellite Class

The SatNOGS Network API lets you filter observations by satellite (NORAD ID), transmitter mode, frequency, and status — but not by satellite class (amateur radio, cubesat, weather, etc.). This is because satellite classification is community-sourced and lives in the **SatNOGS DB API**, not the Network API.

To filter observations by satellite class, you need to cross-reference both APIs.

### The Problem

You want to collect telemetry from a specific class of satellite — say, all amateur radio satellites, or all cubesats. The Network API doesn't know what "class" a satellite is. It only knows the NORAD catalog ID, transmitter UUID, mode, and frequency.

### What Data Indicates Satellite Class

The [SatNOGS DB API](https://db.satnogs.org/api/) (via the `satnogs-db-api-client` PyPI package) has richer satellite and transmitter metadata:

| Field | DB API Location | What It Tells You |
|---|---|---|
| `service` | Transmitter | Official ITU service category: `Amateur`, `Space Research`, `Earth Exploration`, `Broadcasting`, `Meteorological`, etc. |
| `iaru_coordination` | Transmitter | `IARU Coordinated` = confirmed amateur satellite |
| `operator` | Satellite | Operating organization (e.g. AMSAT, universities, space agencies) |
| `name` / `names` | Satellite | Naming conventions hint at class (e.g. `AO-73`, `FO-99`, `CAS-`) |
| `mode` | Transmitter | Transmission mode (CW, AFSK, BPSK, FM, LORA are common on amateur sats) |
| `downlink_low` | Transmitter | Frequency band (144-148 MHz VHF, 430-440 MHz UHF = amateur allocations) |

### Solution: Cross-Reference DB and Network APIs

Install the DB API client:

```bash
pip install satnogs-db-api-client
```

#### Example: Collect observations from amateur radio satellites

```python
from satnogs_network_api import SatnogsNetworkClient
import satnogsdbapiclient

# Set up both clients
net = SatnogsNetworkClient()

db_config = satnogsdbapiclient.Configuration(host="https://db.satnogs.org")
db_client = satnogsdbapiclient.ApiClient(db_config)
tx_api = satnogsdbapiclient.TransmittersApi(db_client)
sat_api = satnogsdbapiclient.SatellitesApi(db_client)

# Step 1: Get all transmitters with service="Amateur"
transmitters = tx_api.transmitters_list()
amateur_norad_ids = set()
for tx in transmitters:
    if tx.service == "Amateur" and tx.alive:
        amateur_norad_ids.add(tx.norad_cat_id)

print(f"Found {len(amateur_norad_ids)} amateur satellites")

# Step 2: Collect observations for those satellites
for norad_id in amateur_norad_ids:
    for obs in net.observations.list(norad_cat_id=norad_id, status="good"):
        print(f"Obs {obs.id}: NORAD {obs.norad_cat_id} mode={obs.transmitter_mode}")
        break  # just one per satellite for demo
```

#### Example: Find IARU-coordinated satellites

```python
transmitters = tx_api.transmitters_list()
iaru_norad_ids = set()
for tx in transmitters:
    if tx.iaru_coordination == "IARU Coordinated" and tx.alive:
        iaru_norad_ids.add(tx.norad_cat_id)

print(f"Found {len(iaru_norad_ids)} IARU-coordinated satellites")
```

#### Example: Find cubesats by name pattern

```python
satellites = sat_api.satellites_list(status="alive", in_orbit=True)

cubesat_keywords = ["cubesat", "cube", "1u", "2u", "3u", "6u", "12u"]
cubesat_norad_ids = set()

for sat in satellites:
    combined_names = f"{sat.name} {sat.names}".lower()
    if any(kw in combined_names for kw in cubesat_keywords):
        cubesat_norad_ids.add(sat.norad_cat_id)

print(f"Found {len(cubesat_norad_ids)} likely cubesats by name")
```

#### Example: Filter by amateur frequency bands

```python
# ITU amateur satellite allocations (Hz)
AMATEUR_BANDS = [
    (144_000_000, 148_000_000),   # 2m VHF
    (430_000_000, 440_000_000),   # 70cm UHF
    (1_260_000_000, 1_270_000_000),  # 23cm L-band
    (10_450_000_000, 10_500_000_000),  # 3cm S-band
]

def is_amateur_freq(freq):
    if freq is None:
        return False
    return any(lo <= freq <= hi for lo, hi in AMATEUR_BANDS)

transmitters = tx_api.transmitters_list()
amateur_freq_norad_ids = set()
for tx in transmitters:
    if tx.alive and is_amateur_freq(tx.downlink_low):
        amateur_freq_norad_ids.add(tx.norad_cat_id)

print(f"Found {len(amateur_freq_norad_ids)} satellites on amateur bands")
```

### Combining Multiple Signals

No single field perfectly classifies a satellite. For better accuracy, combine multiple signals:

```python
def classify_satellite(norad_id, transmitters, satellite):
    """Score a satellite across classification categories."""
    scores = {
        "amateur": 0,
        "cubesat": 0,
        "weather": 0,
        "research": 0,
    }

    for tx in transmitters:
        if tx.norad_cat_id != norad_id:
            continue
        if tx.service == "Amateur":
            scores["amateur"] += 3
        if tx.iaru_coordination == "IARU Coordinated":
            scores["amateur"] += 2
        if is_amateur_freq(tx.downlink_low):
            scores["amateur"] += 1
        if tx.service == "Meteorological":
            scores["weather"] += 3
        if tx.service == "Space Research":
            scores["research"] += 3
        if tx.service == "Earth Exploration":
            scores["research"] += 2

    name = f"{satellite.name} {satellite.names}".lower()
    if any(kw in name for kw in ["cubesat", "cube", "1u", "2u", "3u", "6u"]):
        scores["cubesat"] += 3

    operator = (satellite.operator or "").lower()
    if any(kw in operator for kw in ["amsat", "amateur"]):
        scores["amateur"] += 2
    if any(kw in operator for kw in ["noaa", "eumetsat", "meteor"]):
        scores["weather"] += 2

    return scores
```

### DB API Service Categories

For reference, these are the `service` values available on transmitters in the DB API:

| Service | Typical Satellites |
|---|---|
| `Amateur` | AMSAT, university, hobbyist satellites |
| `Broadcasting` | Commercial broadcast satellites |
| `Earth Exploration` | Remote sensing, imaging |
| `Fixed` | Fixed-service communication |
| `Inter-satellite` | Inter-satellite links |
| `Maritime` | Maritime communication |
| `Meteorological` | Weather satellites (NOAA, Meteor, etc.) |
| `Mobile` | Mobile communication |
| `Radiolocation` | Radar, tracking |
| `Radionavigational` | GPS, GLONASS, Galileo |
| `Space Operation` | Satellite operations/control |
| `Space Research` | Scientific missions |
| `Standard Frequency and Time Signal` | Time reference satellites |
| `Unknown` | Unclassified |
