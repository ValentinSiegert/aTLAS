from abc import ABC, abstractmethod


class BasicDistributor(ABC):
    """
    Basic distributor to decide which agents to place on which supervisors for one scenario run.
    """
    @abstractmethod
    def distribute(self, agents, supervisors):
        pass

