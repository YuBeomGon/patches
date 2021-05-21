import os
import yaml
import logging


def read_config(config_name):
    with open(config_name, "r") as f:
        config = yaml.safe_load(f)
    return config


def get_logger(name, log_file_path):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(process)d - %(filename)s#%(lineno)d - %(funcName)s - %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def get_slide_name(file_path):
    base_name = os.path.basename(file_path)
    return os.path.splitext(base_name)


def split_data(data, n):
    dic = {}
    for i in range(n):
        dic[i] = []

    i = 0
    while data:
        file = data.pop()
        dic[i].append(file)
        i = 0 if i == n - 1 else i + 1

    return dic
