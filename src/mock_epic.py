from .base_epic import BaseEpic

class MockEpic(BaseEpic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = []  # Initialize empty tasks list

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task_title):
        self.tasks = [task for task in self.tasks if task["title"] != task_title]

    def get_tasks(self):
        return self.tasks

    def load_json(self, file_path):
        # Mock JSON loading
        pass

    def save_json(self, file_path):
        # Mock JSON saving
        pass

    def edit_task(self, task_title, new_data):
        for task in self.tasks:
            if task["title"] == task_title:
                task.update(new_data)
                return True
        return False