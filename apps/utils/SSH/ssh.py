__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

import re
import os
import scp
import time
import pysftp
import select
import paramiko
import logging
from pegasusautomation import settings
from apps.vmm.models import VM
from pssh.clients import ParallelSSHClient
from apps.secrets.secrets import SecretsDB
import platform  # For getting the operating system name
import subprocess

# logger
logger = logging.getLogger(__name__)


class SSHCmd:
    result_path_local = os.path.join(settings.BASE_DIR, "results")


class SSHConnection:
    """
        Class allows ssh connections to machines
    """

    def __init__(self, vm=None):
        try:

            self.vm = vm
            self.vm_tag = self.get_vm_tag()
            self.config = SSHCmd
            self.cnopts = pysftp.CnOpts()
            self.cnopts.hostkeys = None
            self.ip, self.user, self.passwd = self.parse_vm_creds(vm)
            logger.info("Building SSH connection with Remote machine {vm}: {ip} {user}".format(vm=self.vm, ip=self.ip,
                                                                                               user=self.user))

            self.db = SecretsDB()

            self.passwd = self.db.get_password_model(vm=self.vm)
            self.client = self.ssh_connect()

        except Exception as e:
            logger.error('ssh connection failure on vm {}. Error {}'.format(self.vm, e))

    def get_vm_tag(self):
        """"""

        try:
            vm_obj = VM.objects.filter(vm_name=self.vm).values('tag')
            for vmobj in vm_obj:
                return vmobj['tag']
        except Exception as e:
            return "win"

    def keep_channel_alive(self):

        chan = self.client.invoke_shell()
        resp = chan.recv(9999)

        while True:
            chan.send_ready()
            chan.send('copy running-config tftp\n')
            time.sleep(3)
            # logger.warning("Keep the channel alive")
            resp = chan.recv(9999)

    def __del__(self):
        self.client.close()

    @staticmethod
    def parse_vm_creds(vm):
        vm_group = VM.objects.get(vm_name=vm)
        return vm_group.ip, vm_group.user, vm_group.password

    def connection_client(self):
        return self.client

    def connection_sftp(self):
        sftp = None
        try:
            sftp = self.client.open_sftp()
        except Exception as e:
            logger.error('STFP failure'.format(e))
        return sftp

    def connection_check(self):
        try:
            stout = self.execute_command(cmd="echo risa", console=True)
            if "risa" in str(stout):
                return True

        except Exception as e:
            logger.error(e)

        return False

    def setup(self):
        self.mkdir_base_path()

    def mkdir_base_path(self):
        if self.vm_tag == "win":

            self.execute_command(r"mkdir {win_path}".format(win_path=settings.BASE_DIR_WIN))
            self.execute_command(r"mkdir {win_path}".format(win_path=settings.BASE_DIR_WIN_RESULTS))
        else:

            self.execute_command(r"mkdir {win_path}".format(win_path=settings.BASE_DIR_MAC))
            self.execute_command(r"mkdir {win_path}".format(win_path=settings.BASE_DIR_MAC_RESULTS))

        if not os.path.exists(os.path.join(self.config.result_path_local, str(self.vm))):
            os.mkdir(os.path.join(self.config.result_path_local, str(self.vm)))

    def ping_test(self):
        """
        Returns True if host (str) responds to a ping request.
        """

        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower() == 'windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', self.ip]

        return subprocess.call(command) == 0

    def ssh_connect(self):
        try:

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.ip, username=self.user, password=self.passwd, timeout=60, banner_timeout=100)

            counter = 0

            while not client and counter <= 2:
                logger.warning("SSH failure. Trying again...")
                time.sleep(30)

                client.connect(hostname=self.ip, username=self.user, password=self.passwd, timeout=60,
                               banner_timeout=100)
                counter += 1

            logger.info("SSH connection successful with machine {ip}".format(ip=self.ip))
            return client
        except paramiko.BadHostKeyException as e:
            # if the server’s host key could not be verified
            logger.error("SSH bad key exception {}".format(e))
        except paramiko.AuthenticationException as e:
            # if authentication failed
            logger.error("SSH Auth error {}".format(e))
        except paramiko.SSHException as e:
            # if there was any other error connecting or establishing an SSH session
            logger.error("SSH Exception error {}".format(e))
        # except paramiko.socket.error as e:
        #     if a socket error occurred while connecting
        # logger.error("SSH socket error {}".format(e))
        except Exception as e:
            logger.error("SSH Error : {}".format(e))
        return None

    def mkdir(self, path):
        try:
            return self.sftpy.mkdir(path)
        except Exception as e:
            obj = SSHConnection(self.vm)
            return obj.sftpy.mkdir(path)
        return False

    def file_size(self, path):
        try:
            if self.path_exists(path):
                info = self.sftpy.stat(path)
                return info.st_size
        except Exception as e:
            pass
            # logger.error("Dir {} cannot be created. Error : {}".format(path, e))
        return 0

    def get_hostname(self):
        out, err, rc = self.execute_command(cmd=" hostname")
        if rc == 0:
            return out.readlines()
        else:
            return None

    def disconnect(self):
        if self.client:
            self.client.close()
        if self.sftpy:
            self.sftpy.close()  # close your connection to hostname

