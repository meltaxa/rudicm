#!/usr/bin/env python

import os
import logging
from . import runner

class Task():

    def __init__(self,target_ip,username,password):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.target_ip = target_ip
        self.logger = logging.getLogger(__name__)
        self.run = runner.Task(target_ip,username,password)

    def action(self,options):
        '''Task to perform service command actions.
           name: <service> The service daemon.
           action: <stop|start|restart|reload> action to perform.
           local: <boolean> indicates if the task should run locally. Default is False.
        '''
        name = options['name']
        action = options['action']
        cmd = "sudo service %s %s" % (name, action)
        try:
            run_local = options['local']
        except KeyError:
            run_local = False
        if run_local:
            stdout, rc = self.run.local(cmd)
        else:
            stdout, rc = self.run.ssh(cmd)
        if rc == 0:
            self.logger.info('Exit code: ' + str(rc))
        else:
            self.logger.error('Exit code: ' + str(rc))
        return rc, cmd
