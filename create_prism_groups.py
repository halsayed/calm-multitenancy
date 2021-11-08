# Name: Create tenant groups on Prism
# Task Type: set variable
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 25-09-2021
# Description:

import requests

# -------------- General settings ------------------



# -------------- Test Environment ------------------
import urllib3
urllib3.disable_warnings()
authorization = 'Basic YWRtaW46bngyVGVjaDkxMSE='
url = 'https://10.38.12.9:9440/api/nutanix/v3/{}'
project_code = 'P010'
ad_path = 'OU=TENANTS, DC=demo, DC=lab'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# project_code = '@@{PROJECT_CODE}@@'
# ad_path = '@@{AD_PATH}@@'

kwargs = {
    'verify': False,
    'headers': {'Authorization': authorization}
}


# create admins group
# ----------------------------------------------
payload = {
    'spec': {
        'resources': {
            'directory_service_user_group': {
                'distinguished_name': 'CN={}-admins, OU={}, {}'.format(project_code, project_code, ad_path)
            }
        }
    },
    'metadata': {
        'kind': 'user_group'
    }
}

r = requests.post(url.format('user_groups'), json=payload, **kwargs)
if r.status_code == 202:
    print('GROUP_ADMINS_UUID={}'.format(r.json()['metadata']['uuid']))


# create consumers group
# ----------------------------------------------
group_path = 'CN={}-consumers, OU={}, {}'.format(project_code, project_code, ad_path)
payload['spec']['resources']['directory_service_user_group']['distinguished_name'] = group_path

r = requests.post(url.format('user_groups'), json=payload, **kwargs)
if r.status_code == 202:
    print('GROUP_CONSUMERS_UUID={}'.format(r.json()['metadata']['uuid']))

# create Operators group
# ----------------------------------------------
group_path = 'CN={}-operators, OU={}, {}'.format(project_code, project_code, ad_path)
payload['spec']['resources']['directory_service_user_group']['distinguished_name'] = group_path

r = requests.post(url.format('user_groups'), json=payload, **kwargs)
if r.status_code == 202:
    print('GROUP_OPERATORS_UUID={}'.format(r.json()['metadata']['uuid']))