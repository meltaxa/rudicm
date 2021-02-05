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
        '''Task to create a symlink. 
           file: <filename> is the source of the real file to be linked.
           link: <filename> will be the symbolic link that points to "file".
           local: <boolean> indicates if the task should run locally. Default is False.
        '''
        try:
            run_local = options['local']
        except KeyError:
            run_local = False
        file = options['file']
        link = options['link']
        cmd = "ln -sf %s %s" % (file, link)
        if run_local:
            stdout, rc = self.run.local(cmd)
        else:
            stdout, rc = self.run.ssh(cmd)
        if rc == 0:
            self.logger.info('Exit code: ' + str(rc))
        else:
            self.logger.error('Exit code: ' + str(rc))
        return rc, cmd
