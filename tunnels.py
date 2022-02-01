#!/usr/bin/env python3

import json
import csv
import requests
import os
import sys
import argparse
from saseapi import get_uuid, update_api

URL_BASE = "https://api-qa.us.prismaaccess.paloaltonetworks.com"


def create_tunnel_payload(t):
    # Create the required payload
    new_tunnel = {
        "name": t["tunnel_name"],
        "auto_key": {
            "ike_gateway": [{"name": "gw-" + t["tunnel_name"]}],
            "ipsec_crypto_profile": t["tunnel_ipsec_profile"]
        }
    }

    # Add proxy-ids if provided
    proxy_ids = []
    for p in [1, 2, 3, 4]:
        proxy_dict = {}
        if t["tunnel_proxy_id_" + str(p) + "_name"]:
            proxy_dict = {
                "name": t["tunnel_proxy_id_" + str(p) + "_name"],
                "local": t["tunnel_proxy_id_" + str(p) + "_local"],
                "remote": t["tunnel_proxy_id_" + str(p) + "_remote"]
            }
            if t["tunnel_proxy_id_" + str(p) + "_protocol"].lower() in ["tcp", "udp"]:
                proxy_dict["protocol"] = {
                    t["tunnel_proxy_id_" + str(p) + "_protocol"].lower(): {
                        "local_port": int(t["tunnel_proxy_id_" + str(p) + "_protocol_local_port"]),
                        "remote_port": int(t["tunnel_proxy_id_" + str(p) + "_protocol_remote_port"])
                    }
                }
            elif t["tunnel_proxy_id_" + str(p) + "_protocol"].lower() == "number":
                proxy_dict["protocol"] = {
                    "number": int(t["tunnel_proxy_id_" + str(p) + "_protocol_number"])
                }
            proxy_ids.append(proxy_dict)

    new_tunnel["auto_key"]["proxy_id"] = proxy_ids



    # Add anti_replay if provided
    if t["tunnel_anti_replay"].lower() == "true":
        new_tunnel["anti_replay"] = True

    # Add copy_tos if provided
    if t["tunnel_copy_tos"].lower() == "true":
        new_tunnel["copy_tos"] = True

    # Add enable_gre_encapsulation if provided
    if t["tunnel_gre_encapsulation"].lower() == "true":
        new_tunnel["enable_gre_encapsulation"] = True

    # Add tunnel_monitor if provided
    if t["tunnel_monitor_ip"]:
        new_tunnel["tunnel_monitor"] = {
            "enable": True,
            "destination_ip": t["tunnel_monitor_ip"]
        }
        if t["tunnel_monitor_proxy_id"]:
            new_tunnel["tunnel_monitor"]["proxy_id"] = t["tunnel_monitor_proxy_id"]

    # Return the json body
    return(new_tunnel)


