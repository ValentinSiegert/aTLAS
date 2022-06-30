from trustlab.lab.distributors.basic_distributor import BasicDistributor
from asgiref.sync import sync_to_async


class RoundRobinDistributor(BasicDistributor):
    """
    Distributes given agents of a scenario in a fair fashion over all available supervisors
    with a Round Robin algorithm. All supervisors get min(free_agents, fair_share) agents.
    """
    @sync_to_async
    def distribute(self, agents, supervisors):
        distribution = {}
        supervisors = sorted(supervisors, key=lambda s: s.max_agents - s.agents_in_use)
        rest_supervisors = len(supervisors)
        rest_agents = len(agents)
        for supervisor in supervisors:
            free_agents = supervisor.max_agents - supervisor.agents_in_use
            fair_share = rest_agents // rest_supervisors
            agents_to_take = min(free_agents, fair_share)
            rest_agents -= agents_to_take
            rest_supervisors -= 1
            distribution[supervisor.channel_name] = agents[:agents_to_take]
            agents = agents[agents_to_take:]
        distribution = {key: value for key, value in distribution.items() if value}
        return distribution
