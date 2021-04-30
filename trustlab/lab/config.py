from os.path import dirname, abspath
import re
import asyncio
from datetime import datetime
from random import randint

PREPARE_SCENARIO_SEMAPHORE = asyncio.Semaphore(1)
DISTRIBUTOR = "greedy"
# variables for trustlab/models.py
PROJECT_PATH = abspath(dirname(__name__))
SCENARIO_PATH = f'{PROJECT_PATH}/trustlab/lab/scenarios'
SCENARIO_PACKAGE = "trustlab.lab.scenarios"
RESULT_PATH = f'{PROJECT_PATH}/trustlab/lab/results'

TIME_MEASURE = False


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_scenario_run_id():
    # return "scenarioRun:" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") # URI version but not usable as channel_name
    return f'scenarioRun_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{randint(0, 999):0=3d}'


def validate_scenario_run_id(scenario_run_id):
    id_pattern = r"^scenarioRun_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}_[0-9]{3}$"
    return re.match(id_pattern, scenario_run_id)


