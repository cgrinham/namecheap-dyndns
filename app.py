"""
Namecheap dynamic DNS updater
"""

import requests
import logging
import datetime
import yaml

TEMPLATE = 'https://dynamicdns.park-your-domain.com/update?host={host}&domain={domain}&password={password}&ip={ip_address}'

IP_ADDRESS_PROVIDERS = [
    "http://ifconfig.me",
    "http://icanhazip.com"
]


def read_config():
    """ Read settings from YAML file"""
    logging.info("Read settings...")
    try:
        with open('config.yaml', 'r') as configfile:
            config = yaml.load(configfile)
        return config
    except FileNotFoundError:
        return {}


def write_config(data):
    """Write the previous image to settings file"""
    logging.info("Writing settings...")
    with open('config.yaml', 'w') as outfile:
        outfile.write(yaml.dump(data, default_flow_style=True))


def add_domain():
    config = read_config()
    host = input("Please enter the host: ")
    domain = input("Please enter the domain name: ")
    password = input("Please enter the dynamicdns password: ")
    if "domains" not in config:
        config["domains"] = []
    config["domains"].append({
        "host": host,
        "domain": domain,
        "password": password
    })
    write_config(config)


def log_message(message):
    print(message)
    with open('namecheapdns.log', 'a') as logfile:
        logfile.write("{} -  {}\n".format(datetime.datetime.now(), message))


def get_ip_address():
    for provider in IP_ADDRESS_PROVIDERS:
        logging.info("Get IP address from {}".format(provider))
        ip_address_resp = requests.get(provider)
        if ip_address_resp.status_code == 200:
            break
    else:
        raise ValueError("Could not retrieve IP Address")
    ip_address = ip_address_resp.content
    if isinstance(ip_address, bytes):
        ip_address = ip_address.decode('utf-8')
    ip_address = ip_address.strip()
    return ip_address


def main():
    config = read_config()
    ip_address = get_ip_address()
    for domain in config["domains"]:
        log_message("Update IP address for {host}:{domain}".format(**domain))
        resp = requests.get(TEMPLATE.format(ip_address, **domain))
        if resp.status_code != 200:
            log_message(
                "Updating domain {} failed - HTTP Status {} - Response {}".format(
                    domain['domain'], resp.status_code, resp.content))
        else:
            log_message(
                "Updating domain {} successful - updated IP address to {}".format(
                    domain['domain'], ip_address))


if __name__ == "__main__":
    main()