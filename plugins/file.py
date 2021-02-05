#!/usr/bin/env python

import os
import logging
from . import runner
import tempfile

class Task():

    def __init__(self,target_ip,username,password):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.target_ip = target_ip
        self.logger = logging.getLogger(__name__)
        self.run = runner.Task(target_ip,username,password)

    def action(self,options):
        '''Task to delete a file:
           remove: <filename> is the path and filename to be deleted.

           Task to create a file:
           dest: <filename> is the path and filename for the new file.
           owner: <owner> is the username for ownership.
           group: <group> is the group name for group ownership.
           perms: <int> the chmod values for file mode.
           content: <text> contains the text in the new file.

           Additional Task options:
           local: <boolean> indicates if the task should run locally. Default is False.
        '''

        try:
            remove = options['remove']
            cmd = "rm -f %s" % remove
        except KeyError:
            pass

        try:
            content = options['content']
            dest = options['dest']
            owner = options['owner']
            group = options['group']
            perms = options['perms']
            tf, src = tempfile.mkstemp()
            f = open(tf,"w+")
            f.writelines(content)
            f.close()
           # cmd = 'echo "%s" > %s' % (content, options['dest'])
            cmd = 'create'
        except KeyError:
            pass

        try:
            run_local = options['local']
        except KeyError:
            run_local = False
        if run_local:
            if cmd == 'create':
                stdout, rc = self.run.local('mv %s %s' % (src, options['dest']))
            else:
                stdout, rc = self.run.local(cmd)
        else:
            if cmd == 'create':
                stdout, rc = self.run.sftp(src,dest,owner,group,perms)
                os.remove(src)
            else:
                stdout, rc = self.run.ssh(cmd)
        if rc == 0:
            self.logger.info('Exit code: ' + str(rc))
        else:
            self.logger.error('Exit code: ' + str(rc))
        return rc, cmd
