#!/usr/bin/env python3

import requests
import json
import os

def get_uuid(url, endpoint, p):
    headers = {}
    headers['Authorization'] = "Bearer " + os.getenv("API_TOKEN")
    headers['Content-Type'] = "application/json"
    params = {}
    params['scope'] = "Remote Networks"
    params['name'] = p['name']
    
    try:
        r = requests.get(url + endpoint, headers=headers, params=params)
    except requests.exceptions.RequestException as e:
        SystemExit(e)
    
    result = r.json()

    if r.status_code == 200:
        return result[0]['id']
    else:
        return None


def update_api(url, endpoint, p, delete_flag):
    headers = {}
    headers['Authorization'] = "Bearer " + os.getenv("API_TOKEN")
    headers['Content-Type'] = "application/json"
    params = {}
    params['scope'] = "Remote Networks"

    uuid = get_uuid(url, endpoint, p)
    if uuid is None:
        try:
            r = requests.post(url + endpoint, headers=headers, params=params, data=json.dumps(p))
        except requests.exceptions.RequestException as e:
            SystemExit(e)
    elif uuid is not None and delete_flag is False:
        endpoint = endpoint + "/" + uuid
        try:
            r = requests.put(url + endpoint, headers=headers, params=params, data=json.dumps(p))
        except requests.exceptions.RequestException as e:
            SystemExit(e)
    elif uuid is not None and delete_flag is True:
        endpoint = endpoint + "/" + uuid
        try:
            r = requests.delete(url + endpoint, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            SystemExit(e)

    return r.status_code, r.json()