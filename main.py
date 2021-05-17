from agent.settings import CONFIG
from agent.utils import split_data
from agent.file_watcher import Watcher
from agent.filter_abnormal_area import FilterArea

if __name__ == "__main__":
    folder = CONFIG["path"]["read"]

    watcher = Watcher()
    file_list = watcher.collect_files()

    process_num = CONFIG["multiprocessing"]["process_num"]

    split_dict = split_data(file_list, process_num)

    processes = [
        FilterArea(split_dict[i])
        for i in range(CONFIG["multiprocessing"]["process_num"])
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join()
