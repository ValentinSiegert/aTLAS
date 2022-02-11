from os.path import dirname, abspath
from pathlib import Path
import re
import asyncio
from datetime import datetime
from random import randint

PREPARE_SCENARIO_SEMAPHORE = asyncio.Semaphore(1)
DISTRIBUTOR = "greedy"
# variables for trustlab/models.py
PROJECT_PATH = Path(abspath(dirname(__name__)))
SCENARIO_PATH = PROJECT_PATH / 'trustlab' / 'lab' / 'scenarios'
SCENARIO_PACKAGE = "trustlab.lab.scenarios"
RESULT_PATH = PROJECT_PATH / 'trustlab' / 'lab' / 'results'
# determines the file size of scenario files which are declared as large in bytes
SCENARIO_LARGE_SIZE = 1000000
# determines the max size of one websocket message in bytes for potential chunked websocket messages
WEBSOCKET_MAX = 900000  # tested this limit 990000 seems to large for supervisor side

SCENARIO_CATEGORY_SORT = ['ConTED_ICWE22', 'aTLAS_WI-IAT20']

TIME_MEASURE = False


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_scenario_run_id():
    """
    Creates a new Scenario Run ID with datetime pattern plus 3 digit random int,
    e.g. 'scenarioRun_2021-05-18_16-37-54_383'.

    :return: new Scenario Run ID
    :rtype: str
    """
    return f'scenarioRun_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{randint(0, 999):0=3d}'


def validate_scenario_run_id(scenario_run_id):
    """
    Validates a given Scenario Run ID by pattern matching.

    :param scenario_run_id: Scenario Run ID to evaluate
    :type scenario_run_id: str
    :return: True if validation was successful else False
    :rtype: bool
    """
    id_pattern = r"^scenarioRun_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}_[0-9]{3}$"
    return True if re.match(id_pattern, scenario_run_id) else False

