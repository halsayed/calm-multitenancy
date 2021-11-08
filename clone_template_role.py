# Name: Clone user roles from template project
# Task Type: Excute
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 25-09-2021
# Description:

import requests

# -------------- General settings ------------------



# -------------- Test Environment ------------------
from time import sleep
import uuid
import urllib3
urllib3.disable_warnings()
authorization = 'Basic YWRtaW46bngyVGVjaDkxMSE='
url = 'https://10.38.12.9:9440/api/nutanix/v3/{}'
project_template = 'TEMPLATE'
project_uuid = 'ff13fc4e-9394-4568-b0e2-3abf4856596f'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# project_template = '@@{PROJECT_TEMPLATE}@@'
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
    groups_list = template['spec']['resources']['external_user_group_reference_list']

    print('INFO - template project uuid: {}'.format(template_uuid))
else:
    print('ERROR - No template project found, stopping, status code: {}, msg: {}'.format(r.status_code, r.content))
    exit(1)

