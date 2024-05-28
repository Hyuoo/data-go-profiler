from utils.crawler_helper import DATA_GO
from utils.crawler_helper import block_function
import os
from glob import glob

dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    option_list = glob(dir+"/options/*.py")

    for fn in option_list:
        option = DATA_GO.read_option(fn)
        print(f"{fn} [RUN: {option.get("RUN", False)}]")

        if option.get("RUN", False):
            ret = block_function(option)
    
    # option = DATA_GO.read_option(fn)
    # for org in option["ORG"]:
    #     t = DATA_GO(org, option["DTYPE"], option["SELECT"])
    # print(t)
    # t.get_dtype_count()
    
    

