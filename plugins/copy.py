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
        '''Task to copy files from src to dest and apply metadata.
           src: <filename> is the source path and filename.
           dest: <filename> is the destinate path and filename.
           owner: <username> is the Ubuntu user who will own the file.
           group: <group> is the Ubuntu group the file belongs too.
           perms: <int> is the chmod mode permsions of the file, eg: 750.
           local: <boolean> indicates if the task should run locally. Default is False.
        '''
        try:
            run_local = options['local']
        except KeyError:
            run_local = False
        src = options['src']
        dest = options['dest']
        owner = options['owner']
        group = options['group']
        perms = options['perms']
        if run_local:
            stdout, rc = self.run.local("cp " + src + " " + dest)
        else:
            stdout, rc = self.run.sftp(src,dest,owner,group,perms)
        if rc == 0:
            self.logger.info('Exit code: ' + str(rc))
        else:
            self.logger.error('Exit code: ' + str(rc))
        return rc, run_local
