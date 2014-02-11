#!/usr/bin/python

config = {}

# rabbitmq connection variables
config['openstack_rabbitmq'] = {
    'host':             'rabbitmq-host',
    'user':             'openstack_rabbitmq_username',
    'pass':             'openstack_rabbitmq_password',
    'port':             5672,
    'virtual_host':     '/',
    'queue':            'notifications.info',
    'queue_arguments':  {'x-ha-policy':'all'}
}

config['db_track'] = {
    'host': 'db_track_host',
    'user': 'db_track_username',
    'pass': 'db_track_password',
    'db':   'openstacktrack'
}

config['pitchfork'] = {
    'track': True
}

# we want to take some action on these event types
# TODO: add (and comment out) all known event types
config['actionable_events'] = [
    'compute.instance.create.start',
    'compute.instance.create.end',
]

def get_openstacktrack_conf():
    return config['db_track']

def get_rabbitmq_conf():
    return config['openstack_rabbitmq']

def get_actionable_events():
    return config['actionable_events']
