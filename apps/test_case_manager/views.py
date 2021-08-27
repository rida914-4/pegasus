import os
import re
import logging
import paramiko
from rest_framework import status
from rest_framework import viewsets
from multiprocessing import Process
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views import View
from django.utils.html import escape
from pegasusautomation import settings
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.test_case_manager.models import TestSuiteDB
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.test_case_manager.serializers import TestSuiteDBSerializer
from django_datatables_view.base_datatable_view import BaseDatatableView
from apps.test_case_manager.models import TestCaseExecution, TestSuiteDB, BuildTesting, BuildResult, RunTestCaseModel
from apps.test_case_manager.forms import TestCaseExecutionForm, BuildTestCaseExecutionForm, \
    BuildTestCaseExecutionFormBaseline

# Get an instance of a logger
logger = logging.getLogger(__name__)

TestType = [

    ('1', 'sanity'),
    ('2', 'functional'),
    ('3', 'performance'),
    ('4', 'custom'),
]


class TestCaseExecuteView(LoginRequiredMixin, View):
    """
        Main class for test case execution
    """
    login_url = '/login/'

    def get(self, request):
        """
            Get all test cases and display them in a table
        :return:
        """
        form = TestCaseExecutionForm()
        return render(request, 'testcase_execution.html', {'form': form, 'test_id': 0})

    def run_test(self, request, test_obj):

        """
                run test based on the user specified test type
            :return: True, messages will show the appropriate results/error
        """

        version, load_status, events_status, msg = test_obj.run()
        test_obj = TestSuiteDB.objects.filter(id=test_obj.test_id)

        if str(version) != '0' and load_status and msg == "Success":
            for element in test_obj:
                element.status = '0'
                element.error_msg = msg
                element.save()
            messages.info(request=request,
                          message="Sanity Test Run (ID:{id}) complete on agent {version}. {msg}".format(
                              id=test_obj.test_id,
                              version=version, msg=msg))
        else:
            for element in test_obj:
                element.status = '3'
                element.error_msg = msg
                element.save()
            messages.error(request=request,
                           message="Sanity Test Run (ID:{id}) complete on agent {version}. Error : {msg}".format(
                               id=test_obj.test_id,
                               version=version, msg=msg))
        return True

    def post(self, request):
        """
            POST request from the user
            :return: render view
        """

        test_id = 0
        test_obj = None
        form = TestCaseExecutionForm(request.POST)
        logger.info("Run Request: {}".format(request.POST))

        if request.method == 'POST':
            try:

                if form.is_valid():

                    post = form.save(commit=True)
                    test_id = post.id
                    test_obj = TestCaseExecution(id=test_id, vms=[vm for vm in form.cleaned_data['vms']],
                                                 type='1', name=form.cleaned_data['name'].lower(),
                                                 build=form.cleaned_data['builds'])
                    self.run_test(request, test_obj)

                else:
                    messages.error(request=request, message="Test Case form failed.Enter correct values.")

            except paramiko.SSHException as e:
                # if there was any other error connecting or establishing an SSH session
                logger.error("SSH Exception error {}. Request # 2".format(e))
                try:
                    self.run_test(request, test_obj)
                except Exception as e:
                    messages.error(request=request,
                                   message="Sanity Test Run failed. Check logs for Error ({})".format(e))
            except Exception as e:

                if "SSH session not active" in str(e):
                    logger.warning("[Test{}] Observed SSH inactive session issue . Request # 2".format(test_id))
                    try:
                        self.run_test(request, test_obj)
                    except Exception as e:
                        messages.error(request=request,
                                       message="Sanity Test Run failed. Check logs for Error ({})".format(e))
                else:
                    messages.error(request=request,
                                   message="Sanity Test Run failed. Check logs for Error ({})".format(e))

        return render(request, 'testcase_execution.html', {'form': form, 'test_id': test_id})


