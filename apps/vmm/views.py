import logging
from django.shortcuts import render
from django.views import View
from .forms import VMInfoForm, PeagasusUserForm, VMForm
from apps.utils.psexec.psexec import PsExecConnection
from apps.vmm.utils import vm_connection_test, vm_setup
from .models import VmInfo, VM
from apps.secrets.secrets import SecretsDB
from django.contrib.auth.mixins import LoginRequiredMixin

# # Get an instance of a logger
logger = logging.getLogger(__name__)

# Instance of vminfo model
vminfo_model = VmInfo()

# todo: add decos
# decorators = [never_cache, login_required]
decorators = []


class VMMView(LoginRequiredMixin, TemplateView):
    form_class = VMInfoForm
    initial = {'key': 'value'}
    template_name = 'vm_table.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):

        form = VMForm()

        return render(request, self.template_name, {'form': form, 'vms': VM.objects.all()})

    def post(self, request, *args, **kwargs):
        vm_name = None
        form = VMForm(request.POST)
        if form.is_valid():
            # if True:
            logger.debug(form.cleaned_data)
            # vm_name = request.POST['vm_name']
            vm_name = form.cleaned_data['vm_name']
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            ip = form.cleaned_data['ip']

            ps = PsExecConnection(vm=vm_name)
            ps.setup()
            # ps.test_ssh()
            # ps.install_ssh()

            vm_obj = VM(vm_name=vm_name, user=user, ip=ip)
            vm_obj.save()
            db = SecretsDB()  # SecretsDB class
            db.set_password_model(vm_obj, password=password)

        else:
            logger.error("Invalid form")
        messages.info(request=request,
                      message="VM {} Added to the Database".format(vm_name))

        return render(request, self.template_name, {'form': form, 'vms': VM.objects.all()})


class VMMUser(LoginRequiredMixin, TemplateView):
    form_class = VMInfoForm
    initial = {'key': 'value'}
    template_name = 'pegasus_user.html'
    login_url = '/login/'
    db = SecretsDB()
    password = None

    def get(self, request, *args, **kwargs):

        form = PeagasusUserForm()
        user = self.db.user()
        messages.info(request=request, message="Add a agent User.")
        if user is None:
            password = None
        else:
            password = '<Not Visible in PlainText>'
        return render(request, self.template_name, {'form': form, 'user': user, 'password': password})

    def post(self, request, *args, **kwargs):
        user = None
        password = None
        form = PeagasusUserForm(request.POST)

        if form.is_valid():

            logger.debug(form.cleaned_data)
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            self.db.set_pegasus_password(user=user, password=password)
            if user is None:
                password = None
            else:

                password = '<Not Visible in PlainText>'

        else:
            logger.error("Invalid form")

        return render(request, self.template_name, {'form': form, 'user': user, 'password': password})


class VMManagerView(LoginRequiredMixin, View):
    """ Execute various queries on the virtual machine"""

    form_class = VMInfoForm
    login_url = '/login/'
    template_name = 'vm_manager.html'

    def get(self, request, *args, **kwargs):

        form = VMForm()

        url = request.build_absolute_uri().strip("/").split('/')[-1]

        if url == 'cmd':
            return render(request, self.template_name,
                          {'tab': 2, 'form': form, 'vms': [(index, x) for index, x in enumerate(VM.objects.all())]})
        if url == 'agent':
            return render(request, self.template_name,
                          {'tab': 1, 'form': form, 'vms': [(index, x) for index, x in enumerate(VM.objects.all())]})
        if url == 'installer':
            return render(request, self.template_name,
                          {'tab': 3, 'form': form, 'vms': [(index, x) for index, x in enumerate(VM.objects.all())]})

        return render(request, self.template_name,
                      {'tab': 1, 'form': form, 'vms': [(index, x) for index, x in enumerate(VM.objects.all())]})

    def post(self, request, *args, **kwargs):
        form = VMForm(request.POST)
        if form.is_valid():
            logger.debug(form.cleaned_data)
            vm_name = form.cleaned_data['vm_name']
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            ip = form.cleaned_data['ip']

            tag = form.cleaned_data['tag']
            if tag == '0':
                tag = 'dec'
            else:
                tag = 'nodec'

            vm_obj = VM(vm_name=vm_name, user=user, ip=ip)
            vm_obj.save()
            db = SecretsDB()  # SecretsDB class
            db.set_password_model(vm_obj, password=password)

        else:
            logger.error("Invalid form")

        return render(request, self.template_name,
                      {'form': form, 'vms': [(index, x) for index, x in enumerate(VM.objects.all())]})


class VMMAlive(LoginRequiredMixin, TemplateView):
    form_class = VMInfoForm
    initial = {'key': 'value'}
    template_name = 'agent.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        vm_connection_test()
        return render(request, self.template_name, {'vms': VM.objects.all()})


class VMInfoView(LoginRequiredMixin, TemplateView):
    form_class = VMInfoForm
    login_url = '/login/'
    template_name = 'agent.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'vms': VM.objects.all()})


class VMMSetup(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    form_class = VMInfoForm
    initial = {'key': 'value'}
    template_name = 'agent.html'

    def get(self, request, *args, **kwargs):
        vm_setup()
        return render(request, self.template_name, {'vms': VM.objects.all()})
