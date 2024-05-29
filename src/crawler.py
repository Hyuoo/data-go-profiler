"""
공공데이터포털(https://www.data.go.kr/)내의 제공 데이터 목록을 크롤/스크래핑 합니다.


"""

import requests
from requests.adapters import HTTPAdapter
from requests import HTTPError
from bs4 import BeautifulSoup
import re
import logging
import traceback
from pprint import pprint



LOG_FORMAT = '[%(asctime)s][%(levelname)s: File "%(filename)s", line %(lineno)s in %(funcName)s] %(message)s'
LOG_FORMAT_SHORT = '[%(levelname)s:line %(lineno)s in %(funcName)s] %(message)s'

SEARCH_URL = "https://www.data.go.kr/tcs/dss/selectDataSetList.do" \
                "?dType={dtype}&keyword=&operator=&detailKeyword=&publicDataPk=" \
                "&recmSe=&detailText=&relatedKeyword=&commaNotInData=&commaAndData=" \
                "&commaOrData=&must_not=&tabId=&dataSetCoreTf=&coreDataNm=" \
                "&sort=updtDt&relRadio=&orgFullName={org}&orgFilter={org}&org={org}" \
                "&orgSearch=&currentPage={current_page}&perPage=10&brm=&instt=" \
                "&svcType=&kwrdArray=&extsn=&coreDataNmArray=&pblonsipScopeCode="
BASE_URL = "https://www.data.go.kr"


# strip + 2칸이상 공백 제거
rmln = lambda x:" ".join(x.split())

def tel_no_format(telno: str) -> str:
    # 전화번호 하이픈 없을 경우 추가
    if telno and not re.findall(r"\d{2,3}-\d{4}-\d{4}", telno):
        return "-".join(re.search(r"^(02.{0}|01.{1}|[0-9]{3})([0-9]+)([0-9]{4})", telno).groups())
    return telno

def get_soup(
        url: str,
        *,
        logger: logging.Logger = None
    ) -> BeautifulSoup:
    """
    url 문자열을 입력받아 요청 후, 페이지 파싱 객체를 리턴
    
    :return: 요청 페이지의 bs4객체를 반환
    :rtype: BeautifulSoup
    """
    logger = logger or logging.getLogger("dummy")

    logger.info(f":: request to [{url}] ::")
    s = requests.session()
    s.mount('https://', HTTPAdapter(max_retries=3, ))
    res = s.get(url)

    logger.debug(f"response status: {res.status_code}")
    
    if res.status_code != 200:
        raise HTTPError
    
    soup = BeautifulSoup(res.text, "html.parser")
    return soup


def get_page_count(
        *,
        org: str,
        dtype: str,
        logger: logging.Logger = None,
    ) -> tuple[int]:
    """
    :param org: 기관명 ("통일부")
    :param dtype: FILE, API등 공공데이터 타입 ("API")

    :return: 페이지네이션의 수와 데이터 건수를 함께 반환함.
    :rtype: (int, int)
    """
    logger = logger or logging.getLogger("dummy")

    url = SEARCH_URL.format(
        dtype=dtype,
        org=org,
        current_page=1,
    )
    soup = get_soup(url, logger=logger)
    
    # 데이터 건 수
    dtype_count = -1
    if dtype.lower() == "api":
        dtype_count = soup.select_one("#apiCnt").text
    elif dtype.lower() == "file":
        dtype_count = soup.select_one("#fileCnt2").text
    elif dtype.lower() == "linked":
        dtype_count = soup.select_one("#linkedCnt").text
    
    # 전체 페이지 개수 리턴
    page_div = soup.select("nav.pagination")
    if not page_div:
        # 검색결과 자체가 없음 (0건)
        return (0, dtype_count)
    try:
        # 맨 뒤 버튼이 있는 경우
        last_a = page_div[0].select("a.control.last")
        # 예시로 가져온 a 태그의 onclick 속성 값
        onclick_value = last_a[0].get('onclick')

        # 숫자만 추출하는 정규 표현식
        numbers = re.findall(r'\d+', onclick_value)
        page_count = int(numbers[0])
    except:
        # 없는 경우 a 태그 개수를 세야함
        count_a = len(page_div[0].select("a"))
        page_count = count_a + 1
    
    return (page_count, dtype_count)


