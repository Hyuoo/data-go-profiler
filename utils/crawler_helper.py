from __future__ import annotations
import sys

if __name__ == "__main__":
    sys.path.append(r"C:\Users\user\lhwoo\90_data_go")

from utils import crawler
from utils.util import *
import os
import traceback
import json
import pandas as pd
import logging
from textwrap import dedent
from time import sleep
from datetime import datetime

LOG_FORMAT = '[%(asctime)s][%(levelname)s: File "%(filename)s", line %(lineno)s in %(funcName)s] %(message)s'
LOG_FORMAT_SHORT = '[%(levelname)s:line %(lineno)s in %(funcName)s] %(message)s'

logging.basicConfig(
    level=logging.ERROR,
    format=LOG_FORMAT_SHORT,
)

class DATA_GO:
    exist_obj_list = []

    _DATA_DIR = "data/"
    _LOG_DIR = "logs/"
    _URL_FILE = _DATA_DIR + "{org}_urls_{date}_{dtype}.txt"
    _RAW_FILE = _DATA_DIR + "{org}_공공데이터_{date}_{dtype}.json"
    _CSV_FILE = _DATA_DIR + "{org}_공공데이터_{date}_{dtype}.csv"
    _LOG_FILE = _LOG_DIR + "{org}_공공데이터_{date}_{dtype}.log"


    def __init__(
        self,
        ORG: str,
        DTYPE: list,
        SELECT: str
    ):

        self.org = ORG
        self.dtype = DTYPE
        self.select = SELECT
        self.date = datetime.now().strftime("%Y%m%d")

        self.csv_file = self._CSV_FILE.format(org=self.org, date=self.date, dtype="_".join(self.dtype))
        self.url_file = self._URL_FILE.format(org=self.org, date=self.date, dtype="_".join(self.dtype))
        self.raw_file = self._RAW_FILE.format(org=self.org, date=self.date, dtype="_".join(self.dtype))

        self.headers, self.select_key_list = column_header_n_select(self.select)
    
        self.exist_obj_list.append(self)


        self.logger = logging.getLogger("{}.{}".format(__class__.__qualname__, ORG))
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(self._LOG_FILE.format(org=self.org, date=self.date, dtype="_".join(self.dtype)), encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        self.logger.addHandler(file_handler)

        # stream_handler = logging.StreamHandler(sys.stdout)
        # stream_handler.setLevel(logging.DEBUG)
        # stream_handler.setFormatter(logging.Formatter(LOG_FORMAT_SHORT))
        # self.logger.addHandler(stream_handler)

        self.logger.debug(f"initializing [{ORG}]\tlogger [{self.logger.name}]")
        self.option_logging()
    
    def __repr__(self):
        return f"기관명: \"{self.org}\"\tDTYPE: {self.dtype}"
    
    def option_logging(self) -> None:
        self.logger.info(f"[OPTION] ORG: {self.org}")
        self.logger.info(f"[OPTION] DTYPE: {self.dtype}")
        self.logger.info("[OPTION] COLUMN << CONTENT")
        for k, v in zip(self.headers, self.select_key_list):
            self.logger.info(f"{k} << {v}")


    def get_dtype_count(self) -> str:
        """
        모든 각 dtype에 대하여 (페이지 개수, 데이터 건수)를 셈

        :return: 각 dtype별 건수와 페이지 문자열
        """
        self.page_count = {}
        self.dtype_count = {}

        ret = ""
        for dtype in self.dtype:
            page_count, dtype_count = crawler.get_page_count(org=self.org, dtype=dtype, logger=self.logger)
            self.page_count[dtype] = page_count
            self.dtype_count[dtype] = dtype_count
            ret += f"{dtype}: {dtype_count}건({page_count}페이지)\t"
        
        self.logger.info(ret)
        return ret
    
    def crawl_n_save_urls(self):
        """
        ORG의 모든 DTYPE에 대하여 모든 서비스의 url을 txt로 저장.
        ["데이터(서비스)명", "상세링크_URL", "조회수"]를 줄 단위로 저장함.
        (sep="\t")

        file >> "{DATA_DIR}{org}_urls.txt"
        """
        if os.path.exists(self.url_file):
            msg = f'already exists "{self.url_file}"'
            raise FileExistsError(msg)

        f = open(self.url_file, "w", encoding="utf-8")

        for dtype in self.dtype:
            self.logger.info(f"[{dtype}]pagination: {self.page_count[dtype]}")

            for page_number in range(1, self.page_count[dtype]+1):
                self.logger.info(f"[{dtype}]page_processing: {page_number}/{self.page_count[dtype]}.")
                records = crawler.get_list_one_page(org=self.org, dtype=dtype, page_number=page_number, logger=self.logger)
                
                for r in records:
                    r_name = r.get("데이터명", "")
                    r_url = r.get("상세링크", "")
                    r_view = r.get("조회수", "")
                    f.write(f"{r_name}\t{r_url}\t{r_view}\n")
        
        f.close()

    def read_urls(self):
        """
        self.url_file을 읽어서 필요한 url, views만 가져와 중첩 리스트로 반환
        """
        if not os.path.exists(self.url_file):
            msg = f'not exists "{self.url_file}"'
            raise FileExistsError(msg)

        with open(self.url_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        urls = []
        for line in lines:
            title, url, views = line.split("\t")
            views = views.rstrip()

            urls.append([url, views])
        return urls
    
    def save_raw_data(self, raw_data):
        with open(self.raw_file, "w") as f:
            json.dump(raw_data, f)
    
    def crawl_detail_pages(self, urls):
        """
        urls: [[url, views], ...]
        상세 페이지의 정보와 조회수를 합쳐서 아래 데이터를 생성함
        - raw_data: 딕셔너리 그대로의 json파일
        - data: 필요한 컬럼만 뽑은 csv를 만들기 위한 레코드 집합
        """
        raw_data = []
        data = []

        for url, views in urls:
            record = []
            try:
                result = crawler.get_detail_page(url, logger=self.logger)
                result["조회수"] = views
                raw_data.append(result)
                # pprint(result)
                for select in self.select_key_list:
                    for s in select:
                        if s in result:
                            record.append(result.get(s, ""))
                            break
                    else:
                        record.append("")
                sleep(1)
            except:
                print(traceback.format_exc())
            
            data.append(record)

        self.save_raw_data(raw_data)
        return data

    def save_to_csv(self, data):
        try:
            df = pd.DataFrame(data, columns=self.headers)
            df.to_csv(
                self.csv_file,
                header=True,
                index=True,
                index_label="index",
                encoding="utf-8",
            )
        except Exception as e:
            print(e)
            return -1
        return 0
    
    def is_exists(self):
        # 최종파일인 csv파일이 존재하는지 여부
        if os.path.exists(self.csv_file):
            return True
        return False
    
    def log_print(self, msg, level:str|int=logging.INFO):
        if isinstance(level, int):
            level = logging.getLevelName(level).lower()
        elif isinstance(level, str):
            level = level.lower()
        else:
            self.logger.error("log set_level Erorr.")
        
        getattr(self.logger, level)(msg)

    @staticmethod
    def read_option(file_name: str) -> dict:
        """
        ORG, DTYPE, SELECT가 정의된 options파일을 읽어 DATA_GO객체 생성
        """
        with open(file_name, "r", encoding="utf-8") as f:
            option = eval(f.read())
            
        for requirement_value in ["ORG", "DTYPE", "SELECT"]:
            if requirement_value not in option:
                raise SyntaxError(f"no reqiured key: [{requirement_value}]")

        option["SELECT"] = dedent(option["SELECT"])
        # print(option)
        option["MERGE"] = option.get("MERGE", False)

        option["ORG"] = (
                option["ORG"]
                if isinstance(option["ORG"], list)
                else [
                    option["ORG"],
                ]
            )

        return option

    @staticmethod
    def merge_csv(file_list):
        dfs = []
        orgs = []
        for file in file_list:
            org = file.split("/")[-1].split("\\")[-1].split("_")[0]
            tmp = pd.read_csv(file)
            tmp["org"] = org
            orgs.append(org)
            dfs.append(tmp)

        output_file = DATA_GO._DATA_DIR + f"merged_{orgs[0]}_공공데이터.csv"
        all_df = pd.concat([*dfs])
        all_df["org"] = pd.Categorical(all_df["org"], categories=orgs)
        all_df.to_csv(output_file, index=False)
        
        return output_file


def block_function(option_arg: any):
    """
    일괄실행 함수
    - 옵션파일 or read_option()의 딕셔너리 입력하여 실행

    옵션 -> urls생성 -> 상세페이지 수집 -> csv 저장 -> 통합
    """
    option = None
    if isinstance(option_arg, str):
        # 문자열일 경우 파일 경로 입력
        if not os.path.exists(option_arg):
            msg = f"not exists file: [{option_arg}]"
            raise FileNotFoundError(msg)
        
        option = DATA_GO.read_option(option_arg)
    elif isinstance(option_arg, dict):
        # read_option을 수행 한 딕셔너리 입력
        option = option_arg

    if option is None:
        msg = f"No option file or dict. {option_arg}"
        print(msg)
        return -1
    
    obj_list = []

    for org in option["ORG"]:
        t = DATA_GO(ORG=org, DTYPE=option["DTYPE"], SELECT=option["SELECT"])
        obj_list.append(t)

    output_file_list = []

    for obj in obj_list:
        obj:DATA_GO
        if obj.is_exists():
            obj.log_print(f"already exists {obj.csv_file} - SKIP")
            output_file_list.append(obj.csv_file)
            continue

        print("START OPTION:", obj.org)
        obj.get_dtype_count()
        # print(obj.page_count)
        # print(obj.dtype_count)

        try:
            obj.crawl_n_save_urls()
        except Exception as e:
            print(e)

        # urls: [[url, views], ...]
        urls = obj.read_urls()
        if obj.save_to_csv(obj.crawl_detail_pages(urls=urls)) == 0:
            output_file_list.append(obj.csv_file)
    
    if option["MERGE"] and len(output_file_list) > 1:
        tmp = DATA_GO.merge_csv(output_file_list)
        output_file_list.append(tmp)
    
    return output_file_list


if __name__ == "__main__":
    ...
    # ret = DATA_GO.read_option("options/통일부.py")

    # for obj in ret:
    #     print(obj.org)
    #     obj.get_dtype_count()
    #     # print(obj.page_count)
    #     print(obj.dtype_count)

    #     try:
    #         obj.crawl_n_save_urls()
    #     except Exception as e:
    #         print(e)

    #     if obj.is_exists():
    #         continue

    #     # urls: [[url, views], ...]
    #     urls = obj.read_urls()

    #     data = obj.crawl_detail_pages(urls=urls)
    #     obj.save_to_csv(data)
