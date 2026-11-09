# LanUpdater

Keeps a Porkbun DNS record pointed at this machine's LAN IP address, so a
self-hosted service stays reachable at a stable hostname when DHCP hands out a
new address.

## How it works

- Every 30 seconds the script determines the LAN IP by opening a UDP socket
  toward `8.8.8.8` (no traffic is sent).
- When the address changes, it calls Porkbun's DNS API
  (`editByNameType`) and sets the record to the new IP with a TTL of 60
  seconds.
- Each address and update result is appended to `lan_ip.log`.

> The DNS record points at a private LAN address, so the hostname is only
> reachable from inside that network.

## Requirements

- A [Porkbun](https://porkbun.com/) API key and secret with DNS edit access
- Docker with Compose (recommended), or Python 3.9+

## Configuration

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
| --- | --- |
| `PORKBUN_DOMAIN` | Domain managed by Porkbun, e.g. `example.com` |
| `PORKBUN_RECORD_TYPE` | Record type to update, e.g. `A` for IPv4 |
| `PORKBUN_SUBDOMAIN` | Host label to update, e.g. `home` |
| `PORKBUN_API_KEY` | Porkbun API key |
| `PORKBUN_SECRET_API_KEY` | Porkbun secret API key |

The `.env` file contains secrets and is excluded from Git. Never commit it.

## Run with Docker

```bash
cp .env.example .env   # then edit it
docker compose up -d --build
docker compose logs -f
```

The service uses `network_mode: host` so the container can see the host's LAN
address. Host networking is supported on Linux; on Docker Desktop for macOS or
Windows the container will not see the host's LAN IP correctly.

The repository is bind-mounted into the container, so the log is written to
`main/lan_ip.log` on the host.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python main/lan_ip_logger.py
```

The script writes `lan_ip.log` to the current working directory.

## Project layout

```
.
├── main/lan_ip_logger.py   # IP watcher and DNS updater
├── Dockerfile              # Container image
├── compose.yaml            # Compose service definition
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variable template
```

## Security notes

- Keep `.env` private and rotate the Porkbun API keys if they are ever exposed.
- Grant the API key only the permissions it needs (DNS editing for the domain).
