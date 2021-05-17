from agent.utils import read_config, get_logger

CONFIG = read_config("resources/config.yaml")
LOGGER = get_logger("agent", CONFIG["log"]["path"])
