from src import read_option, block_function
import os
import sys
from glob import glob



def run_options():
    """
    if no argv, run with all options in './options/*.py'
    """
    dir = os.path.dirname(os.path.abspath(__file__))

    # options 내의 python파일을 모두 스캔
    option_list = glob(dir+"/options/*.py")

    for fn in option_list:
        option = read_option(fn)
        print(f"{fn} [RUN: {option.get('RUN', False)}]")

        # option["RUN"]이 True로 설정 된 경우에만 크롤링 실행
        if option.get("RUN", False):
            ret = block_function(option)


if __name__ == "__main__":
    if len(sys.argv)==1:
        run_options()
    else:
        print("not support arguments.")


