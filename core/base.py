from abc import ABC, abstractmethod


class BaseSite(ABC):

    NAME = ""

    @abstractmethod
    def latest(self):
        pass
