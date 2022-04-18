import sys
from agent.filter_abnormal_area import FilterArea

if __name__ == "__main__":
    # print(len(sys.argv))
    if len (sys.argv) > 2 :
        src_folder = sys.argv[1]
        des_folder = sys.argv[2]
        process_num = 1
    else :
        print('************** error , src dest dir should be sent **********')

    FilterArea(src_folder, des_folder).run()

