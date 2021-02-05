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
        '''Task to perform apt package manager actions.
           update: <boolean> will perform an apt update. Default if False.
           install: <pkg> will perform an apt install.
           remove: <pkg> will perform an apt remove.
           autoremove: <boolean> will perform an apt autoremove.
           local: <boolean> indicates if the task should run locally. Default is False.
        '''
        try:
            update = options['update']
        except KeyError:
            update = False
        try:
            install = options['install']
            cmd = "sudo apt-get -y install %s" % install
        except KeyError:
            pass
        try:
            remove = options['remove']
            cmd = "sudo apt-get -y remove --purge %s" % remove
        except KeyError:
            pass
        try:
            autoremove = options['autoremove']
            cmd = "sudo apt -y autoremove"
        except KeyError:
            pass
        try:
            run_local = options['local']
        except KeyError:
            run_local = False
        if run_local:
            if update:
                stdout, rc = self.run.local('sudo apt update')
            stdout, rc = self.run.local(cmd)
        else:
            if update:
                stdout, rc = self.run.ssh('sudo apt update')
            stdout, rc = self.run.ssh(cmd)
        if rc == 0:
            self.logger.info('Exit code: ' + str(rc))
        else:
            self.logger.error('Exit code: ' + str(rc))
        return rc, cmd
