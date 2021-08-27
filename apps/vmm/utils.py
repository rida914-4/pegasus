__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

import paramiko
import atexit
import logging
from pyVmomi import vim
from .models import VM
from pyVim import connect
from apps.utils.SSH.ssh import SSHConnection
from apps.utils.psexec.psexec import PsExecConnection
from pyVim.connect import Disconnect
from pegasusautomation import settings
from background_task import background
from django.http import HttpResponse

MAX_DEPTH = 10


# # Get an instance of a logger
logger = logging.getLogger("vmm")


def exception_handler(func):
    def called_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.debug("{} {error}".format(func.__name__, error=e))
            logger.error(e)
    return called_function


class ESXI:

    server_ip = settings.server_ip
    server_public_ip = settings.server_public_ip
    server_name = settings.server_name
    server_user_name = settings.server_user_name
    server_passwd = ''
    server_port = settings.server_port

    vm_port = 443



esxi_config = ESXI()


class VmmUtils:

    def __init__(self):
        try:
            self.host = None
            # self.host = self.connect_to_server()
            # self.vms = self.get_vm_detailed_info()


        except Exception as e:
            logger.error("Virtual Machine Manager failure.")

    def print_vm_info(self, vm, depth=1):
        """
        Print information for a particular virtual machine or recurse into a folder
        with depth protection
        """

        # if this is a group it will have children. if it does, recurse into them
        # and then return
        if hasattr(vm, 'childEntity'):
            if depth > MAX_DEPTH:
                return
            vmlist = vm.childEntity
            for child in vmlist:
                self.print_vm_info(child, depth + 1)
            return

        return vm.summary

    @staticmethod
    def connect_to_server():
        """
            connect to Host ESXi server
        :return: 
        """
        host = None
        try:
            host = connect.SmartConnectNoSSL(host=esxi_config.server_ip, port=esxi_config.server_port,
                                      user=esxi_config.server_user_name,
                                      pwd=keyring.get_password(esxi_config.server_ip, esxi_config.server_user_name),)
        except Exception as e:
            host = connect.SmartConnectNoSSL(host=esxi_config.server_public_ip, port=esxi_config.server_port,
                                      user=esxi_config.server_user_name,
                                      pwd=keyring.get_password(esxi_config.server_ip, esxi_config.server_user_name))
        if not host:
            logger.error("Cannot Connect to ESXI server {ip} (Username : {name})".format(ip=esxi_config.server_ip,
                                                                                           name=esxi_config.server_user_name))

        return host

    def get_vm_detailed_info(self):
        """
            Get virtual machine list
        :return:
        """
        vm_info = list()
        atexit.register(Disconnect, self.host)
        content = self.host.RetrieveContent()
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vm_folder = datacenter.vmFolder
                vm_list = vm_folder.childEntity
                for vm in vm_list:
                    vm_info.append(self.print_vm_info(vm))
        return vm_info

    def get_vm_list(self):
        """ Get name list of all vms on ESXI server"""
        return [vm.config.name for vm in self.vms]

    def get_vm_state(self):
        return [vm.guest.guestState for vm in self.vms]

    def create_snapshot(self):
        try:
            vm = self.host.content.searchIndex.FindByUuid(None, '5241b35f-691f-55ea-f0a4-f4f36bb80abd', True, True)

            if vm is None:
                raise SystemExit("Unable to locate VirtualMachine.")

            task = vm.CreateSnapshot_Task(name='testautomatio',
                                          description='desc',
                                          memory=True,
                                          quiesce=True
                                          )
            logger.debug("Snapshot Completed.")
            del vm
            vm = self.host.content.searchIndex.FindByUuid(None, '5241b35f-691f-55ea-f0a4-f4f36bb80abd', True, instance_search=True)
            snap_info = vm.snapshot

            tree = snap_info.rootSnapshotList
            while tree[0].childSnapshotList is not None:
                logger.debug("Snap: {0} => {1}".format(tree[0].name, tree[0].description))
                if len(tree[0].childSnapshotList) < 1:
                    break
                tree = tree[0].childSnapshotList
        except Exception as e:
            logger.debug(e)

    def revert_snapshot(self):
        try:
            snapshot_name = "test"
            atexit.register(Disconnect, self.host)

            # Retreive the list of Virtual Machines from the inventory objects
            # under the rootFolder
            content = self.host.content
            objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                              [vim.VirtualMachine],
                                                              True)
            vmList = objView.view
            objView.Destroy()

            for vm in vmList:

                try:
                    if "workstation" in vm.name and  "clone" in vm.name:
                        snapshots = vm.snapshot.rootSnapshotList
                        # logger.debug("VM {}, Snapshots {}".format(vm.name, snapshots))
                        for snapshot in snapshots:
                            logger.debug(snapshot.name)
                            if snapshot_name == snapshot.name:
                                snap_obj = snapshot.snapshot
                                logger.debug("Reverting snapshot ", snapshot.name)
                                task = [snap_obj.RevertToSnapshot_Task()]
                                # WaitForTasks(task, si)
                except Exception as e:
                    continue
        except Exception as e:
            logger.debug(e)




