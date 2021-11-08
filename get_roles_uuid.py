# Name: Get prism roles UUIDs
# Task Type: set variable
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 25-09-2021
# Description:

import requests

# -------------- General settings ------------------
admin_role = 'Project Admin'
consumer_role = 'Consumer'
operators_role = 'Operator'


# -------------- Test Environment ------------------
import urllib3
urllib3.disable_warnings()
authorization = 'Basic YWRtaW46bngyVGVjaDkxMSE='
url = 'https://10.38.12.9:9440/api/nutanix/v3/{}'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'


kwargs = {
    'verify': False,
    'headers': {'Authorization': authorization}
}

payload = {
    'filter': 'name=={}'.format(admin_role),
    'kind': 'role'
}

r = requests.post(url.format('roles/list'), json=payload, **kwargs)
if len(r.json()['entities']):
    print('ADMIN_ROLE_UUID={}'.format(r.json()['entities'][0]['metadata']['uuid']))


payload['filter'] = 'name=={}'.format(consumer_role)
r = requests.post(url.format('roles/list'), json=payload, **kwargs)
if len(r.json()['entities']):
    print('CONSUMER_ROLE_UUID={}'.format(r.json()['entities'][0]['metadata']['uuid']))

payload['filter'] = 'name=={}'.format(operators_role)
r = requests.post(url.format('roles/list'), json=payload, **kwargs)
if len(r.json()['entities']):
    print('OPERATOR_ROLE_UUID={}'.format(r.json()['entities'][0]['metadata']['uuid']))