import sys
from agent.settings import CONFIG
from agent.utils import split_data
from agent.file_watcher import Watcher
from agent.filter_abnormal_area import FilterArea

if __name__ == "__main__":
    # print(len(sys.argv))
    if len (sys.argv) > 2 :
        src_folder = sys.argv[1]
        des_folder = sys.argv[2]
        process_num = 1
    else :
        src_folder = CONFIG["path"]["read"]
        des_folder = CONFIG["path"]["save"]
        process_num = CONFIG["multiprocessing"]["process_num"]
        
    print('******',src_folder, des_folder)

#     watcher = Watcher(src_folder)
#     file_list = watcher.collect_files()

#     split_dict = split_data(file_list, process_num)
#     print('split_dict', split_dict)
    
    FilterArea(src_folder, des_folder).run()

#     processes = [
#         FilterArea(split_dict[i], des_folder)
#         for i in range(CONFIG["multiprocessing"]["process_num"])
#     ]

#     for process in processes:
#         process.start()

#     for process in processes:
#         process.join()
