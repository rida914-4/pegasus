"""
    Forms for virtual machine maanger
"""

__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

from django import forms
from .models import VM


class VMManagerForm(forms.ModelForm):

    def __init__(self, *args, **kargs):
        pass

    decvm = forms.ModelChoiceField(queryset=VM.objects.filter(tag='dec').values_list('vm_name').distinct(),
                                   empty_label="agent Machines", required=True)
    nodecvm = forms.ModelChoiceField(queryset=VM.objects.filter(tag='nodec').values_list('vm_name').distinct(),
                                     empty_label="No agent Virtual Machines", required=True)

    class Meta:
        model = VM
        fields = ['vm_name', 'ip', 'user', 'password']


class VMForm(forms.ModelForm):

    def __init__(self, *args, **kargs):
        super(VMForm, self).__init__(*args, **kargs)

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=False)
    vm_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Virtual Machine Name'}), required=False,
                              help_text="")
    ip = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0.0.0.0'}), required=False)
    user = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), required=False)
    tag = forms.ChoiceField(choices=((0, 'dec'), (1, 'nodec')), required=False)

    class Meta:
        model = VM
        fields = ['vm_name', 'ip', 'user', 'password']
        labels = {
            'vm_name': 'new_name',
        }


class PeagasusUserForm(forms.Form):

    def __init__(self, *args, **kargs):
        super(PeagasusUserForm, self).__init__(*args, **kargs)

    user = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True)