def get_page_list(
        *,
        org: str,
        dtype: str,
        page_number: int,
        logger: logging.Logger = None,
    ) -> list[dict[str]]:
    """
    한 페이지의 데이터 목록을 List[Dict[str]] 형태로 반환함.

    :param org: 기관명 ("통일부")
    :param dtype: FILE, API등 공공데이터 타입 ("API")
    :param page_number:
    
    :return: 
    :rtype: 
    """
    logger = logger or logging.getLogger("dummy")

    url = SEARCH_URL.format(
        dtype=dtype,
        org=org,
        current_page=page_number,
    )
    soup = get_soup(url, logger=logger)
   
    result_list = soup.select_one("div.result-list")
    li_list = result_list.find_all("li")
    records = []  # 각 행의 데이터를 담을 리스트

    for li in li_list:
        # 리스트의 각 행을 순회
        _is_recent = False
        dt = li.find("dl").find("dt")
        try:
            title = dt.find("span", class_ = "title").text.strip()
        except:
            # 업데이트 된 데이터의 경우 라벨이 붙으며 class 명이 달라짐.
            title = next(dt.find("span", class_ = "recent-title").strings).strip()
            _is_recent = True
        # 상세 링크
        info_url = dt.find("a")["href"]
        # 확장자 / 데이터포맷
        tagset = ','.join(span.text.strip() for span in dt.find_all("span", class_= "tagset"))
        
        # 목록 하단 키워드 (k-v)
        div_info_list = li.find("div", class_ = "info-data").find_all("p")

        info_dict = {}
        for info in div_info_list:
            tit = info.find("span", class_ = "tit").text.strip()
            # tit 예외처리
            if (tit == "제공기관"):
                data = info.find("span", class_ = "data").text.strip()
            elif(tit == "키워드"):
                data = list(info.children)[-1].strip()
            elif(tit == "수정일" and _is_recent):
                # 업데이트 된 데이터의 경우 수정일 class 명이 달라짐.
                data = info.find("span", class_ = "recent-update-dt").text.strip()
            else:
                data = info.find("span", class_ = "data").text.strip()
            info_dict[tit] = data

        # 각 행의 데이터를 리스트에 추가
        # 현재 데이터명, 상세링크, 조회수만 urls에 저장함
        # # 나머지 내용은 상세 페이지에서 수집 가능.
        temp_data = {
            "데이터명": title,
            "상세링크": BASE_URL + info_url, 
            "제공기관": info_dict.get("제공기관", ""), 
            "수정일": info_dict.get("수정일", ""), 
            "조회수": info_dict.get("조회수", ""), 
            "키워드": info_dict.get("키워드", ""),
            }
        
        if dtype.lower() == "api":
            temp_data["데이터포맷"] = tagset
            temp_data["활용신청"] = info_dict.get("활용신청", "")
        elif dtype.lower() == "file":
            temp_data["확장자"] = tagset
            temp_data["다운로드"] = info_dict.get("다운로드", "")
        elif dtype.lower() == "linked":
            temp_data["확장자"] = tagset
            # 연계데이터의 바로가기 횟수는 목록에서 제공안함
            # temp_data["바로가기 횟수"] = info_dict.get("바로가기 횟수", "")

        records.append(temp_data)

    # 각 페이지별 list를 반환
    return records


