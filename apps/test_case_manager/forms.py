"""

"""
__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

from django import forms
from django.core.exceptions import ValidationError
from apps.test_case_manager.models import TestSuiteDB
from apps.vmm.models import VM
from .models import Manager
from apps.agent_manager.utils.utils import agent_build_list, agent_build_list


class InstallForm(forms.ModelForm):
    """ """
    def __init__(self, *args, **kargs):
        pass

    builds = forms.ModelChoiceField(queryset=Manager.objects.values_list('builds').distinct(),
                                    empty_label="agent Builds", required=False)

    class Meta:
        model = Manager
        fields = '__all__'


class TestCaseExecutionForm(forms.ModelForm):
    """ """
    def __init__(self, *args, **kargs):
        super(TestCaseExecutionForm, self).__init__(*args, **kargs)
        for visible in self.visible_fields():

            visible.field.widget.attrs['class'] = 'form-control'
            if (isinstance(visible.field, forms.ModelMultipleChoiceField)):
                visible.field.widget.attrs['multiple'] = "multiple"
                visible.field.widget.attrs['data-plugin-multiselect'] = ''
                visible.field.widget.attrs['id'] = 'ms_example0'
                # visible.field.widget.attrs['data-plugin-options'] = '{ "includeSelectAllOption": true }'


    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Test Name'}))
    vms = forms.ModelMultipleChoiceField(
        queryset=VM.objects.all().order_by('vm_name'),
        # widget=forms.CheckboxSelectMultiple
    )

    builds = forms.ChoiceField(choices=(('None', (('', 'Select Current Build'),)), ('agent', tuple(agent_build_list())), ('agent', tuple(agent_build_list()))), required=False)


    class Meta:
        model = TestSuiteDB
        fields = ['name', 'vms', 'activity_key']


class BuildTestCaseExecutionForm(forms.ModelForm):
    """ """
    def __init__(self, *args, **kargs):
        super(BuildTestCaseExecutionForm, self).__init__(*args, **kargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if (isinstance(visible.field, forms.ModelMultipleChoiceField)):
                visible.field.widget.attrs['multiple'] = "multiple"
                visible.field.widget.attrs['data-plugin-multiselect'] = ''
                visible.field.widget.attrs['id'] = 'ms_example0'
                # visible.field.widget.attrs['data-plugin-options'] = '{ "includeSelectAllOption": true }'

            if (isinstance(visible.field, forms.MultipleChoiceField)):
                visible.field.widget.attrs['multiple'] = "multiple"
                visible.field.widget.attrs['data-plugin-multiselect'] = ''
                visible.field.widget.attrs['id'] = 'ms_example0'
                visible.field.widget.attrs['selected'] = ''

    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Test Name'}))
    vms = forms.ModelMultipleChoiceField(
        queryset=VM.objects.all().order_by('vm_name'),
    )

    builds = forms.ChoiceField(choices=(('No DEC', (('', 'Select Current Build'),)), ('agent', tuple(agent_build_list())), ('agent', tuple(agent_build_list()))), required=False)
    update = forms.MultipleChoiceField(choices=(('agent', tuple(agent_build_list())), ('agent', tuple(agent_build_list()))), required=False)
    list_agent = [('None', 'Select Current Build')] + agent_build_list()

    class Meta:
        model = TestSuiteDB
        fields = ['name', 'vms', 'activity_key']

    def clean(self):
        cleaned_data = super().clean()
        test_name = cleaned_data.get("name")

        if test_name:

            if any(x in test_name for x in ["$", ".", ",", "/", "~"]):

                raise ValidationError(
                    "Test Name is invalid. Special characters found."
                )


class BuildTestCaseExecutionFormBaseline(forms.Form):
    """ """
    def __init__(self, *args, **kargs):
        super(BuildTestCaseExecutionFormBaseline, self).__init__(*args, **kargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    list_agent = (('No DEC', (('', 'Select Baseline Build'),)), ('agent', tuple(agent_build_list())), ('agent', tuple(agent_build_list())))
    bbbuilds = forms.ChoiceField(choices=list_agent, required=False)


class CustomTestCaseExecutionForm(forms.ModelForm):
    """ """
    def __init__(self, *args, **kargs):
        super(CustomTestCaseExecutionForm, self).__init__(*args, **kargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if (isinstance(visible.field, forms.ModelMultipleChoiceField)):
                visible.field.widget.attrs['multiple'] = "multiple"
                visible.field.widget.attrs['data-plugin-multiselect'] = ''
                visible.field.widget.attrs['id'] = 'ms_example0'
                # visible.field.widget.attrs['data-plugin-options'] = '{ "includeSelectAllOption": true }'

            if (isinstance(visible.field, forms.MultipleChoiceField)):

                visible.field.widget.attrs['multiple'] = "multiple"
                visible.field.widget.attrs['data-plugin-multiselect'] = ''
                visible.field.widget.attrs['id'] = 'ms_example0'
                visible.field.widget.attrs['selected'] = ''
                # visible.field.widget.attrs['data-plugin-options'] = '{ "includeSelectAllOption": true }'

    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Test Name'}))
    vms = forms.ModelMultipleChoiceField(
        queryset=VM.objects.all().order_by('vm_name'),
        # widget=forms.CheckboxSelectMultiple
    )
    # builds = forms.ChoiceField(choices=[('None', 'Select Current Build')] + agent_build_list(), required=True)

    class Meta:
        model = TestSuiteDB
        fields = ['name', 'vms', 'activity_key']
