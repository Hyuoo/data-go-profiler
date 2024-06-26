# data-go-profiler

각 기관의 공공데이터 현황을 파악하기 위한 레포지토리.
공공데이터 포털의 데이터 현황을 크롤링하여 csv파일로 저장합니다.

## Quick start

```
git clone https://github.com/Hyuoo/data-go-profiler.git
cd data-go-profiler
pip install -r requirements.txt
python datagov.py
```


### 필요 기능

- 공공데이터 포털의 기관 별 데이터 현황 검색 (파일, API, 연계 등)
- 각 공공데이터 상세 내용 크롤링, csv로 저장
- 추출 한 기관 별 파일 병합
- 각 공공데이터 다운로드 파일 다운로드
    - 간단한 시각화를 통한 분석레포트
- 간단한 시각화 이미지 생성


### 간단한 분석 목표

- 제공 데이터 타입 비율 비교 (pie chart)
- 특정 데이터의 컬럼
- 데이터 품질 분석


## 사용방법

`python datagov.py` 커맨드를 통해서 실행.

입력 인자가 없을 경우 `options` 디렉토리 내의 각 옵션파일을 통해서 실행 됨.

##### *옵션에 대한 설명은 [options/readme.md](./options/readme.md)파일을 참고


실행 시 다음과 같은 파일이 생성됨.
- `ORG`당 1개의 파일 세트
    <br>date는 `%Y%m%d`형식
    - `raw_data/{ORG}_urls_{date}.txt`
    - `raw_data/{ORG}_공공데이터_{date}.json`
    - `data/{ORG}_공공데이터_{date}.csv`
    - `logs/{ORG}_공공데이터_{date}.log`
    
## 디렉토리 설명

|디렉토리|설명|
|-|-|
|data|공공데이터 현황 csv파일 저장|
|~filedata~|~각 서비스별 첨부파일이 저장~(미구현)|
|logs|실행 로그 파일|
|options|실행옵션 파일|
|~report~|~분석 결과~(미구현)|
|raw_data|수집 중 발생한 urls.txt 및 json파일|
|src|크롤링 코드|


## 개선사항

- (2024.05.28)
    - 생성되는 파일명에 DTYPE항목 명시
    - 로그에 상세페이지 인덱스 추가
- (2024.05.29)
    - 불필요한 함수 제거, 주석 보충, 자잘한 기능 변경
    - 여러 기관 검색 시 index가 초기화되지 않는 문제 수정

### TODO

- [ ] 상세페이지에서 파일 다운로드 받기
- [ ] 간단한 유형 별 분석시각화생성
    > - [ ] 기관 별 제공데이터 유형 비율 (FILE,API 등) (--파이차트)
    > - [ ] 파일데이터 중 파일형식 분포 (Open포맷3단계) (--누적막대차트)
    > - [ ] 조회수 및 다운로드/활용신청 순 목록 그래프 (--막대차트)
    > - [ ] 조회수-다운로드/활용신청 분포 그래프 (--scatter chart)
- [ ] 옵션에서 파일 덮어쓰기 항목 추가
- [x] 생성되는 파일명에 DTYPE항목 명시
- [ ] SELECT 쿼리에서 이미 생성한 두 컬럼을 조합하여 파생컬럼을 생성하기
    - ex) 활용도 = 다운로드수/조회수*100
- [ ] MERGE 실행 시 index 초기화하기
- [ ] MERGE 실행 시 org 컬럼 앞으로 위치하게 하기
- [ ] cli argument에 ORG를 직접입력하여 수집 실행
