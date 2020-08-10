from abc import ABC, abstractmethod


class BasicDistributor(ABC):
    @abstractmethod
    def distribute(self, agents, supervisors):
        pass

