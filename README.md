# Hitron Cable Modem MQTT Exporter 📡➡️📊

This Python-based tool scrapes diagnostic stats from a Hitron cable modem and publishes them via MQTT using Home Assistant Auto Discovery. You can graph signal strength, SNR, error rates, and upstream power in Grafana, or monitor your connection status directly from Home Assistant.

---

## 📦 Features

- 🔐 Authenticates using `nologin` mode
- 📋 Extracts:
  - Downstream & Upstream channels
  - Signal strength (dBmV)
  - SNR (dB)
  - Corrected & Uncorrected error counts
  - OFDMA upstream parameters (rep power, attenuation, FFT)
- 📡 Publishes each metric to MQTT under `modem/{key}`
- 🏠 Supports **Home Assistant MQTT Auto Discovery**
- 📊 Compatible with InfluxDB + Grafana dashboards

---

## 🚀 Installation

### 1. Clone the Repo

```bash
git clone https://github.com/YOUR_USERNAME/hitron-scraper.git
cd hitron-scraper
```

### 2. Configure Environment

Copy `config.py.example` to `config.py`:

```bash
cp config.py.example config.py
```

Edit the file with your MQTT broker and modem IP address:

```python
MODEM_URL = "http://192.168.100.1"
MQTT_BROKER = "mqtt.example.com"
MQTT_PORT = 1883
MQTT_USER = "youruser"
MQTT_PASS = "yourpass"
```

---

## 🐳 Docker Usage

### Option 1: Run Once (Test)

```bash
docker build -t hitron-scraper .
docker run --rm --name hitron hitron-scraper
```

### Option 2: Run Every 60 Seconds with Cron

#### a) Add to host cron:

```bash
* * * * * docker run --rm hitron-scraper >> /var/log/hitron-scraper.log 2>&1
```

#### b) Or use a container with built-in cron (see `docker-compose.yml` below)

---

## 🏠 Home Assistant Integration

Ensure MQTT is enabled and `discovery: true` in your `configuration.yaml`.

After the first run, sensors like:

- `sensor.hitron_cable_modem_signal_strength_0`
- `sensor.hitron_cable_modem_snr_0`
- `sensor.hitron_cable_modem_correcteds_0`

...will automatically appear in Home Assistant.

---

## 🧪 Dashboard Examples

- Signal levels as gauges
- Error counters in entity cards
- Upstream power in graphs

---

## 🐘 InfluxDB + Grafana

To integrate with InfluxDB:

- Point Telegraf or Home Assistant's `recorder` to InfluxDB
- Use MQTT to store metrics
- Build dashboards per channel ID

---

## 🛠 docker-compose.yml Example

```yaml
version: "3"
services:
  hitron-scraper:
    build: .
    container_name: hitron-scraper
    restart: unless-stopped
    volumes:
      - ./config.py:/app/config.py
    environment:
      - TZ=America/Chicago
```

---

## 🧾 License

MIT

---

## 🧠 Credits

Built by Clint @ [TheChance.Family](https://home.thechance.family) — because modems should be visible too.
