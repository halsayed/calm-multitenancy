# Name: add category key to VM
# Task Type: Excute
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 14-11-2021
# Description:

import requests

# -------------- General settings ------------------



# -------------- Test Environment ------------------
from time import sleep
import urllib3
import re
from base64 import b64encode
from decouple import config
urllib3.disable_warnings()

PRISM_HOST = config('PRISM_HOST')
PRISM_PORT = config('PRISM_PORT')
PRISM_USER = config('PRISM_USER')
PRISM_PASS = config('PRISM_PASS')
authorization = 'Basic {}'.format(b64encode(f'{PRISM_USER}:{PRISM_PASS}'.encode()).decode())
url = f'https://{PRISM_HOST}:{PRISM_PORT}/api/nutanix/v3/'+'{}'

vm_uuid = '01a384c2-6044-4af4-a0be-f49e7692dca3'
category_name = 'SLA'
category_key = 'Gold'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# vm_uuid = '@@{id}@@'
# category_name = '@@{CATEGORY_NAME}@@'
# category_key = '@@{CATEGORY_KEY}@@'

kwargs = {
    'verify': False,
    'headers': {'Authorization': authorization}
}

sleep(3)
r = requests.get(url.format('vms/'+vm_uuid), **kwargs)
payload = r.json()
del(payload['status'])
payload['metadata']['categories'][category_name] = category_key

r = requests.put(url.format('vms/'+vm_uuid), json=payload, **kwargs)
if r.status_code == 202:
    print('INFO - VM updated with category')
else:
    print('ERROR - Catgory update failed, status code: {}, msg: {}'.format(r.status_code, r.content))
