from trustlab_host.models import Scenario
from django.db import models
import re
import importlib
import importlib.util
import inspect
from os import listdir
from os.path import isfile, join, dirname, abspath

# TODO bring these config vars in config file
SCENARIO_PATH = '/trustlab/lab/scenarios'
SCENARIO_PACKAGE = "trustlab.lab.scenarios"


class Supervisor(models.Model):
    channel_name = models.CharField(max_length=120)
    max_agents = models.IntegerField(default=0)
    agents_in_use = models.IntegerField(default=0)


class ScenarioFactory:
    # load all scenarios in /trustlab/lab/scenarios with dynamic read of parameters from Scenario.__init__
    @staticmethod
    def load_scenarios():
        scenarios = []
        project_path = abspath(dirname(__name__))
        # path of scenario_config_module files
        scenario_path = project_path + SCENARIO_PATH
        scenario_file_names = [file for file in listdir(scenario_path)
                               if isfile(join(scenario_path, file)) and file.endswith("_scenario.py")]
        for file_name in scenario_file_names:
            # python package path
            import_package = SCENARIO_PACKAGE + '.' + file_name.split(".")[0]
            # ensure package is accessible
            implementation_spec = importlib.util.find_spec(import_package)
            if implementation_spec is not None:
                # check if module was imported during runtime to decide if reload is required
                scenario_spec = importlib.util.find_spec(import_package)
                # import scenario config to variable
                scenario_config_module = importlib.import_module(import_package)
                # only reload module after importing if spec was found before
                if scenario_spec is not None:
                    scenario_config_module = importlib.reload(scenario_config_module)
                # get all parameters of scenario init
                scenario_args = inspect.getfullargspec(Scenario.__init__)
                # get only args without default value and not self parameter and capitalize them
                mandatory_args = [a.upper() for a in scenario_args.args[1:-len(scenario_args.defaults)]]
                all_args = [a.upper() for a in scenario_args.args[1:]]
                # check if all mandatory args are in scenario config
                if all(hasattr(scenario_config_module, attr) for attr in mandatory_args):
                    scenario_attrs = []
                    for attr in all_args:
                        # check if attr is in config as some are optional with default value
                        if hasattr(scenario_config_module, attr):
                            scenario_attrs.append(getattr(scenario_config_module, attr))
                    try:
                        # add all attrs which are in config to scenario object
                        scenario = Scenario(*scenario_attrs)
                    except ValueError as value_error:
                        # TODO log value_error
                        continue
                    if any(scen.name == scenario.name for scen in scenarios):
                        # TODO log non-loading of scenario due to name is already given
                        continue
                    scenario.file_name = file_name
                    scenarios.append(scenario)
        return scenarios

    def stringify_arg_value(self, obj, arg):
        value = getattr(obj, arg.lower())
        # add surrounding " if variable is of type string
        if isinstance(getattr(obj, arg.lower()), str):
            value = '"' + value + '"'
        return str(value)

    def save_scenarios(self):
        for scenario in self.scenarios:
            # create or use existing file name for config file of scenario
            scenario_path = abspath(dirname(__name__)) + SCENARIO_PATH + "/"
            # get all parameters of scenario init
            scenario_args = inspect.getfullargspec(Scenario.__init__)
            # all attr
            all_args = [a.upper() for a in scenario_args.args[1:]]
            if hasattr(scenario, "file_name"):
                config_path = scenario_path + scenario.file_name
                with open(config_path, 'r+') as config_file:
                    # read in file
                    config_data = config_file.read()
                    # exchange all args which are in config file data
                    for arg in all_args:
                        # create regex to find argument with value
                        replacement = re.compile(arg + r' = .*\n')
                        value = self.stringify_arg_value(scenario, arg)
                        if re.search(replacement, config_data):
                            # substitute current value in config_data
                            config_data = replacement.sub(arg + ' = ' + value + '\n', config_data)
                        else:
                            # get position of last non whitespace char in config data
                            position = config_data.rfind(next((char for char in reversed(config_data) if char != "\n"
                                                               and char != "\t" and char != " "))) + 1
                            arg_value = "\n" + arg + " = " + value
                            # append argument configuration at position -> end of file + whitespace tail
                            config_data = config_data[:position] + arg_value + config_data[position:]
                    # jump back to begin of file and write new data
                    config_file.seek(0)
                    config_file.write(config_data)
                    config_file.truncate()
            else:
                # create file name without spaces _ and alphanumeric chars only
                file_name = re.sub('[^A-Za-z0-9_ ]+', '', scenario.name).replace(" ", "_").lower()
                if file_name.endswith("scenario"):
                    file_name += ".py"
                else:
                    file_name += "_scenario.py"
                config_path = scenario_path + file_name
                with open(config_path, 'w+') as config_file:
                    config_file.write('"""\n')
                    config_file.write('This file was auto-generated by ScenarioFactory of aTLAS\n')
                    config_file.write('"""\n')
                    config_file.write("\n\n")
                    for arg in all_args:
                        value = self.stringify_arg_value(scenario, arg)
                        config_file.write(arg + " = " + value + "\n")
                    config_file.write("\n\n\n\n")

    def __init__(self):
        self.scenarios = ScenarioFactory.load_scenarios()
        self.init_scenario_number = len(self.scenarios)

    def __del__(self):
        self.save_scenarios()


