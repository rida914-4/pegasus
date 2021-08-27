"""pegasusautomation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
# project imports
from apps.job_manager import views as jb
from apps.vmm import views as vmm
from apps.controller import views as controller
from apps.functional import views as functional_views
from apps.test_beds import views as testbeds
from apps.test_case_manager import views as testcases
from apps.performance import views as performance
from apps.report_manager import views as reports
from apps.agent_manager import views as manager
from apps.testlink import views as testlink
from apps.mac import views as mac
from pegasusautomation import settings
from apps.vmm.utils import vm_connection_test

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'buildtest', testcases.TestSuiteDBView)


urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), {'next_page': '/'}, name='logout'),

    # Controller
    path('home/', controller.ControllerView.as_view(), name='home'),
    path('result/<int:id>', controller.generate_report, name='rresult'),
    path('email/<int:id>', controller.sendmail, name='email'),
    # path('', views.index, name='index'),

    # Job manager
    path('job_manager/', jb.RunTestCase.as_view(), name='job_manager'),
    # path('django-rq/', include('django_rq.urls')),
    # (r'^admin/rq/', include('django_rq_dashboard.urls')),

    # VMM
    path('vms/', vmm.VMMView.as_view(), name='vms'),
    path('adduser/', vmm.VMMUser.as_view(), name='adduser'),
    path('alivevm/', vmm.VMMAlive.as_view(), name='alivevm'),
    path('setupvm/', vmm.VMMSetup.as_view(), name='setupvm'),
    path('vmmanager/', vmm.VMManagerView.as_view(), name='vmmanager'),

    # agent manager
    path('agent/', manager.DECWManagerView.as_view(), name='agent'),
    path('info/<int:test_id>/', manager.agent_info, name='info'),
    path('ninfo/<int:test_id>/', performance.network_info, name='ninfo'),
    path('winfo/<int:test_id>/', performance.winsat_info, name='winfo'),

    # Testcase Manager
    # path('performance/', testcases.PerformanceWinSATView.as_view(), name='performance'),
    path('sanity/', testcases.TestCaseExecuteView.as_view(), name='sanity'),
    path('run/', testcases.RunTestCase.as_view(), name='run'),
    # path('asanity/', testcases.TestCaseAJAXExecuteView.as_view(), name='asanity'),
    path('log/<str:test_id>/', testcases.LogView.as_view(), name='log'),

    # Build Tests
    path('build/', testcases.BuildTest.as_view(), name='build'),
    path('buildtest/', testcases.TestSuiteDBView, name='buildtest'),
    path('result/', testcases.OrderListJson.as_view(), name='result'),
    path('testresult/', testcases.RefreshTests.as_view(), name='testresult'),

    # Functional Tests
    path('functional/', functional_views.FunctionalFileView.as_view(), name='file'),
    path('file/', functional_views.FunctionalFileView.as_view(), name='file'),
    path('event/', functional_views.FunctionalEventView.as_view(), name='event'),
    path('registry/', functional_views.FunctionalRegistryView.as_view(), name='registry'),
    path('fnetwork/', functional_views.FunctionalNetworkView.as_view(), name='fnetwork'),
    path('directory/', functional_views.FunctionalDirectoryView.as_view(), name='directory'),
    path('process/', functional_views.FunctionalProcessView.as_view(), name='process'),
    path('cmd/', functional_views.FunctionalCMDView.as_view(), name='cmd'),

    # Performance Tests
    path('performance/', performance.PerformanceWinSATView.as_view(), name='performance'),
    path('winsat/', performance.PerformanceWinSATView.as_view(), name='winsat'),
    path('network/', performance.PerformanceNetworkView.as_view(), name='network'),
    path('ts/', performance.PerformanceTerminalServerView.as_view(), name='ts'),
    path('fs/', performance.PerformanceFSView.as_view(), name='fs'),
    path('upload/<size>', testcases.UploadView.as_view(), name='upload'),

    # path('download/<size>', testcases.DownloadView.as_view(), name='download'),
    # path('', testcases.UploadView.as_view(), name='fileupload'),

    # Reports and test suite results
    path('report/', reports.ComparisonReportView.as_view(), name='report'),
    path('breport/', reports.ComparisonBuildReportView.as_view(), name='breport'),
    path('pdf/<str:pdf_name>', reports.ReportPDF.as_view(), name='pdf'),
    path('runcomparison/', reports.ComparisonReportView.as_view(), name=''),
    path('report/<int:c>/<int:b>', reports.SanityReportParameterized, name='bireport'),
    path('cb/<int:c>/<int:b>', reports.ComparisonBuildReportView.as_view(), name='cbreport'),
    path('treport/<int:c>/<int:b>', reports.ComparisonReportView.as_view(), name='treport'),
    path('runreport/<int:c>', reports.RunReportView.as_view(), name='runreport'),
    path('events/', reports.events_view, name='events'),

    # dec-W installer
    path('manage/', manager.InstallerView.as_view(), name='manage'),
    path('vm/', manager.InstallerView.as_view(), name='manage'),


    # MAC operations
    path('mac/', mac.MACView.as_view(), name='mac'),


    # Testlink
    path('testlink/', testbeds.TestLinkView.as_view(), name='testlink'),
    path('hardware/', controller.hardware_status, name='hardware'),

    # Rest API
    path('', include(router.urls)),
    path('api/', testcases.BuildApiView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
