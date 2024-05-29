{
    "ORG": ["기상청 항공기상청", "서울에너지공사", "한국문화관광연구원"],
    "DTYPE": ["FILE", "API"],
    "SELECT": """
        service_id as id
        type as 제공 형태
        title as 타이틀
        description as 설명
        제공기관
        조회수
        키워드
        service_url as 서비스 URL
        """,
    "MERGE": True,
    "MERGE_NAME": "example",
    "RUN": True,
}