# class SSHConnection:
#     """
#         Class allows ssh connections to machines
#     """
#     def __init__(self, vm=None):
#         try:
#             logger.debug('yyyyyyyyy')
#             self.vm = vm
#             logger.info("SSH connection creation for VM : {}".format(self.vm))
#             self.ip, self.user, self.password = self.vm.ip, self.vm.user, self.vm.password
#             logger.debug("Building SSH connection with Remote machine {vm}: {ip}".format(vm=self.vm, ip=self.ip))
#             logger.info("Building SSH connection with Remote machine {vm}: {ip}".format(vm=self.vm, ip=self.ip))
#             self.client = self.ssh_connect()
#             try:
#                 self.sftp = self.client.open_sftp()
#             except Exception as e:
#                 logger.error('STFP failure'.format(e))
#
#         # client.close()
#
#         except Exception as e:
#             logger.error('ssh connection failure on vm {}. Error {}'.format(self.vm, e))
#
#     def connection_client(self):
#         return self.client
#
#     def connection_sftp(self):
#         return self.sftp
#
#     def connection_check(self):
#         return self.client
#
#     def ssh_connect(self):
#         try:
#             client = paramiko.SSHClient()
#             client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#             client.connect(hostname=self.ip, username=self.user, password=self.password)
#             logger.info("SSH connection successful with machine {ip}".format(ip=self.ip))
#             return client
#         except Exception as e:
#             logger.error("Error : {}".format(e))
#             return None
#
#     def copy_data_to_vm(self, local_path, remote_path):
#         try:
#             scp_client = scp.SCPClient(self.client.get_transport())
#             scp_client.put(local_path, recursive=True, remote_path=remote_path)
#             scp_client.close()
#         except Exception as e:
#             logger.error("Cannot copy data to remote machine ({}). Error : {}".format(remote_path, e))
#
#     def copy_data_from_vm(self, local_path, remote_path):
#         try:
#             scp_client = scp.SCPClient(self.client.get_transport())
#             scp_client.get(remote_path, local_path, recursive=True)
#             scp_client.close()
#         except Exception as e:
#             logger.error("Cannot copy data from remote machine ({}) to local path {}. Error : {}".format(remote_path, local_path, e))
#
#     def execute_command(self, cmd='', get_pty=True):
#
#         if not self.client:
#             logger.error('SSH connection failure!')
#             return False
#
#         output, error = '', ''
#         stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=get_pty)
#         channel = stdout.channel
#
#         if get_pty:
#             exit_status = channel.recv_exit_status()
#
#             while not stdout.channel.exit_status_ready():
#
#                 # Only print data if there is data to read in the channel
#                 if stdout.channel.recv_ready():
#                     rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
#                     if len(rl) > 0:
#                         # Print data from stdout
#                         output = stdout.channel.recv(1024)
#                         logger.info(output)
#
#             while not stderr.channel.exit_status_ready():
#
#                 # Only print data if there is data to read in the channel
#                 if stderr.channel.recv_ready():
#                     rl, wl, xl = select.select([stderr.channel], [], [], 0.0)
#                     if len(rl) > 0:
#                         # Print data from stdout
#                         error = stderr.channel.recv(1024)
#                         logger.error('Error {}'.format(error))
#
#         return stdin, output, error
#
#     def path_exists(self, path):
#         try:
#             self.sftp.stat(path)
#             return True
#         except Exception as e:
#             logger.warning("{} : {}".format(e, path))
#             return False
#
#     def list_dir(self, path):
#         try:
#             return self.sftp.listdir(path)
#         except Exception as e:
#             logger.error("Dir {} empty. Error : {}".format(path, e))
#         return []
#
#     def rm_dir(self, path):
#         try:
#             return self.sftp.rmdir(path)
#         except Exception as e:
#             logger.error("Dir {} cannot be deleted. Error : {}".format(path, e))
#         return False
#
#     def rm_file(self, path):
#         try:
#             return self.sftp.remove(path)
#         except Exception as e:
#             # logger.error("File {} cannot be deleted. Error : {}".format(path, e))
#             pass
#         return False
#
#     def mkdir(self, path):
#         try:
#             if not self.path_exists(path):
#                 return self.sftp.mkdir(path)
#         except Exception as e:
#             pass
#             # logger.error("Dir {} cannot be created. Error : {}".format(path, e))
#         return False
#
#     def file_size(self, path):
#         try:
#             if self.path_exists(path):
#                 info = self.sftp.stat(path)
#                 return info.st_size
#         except Exception as e:
#             pass
#             # logger.error(" {} file size Error : {}".format(path, e))
#         return 0
#
#     def disconnect(self):
#         self.client.close()


