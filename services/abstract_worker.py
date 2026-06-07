from abc import abstractmethod, ABC

from kgtool.interface import *
from multiprocessing import Process


class Worker(ABC):
    """
    A class representing a worker which uses the ChemEngKG.
    - Every service used with the ChemEngKG implements this class.
    - The worker should not be instantiated directly.
    """

    def __init__(self):
        self._chemkg = ChemKG.dev()
        self.process = Process()

    @classmethod
    @abstractmethod
    def asWorker(cls):
        """
        This function returns an instance of the service which is not setup to a specific task.
        - This function should only be used if the service is used in context of the ChemEngKG.
        - Each service must provide this function.
        """
        raise NotImplementedError("Each subclass of the worker class must implement the function *asWorker*.")

    @abstractmethod
    def _ask_for_task(self):
        """
        This function consults the ChemEngKG to get information about the next task for the service and sets up the service to be able to execute this task.

        E.g.: The PublicationMetaDataMiner asks the ChemEngKG for the next publication which has missing metadata.
        - This function should only be used if the service is used in context of the ChemEngKG.
        - Each service must provide this function.
        """
        raise NotImplementedError("Each subclass of the worker class must implement the function *ask_for_task*.")

    @abstractmethod
    def _execute_task(self):
        """
        This function executes the task which was set up by the function *ask_for_task*.
        - This function should only be used if the service is used in context of the ChemEngKG.
        - Each service must provide this function.
        """
        raise NotImplementedError("Each subclass of the worker class must implement the function *execute_task*.")

    @abstractmethod
    def _send_result(self):
        """
        This function sends the result of the task to the ChemEngKG.
        - This function should only be used if the service is used in context of the ChemEngKG.
        - Each service must provide this function.
        """
        raise NotImplementedError("Each subclass of the worker class must implement the function *send_result*.")

    @abstractmethod
    def run_worker(self):
        """
        This function runs the whole workflow as a worker.
        The workflow is: ask_for_task -> execute_task -> send_result
        - This function should only be used if the service is used in context of the ChemEngKG.
        - Each service must provide this function.
        """
        raise NotImplementedError("Each subclass of the worker class must implement the function *runWorker*.")