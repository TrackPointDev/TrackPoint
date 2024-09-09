from abc import ABC, abstractmethod

class BaseEpic(ABC):
    def __init__(self, title, problem, feature, value):
        self.title = title
        self.problem = problem
        self.feature = feature
        self.value = value
        self.tasks = []

    @abstractmethod
    def add_task(self, task):
        pass

    @abstractmethod
    def remove_task(self, task_title):
        pass

    @abstractmethod
    def get_tasks(self):
        pass

    @abstractmethod
    def load_json(self, file_path):
        pass

    @abstractmethod
    def save_json(self, file_path):
        pass
