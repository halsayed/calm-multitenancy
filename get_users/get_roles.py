import json

admins = '[{"GivenName":"Ahmed","Surname":"Badawy","UserPrincipalName":null,"SamAccountName":"ahmed","mail":null},{"GivenName":"test","Surname":"te","UserPrincipalName":"test123@ntnx.me","SamAccountName":"test123","mail":null}]'
consumers = ''
operators = '{"GivenName":"gfg","Surname":"gffg","UserPrincipalName":"ggfg@ntnx.me","SamAccountName":"ggfg","mail":null}'

# admins = '@@{ADMINS}@@'
# consumers = '@@{CONSUMERS}@@'
# operators = '@@{OPERATORS}@@'

roles = {
    'admins': admins,
    'consumers': consumers,
    'operators': operators
}

for role in roles:
    try:
        users = json.loads(roles[role])
        if isinstance(users, dict):
            roles[role] = [users]
        else:
            roles[role] = users
    except ValueError:
        roles[role] = []

print(roles)