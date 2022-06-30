import importlib
import importlib.util
import inspect
import pprint
import re
import shutil
import traceback
from django.db import models
from os import listdir, mkdir
from os.path import isfile, exists, isdir, getsize, basename
from pathlib import Path
from trustlab.lab.config import SCENARIO_PATH, SCENARIO_PACKAGE, RESULT_PACKAGE, RESULT_PATH, SCENARIO_LARGE_SIZE,\
    SCENARIO_CATEGORY_SORT, get_scenario_run_name
from trustlab_host.models import Scenario
from types import SimpleNamespace


class Supervisor(models.Model):
    channel_name = models.CharField(max_length=120, primary_key=True)
    max_agents = models.IntegerField(default=0)
    agents_in_use = models.IntegerField(default=0)
    ip_address = models.CharField(max_length=20, default="")
    hostname = models.CharField(max_length=260, default="")


class ObjectFactory:
    """
    Generic Class for Object Factories loading and saving objects in a DSL (.py) file.
    """
    @staticmethod
    def load_object(import_package, object_class_name, object_args, lazy_args=None, known_key_values=None):
        """
        Imports the DSL file of an given object and initiates it.

        :param import_package: python package path of the DSL file.
        :type import_package: str
        :param object_class_name: the name of the object's class.
        :type object_class_name: str
        :param object_args: All the parameters of the to initiate object
        :type object_args: inspect.FullArgSpec or SimpleNamespace
        :param lazy_args: List of arguments for the lazy load of too large files. Default is None.
        :type lazy_args: list
        :param known_key_values: Dict of known key value pairs. Default is None.
        :type known_key_values: dict
        :return: the initiated object to be loaded
        :rtype: Any
        :raises AttributeError: One or more mandatory attribute was not found in object's DSL file.
        """
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
                object_attrs = known_key_values if known_key_values else {}
                if not lazy_args:
                    for attr in all_args:
                        # check if attr is in config as optional ones may not be present with allowance
                        if hasattr(object_config_module, attr):
                            object_attrs[attr.lower()] = getattr(object_config_module, attr)
                else:
                    for attr in lazy_args:
                        # check if attr is in config as optional ones may not be present with allowance
                        if hasattr(object_config_module, attr):
                            object_attrs[attr.lower()] = getattr(object_config_module, attr)
                # get object's class by name, requires class to be in global spec thus imported
                object_class = globals()[object_class_name]
                # add all attrs which are in config to object
                obj = object_class(**object_attrs)
                return obj
            raise AttributeError("One or more mandatory attribute was not found in object's DSL file.")

    def save_object(self, obj, object_args, file_path, file_exists=False):
        """
        Saves an object to a DSL file. Double new lines (empty line) within value definition of variable causes error
        as script sees \n\n as indicator for variable end.
        Only writes into files if object or its string representation has changed since loading.

        :param obj: the object to be saved.
        :type obj: Any
        :param object_args: All the parameters of the to initiate object
        :type object_args: inspect.FullArgSpec or SimpleNamespace
        :param file_path: Full path to the object's DSL file.
        :type file_path: Path
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
                # add newline feed for parsing with double new lines as delimiter for value end
                object_data = object_file.read() + '\n'
                # exchange all args which are in config file data
                for arg in all_args:
                    # create regex to find argument with value.
                    replacement = re.compile(arg + r' = .+?\n\n', re.DOTALL)  # variables end with double new lines
                    value = self.stringify_arg_value(obj, arg)
                    match = re.search(replacement, object_data)
                    arg_value_str = f"{arg} = {value}\n\n"
                    object_changed = False
                    if match and match.group() != arg_value_str:
                        # only substitute value if object changed
                        # substitute current value in config_data.
                        object_data = replacement.sub(arg_value_str, object_data)
                        # set object_changed to true to indicate file writing later on
                        object_changed = True
                    elif match and match.group() == arg_value_str:
                        # not changing anything if file does not need a change for this arg
                        pass
                    else:
                        # as object added obligatory argument, file needs to be written again
                        object_changed = True
                        # get position of last non whitespace char in config data
                        position = object_data.rfind(next((char for char in reversed(object_data) if char != "\n"
                                                           and char != "\t" and char != " "))) + 1
                        arg_value = f"\n\n{arg} = {value}"  # Double new lines are added to support parsing
                        # append argument configuration at position -> end of file + whitespace tail
                        object_data = object_data[:position] + arg_value + object_data[position:]
                # only write anything if object changed after load
                if object_changed:
                    # delete last new line feed to format in PEP8 style
                    object_data = object_data[:-1]
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
                    # Double new lines are added to support parsing
                    print(f"{arg} = {value}\n\n", file=object_file)

    @staticmethod
    def stringify_arg_value(obj, arg):
        """
        Prettifying the value argument's value at the given object.
        """
        value = getattr(obj, arg.lower())
        # Prettifying the value for better human readability.
        value_prettified = pprint.pformat(value)
        # delete leading and trailing brackets at string prettifying AND add backslash to newline feed
        if type(value) is str and value_prettified.startswith('('):
            value_prettified = value_prettified.replace('\n', '\\\n')[1:-1]
        return value_prettified

    def __init__(self):
        pass


class ScenarioFactory(ObjectFactory):
    def load_scenarios(self):
        """
        Loads all scenarios saved /trustlab/lab/scenarios with dynamic read of parameters from Scenario.__init__.

        :return: scenarios initialized as Scenario objects or tuple representation from lazy load
        :rtype: list
        """
        scenarios = []
        scenario_files = self.get_scenario_files()
        for file_name, file_package in scenario_files:
            file_size = getsize(self.scenario_path / file_name)
            try:
                if (not self.large_file_size or (self.large_file_size and file_size < self.large_file_size)) \
                        and not self.names_only_load:
                    scenario = self.load_object(f"{SCENARIO_PACKAGE}.{file_package}", "Scenario", self.scenario_args)
                else:
                    scenario = self.load_object(f"{SCENARIO_PACKAGE}.{file_package}", "Scenario", self.scenario_args,
                                                self.scenario_lazy_args)
                    if not self.names_only_load:
                        if self.large_file_size > 999999:
                            file_size_str = f'{file_size / 1000000} MB'
                            large_size_str = f'{self.large_file_size / 1000000} MB'
                        else:
                            file_size_str = f'{file_size / 1000} KB'
                            large_size_str = f'{self.large_file_size / 1000} KB'
                        scenario.lazy_note = f'This scenario file exceeded with its file size of {file_size_str} ' \
                                             f'the file size limit of {large_size_str}. Thus, the scenario was lazy ' \
                                             f'loaded and will only include its description.'
                    scenario.not_fully_loaded = True
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

    def get_scenario_files(self):
        """
        To categorize scenarios, this method scans for scenarios in direct subdirs of the scenario dir.

        :return: All scenario files as tuples with their package name.
        :rtype: list
        """
        scenario_file_names = [file for file in listdir(self.scenario_path)
                               if isfile(self.scenario_path / file) and file.endswith("_scenario.py")]
        subpackages = [self.scenario_path / sub for sub in listdir(self.scenario_path)
                       if isdir(self.scenario_path / sub) and '__init__.py' in listdir(self.scenario_path / sub)]
        for subpackage in subpackages:
            subpackage_scenarios = [f'{basename(subpackage)}/{file}' for file in listdir(subpackage)
                                    if isfile(subpackage / file) and file.endswith("_scenario.py")]
            scenario_file_names += subpackage_scenarios
        scenario_files = [(file, self.get_package(file)) for file in scenario_file_names]
        return scenario_files

    def get_scenarios_in_categories(self):
        """
        Creates a dict of categories as keys and list of scenario names as values to visualize in scenario.hmtl card.

        :return: Dictionary items of categories as keys, and list of scenario's names related to the scenario.
        :rtype: list
        """
        scenario_categories = {}
        for scenario in self.scenarios:
            if '/' in scenario.file_name:
                category = scenario.file_name.split('/')[0]
            else:
                category = 'Misc'
            if category not in scenario_categories.keys():
                scenario_categories[category] = []
            scenario_categories[category].append(scenario.name)
        for key in scenario_categories.keys():
            scenario_categories[key] = sorted(scenario_categories[key])
        # sort by categories
        category_sort = SCENARIO_CATEGORY_SORT + sorted([c for c in scenario_categories.keys() if c not in
                                                         SCENARIO_CATEGORY_SORT and c != 'Misc']) + ['Misc']
        index_map = {v: i for i, v in enumerate(category_sort)}
        return sorted(scenario_categories.items(), key=lambda pair: index_map[pair[0]])

    def get_scenario(self, name):
        """
        Returns the fully loaded scenario with the given name.

        :param name: Name of the scenario.
        :type name: str
        :return: Scenario with the given name.
        :rtype: Scenario
        :raises RuntimeError: If no scenario with the given name is found or Scenario could not be loaded.
        """
        for scenario_in_list in self.scenarios:
            if scenario_in_list.name == name:
                if hasattr(scenario_in_list, "not_fully_loaded"):
                    try:
                        scenario = self.load_object(f"{SCENARIO_PACKAGE}.{self.get_package(scenario_in_list.file_name)}",
                                                    "Scenario", self.scenario_args)
                    except (ValueError, AttributeError, TypeError, ModuleNotFoundError, SyntaxError):
                        print(f'Error at Scenario file @{scenario_in_list.file_name}:')
                        traceback.print_exc()
                        raise RuntimeError(f"Scenario {scenario_in_list.name}@{scenario_in_list.file_name}"
                                           f"was not loaded due to error.")
                    return scenario
                else:
                    return scenario_in_list
        raise RuntimeError(f"Scenario {name} not found.")

    def scenario_exists(self, name):
        """
        Returns True if a scenario with the given name exists by only checking scenario names.

        :param name: Name of the scenario.
        :type name: str
        :rtype: bool
        """
        return any([True if scenario.name == name else False for scenario in self.scenarios])

    @staticmethod
    def get_package(file_name):
        """
        Returns the package name of the scenario with the given file name.

        :param file_name: Name of the scenario file.
        :type file_name: str
        :return: Package name of the scenario.
        :rtype: str
        """
        return file_name.split(".")[0].replace('/', '.')

    def __init__(self, lazy_load=False, names_only_load=False):
        super().__init__()
        self.scenario_path = SCENARIO_PATH
        self.large_file_size = SCENARIO_LARGE_SIZE if lazy_load else None
        self.names_only_load = names_only_load
        # get all parameters of scenario init
        self.scenario_args = inspect.getfullargspec(Scenario.scenario_args)
        # only take name and description as more is not required for lazy load
        self.scenario_lazy_args = ['NAME', 'DESCRIPTION']
        self.scenarios = self.load_scenarios()

    def __del__(self):
        if not self.large_file_size and not self.names_only_load:
            self.save_scenarios()


class ScenarioResult:
    """
    Represents the results of one scenario run with its id.
    """
    def __init__(self, scenario_run_id, scenario_name, supervisor_amount, trust_log, trust_log_dict, agent_trust_logs,
                 agent_trust_logs_dict, atlas_times=None):
        self.scenario_run_id = scenario_run_id
        self.scenario_name = scenario_name
        self.supervisor_amount = supervisor_amount
        self.trust_log = trust_log
        self.trust_log_dict = trust_log_dict
        self.agent_trust_logs = agent_trust_logs
        self.agent_trust_logs_dict = agent_trust_logs_dict
        self.atlas_times = atlas_times


class ResultFactory(ObjectFactory):
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
            result_key_values = {'scenario_run_id': scenario_run_id, 'scenario_name': '', 'supervisor_amount': 0,
                                 'trust_log': trust_log, 'trust_log_dict': None, 'agent_trust_logs': agent_trust_logs,
                                 'agent_trust_logs_dict': None, 'atlas_times': None}
            return self.load_object(f'{self.result_package}.{result_dir.name}.{get_scenario_run_name(scenario_run_id)}',
                                    "ScenarioResult", self.dict_log_params, known_key_values=result_key_values)
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
        dict_log_path = result_dir / f"{get_scenario_run_name(scenario_result.scenario_run_id)}.py"
        self.save_object(scenario_result, self.dict_log_params, dict_log_path, file_exists=False)

    def save_dict_log_result(self, scenario_result):
        """
        Save only dict_log variables to file.

        :param scenario_result: ScenarioResult object to be saved.
        :type scenario_result: ScenarioResult
        :rtype: None
        """
        result_dir = self.get_result_dir(scenario_result.scenario_run_id)
        if not exists(result_dir) or not isdir(result_dir):
            mkdir(result_dir)
        dict_log_path = result_dir / f"{get_scenario_run_name(scenario_result.scenario_run_id)}.py"
        self.save_object(scenario_result, self.dict_log_params, dict_log_path, file_exists=False)

    def get_result_dir(self, scenario_run_id):
        """
        :param scenario_run_id: Scenario run id to identify according results.
        :type scenario_run_id: str
        :return: Path to results of scenario run id.
        :rtype: pathlib.Path
        """
        folder_name = get_scenario_run_name(scenario_run_id)
        return self.result_path / folder_name

    def copy_result_pys(self, scenario_run_id):
        """
        Copy python files from result folders to evaluator results dir.

        :param scenario_run_id: Scenario run id.
        :type scenario_run_id: str
        :return: None
        """
        eval_result_path = self.result_path / 'evaluator_results'
        if not exists(eval_result_path):
            mkdir(eval_result_path)
        shutil.copy(self.get_result_dir(scenario_run_id) / f"{get_scenario_run_name(scenario_run_id)}.py",
                    eval_result_path)

    def __init__(self):
        super().__init__()
        # adding dict log parameters for loading and saving, is in SimpleNameSpace for object with args variable
        self.dict_log_params = SimpleNamespace(args=['self', 'scenario_name', 'supervisor_amount', 'trust_log_dict',
                                                     'agent_trust_logs_dict', 'atlas_times'], defaults=tuple([None]))
        self.result_path = RESULT_PATH
        self.result_package = RESULT_PACKAGE
        if not exists(RESULT_PATH) or not isdir(RESULT_PATH):
            mkdir(RESULT_PATH)
