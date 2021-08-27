__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"


from rest_framework import serializers

from apps.test_case_manager.models import TestSuiteDB


class TestSuiteDBSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestSuiteDB
        fields = ('name', 'type', 'vms', 'agent_version')

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class BuildApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        todos = TestSuiteDB.objects.all()
        serializer = TestSuiteDBSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        logger.debug(request.data)
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

            # for process_name in process_list:
            #     logger.debug("Process Name {} completion wait.".format(process_name))
            #     process_name.join()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


