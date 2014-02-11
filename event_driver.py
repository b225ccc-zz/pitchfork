#!/usr/bin/env python
#
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import json
import sys
import logging
import pitchfork_config as config
import mysql

logger = logging.getLogger('root')

def compute_instance_create_end(body):
    logger.debug("in compute_instance_create_end()")

    #
    # Incorporate interfacing modules here
    #

    #
    # ex. Add host info to PowerDNS MySQL backend
    for i, val in enumerate(body['payload']['fixed_ips']):
        ip_address = body['payload']['fixed_ips'][i]['address']
        hostname = body['payload']['hostname']

        # TODO: need to figure out zone here... see powerdns_config.py
        zone = ''
        
        # if created host got conf'd w/ multiple IPs, we're only handling
        # the first one for now.... TODO
        if i == 0:
            logger.info("working on %s with ip %s" % (hostname, ip_address))
            add_record(hostname,zone,ip_address,'A')
        else:
            logger.info("ignoring multiple interface %s" % ip_address)

    # returning true will signal to calling function to ACK rabbitmq message
    return True


def compute_instance_delete_end(body):
    # note for delete.end event, we don't get any IP info, just hostname
    logger.debug("in compute_instance_delete_end()")

    #
    # Incorporate interfacing modules here
    #

    #
    # ex. Remove host info from PowerDNS MySQL backend
    import modules.powerdns.powerdns as powerdns, modules.powerdns.powerdns_config as powerdns_config
    db_powerdns_config = powerdns_config.get_db_powerdns_config()
    db_powerdns = mysql.db(db_powerdns_config['host'],db_powerdns_config['user'],db_powerdns_config['pass'],db_powerdns_config['db'])
    logger.info("Removing host record from DNS database.")
    remove_name = body['payload']['hostname']
    #try:
    powerdns.remove_record(remove_name,'domain_name','A')
    #except
    #   blah

    # returning true will signal to calling function to ACK rabbitmq message
    return True

def add_context_to_db(body):
    #
    # add info to openstacktrack db
    #

    # get openstacktrack db config and open connection
    db_openstacktrack = get_openstacktrack_conf()
    db_track = mysql.db(db_openstacktrack['host'],db_openstacktrack['user'],db_openstacktrack['pass'],db_openstacktrack['db'])

    # some data isn't present in every message
    if '_context_request_id' in body:
        context_request_id = body['_context_request_id']
    else:
        context_request_id = ''
    if '_context_user_name' in body:
        context_user_name = body['_context_user_name']
    else:
        context_user_name = ''
    if '_context_remote_address' in body:
        context_remote_address = body['_context_remote_address']
    else:
        context_remote_address = ''

    event_type = body['event_type']
    publisher_id = body['publisher_id']
    timestamp =body['timestamp']

    query = """INSERT INTO track 
                (context_request_id,context_user_name,context_remote_address,event_type,publisher_id,timestamp) 
                VALUES ('%s','%s','%s','%s','%s','%s')""" % 
                (context_request_id,context_user_name,context_remote_address,event_type,publisher_id,timestamp)
    logger.debug("Executing query: %s" % query)

    results = db_track.query(query)
    track_id = results['last_id']


    # add json body to message table
    query = """INSERT INTO message (track_id,message) VALUES (%i,"%s")""" % (track_id,body)
    logger.debug("Executing query: %s" % query)
    results = db_track.query(query)

    # return db id
    return track_id

def process_event(body):

    logger.debug("BODY: %s" % (json.dumps(body)))

    if config.config['pitchfork']['track']:
        # add event info to db
        db_id = add_context_to_db(body)

    event_type = body['event_type']

    logger.info("Working on event type %s" % event_type)

    if event_type == 'compute.instance.create.end':
        logger.info("Message BODY: %r" % body)
        try:
            compute_instance_create_end(body)
            # this will ack the message
            return True
        except:
            logger.error("Error processing message")
            return False
    elif event_type == 'compute.instance.delete.end':
        try:
            compute_instance_delete_end(body)
            # this will ack the message
            return True
        except:
            logger.error("Error processing message")
            return False
    else:
        logger.info("no processing required for event type %s" % event_type)
        # go ahead and ack the message
        return True
