# Name: clone roles from template project
# Task Type: Execute
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 08-11-2021
# Description:

import requests

# -------------- General settings ------------------



# -------------- Test Environment ------------------
from time import sleep
import uuid
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

project_template = 'TEMPLATE'
project_code = 'P015'
user_groups='["cn=P015-operators,ou=P015,ou=tenants,dc=ntnx,dc=me", "cn=P015-consumers,ou=P015,ou=tenants,dc=ntnx,dc=me", "cn=P015-admins,ou=P015,ou=tenants,dc=ntnx,dc=me"]'
project_uuid = 'bdfb4dcd-00fe-4fea-a67a-2aa948ce380e'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# project_template = '@@{PROJECT_TEMPLATE}@@'
# project_code = '@@{PROJECT_CODE}@@'
# user_groups = '@@{USER_GROUPS}@@'
# project_uuid = '@@{PROJECT_UUID}@@'

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
if r.status_code == 200:
    print('INFO - obtain template details')
    template = r.json()

# get the new project details
r = requests.get(url.format('projects_internal/'+project_uuid), **kwargs)
if r.status_code == 200:
    print('INFO - obtain new project details')
    project = r.json()


# prepare the project details to update with roles
del(project['status'])
user_groups = json.loads(user_groups)
template_roles = template['spec']['access_control_policy_list']
groups = []
for item in user_groups:
    # find the reference role from template
    reference_role = ''
    filter = ''
    for role in template_roles:
        if item.replace(project_code, project_template).lower() == role['acp']['resources']['user_group_reference_list'][0]['name'].lower():
            reference_role = role['acp']['resources']['role_reference']['uuid']
            filter = json.dumps(role['acp']['resources']['filter_list']).replace(template_uuid, project_uuid)
            filter = json.loads(filter)

    groups.append({
        'uuid': str(uuid.uuid4()),
        'distinguished_name': item,
        'reference_role': reference_role,
        'filter': filter
    })
    

# update the new project with clone roles
acp_list  = []
groups_list = []
for group in groups:
    # acp_list payload
    acp_list.append({
        'acp': {
            'name': 'nuCalmAcp-{}'.format(str(uuid.uuid4())),
            'resources': {
                'role_reference': {'uuid': group['reference_role'], 'kind': 'role'},
                'user_group_reference_list': [{
                    'name': group['distinguished_name'],
                    'kind': 'user_group',
                    'uuid': group['uuid']
                }],
                'filter_list': group['filter']
            }
        },
        'metadata': {'kind': 'access_control_polic'},
        'operation': 'ADD'
    })

    # user_group_list payload
    groups_list.append({
        'metadata': {'kind': 'user_group', 'uuid': group['uuid']},
        'operation': 'ADD',
        'user_group': {
            'resources': {
                'directory_service_user_group': {
                    'distinguished_name': group['distinguished_name']
                }
            }
        }
    })

project['spec']['access_control_policy_list'] = acp_list
project['spec']['user_group_list'] = groups_list

r = requests.put(url.format('projects_internal/'+project_uuid), json=project, **kwargs)

if r.status_code == 202:
    print('INFO - new project updated with roles')
else:
    print('ERROR - project role update, status code: {}, msg: {}'.format(r.status_code, r.content))
    exit(1)


