# 07: 운전면허 소지자 by 연령 (시도) and 고령운전자 운전면허 자진반납 (시도)

Retrieval date for all files: **2026-09-24** (no login, no API key, public pages / file downloads only). Raw files kept unmodified.
**Geography: 시도 only.** A nationwide 시군구 × 연령 table of licence holders, and any nationwide 시군구-level 자진반납 table, is not published
(searched data.go.kr, KOSIS, TAAS, KOROAD sites; only Seoul and Busan publish 시군구 × age: see §6).
시도 columns (instead of sgg_*): `sido_cd` = 2-digit code valid at the reference date (11,26,27,28,**29 광주**,30,31,36,41,43,44,**46 전남**,47,48,50,51 강원,52 전북),
`sido_nm`, `sido_cd_2026` / `sido_nm_2026` (29 and 46 → **12 전남광주통합특별시**; data are pre-2026-07 so 광주/전남 are kept separate), `map_note`.
경찰청 regions are 시도경찰청 관할: **경기남부 + 경기북부 are summed into 41 경기도** in the wide files (kept separately as `police_agency` in the long files).

---

## 1. TAAS 「시도경찰청별 연령별 성별 운전면허소지자수」 (MAIN, licence holders; source 경찰청)
- **데이터명**: TAAS > 통계분석 > 교통여건 > 사회경제지표 > 「시도경찰청별 연령별 성별 운전면허소지자수」 (pattern 「지방청별 연령별 성별 운전면허소지자수」, patternId 6863, subjectId 383 '기초자료(시도별 연령별 성별 운전면허소지자수)'); 조회범위 2014~2025.
- **제공기관**: 경찰청 (출처 표기) via 한국도로교통공단 교통사고분석시스템(TAAS). **Page**: https://taas.koroad.or.kr/sta/acs/exs/typical.do?menuId=WEB_KMP_OVT_UAS_TSA&patternId=6863
- **How retrieved**: same public viewer as 06 §1: `POST https://taas.koroad.or.kr/OBIP25/analysis/TypicalAnalysis.jsp` (`uid=taas_viewer&pid=6863&vCondition=D2582=2025~2025;`), then
  `POST https://taas.koroad.or.kr/OBIP25/servlet/OctagonProxyServlet` (`info=10001, subjectId=383, trid=0101, cubeinfo=, odfname=, params=…`) with
  `params` = `:row_list="2716",:col_list="2582:2601:2585",:mea_list="1230",:condition="",:pcondition="",:incondition="",:filter="",:agg_function="SUM",:orgdata="",:decimalpoint="",:aggDecimalpoint="",:enumerate="",:vcondition="D2582@|@P08 S01 T111 #OTE![2025]!# #OTE![2025]!#;|;",:mode="A",:chartdatatype="ALL_NOAGG",:pattern_id="6863",:agg_info="D2716;@T;@전체;|D2582;@F;@합계;|D2601;@T;@전국;|D2585;@T;@계;|",:meapos="C",:meaonlyagg="F",:agg_form="L",:agg_position="F",:pagenum="1",:pattern_name="지방청별 연령별 성별 운전면허소지자수",:subject_name="176_기초자료(시도별 연령별 성별 운전면허소지자수)",:SetSchedule="NONE",:subject_id="383",:layout="0"`
  (page default is identical except `:condition="D2601@|@P02 S01 #OTE![전국]!#;|;"`, i.e. 지방청 = 전국 only; removed to get all 18 청 = selecting all 지방청 in 조건설정). 2024: `[2024]`.
