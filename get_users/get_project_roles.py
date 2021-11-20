# Name: Get project roles
# Task Type: Set-Variable
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 09-11-2021
# Description:

import requests

# -------------- General settings ------------------



# -------------- Test Environment ------------------
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
project_name = 'TEMPLATE'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# project_name = '@@{calm_project_name}@@'

kwargs = {
    'verify': False,
    'headers': {'Authorization': authorization}
}


# find the template project to clone the specs
# ----------------------------------------------
payload = {
    'kind': 'project',
    'filter': 'name=={}'.format(project_name)
}

r = requests.post(url.format('projects/list'), json=payload, **kwargs)
if r.status_code == 200 and int(r.json()['metadata']['total_matches']):
    print('INFO - project found')
    project_uuid = r.json()['entities'][0].get('metadata').get('uuid')
    print('INFO - project uuid: {}'.format(project_uuid))
else:
    print('ERROR - No project found, stopping, status code: {}, msg: {}'.format(r.status_code, r.content))
    exit(1)

r = requests.get(url.format('projects_internal/'+project_uuid), **kwargs)
if r.status_code == 200:
    groups = r.json()['spec']['project_detail']['resources']['external_user_group_reference_list']

roles_list = {}
for group in groups:
    cn_name = re.search('cn=(.+?),', group['name'].lower()).group(1)
    role_name = cn_name[cn_name.find('-')+1:]
    roles_list[role_name] = cn_name

print(roles_list)
