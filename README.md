# RudiCM

RudiCM is a Rudimentry Configuration Management (CM) tool inspired by Ansible, Chef
and Puppet.

It is a lightweight CM tool written in Python, designed specifically to address a 
particular problem, to install on two hosts, a production PHP service with it's own 
index.php web page. The challenge was to use abstraction like other CM tools to 
deploy and configure the stack.

# Terminology

To avoid confusion with other CM tool terms such as inventory, recipe, manifest, 
classes, module, roles and playbooks, RudiCM attempts to use terminology that isn't
already taken but still intuitive:

* Task:    A job that is executed to perform a specific function.
* Plugin:  A script providing interfaces for tasks.
* Runbook: An ordered list of tasks to perform.
* Target:  A target server which is grouped with like minded servers.

# Architecture

RudiCM runs on a single "master" host and makes ssh connections to targets to run tasks.

The application is configurable using YAML files. 

Plugins are extensible. To create a new plugin, copy the files/template.py file and
edit the new file accordingly to provide a new interface for a task.

Example plugin:

```
def action(self,options):
    '''Task to perform service command actions.
       name: <service> The service daemon.
       action: <stop|start|restart|reload> action to perform.
       local: <boolean> indicates if the task should run locally. Default is False.
    '''
    name = options['name']
    action = options['action']
    cmd = "sudo service %s %s" % (name, action)
```

Using YAML files for server and runbook configurations along with the extensible
plugin architecture allows RudiCM to be intuitive to use and be easily maintainable. 

Example runbook task:

```
- name: Reload Apache
  service:
    name: apache2
    action: reload
```

# Installation

RudiCM requires Python 3 and the Paramiko library to handle ssh.

Untar the RudiCM package and run the bootstrap.sh script to install the
required dependancies:

Run:
```
tar -xf rudicm.tar
cd rudicm
source bootstrap.sh
```

After the bootstrap.sh script is run, you should be in a Python 3 virtual environment.
To manually enter the environment, use the following command:

```
source ~/venv/bin/activate
```

Update the targets/webservers.yml file with the target ip addresses and credentials for access.

There are two runbooks under the runbooks directory: uptime.yml and challenge.yml. 

Before we run the challenge, let's ensure we can connect to the targets using the uptime
runbook:

```
./rudicm.py --targets webservers.yml --runbook uptime.yml
```

As this is the first time running RudiCM, you will notice messages are displayed to the 
console. For posterity, it is logged to a file under the log directory.

The uptime runbook simply executes the uptime command on the target servers. A success 
indicates the master server is able to connect to the two targets using ssh.

# The Challenge

For the purpose of this exercise, RudiCM addresses the following challenge directives:
* Configure two servers for a PHP production service.
* You may use a bootstrap.sh script to install dependencies not found on a normal Ubuntu server.
* Provide an abstraction that allows specifying a file's content and metadata 
  (owner, group, mode)
* Provide an abstraction that allows installing and removing Debian packages.
* Provide some mechanism for restarting a service. 
* Must be idempotent - it must be safe to apply your configuration over and over again.
* Servers must respond 200 OK and include the string "Hello, world!" in their response.

You can now run the challenge runbook which will install a production PHP service and
a custom index.php page:

```
./rudicm.py --targets webservers.yml --runbook challenge.yml
```

The runbook will perform a smoke test to ensure the index page is being rendered correctly. A
success indicates everything has been deployed and functioning as expected.

To uninstall the stack:

```
./rudicm.py --targets webservers.yml --runbook challenge.yml --tag remove
```

Note the use of tags to change the scope of the runbook. Only tasks with the "remove" tag will
be run. By default, all tags except the "never" tag will run.

# Examples:

To update configuration and index files only on all servers:

```
./rudicm.py --targets webservers.yml --runbook challenge.yml --tag update
```

The update tag also runs a task that reloads Apache.

To run an update, say on a canary host only:

```
./rudicm.py --targets webservers.yml --runbook challenge.yml --tag update --ip <ip_address>
```

Replace <ip_address> with one of the servers in the webservers target file.

# Documentation

Although intuitive to use and to write your own plugins, documentation is provided in the source
code.

For example, the copy plugin has the following docstring that defines the interface
between the plugin and the runbook task definition:

```
def action(self,options):
        '''Task to copy files from src to dest and apply metadata.
           src: <filename> is the source path and filename.
           dest: <filename> is the destinate path and filename.
           owner: <username> is the Ubuntu user who will own the file.
           group: <group> is the Ubuntu group the file belongs too.
           perms: <int> is the chmod mode permsions of the file, eg: 750.
           local: <boolean> indicates if the task should run locally. Default is False.
        '''
```

The respective task definition appears in challenge.yml as:

```
- name: Copy custom Apache security.conf
  # Enable production readiness by disabling certain metadata.
  # Demonstrates copy task that also sets file metadata.
  copy:
    src: files/security.conf
    dest: /etc/apache2/conf-available/security.conf
    owner: root
    group: root
    perms: 644
    tag:
      - install
      - update
```
