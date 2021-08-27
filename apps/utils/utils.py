__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

import os
import logging
import configparser
from apps.utils.SSH.ssh import SSHConnection
from itertools import chain, starmap

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
import subprocess, platform

# logger
logger = logging.getLogger("testcaseManager")


class ManagementCmd:
    """
        Uninstall when the original msi file is not available
        > msiexec /x .msi /passive /l*v .uninstall.log
        At command prompt (64 bit Windows systems):
        > msiexec /x
        > msiexec /x {91FED0E7-BBDF-4FFF-B296-0F77C1B4A3CF} /passive /l*v Peagasus.uninstall.log
        At command prompt (64 bit Windows systems):
        > msiexec /x {91FED0E7-BBDF-4FFF-B296-0F77C1B4A3CF} /passive /l*v Peagasus.uninstall.log
        PeagasusMicroAgentX64.msi /passive /l*v PeagasusMicroAgent.uninstall.log
    """
    server_ip = "<ip>"
    cmd = "cmd.exe /c  {} "
    cmdf = "run.bat > {}"
    msi = "Peagasus.msi"
    agent_SFTP_BUILD_PATH = "/filetransfer/Images/Windows/6.0"

    # Network mappings
    shared_folder = "/home/agent-pegasus/pegasus-automation/shared"
    shared_unc = r"\\{server_ip}\shared".format(server_ip=server_ip)

    # pegasus agent settings
    agent_RECIEVER = 'pegasussystems.com'

    # SFTP server where the agent builds are pulled from
    SFTP_HOST = "<ip>"
    SFTP_USERNAME = "pegasus"

    # Samba
    network_share = r"\\{server_ip}\shared".format(server_ip=server_ip)
    samba_user = "Peagasus"

    # Custom win Paths
    BASE_DIR = r"C:\automation-data"
    BASE_DIR_WIN = r"C:\automation-data"
    log_name = "PeagasusMicroAgent.log"
    cmd_log_name = "cmd.log"
    installation_path = os.sep.join([BASE_DIR_WIN])

    msi_path = os.sep.join([installation_path, msi])
    buildpath_remote = agent_SFTP_BUILD_PATH
    buildpath_local = os.path.join("installers")
    if not os.path.exists(buildpath_local):
        os.mkdir(buildpath_local)

    log_path = '{}\{}'.format(installation_path, log_name)
    cmd_log_path = '{}\{}'.format(installation_path, cmd_log_name)
    run_file = os.sep.join([BASE_DIR_WIN, "run.bat"])

    generic_command = "  /passive ADDRESS=\"{}\" accountname=\"{}\" password=\"{}\" /l*v {}".format(agent_RECIEVER,
                                                                                                    'agent_USERNAME',
                                                                                                    'agent_PASSWORD',
                                                                                                    log_path)
    install_dec = cmd.format('msiexec /i {}'.format(generic_command))
    uninstall_dec = cmd.format('msiexec /x {}'.format(generic_command))
    update_dec = cmd.format("msiexec /i {}".format(generic_command))

    # check_system_driver = "sc query CoreSystemFlt"
    check_network_driver = "sc query CoreNetworkFlt"

    check_system_driver = "sc query WindowsEventReportingFSfilterdriver"

    dec_cmdline = r'ConfigurationCmd.exe'

    dec_version = " -version"
    dec_info = " -info "

    # custom local paths
    test_results = os.path.join(BASE_DIR, "install_agent", "results")
    local_log_path = os.path.join(test_results, log_name)
    local_cmd_log_path = os.path.join(test_results, cmd_log_name)


def json_get_tag_value(dictionary):
    """Flatten a nested json file"""

    def unpack(parent_key, parent_value):
        """Unpack one level of nesting in json file"""
        # Unpack one level only!!!

        if isinstance(parent_value, dict):
            for key, value in parent_value.items():
                temp1 = parent_key + '_' + key
                yield temp1, value
        elif isinstance(parent_value, list):
            i = 0
            for value in parent_value:
                temp2 = parent_key + '_' + str(i)
                i += 1
                yield temp2, value
        else:
            yield parent_key, parent_value

            # Keep iterating until the termination condition is satisfied

    while True:
        # Keep unpacking the json file until all values are atomic elements (not dictionary or list)
        dictionary = dict(chain.from_iterable(starmap(unpack, dictionary.items())))
        # Terminate condition: not any value in the json file is dictionary or list
        if not any(isinstance(value, dict) for value in dictionary.values()) and \
                not any(isinstance(value, list) for value in dictionary.values()):
            break

    return dictionary


def ping_test(sHost):
    try:
        subprocess.check_output("ping -{} 3 {}".format('n' if platform.system().lower() == "windows" else 'c', sHost),
                                shell=True)

    except Exception as e:
        return "VM inaccessible on the network. PING failure."

    return "VM accessible on the Network. Check main.log for connection errors. " \
           "(Make sure Windows2008 and Win7 vms are named properly. Check README.)"
