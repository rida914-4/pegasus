"""

"""

__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

from django import forms

from .models import VM


class VMInfoForm(forms.Form):
    pass


class VMManagerForm(forms.ModelForm):

    def __init__(self, *args, **kargs):
        pass

    decvm = forms.ModelChoiceField(queryset=VM.objects.filter(tag='dec').values_list('vm_name').distinct(),
                                   empty_label="agent Machines", required=True)
    nodecvm = forms.ModelChoiceField(queryset=VM.objects.filter(tag='nodec').values_list('vm_name').distinct(),
                                     empty_label="No agent Virtual Machines", required=True)

    class Meta:
        model = VM
        fields = '__all__'


class VMForm(forms.ModelForm):

    def __init__(self, *args, **kargs):
        super(VMForm, self).__init__(*args, **kargs)

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    vm_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Virtual Machine Name'}))
    ip = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'0.0.0.0'}))
    user = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))

    tag = forms.ChoiceField(choices=((0, 'dec'), (1, 'nodec')), required=False)



    class Meta:
        model = VM
        fields = '__all__'
        labels = {
            'vm_name': 'new_name',
        }