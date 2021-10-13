from trustlab_host.models import Scenario
from django.db import models
import re
import importlib
import importlib.util
import inspect
from os import listdir, mkdir
from os.path import isfile, exists, isdir
import pprint
from trustlab.lab.config import SCENARIO_PATH, SCENARIO_PACKAGE, RESULT_PATH
import traceback


class Supervisor(models.Model):
    channel_name = models.CharField(max_length=120, primary_key=True)
    max_agents = models.IntegerField(default=0)
    agents_in_use = models.IntegerField(default=0)


class ObjectFactory:
    """
    Generic Class for Object Factories loading and saving objects in a DSL (.py) file.
    """
    @staticmethod
    def load_object(file_package, object_package, object_class_name, object_args):
        """
        Imports the DSL file of an given object and initiates it.

        :param file_package: package name of the DSL file.
        :type file_package: str
        :param object_package: package name of the object's class.
        :type object_package: str
        :param object_class_name: the name of the object's class.
        :type object_class_name: str
        :param object_args: All the parameters of the to initiate object
        :type object_args: inspect.FullArgSpec
        :return: the initiated object to be loaded
        :rtype: Any
        :raises AttributeError: One or more mandatory attribute was not found in object's DSL file.
        """
        # python package path
        import_package = f"{object_package}.{file_package}"
        # ensure package is accessible
        implementation_spec = importlib.util.find_spec(import_package)
        if implementation_spec is not None:
            # check if module was imported during runtime to decide if reload is required
            object_spec = importlib.util.find_spec(import_package)
            # import scenario config to variable
            object_config_module = importlib.import_module(import_package)
            # only reload module after importing if spec was found before
            if object_spec is not None:
                object_config_module = importlib.reload(object_config_module)
            # get only args without default value and not self parameter and capitalize them
            mandatory_args = [a.upper() for a in object_args.args[1:-len(object_args.defaults)]]
            all_args = [a.upper() for a in object_args.args[1:]]
            # check if all mandatory args are in scenario config
            if all(hasattr(object_config_module, attr) for attr in mandatory_args):
                object_attrs = []
                for attr in all_args:
                    # check if attr is in config as optional ones may not be present with allowance
                    if hasattr(object_config_module, attr):
                        object_attrs.append(getattr(object_config_module, attr))
                # get object's class by name, requires class to be in global spec thus imported
                object_class = globals()[object_class_name]
                # add all attrs which are in config to scenario object
                obj = object_class(*object_attrs)
                return obj
            raise AttributeError("One or more mandatory attribute was not found in object's DSL file.")

    def save_object(self, obj, object_args, file_path, file_exists=False):
        """
        Saves an object to a DSL file.

        :param obj: the object to be saved.
        :type obj: Any
        :param object_args: All the parameters of the to initiate object
        :type object_args: inspect.FullArgSpec
        :param file_path: Full path to the object's DSL file.
        :type file_path: pathlib.Path
        :param file_exists: whether the object's DSL file already exists.
        :type file_exists: bool
        :return: the initiated object to be loaded
        :rtype: Any
        """
        # all attr
        all_args = [a.upper() for a in object_args.args[1:]]
        # distinguish between new file writing or overwriting existing one
        if file_exists:
            with open(file_path, 'r+') as object_file:
                # read in file
                object_data = object_file.read()
                # exchange all args which are in config file data
                for arg in all_args:
                    # create regex to find argument with value.
                    replacement = re.compile(arg + r' = .+?\n\n', re.DOTALL)  # variables ends with double new lines
                    value = self.stringify_arg_value(obj, arg)
                    if re.search(replacement, object_data):
                        # substitute current value in config_data. Double new lines are added to help parsing
                        object_data = replacement.sub(f"{arg} = {value}\n\n", object_data)
                    else:
                        # get position of last non whitespace char in config data
                        position = object_data.rfind(next((char for char in reversed(object_data) if char != "\n"
                                                           and char != "\t" and char != " "))) + 1
                        arg_value = f"\n\n{arg} = {value}"  # Double new lines are added to help parsing
                        # append argument configuration at position -> end of file + whitespace tail
                        object_data = object_data[:position] + arg_value + object_data[position:]
                # jump back to begin of file and write new data
                object_file.seek(0)
                object_file.write(object_data)
                object_file.truncate()
        else:
            with open(file_path, 'w+') as object_file:
                print('"""', file=object_file)
                print('This file was auto-generated by an ObjectFactory of aTLAS', file=object_file)
                print('"""\n\n', file=object_file)
                for arg in all_args:
                    value = self.stringify_arg_value(obj, arg)
                    print(f"{arg} = {value}\n", file=object_file)  # Double new lines are added to help parsing
                print("\n\n\n", file=object_file) # 4 new lines at end of file

    @staticmethod
    def stringify_arg_value(obj, arg):
        """
        Prettifying the value argument's value at the given object.
        """
        value = getattr(obj, arg.lower())
        # Prettifying the value for better human readability.
        value_prettified = pprint.pformat(value)
        return value_prettified

    def __init__(self):
        pass


