import os
import glob

from agent.settings import CONFIG, LOGGER


class Watcher:
    def __init__(self):
        LOGGER.info("collecting files...")
        self.path = CONFIG["path"]["read"]
        self.extensions = CONFIG["watcher"]["format"]

    def collect_files(self):
        files = glob.glob(
            os.path.join(self.path, f"**/**{self.extensions}"), recursive=True
        )
        return files
