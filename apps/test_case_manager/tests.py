import os
import logging
import unittest
# from ..vmm.models import VM
from pegasusautomation import settings
# from ..vmm.utils import SSHConnection
from ..windows_manager.utils.winsat import WinSATCmd
from .apps import sanity_testconfig, perf_testconfig
from ..windows_manager.utils.powershell import PowershellCmd
from ..windows_manager.utils.commandprompt import CommandPromptExecution, CommandPromptCmd


# logger
logger = logging.getLogger("test_case_manager")

# Instance of powershell execution class model
pwrshell = PowershellCmd()
cmdprompt = CommandPromptExecution()
cmd_command = CommandPromptCmd()
winsat = WinSATCmd()


class PerformanceWinSATTests(unittest.TestCase):

    def test_winsat_setup(self):
        """ create folder """
        if not os.path.exists(self.perf_testconfig.perf_resultfolder_nodec):
            os.mkdir(self.perf_testconfig.perf_resultfolder_nodec)
        self.assertTrue(os.path.exists(self.perf_testconfig.perf_resultfolder_nodec))

    def test_monitoring_script_running(self):
        """ check if the pre-req files are present"""
        if not self.conn.path_exists(self.perf_testconfig.winsat_monitor):
            self.assertTrue(self.conn.copy_data_to_vm(local_path=self.perf_testconfig.winsat_monitor_local,
                                      remote_path=self.perf_testconfig.winsat_monitor))

    def test_run_monitoring(self):
        """ run the monitoring script """

        cmd = "cmd.exe /c echo {} > run.bat & run.bat".format(self.perf_testconfig.winsat_monitor)
        logger.debug(cmd)
        self.assertTrue(self.conn.execute_command(cmd=cmd, get_pty=True))

    def test_file_titles_correct_generated(self, title):
        logger.info("[VM {vm}] Retrieving winsat test results from remote machine.".format(vm=self.vm.upper(), ))
        assert title == self.perf_testconfig.perf_resultpath_nodec.format(title)

    def test_winsat_signal_recieved(self, title):
        self.conn.execute_command(cmd=self.perf_testconfig.kill_previous)
        signal = '{}\{}.txt'.format(self.perf_testconfig.send_signal, title)
        self.assertTrue(self.conn.execute_command(cmd=signal))


if __name__ == '__main__':
    unittest.main()