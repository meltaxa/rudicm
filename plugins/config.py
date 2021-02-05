#!/usr/bin/env python

import os
import yaml
import logging

class Config():

    def __init__(self,filename):
        self.filename = filename
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = current_dir + '/../' + self.filename
        self.last_updated = ''
        self.log = logging.getLogger(__name__)

    def load_config(self):
        """Load the config file.
        """
        with open(self.config_file, 'r') as stream:
            self.config = yaml.load(stream, Loader=yaml.FullLoader)
        self.log.info('Config ' + self.filename + ' loaded.')
        return self.config
