"""

"""

__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"


from django.apps import AppConfig


class VmmConfig(AppConfig):
    """
        This class contains the metadata required by the Virtual Machine Manager to interact with the machines
        in ESXI and XEn server.
    """
    name = 'vmm'
