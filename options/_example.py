{
    "ORG": ["기관명정확히"],
    "DTYPE": ["FILE", "API", "LINKED"],
    "SELECT": """
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
        """,
    "MERGE": False,  # ORG가 2개 이상 일 경우 하나의 csv파일로 합칠지 여부
    "RUN": False,  # True 시에만 크롤링 동작
}