def create_gateway_payload(g):
    # Create the required payload
    new_gw = {
        "name": "gw-" + g["tunnel_name"],
        "authentication_key": g["gateway_shared_key"],
        "protocol": {
            "ikev1": {
                "ike_crypto_profile": g["gateway_ikev1_profile"]    
            },
            "ikev2": {
                "ike_crypto_profile": g["gateway_ikev2_profile"]
            }
        }
    }

    # Add peer_id if provided
    if g["gateway_peer_id_type"].lower() in ["ipaddr", "keyid", "fqdn", "ufqdn"]:
        new_gw[g["gateway_peer_id_type"].lower()] = g["gateway_peer_id_value"]

    # Add local_id if provided
    if g["gateway_local_id_type"].lower() in ["ipaddr", "keyid", "fqdn", "ufqdn"]:
        new_gw[g["gateway_local_id_type"].lower()] = g["gateway_local_id_value"]

    # Add dpd if provided
    if g["gateway_ikev1_dpd"].lower() == "true":
        new_gw["protocol"]["ikev1"]["dpd"] = {"enable": True}
    elif g["gateway_ikev1_dpd"].lower() == "false":
        new_gw["protocol"]["ikev1"]["dpd"] = {"enable": False}

    if g["gateway_ikev2_dpd"].lower() == "true":
        new_gw["protocol"]["ikev2"]["dpd"] = {"enable": True}
    elif g["gateway_ikev2_dpd"].lower() == "false":
        new_gw["protocol"]["ikev2"]["dpd"] = {"enable": False}

    # Disable nat_traversal if provided
    new_gw["protocol_common"] = {
        "nat_traversal": {"enable": True}
    }
    if g["gateway_nat_traversal"].lower() == "false":
        new_gw["protocol_common"]["nat_traversal"] = {"enable": False}

    # Enable fragmentation if provided
    if g["gateway_fragmentation"].lower() == "true":
        new_gw["protocol_common"]["fragmentation"] = {"enable": True}
    else:
        new_gw["protocol_common"]["fragmentation"] = {"enable": False}

    # Add passive_mode if provided
    if g["gateway_passive_mode"].lower() == "true":
        new_gw["protocol_common"]["passive_mode"] = True
    else:
        new_gw["protocol_common"]["passive_mode"] = False

    # Add peer_address (required)
    if g["gateway_peer_address_type"].lower() in ["ip", "fqdn"]:
        new_gw["peer_address"] = {
            g["gateway_peer_address_type"].lower(): g["gateway_peer_address"]
        }
    elif g["gateway_peer_address_type"].lower() == "dynamic":
        new_gw["peer_address"] = {
            "dynamic": {}
        }

    #Return the json payload
    return(new_gw)
    

def process_gateway_payload(gateway_row, url, delete_flag):
    # Process IKE gateway
    gateway_payload = create_gateway_payload(gateway_row)
    # print(json.dumps(gateway_payload)) #DEBUG
    print("Gateway: \"{}\" ... ".format(gateway_payload['name']), end="")
    gateway_status = update_api(url, "/config/v1/ike-gateways", gateway_payload, delete_flag)
    if gateway_status[0] == 201:
        print("Created ({0})".format(gateway_status[0]))
    elif gateway_status[0] == 200 and not delete_flag:
        print("Updated ({0})".format(gateway_status[0]))
    elif gateway_status[0] == 200 and delete_flag:
        print("Deleted ({0})".format(gateway_status[0]))
    else:
        sys.exit("Failed ({0}){1}".format(gateway_status[0], gateway_status[1]))


def process_tunnel_payload(tunnel_row, url, delete_flag):
    #Process IPSec tunnel
        tunnel_payload = create_tunnel_payload(tunnel_row)
        print("Tunnel: \"{}\" ... ".format(tunnel_payload['name']), end="")
        # print(json.dumps(tunnel_payload)) #DEBUG
        tunnel_status = update_api(url, "/config/v1/ipsec-tunnels", tunnel_payload, delete_flag)
        if tunnel_status[0] == 201:
            print("Created ({0})".format(tunnel_status[0]))
        elif tunnel_status[0] == 200 and not delete_flag:
            print("Updated ({0})".format(tunnel_status[0]))
        elif tunnel_status[0] == 200 and delete_flag:
            print("Deleted ({0})".format(tunnel_status[0]))
        else:
            sys.exit("Failed ({0}){1}".format(tunnel_status[0], tunnel_status[1]))


def main():
    my_parser = argparse.ArgumentParser(description="Manage SASE IKE gateways and IPSec tunnels")
    my_parser.add_argument(
        "filename", 
        help = "The CSV file containing IKE gateway and IPSec tunnel information"
        )
    my_parser.add_argument(
        "--delete", 
        help="Delete IKE gateways and IPSec tunnels",
        action="store_true"
        )
    args = my_parser.parse_args()
    filename = args.filename
    delete_flag = args.delete

    with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
        csvReader = csv.DictReader(csvfile)
        for row in csvReader:
            if delete_flag is False:
                process_gateway_payload(row, URL_BASE, delete_flag)
                process_tunnel_payload(row, URL_BASE, delete_flag)
            elif delete_flag is True:
                process_tunnel_payload(row, URL_BASE, delete_flag)
                process_gateway_payload(row, URL_BASE, delete_flag)


if __name__ == "__main__":
    main()