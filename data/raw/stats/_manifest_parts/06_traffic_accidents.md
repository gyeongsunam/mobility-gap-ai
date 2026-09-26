# 06: 교통사고 by 가해운전자(1당) 연령층, 시군구 (도로교통공단 TAAS / 경찰청 교통사고 DB)

Retrieval date for all files: **2026-09-24** (no login, no API key, public pages / file downloads only).
Processing: python/pandas; 시군구 names mapped with `_ref/sggmap.py` (0 unmatched). Raw files kept unmodified.
**Latest year = 2025** (released: TAAS max year 2025; data.go.kr 2025 files registered 2026-08-03/04). 2024 was also built for continuity.

---

## 1. TAAS 「시도 시군구별, 가해운전자 연령대별 교통사고」 (MAIN: the only public 시군구 × 가해운전자 연령 source)

- **데이터명**: 교통사고분석시스템(TAAS) > 통계분석 > 교통사고 상세통계 > 경찰DB교통사고(국가공식) > 사고일반 통계 > 시도 시군구별 > 「시도 시군구별, 가해운전자 연령대별 교통사고」 (patternId 7125, subjectId 131 '분석통계 기본계획(경찰청 사고일반)')
- **제공기관**: 한국도로교통공단 (경찰청 교통사고 DB 기반, 국가공식 교통사고통계). **출처 플랫폼**: taas.koroad.or.kr
- **Page URL**: https://taas.koroad.or.kr/sta/acs/exs/typical.do?menuId=WEB_KMP_OVT_UAS_PDS&patternId=7125
  (public statistics viewer, anonymous 'taas_viewer' session; no login).