class BuildTest(LoginRequiredMixin, View):
    """
        Class for long running test suites chained

    """
    template_name = "build.html"

    def get(self, request, *args, **kwargs):
        """
            GET request for long running chained processes
        """

        form = BuildTestCaseExecutionForm()
        baseline_form = BuildTestCaseExecutionFormBaseline()
        # build_test = BuildTestSuiteDB.objects.order_by('-id')
        return render(request, self.template_name, {'form': form, 'baseline_form': baseline_form, 'test_id': 0,
                                                    'result': ''})

    def get_version(self, version):
        """
            Parse version via regex
        """

        result = re.findall(r"[0-9]\.[0-9]\.[0-9]\.[0-9]+", str(version), re.I)
        if result:
            return result[0]
        else:
            return ""

    def post(self, request, *args, **kwargs):
        """
            POST request from the user
            :return: render view
        """

        test_id = 0
        test_obj = None
        form = BuildTestCaseExecutionForm(request.POST)
        baseline_form = BuildTestCaseExecutionFormBaseline(request.POST)

        logger.info("Run Request: {}".format(request.POST))

        if request.method == 'POST':
            try:

                if form.is_valid():
                    current = ""
                    baseline = ""

                    # save other params
                    name = form.cleaned_data['name'].lower()
                    build = form.cleaned_data['builds']
                    update = form.cleaned_data['update']
                    vms = form.cleaned_data['vms']
                    post = form.save(commit=True)
                    test_id = post.id

                    process_list = list()

                    for vm in form.cleaned_data['vms']:
                        try:
                            result_obj = BuildResult.objects.create()
                            result_obj.status = "Running"
                            result_obj.vm = str(vm)
                            # for now save test id in this variable
                            result_obj.install_code = test_id
                            result_obj.save()
                        except Exception as e:
                            logger.debug(e)

                        try:
                            current = self.get_version(request.POST['builds'])
                            baseline = self.get_version(request.POST['bbbuilds'])

                            # try:
                            # todo: this needs to be fixed
                            #     testobj = TestSuiteDB(id=int(test_id))
                            #     testobj.agent_version = current
                            #
                            #     testobj.save()
                            # except Exception as e:
                            #     logger.debug(e)

                            result_obj.current_build = current if current else ""
                            result_obj.baseline_build = baseline if current else ""
                            result_obj.save()
                        except Exception as e:
                            logger.debug(e)

                        try:
                            # save the agent version early on
                            if not current or current == 0:
                                # pull the agent version from the vm model.
                                # existing agent
                                # todo :
                                pass

                        except Exception as e:
                            logger.debug(e)

                        build_obj = BuildTesting(vm=vm, name=name, build=build, current=current, baseline=baseline,
                                                 request=request.POST, update=update)
                        logger.debug("Launch Build Testing {} on virtual machine {}.".format(name, vm))
                        p = Process(target=build_obj.run, args=(vm, result_obj))
                        p.start()
                        process_list.append(p)
                else:
                    messages.error(request=request, message="Test Case form failed.Enter correct values.")
            except paramiko.SSHException as e:
                # if there was any other error connecting or establishing an SSH session
                logger.error("SSH Exception error {}. Request # 2".format(e))
            except Exception as e:
                messages.error(request=request,
                                   message="Sanity Test Run failed. Check logs for Error ({})".format(e))

        return render(request, self.template_name, {'form': form, 'baseline_form': baseline_form, 'test_id': test_id})


