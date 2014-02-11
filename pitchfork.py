#!/usr/bin/python
# vim: sw=4 sts=4:
#
#
# pitchfork: A framework for integrating Openstack
# with the rest of your systems
#
# Copyright (C) 2014 Photobucket <btalley@photobucket.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from pprint import pprint
import sys
import time
import logging
import pitchfork_config as config
import event_driver

# set up logger
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname) -8s %(asctime)s m:%(module)s f:%(funcName)s l:%(lineno)d: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# get rabbitmq config parameters
rabbitmq_config = config.get_rabbitmq_conf()
# get list of actionable events
actionable_events = config.get_actionable_events()

class Worker(ConsumerMixin):

    nova_x = Exchange('nova', type='topic', durable=False)
    queue_arguments = {'x-ha-policy':'all'}
    info_q = Queue('notifications.info', exchange=nova_x, durable=False, routing_key='notifications.info', queue_arguments=queue_arguments)

    def __init__(self, connection):
        self.connection = connection
        logger.info("Connection to rabbitmq established.  Waiting for messages...")

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[self.info_q], callbacks=[self.on_message])]

    def on_message(self, body, message):
        event_type = body['event_type']
        if event_type in actionable_events:
            if event_driver.process_event(body):
                message.ack()
            else:
                logger.info("Requeing message")
                message.requeue()
                sys.exit(1)

            # message is not actionable, ack
            message.ack()


if __name__ == '__main__':

    def continue_running():
        return True

    def exit_or_sleep(exit=False):
        if exit:
            sys.exit(1)
        time.sleep(5)

    from kombu import Connection
    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='INFO')

    exit_on_exception = True

    while continue_running():
        try:
            with Connection('amqp://%s:%s@%s:%i//' % (
                    rabbitmq_config['user'],
                    rabbitmq_config['pass'],
                    rabbitmq_config['host'],
                    rabbitmq_config['port'])) as conn:
                try:
                    Worker(conn).run()
                except KeyboardInterrupt:
                    print('bye bye')
                    sys.exit()
                except Exception as e:
                    logger.error("!!!!Exception!!!!")
                    logger.exception("exception=%s.  Reconnecting in 5s" % (e))
                    exit_or_sleep(exit_on_exception)
        except:
            logger.error("!!!!Exception!!!!")
            e = sys.exc_info()[0]
            msg = "Uncaught exception: exception=%s. Retrying in 5s"
            logger.exception(msg % (e))
            exit_or_sleep(exit_on_exception)

