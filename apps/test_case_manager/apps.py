from django.apps import AppConfig
from ..test_beds.apps import SanityTestbedsConfig, PerformanceTestBedsConfig

# Get test_beds application configuration
sanity_testconfig = SanityTestbedsConfig()
perf_testconfig = PerformanceTestBedsConfig()


class TestCaseManagerConfig(AppConfig):
    """"""
    name = 'test_case_manager'

    # Windows testcase files
    tc_path_windows_sanity = r"C:\Sanity\Sanity-testCases.ps1"
