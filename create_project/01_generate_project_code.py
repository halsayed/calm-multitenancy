# Name: Generate Generate next avialable project code, format P001
# Task Type: set variable
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 01-11-2021
# Description:

import requests

# -------------- General settings ------------------
CODE_PREFIX = 'P'
COUNT_DIGITS = 3
current_count = 0


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

project_category = 'PROJECTS'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# project_category = '@@{PROJECT_CATEGORY}@@'

kwargs = {
    'verify': False,
    'headers': {'Authorization': authorization}
}

payload = {'kind': 'category'}
r = requests.post(url.format('categories/'+project_category+'/list'), json=payload, **kwargs)
project_code = 'P001'

if r .status_code == 200:
    current_count = int(r.json()['metadata']['total_matches'])
    print('INFO - current project code count: {}'.format(current_count))
    used_codes = []
    for code in r.json()['entities']:
        used_codes.append(int(code['value'][1:]))
    
    used_codes.sort()
    if current_count:
        next_count = used_codes[-1] + 1
        digit_format = '{'+'0:0={}d'.format(COUNT_DIGITS)+'}'
        next_count_txt = digit_format.format(next_count)
        project_code = '{}{}'.format(CODE_PREFIX, next_count_txt)
        print('INFO - adding {} to category'.format(project_code))

# if the category key doesn't exist then create it
if current_count == 0:
    payload = {'name': project_category}
    print('INFO - category key is not available, creating it')
    r = requests.put(url.format('categories/'+project_category), json=payload, **kwargs)
    print('INFO - creating category status code: {}'.format(r.status_code))

# adding the new project code to the category
payload = {'value': project_code}
r = requests.put(url.format('categories/'+project_category+'/'+project_code), json=payload, **kwargs)

print('PROJECT_CODE={}'.format(project_code))
