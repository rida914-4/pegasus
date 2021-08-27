import os
import re
import json
import time
import ntpath
import configparser
import logging
from flatten_dict import flatten
from flatten_dict import unflatten
from apps.secrets.secrets import SecretsDB
from pegasusautomation import settings
from django.db import models
from apps.vmm.models import VM
from apps.mac.models import MACDiskPerformance
from apps.sanity.sanity import SanityTests, SanityMACTests
from apps.utils.SSH.ssh import SSHConnection, PersistentSSHConnection
from apps.agent_manager.install_agent.manager import ManagementAJAXView
from apps.agent_manager.install_agent.manager import ManagementMACView
from apps.report_manager.translate import Translate
from apps.performance.perfmon import Perfmon
from apps.report_manager.report_manager import ReportManager, make_pdf, write_results, write_pdf_file
from apps.functional.registry.registry import RegistryClass
from apps.functional.event_logger.eventlog import EventLogger
from apps.performance.winsat.performance_tests import PerformanceTests
from apps.performance.network.network import PerformanceNetworkTests
from apps.functional.file_hash.filehash import FileHashActivity
from apps.functional.file_hash.hash import FileHashClass
from apps.performance.fs.fs import DiskpdTesting
from apps.test_beds.models import UserActivity, TestRunActivity, KeyStrokeActivity, PeagasusModules, FileClassification, \
    Client

TestType = [

    ('1', 'sanity'),
    ('2', 'functional'),
    ('3', 'performance'),
    ('4', 'build'),
    ('5', 'custom')
]
logger = logging.getLogger('models')


class Upload(models.Model):
    upload_file = models.FileField()
    upload_date = models.DateTimeField(auto_now_add=True)


class VMLIST(models.Model):
    choice = models.CharField(max_length=154, unique=True)


class Manager(models.Model):
    builds = models.CharField(max_length=60, blank=True, default='', verbose_name="")
    install = models.BooleanField(default=False)
    # name = models.CharField(max_length=60, blank=True, default='', verbose_name="Test Name")


class BuildResult(models.Model):
    vm = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    current_build = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    baseline_build = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    status = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    zip_results = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    # report = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    sanity_details = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    winsat_avg = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    winsat_details = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    network_avg = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    network_details = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    install_code = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    install_result = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    install_info = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    # install_error = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    uninstall_code = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    uninstall_result = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    uninstall_info = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    update_code = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    update_result = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    update_info = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    sanity_load_status = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    sanity_events_status = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    sanity_result_path = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    sanity_pdf_report_self = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    sanity_pdf_report_comp = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    fh_load_status = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    fh_events_status = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    fh_result_path = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    fh_pdf_report_self = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    fh_pdf_report_comp = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    reg_load_status = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    reg_events_status = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    reg_result_path = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    reg_pdf_report_self = models.CharField(max_length=100, blank=True, default='', verbose_name="")
    reg_pdf_report_comp = models.CharField(max_length=100, blank=True, default='', verbose_name="")

    ping = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    install = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    uninstall = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    update = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    winsat = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    network = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    registry = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    filehash = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    eventlog = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")
    sanity = models.CharField(max_length=50, blank=True, default='Pending', verbose_name="")

    class Meta:
        db_table = 'build_result'
        managed = True


class TestSuiteModel(models.Model):
    """
        TestSuite naming convention

    """

    class TestStatus(models.IntegerChoices):
        success = 0
        pending = 1
        running = 2
        error = 3
        aborted = 4

    test_no = models.IntegerField(default=0, null=True)
    # type = models.IntegerField(choices=TestType.choices, blank=True, null=True)
    name = models.CharField(max_length=60, blank=True, default='', verbose_name="Test Name", null=True)
    test_start = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    test_end = models.DateTimeField(blank=True, null=True)
    test_update = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.IntegerField(choices=TestStatus.choices, null=True)
    raw_cmd = models.CharField(max_length=60, blank=True, default='', verbose_name="", null=True)
    agent_version = models.CharField(max_length=60, blank=True, default='', verbose_name="", null=True)
    activity_key = models.CharField(max_length=60, blank=True, default='', verbose_name="", null=True)
    error_msg = models.CharField(max_length=60, blank=True, default='', verbose_name="", null=True)

    # vms = models.ManyToManyField(VMLIST)

    @property
    def vm_list(self):
        #  it loads everything in memory
        test = TestSuite.objects.get(name="DC-Win10x64")
        run_vms = test.vm_list
        return list(self.vms.all())

    def date_now(self):
        return self.time.strftime('%d/%m/%Y %H:%M:%S')

    class Meta:
        managed = True
        db_table = 'testsuite'


