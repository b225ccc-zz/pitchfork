#!/usr/bin/python
#
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import sys
import logging

logger = logging.getLogger('root')

try:
    import MySQLdb
    HAS_MYSQL_MODULE = True
except ImportError:
    print "Can't import module MySQLdb"
    #logger.error("Can't import module MySQLdb")
    HAS_MYSQL_MODULE = False

class db:
    
    def __init__(self, host, username, password, database):

        self.host = host
        self.username = username
        self.password = password
        self.database = database

        # on instantiation, connect to db
        self.connect()

    def connect(self):

        # set up dns database connection
        try:
            #print "attempting conn to %s on host %s" % (self.database,self.host)
            logger.debug("attempting conn to %s on host %s" % (self.database,self.host))
            self.connection = MySQLdb.connect(
                host=self.host,
                user=self.username,
                passwd=self.password,
                db=self.database,
            )
        except (AttributeError, MySQLdb.OperationalError), e:
            #raise e
            #logger.error(str(e))
            #print "db connect failed.  bailing"
            logger.error('db connect failed.  bailing')
            sys.exit(1)

        #print 'db connection successful'
        logger.debug('db connection successful')

    def escape_string(self, query):
        return self.connection.escape_string(query)

    def query(self, query):

        try:
            logger.debug("attempting query '%s'" % query)
            cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
            #cursor.escape_string(query)
            cursor.execute(query)
        #    last_id = self.connection.insert_id()
        #    self.connection.commit()
        except (AttributeError, MySQLdb.OperationalError) as e:
            #print 'exception generated during sql query: ', e
            print 'attempting reconnect'
            self.connect()
            # get new cursor
            cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
            # need to re-execute query
            print 're-executing query'
            cursor.execute(query)

        last_id = self.connection.insert_id()
        self.connection.commit()

        results = cursor.fetchall()

        numrows = cursor.rowcount

        cursor.close()
        logger.debug("returning results")
        #return (last_id,results)
        return {'last_id': last_id, 'numrows': numrows, 'results': results}


    def close(self):
        try:
            logger.debug("attempting connection close")
            self.connection.close()
        except (AttributeError, MySQLdb.OperationalError) as e:
            raise e

