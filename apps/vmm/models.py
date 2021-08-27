"""

"""
__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

from django.db import models


class VmInfo(models.Model):
    """ """
    vm_name = models.CharField(max_length=100)
    vm_os = models.CharField(max_length=100)

    # question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def get_vmlist(self):
        """
         Grab the list of vms from the server
        :return:
        """
        # return utils.get_vminfo()
        return

    def get_vminfo(self, vm_name):
        """
            Get full vm info from the server
        :param vm_name:
        :return:
        """
        return

    class Meta:
        managed = True
        db_table = 'vm_info'

        indexes = [
            models.Index(fields=['vm_name'], name='vm_name_idx'),
        ]
        unique_together = ['vm_name', 'vm_os']
        constraints = [
            # models.CheckConstraint(check=models.Q(vm_name__isexact=''),
            # name='vm_name_exact_name'),
        ]
        get_latest_by = ['-vm_name', ]


class VM(models.Model):
    """ """
    vm_name = models.CharField(max_length=250, blank=True, default='', verbose_name="Virtual Machines", unique=True)
    ip = models.CharField(max_length=100, blank=True, default='', verbose_name="IP", unique=True)
    user = models.CharField(max_length=100, blank=True, default='', verbose_name="Username")
    password = models.CharField(max_length=100, blank=True, default='', verbose_name="Password")
    tag = models.CharField(max_length=100, blank=True, default='', verbose_name="handle")
    status = models.BooleanField(default=True)
    passkey = models.CharField(max_length=100, blank=True, default='', verbose_name="passkey")
    # version_x64 = models.BooleanField(default=True)
    # alive_handle = models.CharField(max_length=100, blank=True, default='', verbose_name="handle")


    @staticmethod
    def vm_info(vm):
        """"""
        return [(x.ip, x.user, x.password) for x in VM.objects.filter(vm_name__iexact=vm)]

    @staticmethod
    def vm_tag(vm):
        """"""
        return [x.tag for x in VM.objects.filter(vm_name__iexact=vm)]

    @staticmethod
    def all_vms():
        """"""
        return [x.vm_name for x in VM.objects.
            all()]

    def __str__(self):
        return self.vm_name

    class Meta:
        managed = True
        db_table = 'vm'
        unique_together = (('vm_name', 'ip'),)




