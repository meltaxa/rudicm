
import os
import logging
import paramiko
import shlex
import subprocess

class Task():

    def __init__(self,target_ip,username,password):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.target_ip = target_ip
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)

    def sftp(self,src,dest,owner,group,perms):
        '''Use SFTP to transfer a file to a remote server.
           Change metadata accordingly.
        '''
        self.logger.info('sftp ' + src + ' ' + dest)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.target_ip, username=self.username, password=self.password)
        stdout, rc = self.ssh("getent passwd " + owner)
        uid = stdout.split(":")[2]
        stdout, rc = self.ssh("getent group " + group)
        gid = stdout.split(":")[2]
        sftp_client = ssh.open_sftp()
        sftp_client.put(src,dest)
        sftp_client.chown(dest,int(uid),int(gid))
        self.ssh("chmod " + str(perms) + " " + dest)
        sftp_client.close()
        ssh.close()
        return '', 0

    def ssh(self,command):
        '''Use SSH to run commands on a remote server.
        '''
        self.logger.info('ssh ' + self.target_ip + " : " + command)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.target_ip, username=self.username, password=self.password)
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        stdin.close()
        output = ''
        while True:
            line = stdout.readline()
            output = output + line
            if not line:
                break
            try:
                print(line.strip())
            except Exception:
                pass
        rc = stdout.channel.recv_exit_status()
        stdout=stdout.readlines()
        ssh.close()
        return output, int(rc)

    def local(self,command):
        '''Run a command locally.
        '''
        self.logger.info('Running locally...')
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf8')
        output = ''
        while True:
            line = process.stdout.readline()
            output = output + line
            if line == '' and process.poll() is not None:
                break
            if line:
                self.logger.info(line.rstrip('\r\n'))
      
        # Prepend stderr to output
        lineerr = process.stderr.readlines()
        if lineerr:
            output = "".join(lineerr) + output
        rc = process.poll()

        return output, int(rc)
