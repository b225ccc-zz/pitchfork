#!/usr/bin/python
#
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import time
import logging
import mysql

logger = logging.getLogger('root')

# get openstacktrack config and open connection
db_powerdns = get_db_powerdns_config()
db_dns = mysql.db(db_powerdns['host'],db_powerdns['user'],db_powerdns['pass'],db_powerdns['db'])

powerdns_config = get_powerdns_config()

def remove_record(name,zone,type):

    #query = "DELETE FROM records WHERE name = '%s'" % remove_name
    #results = db_powerdns.query(query)

    pass

def add_record(name,zone,content,type='A',ttl=300):

    # get zone database id
    query = "SELECT id FROM domains WHERE name = '%s'" % zone
    results = db_dns.query(query)
    domain_id = results['results'][0]['id']

    query = "SELECT * FROM records WHERE name='%s.%s' AND content='%s'" % (name,zone,content)
    results = db_dns.query(query)
    numrows = results['numrows']
    if numrows > 0:
        logger.info("Record already exists, skipping.")
        continue
    else:
        t = int(time.time())
        query = "INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES (%i,'%s.%s','A','%s',%i,%i)" % (int(domain_id),host,zone,content,ttl,t)
        results = db_dns.query(query)

    return
