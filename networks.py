#!/usr/bin/env python3

import json
import csv
import requests
import os
import sys
import argparse
from saseapi import get_uuid, update_api


URL_BASE = "https://api-qa.us.prismaaccess.paloaltonetworks.com"


def create_network_payload(rn):
    # Create the required payload
    new_rn = {
        "name": rn["network_name"],
        "ipsec_tunnel": rn["tunnel_1_name"],
        "secondary_wan_enabled": False,
        "license_type": "FWAAS-AGGREGATE",
        "region": rn["network_region"],
        "spn_name": rn["ipsec_termination_node"]
    }

    # Add subnets if provided
    subs = []
    if rn["network_subnets_1"]:
        subs.append(rn["network_subnets_1"])
        if rn["network_subnets_2"]:
            subs.append(rn["network_subnets_2"])
        if rn["network_subnets_3"]:
            subs.append(rn["network_subnets_3"])
        if rn["network_subnets_4"]:
            subs.append(rn["network_subnets_4"])
        new_rn["subnets"] = subs

    # Add secondary tunnel if provided
    if rn["tunnel_2_name"]:
        new_rn["secondary_ipsec_tunnel"] = rn["tunnel_2_name"]

    # Add BGP configs if local IP provided
    if rn["bgp_local_address_1"]:
        new_rn["protocol"] = {
                "bgp": {
                    "enable": True,
                    "peer_as": rn["bgp_peer_as_1"],
                    "peer_ip_address": rn["bgp_peer_address_1"],
                    "local_ip_address": rn["bgp_local_address_1"],
                    "secret": rn["bgp_secret_1"]
                }
            }

        # Add secondary BGP peer if provided
        if rn["bgp_local_address_2"]:
            new_rn["bgp_peer"] = {
                "same_as_primary": True,
                "peer_ip_address": rn["bgp_peer_address_2"],
                "local_ip_address": rn["bgp_local_address_2"],
                "secret": rn["bgp_secret_2"]
            }

        # Add BGP options if provided
        if rn["bgp_summarize_mobile_user_routes"].lower() == "true":
            new_rn["protocol"]["bgp"]["summarize_mobile_user_routes"] = True

        if rn["bgp_originate_default_route"].lower() == "true":
            new_rn["protocol"]["bgp"]["originate_default_route"] = True

        if rn["bgp_do_not_export_routes"].lower() == "true":
            new_rn["protocol"]["bgp"]["do_not_export_routes"] = True

    # Add QoS profile if provided
    if rn["network_qos_profile"]:
        new_rn["qos"] = {
                "qos_profile": rn["network_qos_profile"],
                "enable": True
            }

    if rn["tunnel_2_name"]:
        new_rn["secondary_wan_enabled"] = True

    return(new_rn)


def process_network_payload(network_row, url, delete_flag):
    # Process remote network row
    network_payload = create_network_payload(network_row)
    print("Network: \"{}\" ... ".format(network_payload['name']), end="")
    network_status = update_api(url, "/config/v1/remote-networks", network_payload, delete_flag)
    if network_status[0] == 201:
        print("Created ({0})".format(network_status[0]))
    elif network_status[0] == 200 and delete_flag is False:
        print("Updated ({0})".format(network_status[0]))
    elif network_status[0] == 200 and delete_flag is True:
        print("Deleted ({0})".format(network_status[0]))
    else:
        print("Failed ({0}){1}".format(network_status[0], network_status[1]))


def main():
    my_parser = argparse.ArgumentParser(description="Manage SASE remote networks")
    my_parser.add_argument(
        "filename", 
        help = "The CSV file containing remote network information"
        )
    my_parser.add_argument(
        "--delete", 
        help="Delete SASE remote networks",
        action="store_true"
        )
    args = my_parser.parse_args()
    filename = args.filename
    delete_flag = args.delete

    with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
        csvReader = csv.DictReader(csvfile)
        for row in csvReader:
            process_network_payload(row, URL_BASE, delete_flag)


if __name__ == "__main__":
    main()