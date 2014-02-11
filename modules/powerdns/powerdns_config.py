#!/usr/bin/python

config = {}

# mysql connection variables
config['db_powerdns'] = {
    'host': 'powerdns_db_host',
    'user': 'powerdns_db_username',
    'pass': 'powerdns_db_password',
    'db':   'powerdns'
}

config['powerdns'] = {
    'hostname_is_fqdn':  False,
    'zone':              'vm.local'
}

def get_powerdns_config():
    return config['powerdns']

def get_db_powerdns_config():
    return config['db_powerdns']