- **How retrieved** (curl replicating exactly the request the page's viewer sends on "조회"):
  1. `POST https://taas.koroad.or.kr/OBIP25/analysis/TypicalAnalysis.jsp` with `uid=taas_viewer&pid=7125&vCondition=D1443=202501~202512;` (opens the viewer session, as the page does).
  2. `POST https://taas.koroad.or.kr/OBIP25/servlet/OctagonProxyServlet` with form fields `info=10001, subjectId=131, trid=0101, cubeinfo=, odfname=, params=<below>`; response = XML (grid as HTML table in CDATA), 200 row-lines/page → pages 1~8 per year.
  `params` = `:row_list="906:907",:col_list="888:2736",:mea_list="334:335:701:336:702:337",:condition="",:pcondition="",:incondition="",:filter="",:agg_function="SUM",:orgdata="",:decimalpoint="",:aggDecimalpoint="",:enumerate="",:vcondition="D1443@|@P08 S01 T111 #OTE![202501]!# #OTE![202512]!#;|;",:mode="A",:chartdatatype="ALL_NOAGG",:pattern_id="7125",:agg_info="D906;@T;@합계;|D907;@T;@합계;|D888;@T;@합계;|D2736;@T;@합계;|",:meapos="R",:meaonlyagg="F",:agg_form="S",:agg_position="",:pagenum="1..8",:pattern_name="시도 시군구별‧가해운전자 연령대별 교통사고",:subject_name="251_분석통계 기본계획(경찰청 사고일반) ",:SetSchedule="NONE",:subject_id="131",:layout="0"` (2024: `202401`/`202412`).
  This equals the page default with the viewer's '시군구' and '중상자수/경상자수/부상신고자수' check-boxes ticked (default row_list `906:*907`, mea_list `334:335:701:*336:*702:*337`).
  Note: TAAS's own "내보내기 > 엑셀(xlsx)" posts the client-rendered grid to `/OBIP25/MSConvert.jsp` (no server-side file link), so the server's XML data responses were saved as the original files.
- **기준연도**: 2025 (1~12월 발생) and 2024. Query timestamp is inside each XML footer ([조회 시각] 2026/09/24 ~23:54).
- **Raw files**: `06_traffic_accidents/taas_7125_sgg_x_driver_age/TAAS_p7125_시도시군구별_가해운전자연령대별_교통사고_{2025,2024}_p01..p08.xml` (16 files, ~0.5 MB each).
- **이용조건**: TAAS 이용약관 (2024-07-31 시행): "TAAS에서 제공된 자료를 활용 시 출처 및 자료링크를 명시". Cite: 한국도로교통공단 교통사고분석시스템(TAAS), https://taas.koroad.or.kr, 2026-09-24 조회. (All-age 시군구 totals are identical to data.go.kr §2, 이용허락범위 제한 없음.)

### Tidy outputs
- `tidy/accidents_by_driver_age_2025.csv`: **229 rows** × 32 cols; `tidy/accidents_by_driver_age_2025_long.csv`, **12,366 rows** (229 × 9 age groups × 6 measures).
- `tidy/accidents_by_driver_age_2024.csv`: **229 rows**; `tidy/accidents_by_driver_age_2024_long.csv`, **12,366 rows**.
- Key columns (wide): standard `sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note`, `year`, `sido_src, sgg_src` (TAAS labels);
  `acc_total` (사고건수, 건), `death_total` (사망자수, 명; 30일 이내 사망), `injury_total` (부상자수, 명 = `serious_total` 중상 + `minor_total` 경상 + `reported_total` 부상신고);
  same six measures for 가해운전자(1당) **65세 이상**: `acc_65p, death_65p, injury_65p, serious_65p, minor_65p, reported_65p`;
  accidents by other 1당 age groups `acc_le19, acc_20_29, acc_30_39, acc_40_49, acc_50_59, acc_60_64, acc_unknown` (불명); `acc_known_age`;
  `share_65p` = acc_65p/acc_total, `share_65p_known_age` = acc_65p/acc_known_age, `death_share_65p`, `injury_share_65p` (ratios 0~1, 4 dp).
  Long: `driver_age_group` (합계, 19세 이하, 20-29세, 30-39세, 40-49세, 50-59세, 60-64세, 65세 이상, 불명), `measure` (accidents/deaths/injuries/injuries_serious/injuries_minor/injuries_reported), `measure_src`, `unit` (건/명), `value`.

### Verification (all passed, both years)
- Σ시군구 = each 시도 합계 row = 전국 합계 for every measure × age group (세종 has no 시도 합계 row: single unit); Σ age groups = 합계; 부상 = 중상+경상+부상신고 for every row.
- **2025 전국**: 사고 193,889 / 사망 2,549 / 부상 271,751; **65세 이상 가해**: 45,873 / 843 / 63,640 (23.7% of accidents).
- **2024 전국**: 사고 196,349 / 사망 2,521 / 부상 278,482; **65세 이상 가해**: 42,369 / 761 / 59,776: equal to TAAS '주요 교통사고통계 > 부문별 > 노인운전자 교통사고' (2024 42,369/761/59,776; 2025 45,873/843/63,640).
- 2025 all-age 시군구 values = data.go.kr §2 file for all 229 units (max abs diff 0 for 사고/사망/중상/경상/부상신고); 2025 national 65+ = data.go.kr §3 (65-70세 + 71세이상).

### Caveats
- **Geography = 사고 발생지 시군구** (location of the accident), not the driver's residence; 1당 = primary at-fault party. "운전자" covers all 차 incl. 화물, 이륜, 자전거, PM, 농기계 (2025 national 65+ 1당: 승용 67.9%, 화물 15.8%, 승합 6.5%, 이륜 3.5%, 자전거 2.9%: §4).
- Only accidents with casualties (인피사고) investigated by police; 사망 = within 30 days.
- TAAS uses **229 units** (자치구, 시군 + 제주시/서귀포시 + 세종); **no 일반구** → 13 rows are parent 시 (map_note `parent_si…`: 수원, 성남, 안양, 안산, 고양, 용인, 청주, 천안, 전주, 포항, 창원 and 부천(일반구 since 2024-01-01), 화성(since 2026-02-01)). No 256-unit split is possible from this source.
- Codes valid at 2024-12-31/2025-12-31 in `sgg_cd_ref`; harmonised `sgg_cd`: 광주 29xxx/전남 46xxx → 12xxx (27 rows recoded), 강원 51/전북 52 already; **인천 중구 28110, 동구 28140, 서구 28260 have no 1:1 successor after the 2026-07-01 split** (sgg_cd = old code, map_note split_…). 군위군 is under 대구 (27720) in both years. TAAS label '진구' = 부산진구 (fixed before mapping).
- Age bands: this TAAS dimension ('가해운전자(1당) 연령대', added 2025-09-05) uses 19세 이하/20-29…/60-64/65세 이상/불명; data.go.kr national file uses 20세이하/21-30/…/61-64/65-70/71세이상: the 65+ total is identical. `acc_unknown` (불명 = 1당 age not recorded, e.g. unidentified drivers) is small (2025: 2,477 nationwide); use `share_65p_known_age` if preferred.

---

## 2. 한국도로교통공단_시도 시군구별 교통사고 통계 (2025): all-age totals, cross-check
- 제공: 한국도로교통공단 (AI데이터전략처) / 공공데이터포털 https://www.data.go.kr/data/15070297/fileData.do (등록 2026-08-04; 차기 2027-08-03)
- URL: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003692669&fileDetailSn=1
- Raw: `06_traffic_accidents/datagokr/한국도로교통공단_시도 시군구별 교통사고(2025).csv` (CP949, 229 rows: 시도, 시군구, 사고건수, 사망자수, 중상자수, 경상자수, 부상신고자수). 이용허락범위 제한 없음.
- Used only for verification (identical to §1 합계 column); not separately tidied.

## 3. 한국도로교통공단_가해운전자 연령층별 교통사고 통계 (2025, 전국)
- https://www.data.go.kr/data/15070183/fileData.do (등록 2026-08-03, 수정 2026-08-10); URL: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003702470&fileDetailSn=1
- Raw: `06_traffic_accidents/datagokr/한국도로교통공단_가해운전자 연령층별 교통사고(2025).csv` (CP949, 9 rows, national only). 이용허락범위 제한 없음. Verification only.

## 4. 한국도로교통공단_가해운전자 당사자종별 연령대별 교통사고 통계 (2025, 전국)
- https://www.data.go.kr/data/15150146/fileData.do (등록 2026-08-10); URL: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003702452&fileDetailSn=1
- Raw: `06_traffic_accidents/datagokr/한국도로교통공단_가해운전자 차종별 연령층별 교통사고(2025).csv` (CP949, 91 rows: 차종 × 연령층, national). Context only (vehicle-type mix of 65+ accidents).

## Not used / alternatives checked
- data.go.kr 15094163 「부문별 노인운전자 교통사고 통계」 is a 2018 one-off; 15070295/15070337 (시군구 × 월/일자) have no age. TAAS pattern 7265 「시도 시군구별, 월별 (노인운전자) 교통사고」 gives the same 65+ totals by 시군구 × 월 (not needed).
