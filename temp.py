# api call function
# ================================================================
def http_request(api_endpoint, payload='', method='POST'):
  username = '@@{pc_admin.username}@@'
  username_secret = '@@{pc_admin.secret}@@'
  pc_address = '@@{PC_IP}@@'
  pc_port = '9440'

  url = "https://{}:{}{}".format(
      pc_address,
      pc_port,
      api_endpoint
  )
  
  headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
  }
  
  if len(payload) > 0:
      payload = json.dumps(payload)
      
  
  resp = urlreq(
      url,
      verb=method,
      auth='BASIC',
      user=username,
      passwd=username_secret,
      params=payload,
      headers=headers,
      verify=False
  )
  
  if resp.ok:
      return json.loads(resp.content)
  else:
      print('Error in API call')
      exit(1)




def entity_collection_list(cluster_uuid_list, entities_all, entities_self):

    default_list = []
    for entity in entities_all:
        default_list.append({
            'operator': 'IN',
            'left_hand_side': {'entity_type': entity},
            'right_hand_side': {'collection': 'ALL'}
        })

    for entity in entities_self:
        default_list.append({
            'operator': 'IN',
            'left_hand_side': {'entity_type': entity},
            'right_hand_side': {'collection': 'SELF_OWNED'}
        })

    # add the cluster list to the defualt filter list 
    default_list.append({
        'operator': 'IN',
        'left_hand_side': {'entity_type': 'cluster'},
        'right_hand_side': {'uuid_list': cluster_uuid_list}
    })
    return default_list


def generate_filter_list(project_uuid, cluster_uuid_list, admin=True):
    acl = []
    acl.append({
        'scope_filter_expression_list': [
            {
                'operator': 'IN',
                'left_hand_side': 'PROJECT',
                'right_hand_side': {'uuid_list': [project_uuid]}
            }
        ],
        'entity_filter_expression_list': [
            {
                'operator': 'IN',
                'left_hand_side': {'entity_type': 'ALL'},
                'right_hand_side': {'collection': 'ALL'}
            }
        ]
    })

    if admin:
        entities_all=['image', 'app_icon', 'category']
        entities_self=['marketplace_item', 'app_task', 'app_variable']
    else:
        entities_all=['app_icon', 'category']
        entities_self=[]

    acl.append({
    'entity_filter_expression_list':entity_collection_list(cluster_uuid_list, 
                                                            entities_all, 
                                                            entities_self)})
    return acl
        

def generate_project_payload(RANDOM_ID, AD_PATH, ROLE_ADMIN_UUID,
    ROLE_OPERATOR_UUID, PC_ACCOUNT_UUID, NETWORK_LIST, CLUSTER_LIST, PROJ_UUID,
    GROUP_ADMIN_UUID, GROUP_OPERATOR_UUID, PROJ_SPEC, VCPU, STORAGE, RAM):


    filter_list_admin = generate_filter_list(PROJ_UUID, CLUSTER_LIST)
    filter_list_operator = generate_filter_list(PROJ_UUID, CLUSTER_LIST, False)


    admin_group =   {
                        'kind': 'user_group',
                        'name': 'CN={}-ADMIN,OU={},{}'.format(RANDOM_ID, RANDOM_ID, AD_PATH),
                        'uuid': GROUP_ADMIN_UUID
                    }

    operator_group =    {
                            'kind': 'user_group',
                            'name': 'CN={}-OPERATOR,OU={},{}'.format(RANDOM_ID, RANDOM_ID, AD_PATH),
                            'uuid': GROUP_OPERATOR_UUID
                        }

    acp_admin = {
        'acp': {
            'name': 'ACP-TENANT-{}'.format(RANDOM_ID),
            'resources': {
                'role_reference': {
                    'kind': 'role',
                    'uuid': ROLE_ADMIN_UUID
                },
                'user_group_reference_list': [admin_group],
                'user_reference_list': [],
                'filter_list': {'context_list': filter_list_admin}
            },
            'description': 'Admin role for {}'.format(RANDOM_ID)
        },
        'metadata': {
            'kind': 'access_control_policy'
        },
        'operation': 'ADD'
    }

    acp_operator = {
        'acp': {
            'name': 'ACP-TENANT-{}'.format(RANDOM_ID),
            'resources': {
                'role_reference': {
                    'kind': 'role',
                    'uuid': ROLE_OPERATOR_UUID
                },
                'user_group_reference_list': [operator_group],
                'user_reference_list': [],
                'filter_list': {'context_list': filter_list_operator}
            },
            'description': 'Operator role for {}'.format(RANDOM_ID)
        },
        'metadata': {
            'kind': 'access_control_policy'
        },
        'operation': 'ADD'
    }

    access_control_policy_list = [acp_admin, acp_operator]


    project_detail = {
        'name': 'TENANT-{}'.format(RANDOM_ID),
        'resources': {
            'resource_domain': {
                'resources': [
                    {'limit': VCPU, 'resource_type': 'VCPUS'},
                    {'limit': STORAGE, 'resource_type': 'STORAGE'},
                    {'limit': RAM, 'resource_type': 'MEMORY'}
                ]
            },
            'account_reference_list': [
                {
                    'uuid': PC_ACCOUNT_UUID,
                    'kind': 'account',
                    'name': 'nutanix_pc'
                }
            ],
            'environment_reference_list': [
                {
                    'kind': 'environment',
                    'uuid': '1638025a-8a02-6f43-16d4-9d4d9f6c0969'
                }
            ],
            'external_user_group_reference_list': [admin_group, operator_group],
            'user_reference_list': [],
            'subnet_reference_list': NETWORK_LIST,
            'external_network_list': []
        }
    }

    spec = {
        'access_control_policy_list' : access_control_policy_list,
        'project_detail': project_detail
    }

    metadata = {
        'kind': 'project',
        'uuid': PROJ_UUID,
        'spec_version': PROJ_SPEC,
        'owner_reference': {
            'kind': 'user',
            'uuid': '00000000-0000-0000-0000-000000000000',
            'name': 'admin'
        }
    }

    return {
            'spec': spec,
            'api_version': '3.1',
            'metadata': metadata
            }

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


payload = generate_project_payload('@@{RANDOM_ID}@@', '@@{AD_PATH}@@', '@@{ROLE_ADMIN_UUID}@@',
    '@@{ROLE_OPERATOR_UUID}@@', '@@{PC_ACCOUNT_UUID}@@', [@@{NETWORK_LIST}@@], [@@{CLUSTER_LIST}@@], '@@{PROJ_UUID}@@',
    '@@{GROUP_ADMIN_UUID}@@', '@@{GROUP_OPERATOR_UUID}@@', @@{PROJ_SPEC}@@, @@{VCPU}@@, @@{STORAGE}@@, @@{RAM}@@)
    
print(json.dumps(payload))


api_endpoint = '/api/nutanix/v3/projects_internal/@@{PROJ_UUID}@@'
#username = '@@{pc_admin.username}@@'
#username_secret = '@@{pc_admin.secret}@@'
#pc_address = '@@{PC_IP}@@'
#pc_port = '9440'

#url = 'https://{}:{}{}'.format(pc_address, pc_port, api_endpoint)
#headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
#print(url)
#resp = urlreq(url, verb='PUT', auth='BASIC', user=username, passwd=username_secret, params=payload, headers=headers, verify=False)

result = http_request(api_endpoint, payload, method='PUT')

print(result)