def get_detail_page(
        detail_url: str,
        *,
        logger: logging.Logger = None,
        __index_counting = [0, ""],
    ) -> dict[str]:
    """
    DATA, API, LINKED 공통
    상세페이지의 str타입 url을 입력받아 해당 페이지의 내용들을 딕셔너리로 반환합니다.

    기본 데이터 정보(key):
        - type: 서비스 타입 ("filedata" | "openapi" | "linked")
        - title: 서비스 명
        - description: 서비스 설명
        - service_url: 서비스 상세페이지의 URL
        - service_id: 서비스 id
        - formats: 서비스 지원 포맷
        외 페이지에서 제공하는 데이터 한글 키-값
    
    :param detail_url: 상세 페이지 url
    
    :return: 상세 페이지의 data table의 정보를 모두 key-value로 저장한 딕셔너리
    :rtype: dict[str]
    """
    logger = logger or logging.getLogger("dummy")

    result = {}
    soup = get_soup(detail_url, logger=logger)
    
    tmp = soup.select_one("#contents")
    
    if tmp is None:
        # 폐기된 공공데이터일 경우
        result["type"] = dtype
        result["service_url"] = detail_url
        alert_msg = re.search(r"alert\(([^\)]+)\)", str(soup)).groups()[0]
        result["title"] = alert_msg
        logger.info(f"({dtype}){alert_msg}")
        return result
    
    # board: 본문 영역
    board = tmp.select_one("div.data-search-view")
    
    # url에서 검색 dtype 추출
    dtype = ""
    if "fileData" in detail_url:
        dtype = "filedata"
    elif "openapi" in detail_url:
        dtype = "openapi"
    elif "linked" in detail_url:
        dtype = "linked"

    # title area
    title_area = board.select_one("div.data-set-title")
    
    # formats는 openapi에서만 존재함
    *formats, title = list(title_area.select_one(".tit-area").stripped_strings)
    description = board.select_one(".cont").text.strip()
    
    # 기본 데이터 정보
    result["type"] = dtype
    result["title"] = title
    result["description"] = description
    result["service_url"] = detail_url
    result["service_id"] = re.search(r"\d+", detail_url).group()
    result["formats"] = formats
    
    if __index_counting[1] != logger.name:
        __index_counting[1] = logger.name
        __index_counting[0] = 0
    logger.info(f"({dtype}/{result['service_id']}) 목록명: {__index_counting[0]}.{title}")
    __index_counting[0] += 1
    logger.debug(f"지원포맷: {formats}\t설명: {description}")
    
    # data table
    for data_table_row in board.select("div.file-meta-table-pc > table > tr"):
        # 테이블의 내용을 key-value로 매칭시켜 result에 저장
        cols = data_table_row.find_all(["th", "td"])
        for th, td in zip(cols[::2], cols[1::2]):
            if th.name != "th" or td.name != "td":
                msg = f"data table error. does not matched (th-td). {detail_url}\nth: {th}\ntd: {td}"
                logger.info(msg)
                # raise RuntimeError(msg)
                continue
            key = rmln(th.text)
            value = rmln(td.text)
            if key == "관리부서 전화번호" and not value:
                # 관리부서 전화번호 페이지 구조 예외
                if (tmp_search_result:=re.search(r"telNo.+\"([\d.]+)\"", td.select_one("script").text)):
                    telno = tmp_search_result.groups()[0]
                    value = tel_no_format(telno)
            result[key] = value
            logger.debug("{}: [{}]".format(key, value))
    
    if logger.root.level == logging.DEBUG: input("(DEBUG MODE)wait..")
    
    return result

    

if __name__ == "__main__":
    # detail만 테스트
    urls = [
        "https://www.data.go.kr/data/15085024/openapi.do",
        "https://www.data.go.kr/data/15040578/fileData.do",
        "https://www.data.go.kr/data/15004113/fileData.do",
        "https://www.data.go.kr/data/15001306/fileData.do",
        "https://www.data.go.kr/data/1705866/linkedData.do",
        ]
    
    for url in urls:
        try:
            result = get_detail_page(url)
            pprint(result)
        except:
            print(traceback.format_exc())
