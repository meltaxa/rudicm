#!/usr/bin/env python

import importlib
import argparse
import plugins.config as conf
import logging

logger = logging.getLogger(__name__)

def load_task(nested_dictionary,nest=False):
    '''Construct Runbook tasks
    '''
    global task_name
    global task_plugin
    global task_options
    task_name = {}
    task_options = {}

    for key, value in nested_dictionary.items():
        if key == 'name':
            task_title = value
            continue
        if type(value) is dict:
            task_name = key
            try:
                task_plugin = importlib.import_module('plugins.' + key)
            except Exception as e:
                logger.error('No ' + key + ' plugin found: ' + e)
                task_name = {}
                break
            task_options=value
        else:
            globals()[key] = value
    return task_title,task_name

def runBook(server_name,server_ip,username,password,runbook,runbook_tags):
    '''Execute Runbook tasks. 
       Only run tagged tasks.
    '''
    logger.info('=== RUNBOOK ON %s ===' % server_name)
    runbook = conf.Config('runbooks/' + runbook)
    runbook.load_config()
    tasks = runbook.config
    for task in tasks:
        title, name = load_task(task)
        try:
            tags = task_options['tag']
        except Exception as e:
            tags = []
        if 'never' not in tags:
            tags.append('always')
        if runbook_tags not in tags:
            logger.warning('=== SKIP TASK: %s ===' % title)
            continue
        # Run task
        if task_name != {}:
            logger.info('=== TASK: %s ===' % title)
            runTask = task_plugin.Task(server_ip,username,password)
            rc, cmd = runTask.action(task_options)
            if int(rc) != 0:
                logger.error('=== STOPPING RUNBOOK ===')
                break

def main():
    '''Invoke a RudiCM runbook.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--servers", help="The file containing a list of servers.",
                        action='store', type=str, required=True)
    parser.add_argument("-r", "--runbook", help="The runbook to play.",
                        action='store', type=str, required=True)
    parser.add_argument("-t", "--tag", help="Limit run to tagged tasks.",
                        action='store', type=str, default='always')
    parser.add_argument("-i", "--ip", help="Limit run to host ip only.",
                        action='store', type=str, default='all')

    args = parser.parse_args()

    inventory = conf.Config('servers/%s' % args.servers)
    inventory.load_config()
    servers = inventory.config

    for server in servers['servers']:
        server_ip = servers['servers'][server]['ip']
        if args.ip == 'all' or args.ip == server_ip:
            username = servers['servers'][server]['username']
            password = servers['servers'][server]['password']
            runBook(server,server_ip,username,password,args.runbook,args.tag)
        else:
            logger.info('=== SKIP RUNBOOK ON %s ===' % server_ip)
    logger.info('=== RUDICM FINISED ===')

if __name__ == '__main__':
    main()