- **기준일**: 2025-12-31 and 2024-12-31 (연말 기준 운전면허 소지자, persons). 공표일 not stated on TAAS (경찰청's 2025 연말 면허 file on data.go.kr, §3, was registered 2026-05-19).
- **Raw**: `07_driver_license/taas_6863_license_holders_by_age_sido/TAAS_p6863_지방청별_연령별_성별_운전면허소지자수_{2025,2024}_p01.xml`
- **이용조건**: TAAS 이용약관: 활용 시 출처(경찰청 / 도로교통공단 TAAS) 및 자료링크 명시.
- **Tidy**: `tidy/driver_license_by_age_2025.csv`: **17 rows** × 26 cols; `tidy/driver_license_by_age_2025_long.csv`, **3,564 rows** (18 police agencies × 3 sex × 66 ages);
  `tidy/driver_license_by_age_2024.csv`: **17 rows**; `tidy/driver_license_by_age_2024_long.csv`, **3,564 rows**.
- **Columns** (persons): `ref_date`, `lic_total, lic_male, lic_female`, `lic_16_19, lic_20_29, lic_30_39, lic_40_49, lic_50_59, lic_60_64, lic_65_69, lic_70_74, lic_75_79, lic_80p`,
  `lic_65p, lic_70p, lic_75p, lic_65p_male, lic_65p_female`, `share_65p` (= lic_65p/lic_total), `share_75p`. Long: `police_agency`, `sex` (계/남/여), `age_src` (16…80, 81이상), `age_band`, `license_holders`.
- **Verification (all passed)**: Σ18 청 = 전국 for every age × sex; Σ ages = 합계; 남+여 = 계. **2025 전국 34,936,855** (65+ 5,632,818 = 16.1%); **2024 전국 34,707,289** (65+ 5,166,386 = 14.9%).
  2024 equals KOSIS (§2) exactly: per 지방청 (18/18, diff 0) and per single-year age (diff 0; '81이상' 292,667 = KOSIS Σ81세+).
- **Caveats**: the source's '합계' column (전국 + 18 청 = double count) is dropped. Top code 81이상 (in `lic_80p`). Region = 시도경찰청 managing the licence record (presumably the holder's 주소지 관할; not stated in the source). 세종청 separate since 2019, 경기북부 since 2016.

## 2. KOSIS 경찰청 「운전면허소지자현황(지역별)」 DT_13201_A005 and 「운전면허소지자현황(연령대별)」 DT_13201_A002 (2019~2024): verification
- https://kosis.kr/statHtml/statHtml.do?orgId=132&tblId=DT_13201_A005 and …&tblId=DT_13201_A002 ; downloaded through the statHtml viewer's own public 다운로드 flow (statHtmlContent.do → html.do → downGrid.do → downNormal.do; no login), all periods 2019~2024, 코드포함.
- Raw: `07_driver_license/kosis/KOSIS_경찰청_DT_13201_A005_운전면허소지자현황(지역별)_2019-2024.{xlsx,csv}`, `…DT_13201_A002_운전면허소지자현황(연령대별)_2019-2024.{xlsx,csv}`. KOSIS 이용약관 (출처: 경찰청, 「운전면허소지자현황」, KOSIS).
- A005 = 18 시도경찰청 × 면허종별(총계/1종/2종), no age; A002 = 전국 × single-year age × 면허종별, no region; latest 2024 (2025 not yet on KOSIS). Not tidied (used for checks).

## 3. 경찰청_운전면허소지자 지역별 종별 현황 (2025-12-31): supplementary
- https://www.data.go.kr/data/15048420/fileData.do (등록 2026-05-19); URL: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003642912&fileDetailSn=1
- Raw: `07_driver_license/datagokr/경찰청_운전면허소지자현황(성별 지역별 종별)현황_20251231.csv` (CP949; 18 청 × 성별 × 9 면허종별). 이용허락범위 제한 없음.
- Counts **licences by type** (one person may hold several): Σ = 45,284,543 licences vs 34,936,855 holders → not used in tidy files. No age.

## 4. 경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황 (2025): MAIN for returns
- https://www.data.go.kr/data/15114381/fileData.do (등록 2026-04-10; 차기 2027-04-10); URL: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003624118&fileDetailSn=1
- Raw: `07_driver_license/datagokr/경찰청_운전면허 자진반납 연령별 시도청별 취소처분 현황_20251231.csv` (UTF-8 BOM; 18 청 × 65세 미만, 65…89세, 90세 이상). 이용허락범위 제한 없음.
- **Tidy**: `tidy/license_return_elderly_2025.csv`: **17 rows** × 22 cols; `tidy/license_return_elderly_2025_long.csv`, **486 rows** (18 청 × 27 age classes).
- **Columns** (건 = 자진반납에 따른 면허 취소처분, year 2025): `ret_total_all_ages, ret_lt65, ret_65p, ret_65_69, ret_70_74, ret_75_79, ret_80_84, ret_85_89, ret_90p, ret_70p, ret_75p`, `share_65p_of_returns`,
  `lic_65p_2025, lic_70p_2025` (from §1) and **`ret_65p_per_1000_lic65p`, `ret_70p_per_1000_lic70p`** (returns per 1,000 year-end holders of the same age; denominator is after returns → slight overstatement).
