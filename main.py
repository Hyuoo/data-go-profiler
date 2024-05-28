from utils.crawler_helper import DATA_GO
from utils.crawler_helper import block_function
import os
from glob import glob

dir = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    # options 내의 python파일을 모두 스캔
    option_list = glob(dir+"/options/*.py")

    for fn in option_list:
        option = DATA_GO.read_option(fn)
        print(f"{fn} [RUN: {option.get('RUN', False)}]")

        # option의 값 중 RUN이 True일 경우에만 크롤링 실행
        if option.get("RUN", False):
            ret = block_function(option)


