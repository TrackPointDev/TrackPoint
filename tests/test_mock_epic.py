import unittest
import logging
from src.mock_epic import MockEpic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestMockEpic(unittest.TestCase):
    def setUp(self):
        logger.info("Setting up test environment...")
        self.base_epic = MockEpic("Test Epic", "Problem", "Feature", "Value")
        logger.debug(f"Created MockEpic instance: {self.base_epic}")
        self.base_epic.start()

    def test_init(self):
        logger.info("Running test_init...")
        self.assertIsInstance(self.base_epic, type(self.base_epic))
        logger.debug(f"Type of base_epic: {type(self.base_epic)}")
        self.assertTrue(isinstance(self.base_epic, MockEpic))

    def test_add_task(self):
        logger.info("Running test_add_task...")
        task = {"title": "Task Title", "priority": "High", "description": "Description", "storypoints": 5}
        self.base_epic.add_task(task)
        logger.debug(f"Added task: {task}")
        self.assertEqual(len(self.base_epic.tasks), 1)
        logger.info(f"Verified {len(self.base_epic.tasks)} tasks in the list")

    def test_remove_task(self):
        logger.info("Running test_remove_task...")
        task = {"title": "Task Title", "priority": "High", "description": "Description", "storypoints": 5}
        self.base_epic.add_task(task)
        logger.debug(f"Added task: {task}")
        self.base_epic.remove_task("Task Title")
        logger.info("Removed task")
        self.assertEqual(len(self.base_epic.tasks), 0)
        logger.info(f"Verified {len(self.base_epic.tasks)} tasks remaining")

    def test_get_tasks(self):
        logger.info("Running test_get_tasks...")
        task = {"title": "Task Title", "priority": "High", "description": "Description", "storypoints": 5}
        self.base_epic.add_task(task)
        logger.debug(f"Added task: {task}")
        tasks = self.base_epic.get_tasks()
        logger.debug(f"Retrieved tasks: {tasks}")
        self.assertEqual(tasks[0]["title"], "Task Title")
        logger.info(f"Verified first task title: {tasks[0]['title']}")

if __name__ == '__main__':
    logger.info("Starting unit test execution...")
    unittest.main()