- **Totals 2025**: all ages 143,373; 65+ 141,286; <65 2,087; 70+ 126,879 (row sums = file cells, diff 0; no published national total to compare).
- Caveat: age is age at return; many municipal incentives start at 70 (e.g. 서울: 65~69세 only 1,002 vs 70~74세 12,443).

## 5. 경찰청_시도 경찰청별 고령운전자 자진반납 현황 (2015~2024)
- https://www.data.go.kr/data/15065567/fileData.do (수정 2025-11-10; 차기 2026-11-10); URL: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003518319&fileDetailSn=1
- Raw: `07_driver_license/datagokr/경찰청_시도 경찰청별 고령운전자 자진반납 현황_2015~2024.csv` (CP949; 18 청 × year × {65세 이상, 전체}). 이용허락범위 제한 없음.
- **Tidy**: `tidy/license_return_elderly_2024.csv`: **17 rows** (`ret_total_all_ages, ret_lt65, ret_65p, share_65p_of_returns, lic_65p_2024, ret_65p_per_1000_lic65p`); `tidy/license_return_elderly_2015_2024_long.csv`, **360 rows** (18 청 × 10 years × 2).
- National 65+/전체: 2019 73,293/74,380, 2020 76,002/76,784, 2021 83,997/84,526, 2022 112,942/114,045, 2023 112,896/113,980, **2024 114,436/115,795** (file labelled 2024-12-31, full-year magnitude vs 2023; the portal description's "2024년 6월 기준 256,654건" does not match the file).
- Caveats: 세종 0 in 2015~2018 (세종청 opened 2019-06-25), 경기북부 0 in 2015 (opened 2016-03-25).

## 6. Partial 시군구 × 연령 licence holders (Seoul 2025, Busan 2023~2024): supplementary
- 경찰청_운전면허소지자현황_서울_시군구_연령별_대장별 (2025-12-31): https://www.data.go.kr/data/15127762/fileData.do, URL …atchFileId=FILE_000000003604910&fileDetailSn=1
  → `07_driver_license/datagokr_partial_sgg/경찰청_운전면허소지자(서울,시군구,연령별,대장별)현황_20251231.csv` (UTF-8; 25 구 × age × 1종소계/2종소계/2종 원자).
- 경찰청 부산광역시경찰청_구군별 연령별 운전면허 소지 현황 (2023, 2024): https://www.data.go.kr/data/15164326/fileData.do (등록 2026-09-10), URL …atchFileId=FILE_000000007664622&fileDetailSn=1
  → `07_driver_license/datagokr_partial_sgg/부산경찰청_ 23년 24년구군별 연령별 운정면허 소지 현황.csv` (CP949; 16 구군 × 10-year bands).
- **Tidy**: `tidy/driver_license_by_age_sgg_partial_long.csv`: **481 rows**, 41 units (standard sgg_* columns, `ref_date`, `age_band`, `holders`, `source`).
  Seoul holders = 1종소계 + 2종소계 (Σ 6,340,547 vs TAAS 서울 6,344,358; one row with age '3' dropped); Seoul bands 16-19,20-29,…,60-64,65-69,70-79,80+; **Busan bands are 10-year (60-69 → no 65+ split)**; Busan 2024 Σ 2,031,143 vs TAAS 2,031,713.

## Not obtainable / alternatives
- Nationwide **시군구 × 연령 운전면허 소지자**: not published (경찰청 holds it by 주소지; only Seoul/Busan release). Options: 정보공개청구 to 경찰청 교통기획과 or 도로교통공단; or use `tidy/driver_license_by_age_2025.csv` 시도 shares × 시군구 65+ population as a proxy.
- **시군구 자진반납**: only scattered municipal tables on KOSIS (e.g. 경기 이천 DT_631003_2024A077, 구리/광주/고양/양주/안산 노인등록통계 2023, 오산 2022; 부산 「면허증 보유율 대비 반납률」 DT_202022_F09 2020~2024): not nationally consistent; 지자체별 반납 지원사업 실적 are in press releases only.