class TestSuiteDB(models.Model):
    name = models.CharField(max_length=250, blank=True, default='', verbose_name="Test Name", unique=True)
    type = models.CharField(max_length=250, blank=True, default='', verbose_name="type", null=True, choices=TestType)
    status = models.CharField(max_length=250, blank=True, default='', verbose_name="status", null=True)
    # test_start = models.DateTimeField( blank=True, null=True)
    test_start = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    test_end = models.DateTimeField(blank=True, null=True)
    test_update = models.DateTimeField(blank=True, null=True)
    raw_cmd = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    agent_version = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    # ES key
    activity_key = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    # keywords = models.CharField(max_length=60, blank=True, default='', verbose_name="", null=True)
    error_msg = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    vms = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)

    # msg_detail = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)

    class Meta:
        managed = True
        db_table = 'test'

    def __str__(self):
        return self.name


class BuildTestSuiteDB(models.Model):
    name = models.CharField(max_length=250, blank=True, default='', verbose_name="Test Name", unique=True)
    status = models.CharField(max_length=250, blank=True, default='', verbose_name="status", null=True)
    # test_start = models.DateTimeField( blank=True, null=True)
    test_start = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    test_end = models.DateTimeField(blank=True, null=True)
    test_update = models.DateTimeField(blank=True, null=True)
    raw_cmd = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    agent_version = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    # ES key
    activity_key = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    # keywords = models.CharField(max_length=60, blank=True, default='', verbose_name="", null=True)
    error_msg = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)
    vms = models.CharField(max_length=250, blank=True, default='', verbose_name="", null=True)

    class Meta:
        managed = True
        db_table = 'build_test'

    def __str__(self):
        return self.name


