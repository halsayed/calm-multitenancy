# Name: Get external groups from template project to recreate on cloned
# Task Type: set variable
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 03-11-2021
# Description:

import requests

# -------------- General settings ------------------



# -------------- Test Environment ------------------
from time import sleep
import uuid
import urllib3
import json
urllib3.disable_warnings()
authorization = 'Basic YWRtaW46bngyVGVjaDkxMSE='
url = 'https://10.38.7.9:9440/api/nutanix/v3/{}'
project_template = 'TEMPLATE'
project_code = 'P006'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# project_template = '@@{PROJECT_TEMPLATE}@@'
# project_code = '@@{PROJECT_CODE}@@'

kwargs = {
    'verify': False,
    'headers': {'Authorization': authorization}
}

# find the template project to clone the specs
# ----------------------------------------------
payload = {
    'kind': 'project',
    'filter': 'name=={}'.format(project_template)
}

r = requests.post(url.format('projects/list'), json=payload, **kwargs)
if r.status_code == 200 and int(r.json()['metadata']['total_matches']):
    print('INFO - Template project found')
    template = r.json()['entities'][0]
    template_uuid = template['metadata']['uuid']
    print('INFO - Template project uuid: {}'.format(template_uuid))
else:
    print('ERROR - No template project found, stopping, status code: {}, msg: {}'.format(r.status_code, r.content))
    exit(1)

# get the template project details
r = requests.get(url.format('projects_internal/'+template_uuid), **kwargs)
user_groups = []
if r.status_code == 200:
    spec = r.json()['spec']
    for group in spec['project_detail']['resources']['external_user_group_reference_list']:
        name = group.get('name').replace(project_template.lower(), project_code)
        user_groups.append(name)

print('USER_GROUPS={}'.format(json.dumps(user_groups)))