from epics.base_epic import BaseEpic

class MockEpic(BaseEpic):
    def start(self):
        print("Starting Mock Epic...")

    def create_issues(self):
        # Mock issue creation
        pass

    def get_issues(self):
        # Mock issue retrieval
        pass
    
    def delete_issue(self):
        # Mock issue deletion
        pass

    def format_body(self, task):
        # Mock body formatting
        pass

    def load_json(self, file_path):
        # Mock JSON loading
        pass

    def save_json(self, file_path):
        # Mock JSON saving
        pass
