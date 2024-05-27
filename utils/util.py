import re


def column_header_n_select(text: str) -> tuple[list[str], list[list[str]]]:
    """유사 쿼리 형식의 문자열을 처리하여 header, selector[] 형태로 반환
    
    ex)
        title as 타이틀
        description as 설명
        확장자 or 데이터포맷 as 확장자/데이터포맷
    
    - header는 csv header로 사용함.
    - dictionary에서 앞의 key 값을 통해서 alias로 저장하기 위함.
    - or 등의 서로다른 key값을 통합하기 위해서 selector는 List로 구현됨.
        - A or B or C == collase(A, B, C)
    """
    header = []
    select = []

    for col in text.strip().split("\n"):
        key = []
        alias = ""

        if " as " in col:
            tmp = col.split(" as ")
            if len(tmp) > 2:
                raise SystemError("한 문장에 as는 한번만 사용 가능 \"{str}\"".format(str=col))
            col, alias = tmp
        if " or " in col:
            if not alias:
                raise SyntaxError("as 없이 or 쓸 수 없음 \"{str}\"".format(str=col))
            key = col.split(" or ")
        
        if not key:
            key = [col]
        if not alias:
            alias = key[0]
        
        header.append(alias)
        select.append(key)
    
    return (header, select)


def integrate_csv_to_excel(csv_files: list[str], target: str = None):
    """
    csv파일 목록을 입력받아, 해당 파일들을 하나의 엑셀에 각 시트로 통합하는 함수
    """
    import pandas as pd

    if target is None:
        target = "report/tmp_csv_integrated.xlsx"

    with pd.ExcelWriter(target) as writer:
        for csv_file in csv_files:
            file = csv_file.split("/")[-1].split("\\")[-1]
            file_name = file.split(".")[0]
            df = pd.read_csv(csv_file, index_col=0)
            # df.index.name = "index"
            df.to_excel(writer, sheet_name=file_name, index=False)


if __name__ == "__main__":
    # files = [
    #     "report\\데이터 업데이트 주기.csv",
    #     "report\\데이터 제공 형태.csv",
    #     "report\\등록 데이터 건 수.csv",
    #     "report\\서비스 분류.csv",
    #     "report\\오픈포맷 현황.csv",
    # ]
    # integrate_csv_to_excel(files)
    
    from textwrap import dedent
    COLUMN_SELECT = dedent("""
        type as 제공 형태
        title as 타이틀
        description as 설명
        확장자 or 데이터포맷 as 확장자/데이터포맷
        등록일
        수정일
        제공기관
        업데이트 주기
        조회수
        누적 다운로드(바로가기) * 주기성 데이터 포함 or 다운로드(바로가기) or 활용신청 or 바로가기 횟수 as 다운로드/활용신청
        키워드
        제공형태
        service_url as 서비스 URL
        """)
    ret = column_header_n_select(COLUMN_SELECT)
    for k, v in zip(*ret):
        print(k,":", v)
