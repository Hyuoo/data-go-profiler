from utils.crawler_helper import DATA_GO
from utils.crawler_helper import block_function
from glob import glob



if __name__ == "__main__":
    option_list = glob("options/*.py")

    for fn in option_list:
        option = DATA_GO.read_option(fn)

        if option.get("RUN", False):
            ret = block_function(option)
    # print(ret)
    
    # option = DATA_GO.read_option(fn)
    # for org in option["ORG"]:
    #     t = DATA_GO(org, option["DTYPE"], option["SELECT"])
    # print(t)
    # t.get_dtype_count()
    
    

