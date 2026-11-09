# lan_ip_logger.py

import socket
import time
import logging
import requests
import json
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()


# Create a logger
logger = logging.getLogger('app/lan_ip_logger')
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler('lan_ip.log')
handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


def update_porkbun_dns(ip, subdomain):
    domain = os.getenv("PORKBUN_DOMAIN")
    record_type = os.getenv("PORKBUN_RECORD_TYPE")
    secret_api_key = os.getenv("PORKBUN_SECRET_API_KEY")
    api_key = os.getenv("PORKBUN_API_KEY")

    url = f"https://api.porkbun.com/api/json/v3/dns/editByNameType/{domain}/{record_type}/{subdomain}"
    data = {
        "secretapikey": secret_api_key,
        "apikey": api_key,
        "content": ip,
        "ttl": "60"  # 10 minutes
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def get_lan_ip():
    """Get the LAN IP address."""
    try:
        # Get the IP address of the interface that connects to the default gateway
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.error(f"Failed to get LAN IP: {e}")
        return None

if __name__ == "__main__":
    lan_ip = "0.0.0.0"
    t = 0
    while True:
        prev_ip = lan_ip
        lan_ip = get_lan_ip()
        if lan_ip and lan_ip != prev_ip:
            logger.info(lan_ip)

            subdomain = os.getenv("PORKBUN_SUBDOMAIN")
            safe_sub = subdomain
            # safe_sub = urllib.parse.quote(subdomain, safe='')
            logger.info(f"{safe_sub}")
            response = update_porkbun_dns(lan_ip, safe_sub)
            if response and response.get("status") == "SUCCESS":
                logger.info(f"DNS updated successfully: {lan_ip}")
            else:
                logger.error(f"DNS update failed: {response}")
        time.sleep(30)
        t += 30
        t %= 1800