class SFTP:
    """
    Class for interaction with SFTP server. This server hosts various DEC builds
    """

    def __init__(self):
        self.host = settings.SFTP_HOST
        self.user = 'settings.SFTP_USER'
        self.password = 'settings.SFTP_PASS'
        self.sftpconn = self.connect()
        self.sftpc = self.sftpconn.open_sftp()

        self.transport = paramiko.Transport((self.host, 22))
        self.transport.connect(username=self.user, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def connect(self):
        """ connect to the FTP server """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.host, username=self.user, password=self.password)
            logger.info("SFTP connection successful with server {ip}".format(ip=self.host))
            return client
        except Exception as e:
            logger.error("SFTPError : {}".format(e))
            return None

    def get(self, remote_path, local_path):
        """ download a file on SFTP server """
        try:
            self.sftp.get(remote_path, local_path)
        except Exception as e:
            logger.error(
                "Cannot copy data from remote server ({}) to local path {}. Error : {}".format(remote_path, local_path,
                                                                                                e))

        return None

    def put(self, filename):
        """ Upload a file on SFTP server """
        return self.sftp.put(filename)

    def listdir(self, dir):
        """ return a list of files in the directory"""
        try:
            return self.sftp.listdir(dir)
        except Exception as e:
            logger.error('Cannot list remote SFTP server dir {}.{}'.format(dir, e))
            return []

    def path_exists(self, path):
        try:
            self.sftp.stat(path)
            return True
        except Exception as e:
            logger.warning("{} : {}".format(e, path))
            return False

    def disconnect(self):
        """close the connection """
        return self.sftp.close()


# This will run after every minute and save results in VM model
# @background(schedule=60)
def vm_connection_test():
    for vm in VM.objects.all():
        try:
            logger.debug(vm.vm_name)
            if vm.vm_name == "DC-Win10x64" and vm.vm_name != "server2008-R2" and vm.vm_name != "windows-workstation":
                ps = SSHConnection(vm.vm_name)
                vm_obj = VM.objects.get(vm_name=vm.vm_name)
                vm_obj.status = ps.connection_check()
                logger.debug(vm_obj.status)
                vm_obj.tag = ps.client
                vm_obj.save()
                ps.disconnect()
        except Exception as e:
            logger.debug(e)


    return HttpResponse('<h1>Page was found</h1>')


def vm_alive_list():
    results = list()
    for vm in VM.objects.all():
        if vm.status:
            results.append(vm.vm_name)
    return results


def vm_setup():

    for vm in VM.objects.all():
        try:

            if vm.vm_name == "server2008-R2":
                logger.debug(vm.vm_name)
                ps = PsExecConnection(vm.vm_name)
                vm_obj = VM.objects.get(vm_name=vm.vm_name)
                vm_obj.status = ps.connection_check()
                ps.install_ssh()
                # logger.debug(vm_obj.status)
                # vm_obj.tag = ps
                # vm_obj.save()
                ps.disconnect()
        except Exception as e:
            logger.debug(e)
    return HttpResponse('<h1>Page was found</h1>')