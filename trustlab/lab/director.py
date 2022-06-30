import socket
import trustlab.lab.config as config
from asgiref.sync import sync_to_async
from trustlab.lab.connectors.channels_connector import ChannelsConnector
from trustlab.lab.distributors.greedy_distributor import GreedyDistributor
from trustlab.lab.distributors.round_robin_distributor import RoundRobinDistributor
from trustlab.serializers.scenario_serializer import ScenarioSerializer
from trustlab.models import ResultFactory, ScenarioResult
from trustlab_host.models import Scenario


class Director:
    """
    Organizes the testbed's environment for one specific scenario run.
    Therewith decides which supervisors should be involved,
    prepares the scenarios with them,
    overwatches the run by informing all involved supervisors about done observations,
    and terminates the evaluation run by signalling the end to all involved supervisors.
    All scenario run results are saved with the usage of ScenarioResult and ResultFactory.
    """
    async def prepare_scenario(self):
        """
        Prepares the scenario run by deciding which supervisors to involve,
        signalling them to prepare everything for the run,
        and distributing the global agent discovery to all involved supervisors.

        :return: The amount of supervisors used for this scenario run.
        :rtype: int
        """
        agents = self.scenario.agents
        # check if enough agents are free to work
        sum_max_agents, sum_agents_in_use = await self.connector.sums_agent_numbers()
        free_agents = sum_max_agents - sum_agents_in_use
        if free_agents < len(agents):
            raise Exception('Currently there are not enough agents free for the chosen scenario.')
        # distribute agents on supervisors
        supervisors_with_free_agents = await self.connector.list_supervisors_with_free_agents()
        self.distribution = await self.distributor.distribute(agents, supervisors_with_free_agents)
        # reserve agents at supervisors
        scenario_serializer = ScenarioSerializer(self.scenario)
        await sync_to_async(config.write_scenario_status)(self.scenario_run_id, f"Reserving Agents..")
        self.discovery = await self.connector.reserve_agents(self.distribution, self.scenario_run_id,
                                                             scenario_serializer.data)
        await sync_to_async(config.write_scenario_status)(self.scenario_run_id,
                                                          f"Scenario Distribution:\n{self.discovery}")
        return len(self.distribution.keys())

    async def run_scenario(self):
        """
        Runs the scenario and manages the correct observation sequence by broadcasting end of observation signal
        from one supervisor to all other involved ones.
        Further, it manages the scenario run results and initiates the save.
        """
        await self.connector.start_scenario(self.distribution.keys(), self.scenario_run_id)
        trust_log, trust_log_dict = [], []
        agent_trust_logs = dict((agent, []) for agent in self.scenario.agents)
        agent_trust_logs_dict = dict((agent, []) for agent in self.scenario.agents)
        scenario_runs = True
        observations_to_do_amount = len([observation["observation_id"] for observation in self.scenario.observations])
        done_observations_with_id = []
        while scenario_runs:
            done_dict = await self.connector.get_next_done_observation(self.scenario_run_id)
            await sync_to_async(config.write_scenario_status)(self.scenario_run_id,
                                                              f"Did observation {done_dict['observation_id']}")
            done_observations_with_id.append(done_dict['observation_id'])
            supervisors_to_inform = await self.connector.get_supervisors_without_given(done_dict["channel_name"])
            await self.connector.broadcast_done_observation(self.scenario_run_id, done_observations_with_id,
                                                            supervisors_to_inform)
            # merge send logs to saved results
            obs_receiver = done_dict['receiver']
            recv_trust_log = done_dict['trust_log'].split('<br>')
            new_trust_log = [line for line in recv_trust_log if line not in trust_log]
            recv_trust_dict = done_dict['trust_log_dict']
            new_trust_log_dict = [d for d in recv_trust_dict if d not in trust_log_dict]
            recv_receiver_log = done_dict['receiver_trust_log'].split('<br>')
            new_receiver_log = [line for line in recv_receiver_log if line not in agent_trust_logs[obs_receiver]]
            recv_receiver_log_dict = done_dict['receiver_trust_log_dict']
            new_receiver_log_dict = [d for d in recv_receiver_log_dict if d not in agent_trust_logs_dict[obs_receiver]]
            trust_log.extend(new_trust_log)
            trust_log_dict.extend(new_trust_log_dict)
            agent_trust_logs[obs_receiver].extend(new_receiver_log)
            agent_trust_logs_dict[obs_receiver].extend(new_receiver_log_dict)
            if len(done_observations_with_id) == observations_to_do_amount:
                scenario_runs = False
                await sync_to_async(config.write_scenario_status)(self.scenario_run_id, f"Scenario finished.")
        for agent, log in agent_trust_logs.items():
            if len(log) == 0:
                agent_trust_logs[agent].append("The scenario reported no agent trust log for this agent.")
        await self.save_scenario_run_results(trust_log, trust_log_dict, agent_trust_logs, agent_trust_logs_dict)
        return trust_log, trust_log_dict, agent_trust_logs, agent_trust_logs_dict

    @sync_to_async
    def save_scenario_run_results(self, trust_log, trust_log_dict, agent_trust_logs, agent_trust_logs_dict):
        """
        Saves the scenario run results with the usage of ScenarioResult and ResultFactory.

        :param trust_log: Scenario run trust log.
        :type trust_log: list
        :param trust_log_dict: Scenario run trust log in dictionaries.
        :type trust_log_dict: list
        :param agent_trust_logs: Trust logs per agent.
        :type agent_trust_logs: dict
        :param agent_trust_logs_dict: Trust logs per agent in dictionaries.
        :type agent_trust_logs_dict: dict
        """
        result_factory = ResultFactory()
        result = ScenarioResult(self.scenario_run_id, self.scenario.name, len(self.distribution.keys()), trust_log,
                                trust_log_dict, agent_trust_logs, agent_trust_logs_dict)
        result_factory.save_result(result)

    async def end_scenario(self):
        """
        Signals the end of the scenario run to all involved supervisors.
        """
        await self.connector.end_scenario(self.distribution, self.scenario_run_id)

    def __init__(self, scenario):
        self.HOST = socket.gethostname()
        self.scenario_run_id = config.create_scenario_run_id()
        self.scenario = scenario
        self.connector = ChannelsConnector()
        if config.DISTRIBUTOR == "round_robin":
            self.distributor = RoundRobinDistributor()
        else:
            self.distributor = GreedyDistributor()
        self.distribution = None
        self.discovery = None
