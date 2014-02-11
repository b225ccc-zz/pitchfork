#!/usr/bin/python

config = {}

config['pitchfork'] = {
    # set this to True if you want events logged
    # to a tracking database.  see below for schema
    'track':     True,
    # TODO: log level config not implemented yet
    'log_level': 'info'
}


#
# openstacktrack mysql db schema
#
#  CREATE TABLE track (
#       track_id int(11) NOT NULL auto_increment,
#       context_request_id varchar(42),
#       context_user_name varchar(128),
#       context_remote_address varchar(15),
#       event_type varchar(128),
#       publisher_id varchar(128),
#       timestamp varchar(28),
#       PRIMARY KEY (track_id)
#     ) ENGINE=innodb AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
#
#  CREATE TABLE message (
#       message_id int(11) NOT NULL auto_increment,
#       track_id int(11) NOT NULL,
#       message varchar(16384),
#       PRIMARY KEY (message_id)
#     ) ENGINE=innodb AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


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
