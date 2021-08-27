from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib.auth.hashers import make_password
import logging
from .forms import VMInfoForm, VMManagerForm, VMForm
from .models import VmInfo, VM

# # Get an instance of a logger
logger = logging.getLogger(__name__)

# Instance of vminfo model
vminfo_model = VmInfo()

# todo: add decos
# decorators = [never_cache, login_required]
decorators = []


class VMMView(TemplateView):
    form_class = VMInfoForm
    initial = {'key': 'value'}
    template_name = 'agent.html'

    def get(self, request, *args, **kwargs):
        # form = self.form_class(initial=self.initial)
        form = VMForm()
        for a in VM.objects.all():
            logger.debug(a.vm_name)
        return render(request, self.template_name, {'form': form, 'vms': VM.objects.all()})

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

            p = VM(vm_name=vm_name, user=user, password=make_password(password), tag=tag, ip=ip)
            p.save()

            return HttpResponseRedirect('/vms/')
        else:
            logger.error("Invalid form")

        return render(request, self.template_name, {'form': form, 'vms': VM.objects.all()})
