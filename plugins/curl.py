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
        '''This is a task template.
           Clone this template and change the cmd and allow options accordingly.
           local: <boolean> indicates if the task should run locally. Default is False.
           url: http://%TARGET_IP% is the endpoint to check. The %TARGET_IP% is a special token.
           code: <int> is the HTTP response status code to expect. Default is 200.
           response: <string> is the response string to expect. Optional.
        '''
        url = options['url'].replace('%TARGET_IP%', self.target_ip)
        cmd = 'curl -sv %s' % url
        try:
            run_local = options['local']
        except KeyError:
            run_local = False
        try:
            code = options['code']
        except KeyError:
            code = 200
        try:
            response = options['response']
        except KeyError:
            response = None
        if run_local:
            stdout, rc = self.run.local(cmd)
        else:
            stdout, rc = self.run.ssh(cmd)
        print(stdout)
        if ("HTTP/1.1 %s" % code) not in stdout:
            self.logger.error('HTTP response status code %s not returned.' % code)
            rc = 1
        else:
            self.logger.info('PASSED: status code %s returned.' % code)
        if response is not None and response not in stdout:
            self.logger.error('Response string "%s" not returned.' % response)
            rc = 1
        elif response is not None:
            self.logger.info('PASSED: response string %s returned.' % response)
        if rc == 0:
            self.logger.info('Exit code: ' + str(rc))
        else:
            self.logger.error('Exit code: ' + str(rc))
        return rc, cmd