class OrderListJson(BaseDatatableView):
    """
        List of updated runs coming from Django models
        :return: ajax function returns update test run list
    """
    # The model we're going to show
    model = BuildResult

    # define the columns that will be returned
    columns = ['id', 'status', 'current_build', 'baseline_build', 'vm', 'ping', 'install', 'uninstall', 'update',
               'sanity', 'winsat', 'network', 'filehash', 'registry', 'eventlog', 'zip_results', 'uninstall_code']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id', 'status', 'current_build', 'baseline_build', 'vm', 'ping', 'install', 'uninstall',
                     'update', 'sanity', 'winsat', 'network', 'filehash', 'registry', 'eventlog', 'results',
                     'uninstall_code']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column

        result_obj = BuildResult.objects.filter(id=row.id).values()[0]
        result_id = row.id
        test_id = result_obj['install_code']
        install_status = str(result_obj['install'])
        # logger.debug("{}, {}, {}".format(row.id, row.ping, result_obj['ping']))

        uninstall_status = result_obj['uninstall']
        update_status = result_obj['update']
        network_status = result_obj['network']
        winsat_status = result_obj['winsat']
        sanity_status = result_obj['winsat']
        filehash_status = result_obj['filehash']
        registry_status = result_obj['registry']
        vm = result_obj['vm'].replace("<QuerySet", "").replace("<VM: ", "").replace(">", "").replace("<", "").replace(
            "]", "").replace("[", "")
        vm_name = result_obj['vm']
        result_path = os.path.join(settings.BASE_DIR, "results", str(vm), str(test_id))

        if column == 'vm':
            return escape('{}'.format(str(vm_name).replace("'", "").replace("[", "").replace("]", "")))
        elif column == 'zip_results':
            # escape HTML for security reasons
            return escape(
                '/cb/{ctestid}/{btestid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, ctestid=row.id, btestid=btestid))

        elif column == 'install':
            if not result_obj['install_result'] and not os.path.exists(
                    os.path.join(result_path, "agent", "report.txt")):
                install_status = "Pending"
            return (row.install, '{u}info/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))
        elif column == 'uninstall':
            if not result_obj['uninstall_result']:
                uninstall_status = "Off"
            return (row.uninstall, '{u}info/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))

        elif column == 'update':
            if not result_obj['update_result']:
                update_status = "Off"
            return (row.update, '{u}info/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))

        elif column == 'uninstall_code':
            return escape('/log/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=test_id))
        elif column == 'network':
            if not result_obj['network_details']:
                network_status = "Off"
            return (row.network, '{u}ninfo/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))
        elif column == 'winsat':
            if not result_obj['winsat_details']:
                winsat_status = "Off"
            return (row.winsat, '{u}winfo/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))
        elif column == 'sanity':

            return (row.sanity, '{u}result/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))
        elif column == 'filehash':
            if not result_obj['fh_load_status']:
                filehash_status = "Off"
            return (row.filehash, '{u}winfo/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))
        elif column == 'registry':
            if not result_obj['reg_load_status']:
                registry_status = "Off"

            return (row.registry, '{u}winfo/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))

        elif column == 'eventlog':
            if not result_obj['eventlog']:
                eventlog_status = "Off"
            return (row.eventlog, '{u}winfo/{testid}'.format(u=settings.LOCAL_AUTOMATION_URL_PROD, testid=row.id))
        else:
            return super(OrderListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(name__istartswith=search)

        # filter users
        filter_customer = self.request.GET.get('customer', None)

        if filter_customer:
            customer_parts = filter_customer.split(' ')
            qs_params = None
            for part in customer_parts:
                q = Q(customer_firstname__istartswith=part) | Q(customer_lastname__istartswith=part)
                qs_params = qs_params | q if qs_params else q
            qs = qs.filter(qs_params)
        return qs


class LogView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, test_id='0'):
        """ """
        result = []

        if os.path.exists(os.path.join(settings.LOGGING_DIR, "main.log")):
            with open(os.path.join(settings.LOGGING_DIR, "main.log"), 'r') as f:
                for line in f.readlines():
                    if "Test{}".format(str(test_id)) in line:
                        result.append(line.replace('\n', '').split('|'))

        return render(request, 'log-viewer.html', {'result': result})


@api_view(['GET', 'POST'])
class TestSuiteDBView(viewsets.ModelViewSet):
    queryset = TestSuiteDB.objects.all().order_by('name')
    serializer_class = TestSuiteDBSerializer


class BuildApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        """
            List all the items for given requested user
        """
        serializer = TestSuiteDBSerializer(TestSuiteDB.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
            POST request for serializer
        """
        data = {
            'name': request.data.get('name'),
            'type': request.data.get('type'),
            'vms': request.data.get('vms'),
            'agent_version': request.data.get('agent_version'),
        }

        serializer = TestSuiteDBSerializer(data=data)

        # trigger one click build testsuite
        name = data['name']
        build = data['agent_version']
        vms = data['vms'].replace("'", "").replace("[", "").replace("]", "").split(",")
        process_list = list()

        if serializer.is_valid():

            test_obj = serializer.save()
            test_id = test_obj.id

            for vm in vms:
                build_obj = BuildTesting(vm=vm, name=name, build=build)
                logger.debug("Launch Build Testing {} on virtual machine {}.".format(name, vm))
                p = Process(target=build_obj.run, args=(vm,))
                p.start()
                process_list.append(p)

            # Wait for the process to complete
            for process_name in process_list:
                logger.debug("Process Name {} completion wait.".format(process_name))
                process_name.join()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
