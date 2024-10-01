from abc import ABC, abstractmethod

class BaseEpic(ABC):
    def __init__(self, title, problem, feature, value):
        self.title = title
        self.problem = problem
        self.feature = feature
        self.value = value
        self.tasks = []
    @abstractmethod
    def start(self):
        pass
    
    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task_title):
        self.tasks = [task for task in self.tasks if task["title"] != task_title]

    def get_tasks(self):
        return self.tasks
    
    def edit_task(self, task_title, new_data):
        self.tasks = [new_data if task["title"] == task_title else task for task in self.tasks]

    @abstractmethod
    def create_issues(self):
        pass

    @abstractmethod
    def get_issues(self):
        pass

    @abstractmethod
    def delete_issue(self, title):
        pass

    @abstractmethod
    def format_body(self, task):
        pass

    @abstractmethod
    def load_json(self, file_path):
        pass

    @abstractmethod
    def save_json(self, file_path):
        pass
    
    
