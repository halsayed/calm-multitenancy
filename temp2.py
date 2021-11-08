


# gerneating a new tenant random ID
# ================================================================
def generate_random_id():
  id_len = 0
  while id_len <> 16:
      random_id = base64.b64encode(uuid.uuid4().bytes).decode().replace('+', '').replace('/','')[:16]
      radom_id = random_id.upper()
      if tenant_id_is_unique(random_id):
          id_len = len(random_id)
      else:
          id_len = 0
      

  return random_id.upper()
  

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


# check if generated ID is unique and never used before
# ----------------------------------------------------------
def tenant_id_is_unique(_id):
    api_endpoint = '/api/nutanix/v3/projects/list'
    payload = {
        "filter": "name==TENANT-{}".format(_id),
        "kind": "project",
        "length": 10
    }
    
    resp = http_request(api_endpoint, payload)
    if resp['metadata']['length'] == 0:
        return True
    else:
        return False
    
# convert domain name to Microsoft AD path
# -----------------------------------------------------------
def convert_domain_to_ad_path(domain, root_ou):
    path = ''
    if domain[len(domain)-1:] != '.':
        domain = domain + '.'
    
    while domain.find('.') >= 0:
        x = domain.find('.')
        path = path + ',DC={}'.format(domain[:x])
        domain = domain[x+1:]
    
    return '{},{}'.format(root_ou, path[1:])
    

# get public networks UUIDs
# -----------------------------------------------------------
def get_public_networks(label='@@{PUBLIC_VLAN}@@', owner='SHARED'):
    api_endpoint = '/api/nutanix/v3/subnets/list'
    payload = {
        'kind': 'subnet',
        'filter': 'name==.*[{}].*'.format(label),
        "offset":0
    }
    
    public_vlans = []
    public_list = []
    cluster_list = []
    vlans = http_request(api_endpoint, payload)
    for vlan in vlans['entities']:
        if vlan['metadata']['categories']['OWNER'] == owner:
            public_vlans.append({
                                'name': vlan['spec']['name'],
                                'vlan_id': vlan['spec']['resources']['vlan_id'],
                                'uuid': vlan['metadata']['uuid'],
                                'cluster_uuid': vlan['spec']['cluster_reference']['uuid']
                                })
            
    return public_vlans


# get role UUID using role name (returns first result only)
# ------------------------------------------------------------
def get_role_uuid(role_name):
  api_endpoint = '/api/nutanix/v3/roles/list'
  payload = {
      'filter': 'name=={}'.format(role_name),
      'kind': 'role',
      'offset': 0
  }
  result = http_request(api_endpoint, payload)
  if result['entities']:
      return result['entities'][0]['metadata']['uuid']
  else:
      return None
    

# get Directory service UUID from Prism Central
# ------------------------------------------------------------
def get_directory_uuid(domain_name):
  api_endpoint = '/api/nutanix/v3/directory_services/list'
  payload = {'filter': '', 'kind': 'directory_service'}
  dirs = http_request(api_endpoint, payload)
  for item in dirs['entities']:
    if item['spec']['resources']['domain_name'] == domain_name:
      return item['metadata']['uuid']
    
  return None


# get pc_account uuid
# -------------------------------------------------------------
def get_pc_account_uuid(account_name='NTNX_LOCAL_AZ'):
  api_endpoint = '/api/nutanix/v3/accounts/list'
  payload = {'filter': 'state!=DELETED;state!=DRAFT;name=={}'.format(account_name)}
  accounts = http_request(api_endpoint, payload)
  for account in accounts['entities']:
      if account['metadata']['name'] == account_name:
          return account['metadata']['uuid']
      
  return None


# dump network list
# --------------------------------------------------------------
def dump_network_list(networks):
  network_list = []
  cluster_list = []
  for network in networks:
    network_list.append({'kind': 'subnet', 'name': network['name'], 'uuid': network['uuid']})
    cluster_list.append(network['cluster_uuid'])
    
  if len(network_list) > 0:
    return json.dumps(network_list)[1:-1], json.dumps(cluster_list)[1:-1]
  else:
    return '{}', '{}'




var_id = generate_random_id()
ad_path = convert_domain_to_ad_path('@@{DOMAIN}@@', '@@{ROOT_OU}@@')
public_vlans = get_public_networks(label='@@{PUBLIC_VLAN}@@')
admin_role_uuid = get_role_uuid('@@{ROLE_ADMIN}@@')
operator_role_uuid = get_role_uuid('@@{ROLE_OPERATOR}@@')
directory_uuid = get_directory_uuid('@@{DOMAIN}@@')
pc_account_uuid = get_pc_account_uuid()
network_list, cluster_list = dump_network_list(public_vlans)




print('RANDOM_ID={}'.format(var_id))
print('AD_PATH=OU={}'.format(ad_path))
#print('PUBLIC_VLANS={}'.format(json.dumps(public_vlans)))
print('ROLE_ADMIN_UUID={}'.format(admin_role_uuid))
print('ROLE_OPERATOR_UUID={}'.format(operator_role_uuid))
#print('DIRECTORY_UUID={}'.format(directory_uuid))
print('PC_ACCOUNT_UUID={}'.format(pc_account_uuid))
print('NETWORK_LIST={}'.format(network_list))
print('CLUSTER_LIST={}'.format(cluster_list))

