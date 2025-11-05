

from src.tools.logger import logger


class GitHandler: # Here actual code for pushing that html file to github will be placed

    def __init__(self):
        self.logger = logger
        pass

    def push_file_to_repo(self, file_path):
        """
        This function will take file path for newly created game html file
        then will push this file on specific GIT repo provide in config file
        In return it will get depolyed URL which we can store it in the database
        """
        self.logger.info("Mock function called to push newly created html game file to git repo")