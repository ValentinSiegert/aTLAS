from abc import ABC, abstractmethod


class BasicConnector(ABC):
    """
    Basic class to manage the supervisor connections.
    """
    @abstractmethod
    def sums_agent_numbers(self):
        """
        :return: sum of maximal agents and sum of agents in use over all registered supervisors.
        :rtype: (int, int)
        """
        pass

    @abstractmethod
    def list_supervisors_with_free_agents(self):
        pass

    @abstractmethod
    def get_supervisors_without_given(self, given_channel_name):
        pass

    @abstractmethod
    async def reserve_agents(self, distribution, scenario_run_id, scenario_data):
        pass

    @abstractmethod
    async def start_scenario(self, distribution, scenario_run_id):
        pass

    @abstractmethod
    async def get_next_done_observation(self, scenario_run_id):
        pass

    @abstractmethod
    async def broadcast_done_observation(self, scenario_run_id, done_observations_with_id, supervisors_to_inform):
        pass

    @abstractmethod
    async def end_scenario(self, involved_supervisors, scenario_run_id):
        pass

