pitchfork
=========

A framework for integrating Openstack with the rest of your systems


### quick start
* clone
* update pitchfork_config.py config['openstack_rabbitmq']

### quick start for tracking
* update pitchfork_config.py - track = True and config['db_track']
* create mysql db/tables

### quickstart for integrations
* update pitchfork_config.py - config['actionable_events']
* update module configs
* update event_driver.py to add actions for event types
