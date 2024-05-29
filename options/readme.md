# options

파이썬 파일 그대로 딕셔너리 하나 작성하여 크롤링 옵션으로 사용 함.

## 항목 설명

|Key|Type|Require|Default|Value|Example|
|-|-|-|-|-|-|
|`ORG`|`list[str]`|1|-|크롤링 할 대상 **기관명**.<br>공공데이터 포털의 "**기관별 데이터 검색**"의 이름과 정확히 일치해야 함.|`["통일부"]`|
|`DTYPE`|`list[str]`|1|-|수집 할 데이터 카테고리.<br>도메인: `FILE`, `API`, `LINKED`|`["FILE", "API"]`|
|`SELECT`|`str`|1|-|**기본데이터정보**와 **데이터상세정보 테이블**의 데이터를 **csv 헤더**로 **매핑**하는 쿼리. 각 매핑은 개행으로 구분됨.|`"""title as 타이틀\n확장자 or 데이터포맷 as 확장자/데이터포맷\n누적 다운로드(바로가기) * 주기성 데이터 포함 or 다운로드(바로가기) or 활용신청 or 바로가기 횟수 as 다운로드/활용신청"""`|
|`MERGE`|`bool`|0|`False`|수집 할 기관명이 여러개일 경우, csv를 통합 한 파일을 추가생성 할 지 여부|`True`|
|`MERGE_NAME`|`str`|0|`None`|파일 MERGE 시 생성되는 파일명에 기록 될 문자열<br>지정안할 시 첫 번째 ORG이름이 할당됨|`통합파일`|
|`RUN`|`bool`|0|`False`|해당 옵션파일 실행 여부|`True`|


## SELECT

"데이터 상세"페이지의 데이터 정보에 있는 테이블 속성 명을 그대로 입력하면 해당 내용을 수집함. <br>ex) `파일데이터명`, `분류체계`, `누적 다운로드(바로가기) * 주기성 데이터 포함`

> 가능한 기능 문자 : `or`, `as`

- `as` : `A as B` 형태로 사용하며, 수집한 A의 값을 csv파일에서 B컬럼에 저장함.
- `or` : `A or B as C` 형태로 사용하며, AB중 먼저 있는 항목이 수집되고 C컬럼에 저장됨. <br>(`or`사용 시, `as`를 필수로 사용해야 함.)
    - *A or B or C == collase(A, B, C)*


#### *SELECT 기본항목

항목에서 상세페이지의 테이블 외 기본 수집 데이터
```
# 참고: utils.crawler.get_detail_page
type         서비스 타입 ("filedata" | "openapi" | "linked")
title        서비스 명
description  서비스 설명
service_url  서비스 상세페이지의 URL
service_id   서비스 id (URL에서 숫자부분)
formats      서비스 지원 포맷
```


## 파일 예시

```python
{
    "ORG": ["한국동서발전(주)", "한국남동발전㈜", "한국남부발전(주)", "한국서부발전(주)", "한국중부발전(주)"],
    "DTYPE": ["FILE"],
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
        설명 as 설명_하단
        기타 유의사항
        service_url as 서비스 URL
        """,
    "MERGE": False,
    "RUN": True,
}
```