class ScenarioFactory(ObjectFactory):
    def load_scenarios(self):
        """
        Loads all scenarios saved /trustlab/lab/scenarios with dynamic read of parameters from Scenario.__init__.

        :return: scenarios initialized as Scenario objects
        :rtype: list
        """
        scenarios = []
        scenario_file_names = [file for file in listdir(self.scenario_path)
                               if isfile(self.scenario_path / file) and file.endswith("_scenario.py")]
        # get all parameters of scenario init
        scenario_args = inspect.getfullargspec(Scenario.__init__)
        for file_name in scenario_file_names:
            file_package = file_name.split(".")[0]
            try:
                scenario = self.load_object(file_package, SCENARIO_PACKAGE, "Scenario", scenario_args)
            except (ValueError, AttributeError, TypeError, ModuleNotFoundError, SyntaxError):
                print(f'Error at Scenario file @{file_name}:')
                traceback.print_exc()
                continue
            if any(s.name == scenario.name for s in scenarios):
                error = f"Scenario {scenario.name}@{file_name} was not loaded due to existing scenario with same name."
                try:
                    raise RuntimeError(error)
                except RuntimeError:
                    traceback.print_exc()
                continue
            scenario.file_name = file_name
            scenarios.append(scenario)
        return scenarios

    def save_scenarios(self):
        """
        Saves all scenarios in self.scenarios in /trustlab/lab/scenarios.

        :rtype: None
        """
        for scenario in self.scenarios:
            # get all parameters of scenario init
            scenario_args = inspect.getfullargspec(Scenario.__init__)
            # all attr
            # all_args = [a.upper() for a in scenario_args.args[1:]]
            if hasattr(scenario, "file_name"):
                config_path = self.scenario_path / scenario.file_name
                self.save_object(scenario, scenario_args, config_path, file_exists=True)
            else:
                # create file name without spaces _ and alphanumeric chars only
                file_name = re.sub('[^A-Za-z0-9_ ]+', '', scenario.name).replace(" ", "_").lower()
                if file_name.endswith("scenario"):
                    file_name += ".py"
                else:
                    file_name += "_scenario.py"
                config_path = self.scenario_path / file_name
                self.save_object(scenario, scenario_args, config_path)

    def prepare_web_ui_print(self):
        """
        Prepares object attributes for the Web UI print, as they are only required for easier printing at the UI.

        :rtype: None
        """
        for scenario in self.scenarios:
            if scenario.any_agents_use_metric('content_trust.authority'):
                scenario.authorities = scenario.agents_with_metric('content_trust.authority')
            if scenario.any_agents_use_metric('content_trust.topic'):
                scenario.topics = scenario.agents_with_metric('content_trust.topic')

    def __init__(self):
        super().__init__()
        self.scenario_path = SCENARIO_PATH
        self.scenarios = self.load_scenarios()
        self.init_scenario_number = len(self.scenarios)

    def __del__(self):
        self.save_scenarios()


class ScenarioResult:
    """
    Represents the results of one scenario run with its id.
    """
    def __init__(self, scenario_run_id, trust_log, agent_trust_logs):
        self.scenario_run_id = scenario_run_id
        self.trust_log = trust_log
        self.agent_trust_logs = agent_trust_logs


class ResultFactory:
    """
    Reads and writes scenario run results from/to log files to be able to answer queries on past results.
    """
    def list_known_scenario_run_ids(self):
        """
        :return: all known scenario run ids.
        :rtype: list
        """
        return [directory for directory in listdir(self.result_path) if isdir(self.result_path / directory)]

    def get_result(self, scenario_run_id):
        """
        :param scenario_run_id: Scenario run id to identify according results.
        :type scenario_run_id: str
        :return: ScenarioResult object of given scenario run id.
        :rtype: ScenarioResult
        """
        result_dir = self.get_result_dir(scenario_run_id)
        if exists(result_dir) and isdir(result_dir):
            agent_trust_logs = {}
            trust_log_path = f"{result_dir}/trust_log.txt"
            with open(trust_log_path, 'r') as trust_log_file:
                trust_log = [line for line in trust_log_file.readlines() if line != "\n"]
            agent_trust_logs_paths = [(file_name.split('_trust_log.txt')[0], f"{result_dir}/{file_name}") for file_name
                                      in listdir(result_dir) if file_name.endswith('_trust_log.txt')]
            for agent, path in agent_trust_logs_paths:
                with open(path, 'r') as agent_trust_log_file:
                    agent_trust_log_lines = [line for line in agent_trust_log_file.readlines() if line != "\n"]
                    agent_trust_logs[agent] = ''.join(agent_trust_log_lines)
            return ScenarioResult(scenario_run_id, trust_log, agent_trust_logs)
        else:
            raise OSError(f"Given path '{result_dir}' for scenario result read is not a directory or does not exist.")

    def save_result(self, scenario_result):
        """
        :param scenario_result: ScenarioResult object to be saved.
        :type scenario_result: ScenarioResult
        :rtype: None
        """
        result_dir = self.get_result_dir(scenario_result.scenario_run_id)
        if not exists(result_dir) or not isdir(result_dir):
            mkdir(result_dir)
        trust_log_path = f"{result_dir}/trust_log.txt"
        with open(trust_log_path, 'w+') as trust_log_file:
            print(''.join(scenario_result.trust_log), file=trust_log_file)
        for agent, agent_trust_log in scenario_result.agent_trust_logs.items():
            agent_trust_log_path = f"{result_dir}/{agent}_trust_log.txt"
            with open(agent_trust_log_path, 'w+') as agent_trust_log_file:
                print(''.join(agent_trust_log), file=agent_trust_log_file)

    def get_result_dir(self, scenario_run_id):
        """
        :param scenario_run_id: Scenario run id to identify according results.
        :type scenario_run_id: str
        :return: Path to results of scenario run id.
        :rtype: pathlib.Path
        """
        split_index = len(scenario_run_id.split("_")[0]) + 1  # index to cut constant of runId -> 'scenarioRun_'
        folder_name = scenario_run_id[split_index:]
        return self.result_path / folder_name

    def __init__(self):
        self.result_path = RESULT_PATH
        if not exists(RESULT_PATH) or not isdir(RESULT_PATH):
            mkdir(RESULT_PATH)

