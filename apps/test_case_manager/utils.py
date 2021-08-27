__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

import os
from pathlib import Path
from pegasusautomation import settings
import xml.etree.ElementTree as ET
from apps.test_case_manager.models import TestSuiteDB


def read_file(filename):

    if os.path.exists(filename):
        with open(filename, 'r') as r:
            return r.readlines()
    else:
        return None


def get_run_time(filename):
    if os.path.exists(filename):
        for line in read_file(filename):
            if 'Run Time' in line:
                return line
    else:
        return None


def get_avg_launch_time(filename):
    sum = 0
    index = 1
    for index, line in enumerate(read_file(filename)):
        logger.debug(index, line)
        if index == 1:
            continue
        sum += line
    logger.debug(sum/index-1)
    return sum/index-1


def parse_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    logger.debug([elem.tag for elem in root.iter()])