class TestRunActivity:

    def __init__(self, conn, vm, test_id=10, vm_tag=""):

        self.conn = SSHConnection(vm=vm)
        self.vm = vm
        self.vm_tag = vm_tag
        self.test_id = test_id
        self.file_result = list()

        # initialize file activity class
        self.hash = FileHashClass(conn=self.conn)

        # initialize registry class
        self.reg = RegistryClass(conn=self.conn, vm=self.vm)

        # initialize directory class
        self.dir = DirectoryClass(conn=self.conn, vm=self.vm)

        # initialize process class
        self.process = ProcessClass(conn=self.conn, vm=self.vm)

        # initialize network class
        self.network = NetworkClass(conn=self.conn, vm=self.vm)

        # initialize event class
        self.event = EventLogger(conn=self.conn)

        # General Setup
        self.setup()

        # initialize sanity class in case user has not given custom testcases
        self.sanity = SanityTests(conn=self.conn, id=self.test_id, vm=self.vm)

        self.sanity_mac = SanityMACTests(conn=self.conn, id=self.test_id, vm=self.vm)

        self.operations = {

            # File Activity
            'FileCreated': self.file_create,
            'FileCopied': self.file_copy,
            'FileRenamed': self.file_rename,
            'FileMoved': self.file_move,
            'FileDeleted': self.file_delete,

            # Directory Activity
            'DirectoryCreated': self.dir_create,
            'DirectoryRenamed': self.dir_rename,
            'DirectoryMoved': self.dir_move,
            'DirectoryDeleted': self.dir_delete,

            # Registry Activity
            'RegistryKeyCreated': self.reg_create,
            'RegistryKeyDeleted': self.reg_delete,

            # Process Activity
            'ProcessExecuted': self.process_executed,
            'ProcessTerminated': self.process_terminated,

            # Network Activity
            'WebPageAccessed': self.web_page_accesssed

            # Custom Activity

        }

    def setup(self):
        try:
            logger.debug("[VM{}][Test{}] Setup directories for file testing".format(self.vm, self.test_id))
            os.makedirs(self.result_local_folder, exist_ok=True)
            self.conn.rm_file(self.result_remote)
            self.conn.mkdir(self.remote_base)
        except Exception as e:
            logger.error("[VM{}][Test{}] Setup Error : {}".format(self.vm, self.test_id, e))

    def dir_create(self, source, target):
        self.dir.dir_create(source, target)

    def dir_rename(self, source, target):
        self.dir.dir_rename(source, target)

    def dir_move(self, source, target):
        self.dir.dir_move(source, target)

    def dir_delete(self, source, target):
        self.dir.dir_delete()

    # Registry Activity
    def reg_create(self, source, target):
        reg_value, reg_type, data_value = "None", "STRING", "0"
        values = target.split(',')
        # if values >= 3:
        #     reg_value, reg_type, data_value = values[0], values[1], values[2]
        self.reg.set_reg(full_path=source, reg_value=reg_value, reg_type=reg_type, data_value=data_value)

    def reg_delete(self, source, target):
        self.reg.del_reg(source)

    # Process Activity
    def process_executed(self, source, target):
        self.process_executed(source, target)

    def process_terminated(self, source, target):
        self.process_terminated(source, target)

    # Network Activity
    def web_page_accesssed(self, source, target):
        self.web_page_accesssed(source, target
                                )

    def run_sanity(self):
        if self.vm_tag == "mac":

            self.sanity_mac.run_sanity()
        else:
            self.sanity.run_sanity()

    def run_file_activity(self, file_data=None):
        """
        this method accepts a standard data dict and
        runs either predetermined or user specified
        file activities and generates reports,
        """
        logger.debug("[VM{}] [Test{}] ~~~~~~~~~~~~ File Activity ~~~~~~~~~~~~~~".format(self.vm, self.test_id, ))

        # File Setup
        # self.setup_file_settings()

        if not file_data:
            # this is not a custom test case. use sanity/preconfigured file activities
            if self.vm_tag == "mac":

                self.sanity_mac.file_sanity()
            else:
                self.sanity.file_sanity()

        else:
            # clean file data
            # Run File activity
            self.run_operation(tag="File", operation_dict=file_data)

        # save results
        self.save_run_results(result_list=file_data)

    def run_registry_activity(self, data=None):
        """
        this method accepts a standard data dict and
        runs either predetermined or user specified
        registry activities and generates reports,
        """
        # Registry Setup
        if self.vm_tag == "win":
            self.reg.setup_agent_registry_settings()
            self.reg.create_reg_result_remote()

            if not data:
                # this is not a custom test case. use sanity/preconfigured activities
                reg = RegistryClass(self.conn, self.vm, self.test_id, path=None)
                reg.run_registry()

            else:
                # todo: the user specified data e.g keypath value data is combined into a list
                self.run_operation(tag="Registry", operation_dict=data)
        else:
            logger.warning("Registry testcases do not apply on machine type = {}".format(self.vm_tag))

        # save results
        self.save_run_results(result_list=data)

    def run_process_activity(self, data=None):
        """
        this method accepts a standard data dict and
        runs either predetermined or user specified
        process activities and generates reports,
        """
        # process Setup

        if not data:
            # this is not a custom test case. use sanity/preconfigured activities
            if self.vm_tag == "mac":
                self.sanity_mac.process_sanity()
            else:

                self.sanity.process_sanity()
        else:

            self.run_operation(tag="Process", operation_dict=data)

        # save results
        self.save_run_results(result_list=data)

    def run_network_activity(self, data=None):
        """
        this method accepts a standard data dict and
        runs either predetermined or user specified
        network activities and generates reports,
        """
        # network Setup

        if not data:
            # this is not a custom test case. use sanity/preconfigured activities
            if self.vm_tag == "mac":
                self.sanity_mac.file_sanity()
            else:

                self.sanity.network_sanity()
        else:
            # network activity
            self.run_operation(tag="Network", operation_dict=data)

        # save results
        self.save_run_results(result_list=data)

    def run_directory_activity(self, data=None):
        """
        this method accepts a standard data dict and
        runs either predetermined or user specified
        directory activities and generates reports,
        """
        # Directory Setup

        if not data:
            # this is not a custom test case. use sanity/preconfigured activities
            if self.vm_tag == "mac":
                self.sanity_mac.folder_sanity()
            else:

                self.sanity.folder_sanity()
        else:

            # Directory activity
            self.run_operation(tag="Directory", operation_dict=data)

        # save results
        self.save_run_results(result_list=data)

    def run_eventlogger_activity(self, data=None):
        """
        this method accepts a standard data dict and
        runs either predetermined or user specified
        eventlogger activities and generates reports,
        """
        # event logger Setup
        if self.vm_tag == "win":
            event_log = EventLogger(self.conn)
            event_log.run()

            # save results
            self.save_run_results(result_list=data)
        else:
            logger.error("Event logger not applicable on machine {}".format(self.vm_tag))

    def save_run_results(self, result_list):
        if not result_list:
            # get from the sanity local results
            self.copy_sanity_results()
        else:
            pass

    def run(self, file_dict=None):
        """ generic run method.
            can be used for custom activity
            overall method of execution specified in this function
            """
        try:
            logger.debug("Run Custom activity")
            file_result_dict = dict()

            # Launch user specified operations
            operation_dict = self.clean_dict(file_dict)
            logger.info("Operation Dict : {}".format(operation_dict))

            logger.debug("[VM{}][Test{}] File Activity Result : {}".format(self.vm, self.test_id, file_result_dict))

            self.copy_results_locally()

        except Exception as e:
            logger.error(e)

    def run_operation(self, tag, operation_dict):
        """
             'FileCreated': self.file_create(source, target)
        """
        for element in operation_dict:
            if len(element) >= 3 and tag in element[0]:
                operation = element[0]
                source = element[1]
                target = element[2]
                logger.debug(operation, source, target)
                self.operations[operation](source, target)

    def run_long_running_chained_methods(self, file_dict):

        # 1 file hash for local volumes
        # 2 file hash for network volumes
        # 4 process hash for local volumes
        # 8 process hash for network volumes
        try:
            logger.debug("Run file activity")
            file_result_dict = dict()

            # General Setup
            self.setup()

            # File Setup
            self.create_file_result_remote()

            # setup md5
            self.hash.fileHashingType(type_id="1")

            # setup pegasus setting for local files
            self.hash.hash_local_file()

            if file_dict['add-file']:
                file_result_dict['add-file'] = (file_dict['add-file'], self.file_create(file_dict['add-file']))

            if file_dict['rename-old-file'] and file_dict['rename-new-file']:
                self.create_remote(file_dict['rename-old-file'])
                file_result_dict['rename-file'] = (file_dict['rename-new-file'],
                                                   self.file_rename(file_dict['rename-old-file'],
                                                                    file_dict['rename-new-file']))

            if file_dict['move-old-file'] and file_dict['move-new-file']:
                self.create_remote(file_dict['move-old-file'])
                file_result_dict['move-file'] = (
                file_dict['move-new-file'], self.file_move(file_dict['move-old-file'], file_dict['move-new-file']))

            if file_dict['copy-old-file'] and file_dict['copy-new-file']:
                self.create_remote(file_dict['copy-old-file'])
                file_result_dict['copy-file'] = (
                file_dict['copy-new-file'], self.file_copy(file_dict['copy-old-file'], file_dict['copy-new-file']))

            if file_dict['delete-file']:
                file_result_dict['delete-file'] = (file_dict['delete-file'], self.file_delete(file_dict['delete-file']))

            logger.debug("[VM{}][Test{}] File Activity Result : {}".format(self.vm, self.test_id, file_result_dict))

            # setup pegasus setting for local files
            self.hash.hash_network_file()

            self.hash.hash_process_local()

            self.hash.hash_process_network()

            self.copy_results_locally()

        except Exception as e:
            logger.error("[VM{}][Test{}] Error : {}".format(self.vm, self.test_id, e))

    def run_custom_activities(self):

        try:
            logger.debug("[VM{}] [Test{}]  ~~~~~~~~Run Test ID {} = {} on Machine type ( {} ) ~~~~~~".format(self.vm,
                                                                                                             self.test_id,
                                                                                                             self.test_id,
                                                                                                             self.test_list,
                                                                                                             self.vm_tag))
            conn = SSHConnection(vm=self.vm)

            try:
                conn.client
            except:
                logger.error("[VM{}] [Test{}] SSH failure".format(self.vm, self.test_id))
                self.test_obj.status = "Error"
                self.test_obj.save()

            if not conn.client:
                logger.error("[VM{}] [Test{}] SSH failure".format(self.vm, self.test_id))
                self.test_obj.status = "Error"
                self.test_obj.save()
                return

            user_activity = UserActivity(conn=conn, vm=self.vm, test_id=self.test_id)

            keystroke = KeyStrokeActivity(conn=conn, test_id=self.test_id, vm=self.vm)

            run_obj = TestRunActivity(conn=conn, vm=self.vm, test_id=self.test_id, vm_tag=self.vm_tag)

            operations = run_obj.operations

            # pegasus_modules = PeagasusModules(conn=conn)
            # file_classification = FileClassification(conn=conn, test_id=self.test_id)
            client = Client(conn=conn, vm=self.vm, test_id=self.test_id)

            # run various tests
            logger.debug("[VM{}] [Test{}] TEST LIST : {}".format(self.vm, self.test_id, self.test_list))

            for activity in self.test_list:
                try:
                    # run file activity
                    if "All-Sanity" in activity:
                        run_obj.run_sanity()

                    if "FileActivity" in activity:
                        run_obj.run_file_activity()

                    if "DirectoryActivity" in activity:
                        run_obj.run_directory_activity()

                    if "ProcessActivity" in activity:
                        run_obj.run_process_activity()

                    if "NetworkActivity" in activity:
                        run_obj.run_network_activity()

                    if "eventid" in activity:
                        run_obj.run_eventlogger_activity()

                    if "RegistryActivity" in activity:
                        run_obj.run_registry_activity()

                    if "UserActivity" in activity:
                        if self.vm_tag == "win":
                            if "disable" in activity:
                                user_activity.disable()
                            else:
                                user_activity.enable()

                            if "office" in activity:
                                user_activity.office()

                            if "appsUserActivity" in activity:
                                user_activity.win10apps()

                        if "browser" in activity:
                            if self.vm_tag == "win":
                                user_activity.browser()

                            else:
                                # todo: sanity and user activity
                                pass

                    # Keystroke testcases
                    if "KeyLoggerActivity" in activity:

                        # if "disable" in activity:
                        #     keystroke.disable()
                        # else:
                        #     keystroke.enable()

                        if "longKeyLoggerActivity" in activity:
                            keystroke.long_string_keystrokes()

                        if "random" in activity:
                            keystroke.random_keystrokes()

                        if "notepadkeystrokes" in activity:
                            keystroke.notepad_keystrokes()

                        if "cmdkeystrokes" in activity:
                            keystroke.cmd_keystrokes()

                    # file classification
                    if "FileContentActivity" in activity:

                        if "disableFileContentActivity" in activity:
                            file_classification.disable()
                        else:
                            file_classification.enable()

                            if "enable-type3" in activity:
                                file_classification.enable_type_3()
                            else:
                                file_classification.enable_type_2()

                    if "Client" in activity:
                        if "StartAgent" in activity:
                            logger.debug("TEST : START AGENT ")
                            client.start_agent()

                        if "StopAgent" in activity:
                            logger.debug("TEST : STOP AGENT ")
                            client.stop_agent()

                        if "ClientFileActivity" in activity:
                            logger.debug("TEST : SETUP DB ACCESS ")
                            client.setup_activity_access()

                        if "ClientFetchDB" in activity:
                            logger.debug("TEST : FETCH DB ")
                            client.fetch_db()

                except Exception as e:

                    logger.debug(e)

        except Exception as e:
            logger.debug(e)

        # set test status
        if not self.test_obj.status == "Error":
            self.test_obj.status = "Complete"
            self.test_obj.save()
        logger.debug("[VM{}] [Test{}] Test Complete!".format(self.vm, self.test_id))
        return

