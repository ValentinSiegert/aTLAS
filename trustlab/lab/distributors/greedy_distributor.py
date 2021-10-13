from trustlab.lab.distributors.basic_distributor import BasicDistributor
from asgiref.sync import sync_to_async


class GreedyDistributor(BasicDistributor):
    """
    Distributes given agents of a scenario in a greedy fashion over all available supervisors.
    """
    @sync_to_async
    def distribute(self, agents, supervisors):
        distribution = {}
        while len(agents) > 0:
            free_agents = supervisors[0].max_agents - supervisors[0].agents_in_use
            distribution[supervisors[0].channel_name] = agents[:free_agents]
            agents = agents[free_agents:]
            supervisors = supervisors[1:]
        return distribution

