# 시군구 통계 원자료 매니페스트(수집일 2026-09-24~25)

각 절은 자료별 제공기관, URL, 기준일, 이용조건, 정제 방법, 검증 결과를 담는다. 정제본은 tidy/*.csv.

# 01: 자동차 등록현황 (vehicle registrations), 시군구 × 차종 × 용도, 연료별

Retrieval date for all files: **2026-09-24** (no login, no API key; public download endpoints only).
Processing: python/openpyxl; names mapped with `_ref/sggmap.py` (0 unmatched). Raw files are kept unmodified.

---

## 1. 자동차등록현황보고: 2026년 08월 자동차 등록자료 통계 (MAIN)

- **데이터명**: 자동차등록현황보고 (Total Registered Motor Vehicles), 국가승인통계 제116015호. 월별 Excel 「2026년 08월 자동차 등록자료 통계」
- **제공기관**: 국토교통부 모빌리티자동차국 자동차운영보험과 (시도 → 국토교통부; 자동차관리정보시스템 입력자료 집계)
- **출처 플랫폼**: 국토교통 통계누리 https://stat.molit.go.kr/portal/cate/statMetaView.do?hRsId=58 → '통계 관련파일' → '2026년 08월 자동차 등록자료 통계.xlsx' [다운로드]
- **Download URL** (GET form submitted by the page's `downFile()` JS; works without login):
  `https://stat.molit.go.kr/portal/common/downLoadFile.do?hRsId=58&hFormId=&hSelectId=&sStyleNum=&sStart=&sEnd=&hPoint=&hAppr=&oFileName=2026%eb%85%84+08%ec%9b%94+%ec%9e%90%eb%8f%99%ec%b0%a8+%eb%93%b1%eb%a1%9d%ec%9e%90%eb%a3%8c+%ed%86%b5%ea%b3%84.xlsx&rFileName=2026%eb%85%84+08%ec%9b%94+%ec%9e%90%eb%8f%99%ec%b0%a8+%eb%93%b1%eb%a1%9d%ec%9e%90%eb%a3%8c+%ed%86%b5%ea%b3%84.xlsx&midpath=%2fstat_file%2f`
  (oFileName = display name, rFileName = stored name; for July the stored name is '2026년 07월 자동차 등록자료 통계1.xlsx').
- **기준일**: 2026-08-31 (조회년월 2026.08; 작성대상월 말일). 공표: 익월말 (metadata); latest month on the site on 2026-09-24; workbook's internal modified date 2026-09-14.
- **Raw files** (BASE-relative):
  - `01_vehicle_registration/2026년 08월 자동차 등록자료 통계.xlsx` (447,920 B; sha256 fce1acd8b06d2ceab256c17a856f3be73733057f93cdb1ed3ec980661d8cc1bf): used.
  - `01_vehicle_registration/2026년 07월 자동차 등록자료 통계.xlsx` (428,552 B): kept for reference only (checked 2026-07-01 handling; not tidied).
- **Workbook contents (27 sheets, all inspected)**: 01 시도×차종×용도 / **02 시군구×차종×용도 (관용, 자가용, 영업용, 계)** / 03 수입차 시군구 / 04 성별, 연령 (시도) / 05~08 차종 세부유형 (시도, 전체, 관용, 자가용, 영업용) / 09 유형 / **10 연료×차종×용도(비사업용, 사업용): 시도 only** / 11 최대적재량 / 12 배기량(승용; 전기차, 저속전기차) / 13 차종×사업용, 비사업용 (시도) / 14~15 차령 / 16 승차정원 / 17 규모 / 18~19 추세 / 20~27 신규, 변경, 이전, 말소. **No sheet gives fuel by 시군구.** (The 2025년 12월 annual-basis file has the identical 27-sheet layout, checked.)
- **이용조건**: 국토교통 통계누리 저작권보호정책: 공공누리 제1유형(출처표시), 상업적 이용 포함 자유이용. Cite: 국토교통부, 「자동차등록현황보고」 2026년 8월, 국토교통 통계누리(stat.molit.go.kr), 2026-09-24 다운로드.

### Tidy outputs
- `tidy/vehicle_registration_202608.csv`: **263 rows** (256 analysis units + 7 residual rows), 39 cols.
- `tidy/vehicle_registration_202608_long.csv`: **3,156 rows** (263 × 4 차종 × 3 용도; atomic cells only, no 계 rows).

Key columns (unit: 대 = vehicles):
- standard `sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note`, `ref_date`=2026-08-31, `row_type` (`unit` / `residual`), `src_sido`, `src_sgg` (source labels).
- `{total,car,van,truck,special}_{all,gov,private,commercial,nonbusiness,business}`:
  total=총계, car=승용, van=승합(van+bus), truck=화물, special=특수; all=published 계, gov=관용, private=자가용, commercial=영업용;
  **derived** nonbusiness=비사업용=관용+자가용, business=사업용=영업용.
- long: `vehicle_type` (승용/승합/화물/특수), `use_type` (관용/자가용/영업용), `use_group` (비사업용/사업용), `value`.

### Caveats
- Source has **no codes**; mapped by (시도 label, 시군구 name) with ref_date 2026-08-31 → 0 unmatched; the 256 `unit` codes equal exactly the 256 `is_unit` codes of `_ref/sgg_master_2026.csv`.
- **2026-07-01 reforms are already applied in the July and August 2026 files** (June 2026 file still had 광주/전남 separately and 인천 중구/동구/서구): 시도 label '전남광주' (광주 5 구 + 전남 22 시군 → 12xxx codes), 인천 제물포구(28125)/영종구(28155)/서해구(28275)/검단구(28290).
- **Residual legacy rows** (source lists vehicles still recorded under old/parent codes; they are NOT subtotals): 인천 중구 4,874 / 동구 2,661 / 서구 8,016 (→ codes 28110/28140/28260, no 1:1 successor; shrinking vs July 5,046/2,778/13,811 as records are re-coded), 경기 부천시 287 (41190), 경기 화성시 3,928 (41590), 충북 청원군 19 (43710, abolished 2014), 경북 군위군 36 (47720; geographically 대구 군위군 27720). Kept as `row_type='residual'` with their legacy code in `sgg_cd` (so `sgg_cd` stays unique); total 19,821 (0.074% of national; 인천: 15,551 = 0.88% of 인천). **For unit analysis filter `row_type=='unit'`.**
- **일반구**: the source reports 39 일반구 rows (incl. 화성시 만세/효행/병점/동탄구 since 2026-02-01 and 부천 3 구) and gives no parent-시 subtotals, so nothing was dropped.
- **영업용 is concentrated at company registration addresses** (rental/lease fleets): e.g. 제주시 294,608 (47% of its vehicles), 신안군 122,130 (81%), 해남군 114,639 (72%), 인천 계양구 85,746, 옹진군 71,234, 창원 의창구, 부산 수영구/남구/연제구, 함안군. Registration place ≠ place of use → use `*_private` / `*_nonbusiness` for household car ownership.
- **Verification (all passed)**: every row 관용+자가용+영업용=계 and Σ차종=총계; Σ시군구 (unit+residual) = each of the 16 시도 '계' rows (all 20 columns) = sheet 01 시도 values; national Σ = 합계 **26,687,284** (관용 103,182 / 자가용 24,491,916 / 영업용 2,092,186); derived 비사업용/사업용 by 시도 × 차종 = sheet 13 for all 16 시도 + 총계.

---

## 2. 연료별 등록현황 (same workbook, sheet '10.연료별_등록현황'): 시도 level only

- Same source/URL/기준일/license as §1. Fuel is published only by **시도 × 연료 × 차종 × 용도(비사업용/사업용)**.
- **Tidy**: `tidy/vehicle_fuel_sido_202608.csv`: **16 rows** (2026 시도 codes; 12 = 전남광주통합특별시), 41 cols;
  `tidy/vehicle_fuel_sido_202608_long.csv`: **2,176 rows** (16 × 17 fuels × 4 차종 × 2 용도).
- Columns: `sido_cd, sido_nm, src_sido, map_note, ref_date, total_all`, per-fuel totals `gasoline`(휘발유) `diesel`(경유) `lpg`(엘피지) `kerosene`(등유) `electric`(전기) `alcohol` `solar`(태양열) `cng` `lng` `hybrid_gasoline_electric` `hybrid_diesel_electric` `hybrid_lpg_electric` `hybrid_cng_electric` `hybrid_lng_electric` `hydrogen`(수소) `hydrogen_electric`(수소전기) `other_fuel`(기타연료); `hybrid_total` (5 hybrid types), `hydrogen_total` (수소+수소전기), `electric_{car,van,truck,special}`, `electric_{nonbusiness,business}`, `hydrogen_total_{car,…}`, `hybrid_total_{car,…}`, `ev_share_pct`, `zev_share_pct` (%). Long: `fuel` (source label), `fuel_en`, `fuel_group`, `vehicle_type`, `use_group`, `value` (대).
- National 2026-08-31: 휘발유 12,314,449 / 경유 8,274,544 / LPG 1,824,451 / **전기 1,160,968 (4.35%)** / **하이브리드 계 2,885,164** / **수소 37,421 + 수소전기 11,799 = 49,220** / CNG 23,242 / 기타 155,221.
- The register has two hydrogen codes ('수소', '수소전기'); both kept, plus `hydrogen_total`.
- **Verification (all passed)**: per fuel 소계=Σ차종 and 계=비사업용+사업용; Σfuels = 총계 for every 시도×차종×용도; 총계 = sheet 02/01 totals by 시도 (사업용 = 영업용, 비사업용 = 관용+자가용); Σ시도 = 계 column = 26,687,284.

---

## 3. 한국교통안전공단 전기차 시군구별 등록대수 (finest official EV-by-시군구 alternative)

- **데이터명**: 한국교통안전공단_전국_전기차_차종별_용도별_차량_등록대수(운행차량기준)_20250407
- **제공기관**: 한국교통안전공단 (AI혁신처); source system 자동차검사관리시스템(VIMS), 운행차량 기준. **출처 플랫폼**: 공공데이터포털 https://www.data.go.kr/data/15142951/fileData.do
- **Download URL**: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003121052&fileDetailSn=1&insertDataPrcus=N
- **기준일**: 2025-04-07 (추출일; 1회성 데이터). Registered 2025-04-09, page modified 2026-09-03. **No newer national EV-by-시군구 file exists.**
- **Raw**: `01_vehicle_registration/한국교통안전공단_전국_전기차_차종별_용도별_차량_등록대수(운행차량기준)_20250407.csv` (CP949, 508 rows, 22,035 B, unmodified).
- **이용조건**: data.go.kr 이용허락범위 제한 없음.
- **Tidy**: `tidy/vehicle_fuel_ev_sgg_20250407.csv`: **253 rows** (252 units valid on 2025-04-07 + 1 residual '경기 부천시' 1 EV), 24 cols;
  `tidy/vehicle_fuel_ev_sgg_20250407_long.csv`: **2,024 rows** (4 차종 × 2 용도).
  Columns: standard 5 + `ref_date`, `row_type`, `src_sido`, `src_sgg`, `ev_total`, `ev_nonbusiness`, `ev_business`, `ev_{car,van,truck,special}`, `ev_{car,van,truck,special}_{nonbusiness,business}` (대).
- Caveats: **EV only** (연료 = 전기; no 수소/하이브리드); 용도 only 사업용/비사업용 (no 관용 split); VIMS "운행차량" basis differs slightly from the MOLIT register. Pre-2026 unit structure: 광주(29)/전남(46) recoded to 12xxx (`recoded` notes); 인천 중구/동구/서구 keep 28110/28140/28260 (split notes, no 1:1 successor); 화성시 = single unit 41590 (일반구 only from 2026-02-01; `parent_si` note). The source lists 성주군 twice ('경북 성주군' 1,345 + '경상북도 성주군' 27): same unit, summed into 47840 (noted in map_note).
- **Verification**: every row Σ차종 = 계; total **719,039** (no published total in the file). By 시도 it lies within −0.11% (대구) to +0.76% (인천, 경남) of MOLIT registered EVs on 2025-03-31 (national 716,310) and below 2025-04-30 (733,030), i.e. consistent with a 04-07 snapshot (MOLIT 2025-03/04 files downloaded to scratch only for this check).

---

## Not obtainable nationally: all fuels (and 수소) by 시군구
- MOLIT publishes fuel only by 시도 (monthly workbook sheet 10; interactive tables statView hRsId=58 '자동차등록대수현황 시도별/연도별' = KOSIS 116/DT_MLTM_5498 are 시도-level).
- data.go.kr national files checked: 국토교통부_자동차 등록 현황 (15024777; just links to 통계누리), 한국교통안전공단_수소전기차 등록 현황 (15127777; 시도 only, 2024-03), 한국전력공사_지역별 전기차 현황정보 (15039554; 시도 only), 한국환경공단_지역별 전기 자동차 등록 및 보조금 신청 현황 (15123034; subsidy counts 2022, not stock). No key-free OpenAPI (KOTSA 자동차종합정보 APIs need a personal key and are vehicle-level).
- **Patchwork alternative (not assembled)**: KOSIS 지자체 기본통계 '시군구별 자동차 연료종류별 등록' (연말 기준) exists for 13 시도: 부산 202/DT_1003N (~2024), 인천 204/DT_204002_J000006 (~2024), 광주 205/DT_20503_J001002_1 (~2024), 대전 206/DT_206003_J000001 (~2023), 울산 207/DT_2071J02A (~2024), 경기 210/DT_21002_J026 (~2023), 강원 211/DT_211002_J003 (~2024), 충북 212/DT_E222 (~2024), 충남 213/DT_213003_J000001 (~2024), 전북 214/DT_1J01212 (~2023), 경북 216/DT_216003_J000001 (~2024), 경남 217/DT_217003N_J023 (~2024), 제주 218/DT_21802_J001060 (~2024) (https://kosis.kr/statHtml/statHtml.do?orgId=<org>&tblId=<tbl>); none found for 서울, 대구, 세종, 전남. Regional monthly files exist for some 시도 (서울 열린데이터광장 OA-15640 자치구별 연료별; data.go.kr 15105242 경기도_연료별 용도별 자동차 등록 현황; 15063789 부산 법정동별 연료별). Not assembled because of mixed years (2023/2024), missing 시도 and heterogeneous layouts.
- **Note for `_ref` owner**: `sggmap.py` CODE_VALID and `sgg_crosswalk_2020_2026.csv` mark **43720 (충청북도 보은군, still 존재)** as valid only until 2014-07-01; the abolished 청원군 is **43710**. It did not affect these lookups (fallback returns 43720 for 보은군) but should be corrected.

---

# 02 자동차 주행거리 (한국교통안전공단 「자동차주행거리통계」, 국가승인통계 제426001호)

Retrieved 2026-09-24 (KST). Folder: `02_vehicle_mileage/`. All paths below are relative to BASE.

## Summary
- **Latest edition = 2025 reference year.** TS published it on 2026-06-29 (press release). KOSIS updated the tables on 2026-07-15 (수록기간 2012~2025).
- **시군구 level**: KOSIS `DT_426001_N004` gives the daily km per vehicle (1일 평균주행거리) by 용도 (전체/비사업용/사업용) × 차종 (합계/승용/승합/화물/특수) for 229 시군구.
  - 229 = 226 자치 시군구 + 세종 + 제주시, 서귀포시.
  - **일반구 are not separate.** 13 시 appear only as 시 totals.
- **연료 (fuel) is published at 시도 level only** (KOSIS `DT_42601_N003`).
  - It has 5 classes only: 합계/휘발유/경유/LPG/기타연료.
  - 전기 and 하이브리드 are split out only at national level, in the TS press release attachment.
- **연간 주행거리 (annual VKT) and 대상 대수 (vehicle counts) are not published for 2025.**
  - 연간 주행거리 was removed from the approved statistic in 2026 (국가데이터처 경제통계심사조정과-1219, 2026-04-09).
  - For **2024** KOSIS still has 연간 주행거리 (천km) at 시군구 level. The implied registered-vehicle count (June) can be derived from it, so a 2024 tidy file is also provided.

## Files

### A. KOSIS DT_426001_N004 「용도별 차종별 시군구별 자동차주행거리」
- 제공기관: 한국교통안전공단 (TS)
- 출처 플랫폼: KOSIS 국가통계포털
- Table URL: https://kosis.kr/statHtml/statHtml.do?orgId=426&tblId=DT_426001_N004
- **How it was downloaded:** this is the statHtml page's own non-member '다운로드' button. It was replicated with python requests; no login and no API key were used.
  1. GET `statHtml.do?orgId=426&tblId=DT_426001_N004&conn_path=I2`
  2. POST `includeLeftTree.do`, then `right_layout.do`, then `statHtmlContent.do` (the page frames)
  3. POST `https://kosis.kr/statHtml/html.do` (조회, `isFirst=Y`)
  4. POST `https://kosis.kr/statHtml/downGrid.do`. Parameters:
     - `view=xlsx` with `viewSubKind=2_1` (셀병합), or `view=csv` with `viewSubKind=2_3`
     - `dataOpt=cdko` (코드 포함)
     - `downGridCsvType=UTF-8`
     - The response is JSON `{file}`.
  5. POST `https://kosis.kr/statHtml/downNormal.do` with `file=…` returns the attachment.
  - The non-member download limit is 200,000 cells. The largest request was 105,000 cells.
  - Script: `02_vehicle_mileage/_scripts/kosis_dl.py` (`fetch()`).
- 기준연도: 2025 (the time-series file covers 2012~2025).
- 공표: TS 보도자료 2026-06-29; KOSIS 갱신 2026-07-15.
- Raw files (unmodified):

  | File | Content |
  |---|---|
  | `02_vehicle_mileage/kosis/KOSIS_426_DT_426001_N004_용도별_차종별_시군구별_자동차주행거리_2025.xlsx` | KOSIS default layout, sheet `데이터` plus sheet `메타정보` (주석/출처) |
  | `02_vehicle_mileage/kosis/KOSIS_426_DT_426001_N004_용도별_차종별_시군구별_자동차주행거리_2025_code.csv` | CSV UTF-8 with KOSIS codes |
  | `02_vehicle_mileage/kosis/KOSIS_426_DT_426001_N004_용도별_차종별_시군구별_자동차주행거리_2012-2025_code.csv` | Full series. T001 for all years; T002 for 2012~2024 only |

- Tidy files:

  | File | Rows |
  |---|---|
  | `tidy/vehicle_mileage_2025.csv` | 229 (one row per 시군구) |
  | `tidy/vehicle_mileage_2025_long.csv` | 3,435 (229 × 3 용도 × 5 차종) |
  | `tidy/vehicle_mileage_2024.csv` | 229 |
  | `tidy/vehicle_mileage_2024_long.csv` | 10,305 (229 × 15 × 3 measures) |

- Key columns:
  - `sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note, year`
  - `src_code` (KOSIS 행정구역 code, e.g. 11010 = 종로구, 32xxx = 강원, 39xxx = 제주), `src_sido`, `src_sgg`
  - `daily_km_{all|nonbiz|biz}_{total|passenger_car|van_bus|truck|special}`, in km/day/vehicle
    - all = 전체, nonbiz = 비사업용, biz = 사업용
    - passenger_car = 승용차, van_bus = 승합차, truck = 화물차, special = 특수차
  - 2024 file only:
    - `annual_vkt_1000km_*` (연간 주행거리, 천km/year)
    - `implied_reg_veh_*` = annual×1000/(daily×365). This is **derived**, not published. It is the registered-vehicle population (June 2024) implied by KOSIS's formula. It carries ±0.05/daily_km rounding error, i.e. ≤0.3%.
  - Long files: `use, vehicle_type, measure (daily_km | annual_vkt_1000km | implied_reg_veh), unit, value`
- 이용조건: KOSIS 이용약관, free use with 출처표시. Citation as given in the KOSIS 메타정보: 「자동차주행거리통계」, 한국교통안전공단.

### B. KOSIS DT_42601_N003 「용도별 차종별 연료별 자동차주행거리」 (시도 level)
- Table URL: https://kosis.kr/statHtml/statHtml.do?orgId=426&tblId=DT_42601_N003
- Downloaded the same way as A. Same 기준, 공표 dates.
- Dimensions: 18 regions (전국 + 17 시도) × 3 용도 × 5 차종 × 5 연료 (합계/휘발유/경유/LPG/기타연료).
- Raw files:
  - `02_vehicle_mileage/kosis/KOSIS_426_DT_42601_N003_용도별_차종별_연료별_자동차주행거리_2025.xlsx`
  - `…_2025_code.csv`
  - `…_2012-2025_code.csv`
- Tidy files:
  - `tidy/vehicle_mileage_fuel_sido_2025.csv`: 17 rows.
    - Columns: `sido_cd, sido_nm, sido_cd_ref, sido_nm_ref, map_note, year, src_code, src_sido`, then 75 columns `daily_km_{use}_{vehicle type}_{total|gasoline|diesel|lpg|other}`.
  - `tidy/vehicle_mileage_fuel_sido_2025_long.csv`: 1,275 rows.
- 38 of 1,275 시도 cells are '-' in the source (e.g. 사업용 특수차 기타연료 in several 시도). They are stored as NaN (no vehicles/data), not as 0.
- 광주 (29) and 전남 (46) have no 1:1 2026 successor at 시도 level (merged into 12 전남광주통합특별시 on 2026-07-01). For them `sido_cd` = `sido_cd_ref`, and `map_note` explains.

### C. TS 보도자료 "2025년 자동차주행거리 전년대비 2.3% 감소" (2026-06-29)
- Page: https://main.kotsa.or.kr/portal/bbs/report_view.do?bbscCode=report&cateCode=&bbscSeqn=18886
- Attachments: `https://main.kotsa.or.kr/common/download.do?atflIdxx=F_report1888618669&atflSeqn={0,1,2}`
- Raw files in `02_vehicle_mileage/ts_press_20260629/`:
  - `20260629 2025년 자동차주행거리 전년대비 2.3% 감소.hwp` (contains the 붙임 tables)
  - `….txt`
  - `관련자료.zip` (7 infographic JPGs)
- The 붙임 tables contain:
  - National 연간/일평균 2022~2025 with 자동차등록대수 (2025: 26,408,276, June basis; 연간 339,659,305 천km, noted as "추정, 해석 주의")
  - 시도 일평균 2022~2025, with the note "자동차 소유주의 등록거주지 기준"
  - National by fuel
  - National 전기/하이브리드 detail: 전기 69.4 km (승용 62.9, 승합 200.3, 화물 58.2, 특수 22.7); HEV-휘발유 41.6; HEV-경유 47.0; HEV-LPG 35.6
- No tidy file was made. The attachments are used for verification and as context.
- License: the page shows no 공공누리 mark (it is a press release). Cite 한국교통안전공단.

## Definitions (KOSIS 주석, TS 조사개요)
- **1일 평균주행거리 (km/대)** = 주행거리 ÷ 운행일수.
  - 주행거리 = odometer at the latest 자동차검사 − odometer at the previous 검사.
  - 운행일수 = days between the two 검사.
  - Source records: 자동차검사통합시스템 (VIMS) records of vehicles inspected in the reference year (~1,800 검사소; ~10 million valid vehicles; 3-year 검사 history per 차대번호).
  - It is **not** the distance actually driven in the calendar year. It is the average between the previous and the latest 검사 of vehicles inspected in that year.
  - It is **not** annual/365.
- **연간 주행거리 (천km)** = 1일 평균주행거리 × 365 × 자동차등록대수 (모집단, 6월 기준). Published up to 2024 only.
- **Region**: the vehicle owner's registered residence (사용본거지, 법정동코드 in the 검사 records), per the TS 붙임 note.
- **용도**: 자동차등록 용도. 비사업용 = 자가용/관용; 사업용 = 택시, 버스, 렌터카, 화물운송 etc.
- **차종**: 자동차관리법 classes.
- **기타연료**: CNG, 등유, 전기, 하이브리드, 수소, 알코올 etc.

## Caveats
1. **Method break in 2025.**
   - Through 2024: weighted estimates (vehicle measurements × 차종, 용도, 연료, 지역 weights).
   - From 2025: raw measured means ("측정치를 가공없이 제공").
   - KOSIS did **not** revise its 2012~2024 시군구 series. KOSIS 2024 전국 = 36.0, while TS re-computed 2024 = 38.7 on the new basis, at 전국/시도 level only (press release).
   - The 시도 revisions of 2024 range from +1.0 to +3.9 km (서울 32.7→36.6).
   - → Do **not** compare `vehicle_mileage_2025` with `vehicle_mileage_2024` at 시군구 level as a trend. (Apparent change: 36.0→37.8. Consistent-basis change: 38.7→37.8.)
2. **No 2025 counts or annual VKT at 시군구 level.** For weighting use 국토부 자동차등록현황 (another dataset), or use 2024 `implied_reg_veh_*` as a proxy.
3. **일반구 are not separate.** The source gives 시 totals for 수원, 성남, 안양, 부천, 안산, 고양, 용인, 화성, 청주, 천안, 전주, 포항, 창원. `map_note` = `parent_si_of_ilbangu_2026` or `parent_si: 부천/화성 …`.
   - Of the 256 analysis units in `sgg_master_2026`: 213 match directly, 39 일반구 are covered only by the 13 parent-시 rows, and 4 new 인천 구 (제물포, 영종, 서해, 검단, 2026-07-01) have no 1:1 row. The old 중구 28110, 동구 28140 and 서구 28260 are kept with split notes.
4. **Codes.** The source uses KOSIS 행정구역 codes (kept as `src_code`). Rows were mapped by name with `sggmap` (`ref_date` 2025-12-31 or 2024-12-31): **0 unmatched**.
   - 광주/전남 27 units recoded 29xxx/46xxx → 12xxx (2026-07-01).
   - 강원 = 51xxx, 전북 = 52xxx.
   - 군위군 is under 대구 (27720).
   - KOSIS still lists legacy units with no 2024/2025 data: 청원군 33310, 연기군 34320, 경북 군위군 37310. They were dropped.
5. **Fuel discrepancy.** 휘발유 2025 national = 28.2 km in KOSIS and TMACS, but 29.5 km in the press release text and 붙임. 경유 43.1, LPG 50.0 and 기타 52.8 match. This is unresolved; the tidy file uses KOSIS.
6. There are no suppressed or '-' cells among the 229 시군구 in 2024 or 2025. Values are rounded to 0.1 km (daily) or 0.1 천km (annual).

## Verification
- **2025:**
  - 229 rows, 0 unmatched.
  - The KOSIS 전국 and 17 시도 values equal the TS press-release 시도 table exactly (전국 37.8; 비사업용 30.8; 사업용 94.7; 사업용 승용 69.3).
  - Every 시도 value lies within [min, max] of its 시군구 (0 violations in 255 시도×용도×차종 cells).
  - N003 (fuel = 합계) equals N004 시도/전국 (270 cells, max diff 0.0).
  - The 2025-only file equals the 2025 slice of the 2012~2025 file.
  - There are no weights for 2025, so an exact weighted check is impossible. **Proxy check** (weights = 2024 implied registered vehicles):
    - 전국 37.63 vs 37.8 published
    - 시도 |diff| ≤ 0.72 km (전남 41.08 vs 41.8)
    - Median |diff| over all 255 cells: 0.12 km; 86% of cells within 1 km
    - The largest gaps are in small 사업용 cells (e.g. 전북 사업용 특수차 20.9 km; 대전 사업용 합계 7.3 km)
    - These gaps are expected, because 2025 values are unweighted means over the inspected vehicles.
- **2024:**
  - Σ시군구 연간 주행거리 = 시도 (max relative diff 6.4e-6) and = 전국 (6.8e-7). 전국 2024 = 343,127,137 천km, the same as the press release.
  - Σ시군구 implied registered vehicles = 26,135,198 vs 26,134,475 (June-2024 등록대수 in the TS press release; +0.003%).
  - The implied-count-weighted mean of 시군구 daily km vs published 시도 values: max |diff| 0.088 km.
- Scripts: `02_vehicle_mileage/_scripts/{kosis_dl.py, build_tidy.py, build_fuel.py, verify.py}`

## Checked but not used
- **data.go.kr 파일데이터**: 2019 only, marked "수시 (1회성 데이터)"; 이용허락범위 제한 없음; superseded by KOSIS 2012~2025:
  - 15088483 「한국교통안전공단_용도별 차종별 시군구별 일평균 자동차 주행거리_20191231」: CSV, 230 rows, atchFileId FILE_000000003202423, https://www.data.go.kr/data/15088483/fileData.do
  - 15088482 「…시군구별 일년간 자동차 주행거리_20191231」
  - 15088739 「…시도별 연료별 일평균…_20191231」
  - 15088454 「용도별 차종별 연료별 일평균 자동차주행거리_20221231」
  - 15072343 「국토교통부_교통안전_자동차 주행거리 정보(차종별 연료별)_20241231」: links to TMACS
- **TMACS 교통안전정보관리시스템**, https://tmacs.kotsa.or.kr/web/TG/TG200/TG2200/Tg1700_02.jsp?mid=S3080
  - Covers 시도 × 용도 × 차종 × 5 연료, 2012~2025, with an 엑셀 button. 2025 연간 is blank.
  - Same numbers as KOSIS N003. There is no 시군구 page.
- **Other KOSIS tables** (not needed):
  - `DT_42601_N002`: 용도, 차종, 유형, 규모 × 시도
  - `DT_426001_N006`: 시군구별 주행거리당 사망자수, to 2024

---

# 03 주민등록 인구통계 (시군구별 성, 연령별 인구, 세대수): 2026년 8월 말

## 데이터
- 데이터명: 주민등록 인구통계: 「연령별 인구현황」(월간) 및 「주민등록 인구 및 세대현황」(월간), 행정동별 메뉴
- 제공기관: 행정안전부 (국가승인통계 제110026호) / 출처 플랫폼: 주민등록 인구통계 https://jumin.mois.go.kr
- 기준일: 2026-08-31 (2026년 8월 말; 사이트에서 선택 가능한 최신 월, 2026-09-24 확인). 공표일: 페이지에 표기 없음 (월간 통계, 익월 초 공개)
- 수집일: 2026-09-24 (로그인, API키 없음; 사이트의 공개 'csv 파일 다운로드' 버튼과 동일한 POST 재현)

## 다운로드 방법 (공개 다운로드 버튼 POST)
화면 경로: jumin.mois.go.kr → 행정동별 주민등록 인구통계 → (연령별 인구현황 | 주민등록 인구 및 세대현황) → 월간, 2026.08~2026.08,
행정구역 전국, 등록구분 전체 → 하단 '파일 다운로드' 라디오(전체시군구현황 또는 현재화면) → 'csv 파일 다운로드'.
- 연령별: `POST https://jumin.mois.go.kr/downloadCsvAge.do?searchYearMonth=month&xlsStats=2` (2=전체시군구현황, 1=현재화면[전국+시도])
  form: sltOrgType=1, sltOrgLvl1=A, sltOrgLvl2=A, gender=gender, sum=sum, sltUndefType=(빈값=전체), searchYearStart=2026,
  searchMonthStart=08, searchYearEnd=2026, searchMonthEnd=08, sltOrderType=1, sltOrderValue=ASC, sltArgTypes=5 (5세; 1세판은 1),
  sltArgTypeA=0, sltArgTypeB=100, category=month
- 인구 및 세대: `POST https://jumin.mois.go.kr/downloadCsv.do?searchYearMonth=month&xlsStats=2` (또는 xlsStats=1)
  form: 위와 동일한 기간/지역 필드 + gender=gender, genderPer=genderPer, generation=generation (sltArgType* 없음)

## 원본 파일 (BASE 기준, 수정 없음, CP949 CSV, 천단위 쉼표)
서버 파일명은 모두 `202608_202608_연령별인구현황_월간.csv` / `202608_202608_주민등록인구및세대현황_월간.csv` → 변형 구분용 접미사만 추가.
- 03_population_jumin/202608_202608_연령별인구현황_월간_5세단위_전체시군구현황.csv (지역 296행: 시도 16 + 시 + 일반구 + 시군구 + 출장소)
- 03_population_jumin/202608_202608_연령별인구현황_월간_1세단위_전체시군구현황.csv (296행, 0~99세 + 100세 이상, 계/남/여)
- 03_population_jumin/202608_202608_연령별인구현황_월간_5세단위_현재화면_전국시도.csv (전국 + 16 시도; 검증용)
- 03_population_jumin/202608_202608_주민등록인구및세대현황_월간_전체시군구현황.csv (294행; 총인구, 세대수, 세대당인구, 남, 여, 남녀비율)
- 03_population_jumin/202608_202608_주민등록인구및세대현황_월간_현재화면_전국시도.csv (전국 + 16 시도; 검증용)

## Tidy 파일
- tidy/population_age_202608.csv: 256행 × 41열 (분석단위 256 = 일반구 사용, 모 시 제외)
- tidy/population_age_202608_long.csv: 16,128행 (256 × sex{total,male,female} × 21개 5세 구간)
- tidy/population_age1yr_202608_long.csv: 77,568행 (256 × 3 × 101개 1세 연령 0…99, 100p)
- 주요 열: sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note, ref_date(2026-08-31), src_code(10자리 행정기관코드), src_name,
  pop_total / pop_male / pop_female (명), households (주민등록 세대수, 세대), age_0_4 … age_95_99, age_100p (명, 만 나이),
  pop_0_14, pop_15_64, pop_65p, pop_75p, pop_80p (명), share_65p / share_75p / share_80p (비율 0~1 = 해당인구/pop_total)

## 이용조건
행정안전부 누리집 저작권정책: 공공누리 제1유형(출처표시) 자유이용. 출처표기 예: "행정안전부 주민등록 인구통계(2026.8월 말), jumin.mois.go.kr, 2026-09-24 수집".
(data.go.kr 주민등록 인구 Open API 15108092/15108093은 개인 서비스키 필요 → 사용하지 않음)

## 유의사항 / 검증
- 정의: 등록구분 '전체' = 거주자 + 거주불명자 + 재외국민 (외국인 제외). 세대수는 주민등록 세대(인구주택총조사 '가구'와 다름). 행정동별 메뉴 사용.
- 코드: 원자료 10자리 행정기관코드의 앞 5자리 = 5자리 시군구코드 (256개 단위 전부 일치, sgg_cd_ref 불일치 0건). 전국 코드는 연령별 파일 0000000000, 인구, 세대 파일 1000000000.
- 2026 개편 반영 방식 (2026-08 자료):
  - 전남광주통합특별시: 시도 '전남광주통합특별시 (1200000000)', 27개 시군구 1211000000(목포)…1287000000(신안); 광주 자치구는 동구 1221000000, 서구 1224000000, 남구 1227000000, 북구 1230000000, 광산구 1233000000. 29xxx/46xxx 행 없음.
  - 인천: 제물포구 2812500000, 영종구 2815500000, 서해구 2827500000, 검단구 2829000000 (중구, 동구, 서구 행 없음). 인구 0인 잔존 행 '중구영종출장소'(2811400000), '중구용유출장소'(2811800000), '서구검단출장소'(2826500000) 존재 → 제외.
  - 화성시: 시 합계 4159000000 + 일반구 만세구 4159100000, 효행구 4159300000, 병점구 4159500000, 동탄구 4159700000 (2026-02-01 설치). 부천 일반구 3개도 포함.
  - 강원 51xxx, 전북 52xxx, 군위군 2772000000(대구). map_note는 256행 모두 공란(모두 2026 현행코드).
- 일반구: 모 시 13개(수원, 성남, 안양, 부천, 안산, 고양, 용인, 화성, 청주, 천안, 전주, 포항, 창원) 행은 tidy에서 제외하되, 모 시 = 일반구 합계를 전 항목(총/남/여/세대/연령 21구간) 검증 → 불일치 0.
- 기타 제외: 인구 0 출장소 행(북부출장소 4110500000, 송탄, 안중, 풍양출장소, 동해출장소 5110500000, 사천남양, 장유, 양산시웅상출장소) 및 시도 행. 세종은 시도행(3600000000)과 시군구행(3611000000) 중 후자 사용(36110).
- 검증 결과: 행 256 (2026 분석단위 256과 정확히 일치, 누락, 초과 0), 이름 미매칭 0.
  - 시군구 합 = 전국 공표값: 총인구 51,084,159 / 남 25,412,088 / 여 25,672,071 / 세대 24,505,258, 5세 21구간 × 계, 남, 여 모두 차이 0.
  - 16개 시도별 합 = 공표 시도값 (불일치 0); 1세 단위 합 = 5세 구간 (전 단위, 전 구간 일치); 인구및세대 파일 총/남/여 = 연령별 파일 (전 단위 일치).
  - 65세 이상 비율(전국) 22.08% (75+ 8.78%, 80+ 5.03%); 시군구 범위 7.1%(화성시 동탄구) ~ 50.4%(대구 군위군).
- 대안(미사용): KOSIS DT_1B04005N(행정구역(시군구)별/5세별 주민등록인구), DT_1B040A3, DT_1B040B3: 동일 원천(행정안전부).

---

# 04 소득, 복지, 재정 proxy (시군구): manifest fragment

Retrieval date for every file below: 2026-09-24 (KST; some files saved just after midnight on 2026-09-25). No login, account or API key was used anywhere.
All tidy files are UTF-8 with BOM, codes are zero-padded strings, and the first columns are the standard sggmap columns (sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note).

---
## 04a. 근로소득 연말정산 신고현황 (주소지 시군구별), 국세청
- **데이터명**: 국세통계 「4-2-15. 시군구별 근로소득 연말정산 신고현황(주소지)」 (Year-end Settlement of Wage and Salary Income, Taxpayer's Residence). This is the 2025 국세통계연보 edition, published in the 2025 4분기 release.
- **제공기관 / 플랫폼**: 국세청 원천세과 / 국세통계포털 TASIS (https://tasis.nts.go.kr)
- **Where it is on the site**: TASIS → 국세통계조회 → 국세통계 → 통계표 발행연도 2025 → 4. 원천세 → 4-2. 근로소득 연말정산 신고 현황 → 4-2-15 (STTS_MTA_INFR_ID `20250103D01202541132`).
  - Grid data (JSON): POST `https://tasis.nts.go.kr/wqAction.do?actionId=ATWEPEAA001R02` with body `{"dc_search":{"STT_PBL_YR":"2025","STTS_MTA_INFR_ID":"20250103D01202541132","MENU_ID":"43","LANG":"KOR",...}}`
  - The original Excel is the table's attached file (APND_FLE_ID `200000000150431`), which is what the viewer's file-download button fetches. Two steps: POST `https://tasis.nts.go.kr/keyAction.do` (`{}`) returns an RSA public key. Then POST `https://tasis.nts.go.kr/cfdown.do?actionId=ATWEPZAA009R02` with the form field `xmlValue=<info><encFileId>{RSA-PKCS1v1.5(fileId) hex}</encFileId></info>`. This is the page's own public route, and no login is needed.
- **기준**: 2024년 귀속 (연말정산 신고분). ref_date is set to 2024-12-31. 공표: 2025 발행, 4분기 공개.
  - Newer data check: the TASIS 공개일정 lists the 2026 발행 (2025 귀속) edition of 4-2-15 for **4분기 2026**, so it is not yet available as of 2026-09-24.
- **Raw**: `04a_earned_income_nts/4-2-15. 시군구별 근로소득 연말정산 신고현황(주소지)_TASIS_2025발행_2024귀속.xlsx` (8 sheets = print pages, 66,512 B, sha256 7c21987d…)
- **Tidy**: `tidy/earned_income_nts_2024.csv`, **229 rows** (226 시/군/자치구 + 제주시, 서귀포시 + 세종). 0 unmatched.
- **Columns** (amounts in 백만원, counts in 명):
  - n_filers / gross_wage_mn: 급여총계 인원, 금액. n_filers is the 연말정산 신고인원.
  - n_total_wage / total_wage_mn: 과세대상근로소득(=총급여) 인원, 금액
  - n_tax_base / tax_base_mn: 과세표준
  - n_det_tax / det_tax_mn: 결정세액 (인원 = persons with 결정세액 > 0)
  - Derived columns:
    - total_wage_per_filer_10k_won = 총급여/신고인원 (만원). This is the headline "1인당 평균 총급여" definition; the national value is 4,475만원.
    - total_wage_per_earner_10k_won = 총급여/총급여인원
    - gross_wage_per_filer_10k_won
    - det_tax_per_filer_10k_won
    - taxpayer_share = 결정세액 인원/신고인원 (1 − 면세자 비율)
- **License**: public statistics from 국세청 국세통계포털 (TASIS 이용약관). Cite as 「국세청, 국세통계포털(TASIS) 4-2-15」. I did not find an explicit 공공누리 type on the table page.
- **Caveats**
  - The source uses no codes, only names. Sido names are short (서울, 강원, 전북…) and sgg names are indented. '미추홀구(남구)' is mapped to 28177.
  - The data are at 시 level only. 일반구 are not published, so the 13 시 with 일반구 (수원, 성남, 안양, 안산, 고양, 용인, 부천, 화성, 청주, 천안, 전주, 포항, 창원) carry a map_note of parent_si. 부천 has had 일반구 since 2024-01-01 and 화성 since 2026-02-01.
  - 2026 개편: 인천 중구/동구/서구 keep their old codes (28110/28140/28260, map_note split_2026-07-01). 광주, 전남 are recoded to 12xxx. 군위 is 27720 (대구).
  - 세종 has only a 시도 row in the source; it is used as 36110.
  - 기타[B] row (5,009명; 주소 불분명, 외국인 등) is excluded from tidy.
  - NTS footnote [A]: 신규입사자, 중도퇴사자, 이중근로자 are included, and double counting is possible. The table is therefore "not suitable as a direct indicator of salary level", so use it as a relative proxy.
- **Verification**
  - Σ시군구 = 시도 row exactly for 신고인원 in all 17 시도. Amounts differ by ≤8 백만원 (rounding).
  - Σ229 units + 기타 vs 전국 (21,078,535명; 총급여 943,257,648 백만원; 결정세액 65,160,526 백만원): 인원 −2, 금액 within ±12 백만원.
  - The xlsx value was cross-checked against the TASIS grid JSON: 전국 총급여 is identical.

---
## 04b. 국민기초생활보장 수급자 현황 (시군구), 보건복지부
### (1) Official statistic, the main file
- **데이터명**: 「2025년 국민기초생활보장 수급자 현황」 (국가승인통계, 보건복지부 기초생활보장과). The 시군구 data come from 별첨 <표 1> 일반수급자 현황 - 시･군･구별 (PDF pp.147~156 = 본문 pp.133~142). 시도 totals come from <표 1> 수급자 종류별, 시도별 (p.33) and <표 5> 급여별, 시도별 (p.38).
- **URL**: post https://www.mohw.go.kr/board.es?mid=a10411010300&bid=0019&act=view&list_no=1491455 (발간자료, 작성일 2026-07-29).
  - HWP: https://www.mohw.go.kr/boardDownload.es?bid=0019&list_no=1491455&seq=1
  - PDF: https://www.mohw.go.kr/boardDownload.es?bid=0019&list_no=1491455&seq=2
- **기준일**: 2025-12-31 (행복e음 12월말). 공표 2026-07-29.
- **Raw**: `04b_basic_livelihood/2025년 국민기초생활보장 수급자 현황(수정최종)★.pdf` (9,580,045 B) and `….hwp` (12,701,696 B)
- **License**: 공공누리 **제4유형** (출처표시 + 상업적 이용금지 + 변경금지), as shown on the post. The tidy file re-tabulates figures for non-commercial research. Cite MOHW.
### (2) Complementary file-data (same 행복e음 snapshot, includes 시설수급자 and 급여별 breakdown, 일반구 level)
- **데이터명**: 한국사회보장정보원_복지사업 시군구별 수급권자 현황_20251231 (data.go.kr 15062448; 등록 2026-06-26; 연간)
- **URL**: https://www.data.go.kr/data/15062448/fileData.do. The page's download button calls POST /tcs/dss/selectFileDataDownload.do, which returns atchFileId. The file itself is at https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003664131&fileDetailSn=1
  - NB: the page's JSON-LD contentUrl (FILE_000000007647841) returns an unrelated HWP. This is a portal metadata bug, so use the two-step route instead.
- **Raw**: `04b_basic_livelihood/한국사회보장정보원_복지사업 시군구별 수급권자 현황_20251231.csv` (CP949, 2,577 rows; 10 programs × 시군구). **License**: 이용허락범위 제한 없음.
### Tidy
- `tidy/basic_livelihood_2025.csv`: **229 rows** (시/군/자치구 + 제주시, 서귀포시 + 세종, i.e. the MOHW table level). 0 unmatched.
  - From MOHW:
    - n_general_hh: 일반수급가구 수
    - n_general_persons: 일반수급자 수
  - From SSIS, aggregated from its 일반구/시 rows up to the 시 level:
    - n_total_persons: 수급자 계, 일반+시설
    - n_total_hh: 수급가구 계, incl. 시설
    - n_livelihood/medical/housing/education_persons and _hh: 급여별 수급권자, 가구 (생계/의료/주거/교육)
  - Derived: n_facility_persons_derived = n_total_persons − n_general_persons (시설수급자). All values are ≥ 0.
  - Units: 명 and 가구.
- `tidy/basic_livelihood_ssis_2025.csv`: **264 rows** at the finest SSIS level.
  - 252 `row_type=unit` rows. These are 일반구 where they exist; 화성시 is still one unit in 2025-12, and 인천 uses its pre-2026 구.
  - 12 `row_type=si_residual` rows for 수원, 성남, 안양, 부천, 안산, 고양, 용인, 청주, 천안, 전주, 포항, 창원. These are small amounts recorded at 시 level and not in any 구 (113~1,499 persons each, mostly 1-person/시설 cases), so do not drop them when summing.
  - Wide columns for 10 programs: 기초생활보장 total, 생계, 의료, 주거, 교육, 차상위장애인, 차상위자활, 차상위본인부담경감, 기초연금, 장애인연금. Each has _persons (수급권자) and _hh. Absent source rows are set to 0.
  - `tidy/basic_livelihood_ssis_2025_long.csv`: 2,577 rows (as published: program × area).
- **Caveats**
  - The MOHW 시군구 table covers 일반수급자 only. 시설수급자 by 시군구 is only available as the SSIS−MOHW difference.
  - SSIS counts 수급권자, i.e. persons with eligibility. For 기초생활보장 its totals equal MOHW 수급자 exactly.
  - Codes: ref_date is 2025-12-31. 광주/전남 are recoded to 12xxx. 인천 중, 동, 서구 have split notes. 화성, 부천 carry parent_si notes.
  - Rate per 1,000 was **not** added: MOHW gives no matching 시군구 population. Use the resident population at 2025-12-31 later.
- **Verification**: all published totals match exactly.
  - 일반수급자 Σ229 = 2,732,235명 and 가구 2,013,319 (= 표1 합계). Each 시도 sum also equals 표1.
  - SSIS Σ = 2,836,706명 / 2,117,790가구, equal to MOHW 표1 계 / 표5 계. Each 시도 matches.
  - 시설 derived Σ = 104,471 (= 표1 시설수급자).
  - 생계급여 1,850,688명 / 1,488,204가구 and 의료 1,242,623가구 equal 표5.

---
## 04c. 재정자립도, 재정자주도 (지방자치단체별), 행정안전부
- **데이터명**: 지방재정365 「재정지표 > 재정자립도[당초]」 and 「재정자주도[당초]」, 자치단체별현황 (세입과목 개편 후; 일반회계 당초예산)
- **제공기관 / 플랫폼**: 행정안전부 재정정책과 / 지방재정365 (lofin365.go.kr)
- **UI**: https://www.lofin365.go.kr/portal/LF3110300.do?tab=retvLstBycmSitu&jiPyo=01&srchYr=2026&srchDvCd=01&rgnzDvCd=02. The tab's XLSX/CSV/TXT buttons build the file client-side from the JSON below, so the JSON is the original server output.
  - 재정자립도: POST `https://www.lofin365.go.kr/lf/lnncGramStst/pfinIndc/firSvi/retvLstFirAtnBycmSitu.do`, JSON `{"tab":"retvLstBycmSitu","jiPyo":"01","srchYr":"2026","srchDvCd":"01","rgnzDvCd":"02","lafDvCd":"%"}`
  - 재정자주도: POST `…/pfinIndc/fartSvi/retvLstFartAtnBycmSitu.do` with jiPyo "02"
  - Same requests with srchYr "2025" for the 2025 files.
- **기준**: 2026년 당초예산 (ref_date 2026-01-01) and 2025년 당초예산 (2025-01-01).
  - 재정자립도 = (지방세+세외수입)/일반회계 예산규모×100
  - 재정자주도 = (자체수입+자주재원[지방교부세, 조정교부금 등])/예산규모×100
  - 자치단체별 values use 총계; 전국/시도계 use 순계.
- **Raw** (`04c_fiscal_independence/`): `lofin365_재정지표_재정자립도_당초_{2026,2025}_전국_개편후_자치단체별현황.json` and `lofin365_재정지표_재정자주도_당초_{2026,2025}_…json` (288 rows each: 전국계, 17 시도계, 17 본청, 27 소계, 226 기초)
- **Tidy**:
  - `tidy/fiscal_independence_2026.csv` and `tidy/fiscal_independence_2025.csv`: **227 rows** each (226 시/군/자치구 + 세종본청 as 36110). 0 unmatched.
    - fiscal_independence_pct and fiscal_autonomy_pct in %
    - own_revenue, local_tax, non_tax_revenue, grants_autonomous, autonomous_revenue and gen_acct_budget in **천원** (_thou_krw)
  - `tidy/fiscal_independence_{2026,2025}_sido.csv`: 62 rows each (전국계, 17 시도계 [순계], 17 광역 본청, 27 구계/시계/군계 소계), with level and rate_basis columns.
- **License**: 지방재정365 「저작권 및 공공데이터 이용정책」 (type not shown on the page I checked; cite 행정안전부 지방재정365).
- **Caveats**
  - Values exist for 자치단체 only. There are none for 일반구, so the 13 시 with 일반구 carry parent_si notes. 제주시, 서귀포시 (행정시) have no rows; use 제주 본청 from the _sido file if a proxy is needed. 세종 is single-tier.
  - The 2026 당초예산 still uses pre-2026-07 units: 인천 중, 동, 서구 keep codes 28110/28140/28260 (split note), and 광주, 전남 기초 are recoded to 12xxx.
  - '개편 후' means the 2014 세입과목 개편 basis (잉여금, 이월금, 전입금 etc. excluded).
- **Verification**
  - Rates recompute exactly from their components for all 288 rows (max diff 0.00).
  - 전국 재정자립도 is 42.37 (2026) and 43.18 (2025), and 재정자주도 is 64.11 (2026) and 64.87 (2025). These match the site's published national series.
  - Σ(본청+기초) 지방세 = 시도계 for 16/17 시도. 서울 differs by 1.892조 (2026) / 1.759조 (2025) because of 순계 netting of intra-서울 transfers. 세외수입 also differ because of 순계, so the 시도계/전국 rows are not additive by design.
- **Alternatives, not used**: KOSIS 「재정자립도(시도/시/군/구)」 at https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1YL20921 (table title verified; its year coverage was not checked) and e-나라지표 재정자립도 (시도, 단체유형 averages only).

---

# 05 census_commute_mode: 인구주택총조사 표본(20%) 통근통학 이용 교통수단 (시군구)

## A. 2020 (downloaded)

**데이터명**: 인구총조사(2020 인구주택총조사) 표본(20%) 결과. 사용한 통계표:
- **DT_1PA2003** 「성별/연령별/이용 교통 수단별 통근 통학 인구(12세 이상)-시군구」. 이것이 주 자료다.
- **DT_1PA2001** 「성별 통근 통학 인구(12세 이상)-시군구」. 분모와 교차검증용이다.

**제공기관**: 국가데이터처(구 통계청) 인구총조사과, orgId=101, statId 1962001.

**출처 플랫폼**: KOSIS 국가통계포털.

**페이지 URL**:
- https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1PA2003
- https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1PA2001
- KOSIS 목록 경로: 인구 > 인구총조사 > 인구부문 > 총조사인구(2015년 이후) > 표본(20%)부문 (2020년) > 통근통학(20%표본)

**다운로드 방법**: 로그인 없이 쓸 수 있는 statHtml 뷰어 자체의 다운로드 기능을 그대로 따라 했다. OpenAPI와 API 키는 사용하지 않았다.
1. POST `https://kosis.kr/statHtml/html.do`: 뷰어의 '조회' 단계다.
2. POST `https://kosis.kr/statHtml/downGrid.do`: `{"file": ...}`를 돌려준다.
3. POST `https://kosis.kr/statHtml/downNormal.do`: 파일을 받는다.

선택 조건은 다음과 같다.
- 행정구역 전 항목 327개(전국, 동, 읍면부, 시도, 시군구와 일반구)
- 성별은 계, 연령은 합계
- 통근통학여부별은 계, 통근, 통학
- 항목 14개 전부

옵션은 사이트 기본값(빈셀 부호(-) 켬, 통계부호 끔)에 '코드포함'을 더했다(dataOpt=cdko). 스크립트는 `05_census_commute_mode/_scripts/download_2020.py`와 `kosislib.py`다.

수동으로 받는 방법은 다음과 같다.
1. 위 URL을 연다.
2. '조회설정'에서 행정구역을 모두 선택한다(시군구 레벨 포함). 성별은 계, 연령은 합계로 두고 통근통학여부별은 3개 모두 선택한다.
3. '조회'를 누른다.
4. '다운로드'에서 CSV 또는 EXCEL(xlsx)를 고르고 '코드포함'에 체크한 다음 다운로드한다.

**검색일**: 2026-09-24

**기준일**: 2020-11-01

**공표일**: 2021-11-29. 보도자료 「2020 인구주택총조사 표본 집계 결과 인구 특성 항목」이 나온 날이고, 이 자료에 '(통근통학) 이용교통수단 및 소요시간'이 들어 있다.
- 보도자료 URL: https://mods.go.kr/board.es?mid=a10301020200&bid=203&act=view&list_no=415274
- KOSIS 메타데이터상 갱신일(renewalDate)은 2023-10-11이다.

**원자료 파일** (BASE 기준 상대경로, 내려받은 그대로 수정하지 않음):
- `05_census_commute_mode/DT_1PA2003_성별_연령별_이용_교통_수단별_통근_통학_인구_12세이상_시군구_2020.csv`: CP949 인코딩, 헤더 2행과 데이터 972행(지역 324개 x 통근통학 계/통근/통학), 약 104 KB.
- `05_census_commute_mode/DT_1PA2003_성별_연령별_이용_교통_수단별_통근_통학_인구_12세이상_시군구_2020.xlsx`: 같은 내용을 xlsx로 받은 것.
- `05_census_commute_mode/DT_1PA2001_성별_통근_통학_인구_12세이상_시군구_2020.csv` / `.xlsx`: 데이터 324행.
- `05_census_commute_mode/_meta/`에 있는 파일:
  - 뷰어 메타데이터 JSON(`*_statinfo.json`)
  - 분류 항목 전체 목록(`*_class_items.json`, 행정구역 327항목과 코드)
  - 통계표 주석(`*_주석.html`)
  - 다운로드 로그와 검증 결과 JSON

**정제 파일**:
- `tidy/census_commute_mode_2020.csv`: 250행 x 76열, 시군구당 1행.
- `tidy/census_commute_mode_2020_long.csv`: 10,500행. 250개 단위 x 목적 3개 x 항목 14개.

**이용조건**: KOSIS 이용약관을 따르며 출처를 표시하면 자유롭게 쓸 수 있다. 출처 표기는 "국가데이터처, 「인구총조사」, KOSIS(2026.09.24 검색)"로 한다.

**주요 열(단위)**:
- 공통 선두 열: `sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note, ref_date(2020-11-01), src_code, src_name`
  - `src_code`: KOSIS 통계청 행정구역분류 5자리 코드(예: 11010).
  - `src_name`: KOSIS 명칭이다. 일반구는 상위 시 이름을 앞에 붙였다(예: '수원시 장안구').
- 인원 열(명):
  - `{p}_{mode}` 형식이다. p는 `all`(통근통학 계), `com`(통근), `sch`(통학)이다.
  - mode 값: `total`(T000, 통근통학 인구 12세 이상), `single_total`(T100 단일 수단-계), `walk` 걸어서, `bicycle` 자전거, `car_van` 승용차, 승합차(밴), `truck` 트럭, `bus_local` 시내, 좌석, 마을버스, `shuttle_bus` 통근통학차량, `bus_intercity` 고속, 시외버스, `subway` 전철, 지하철, `train` 기차, `taxi` 택시, `other` 기타, `multi` 복합수단(T200).
- 비율 열(%): `all_share_{mode}`, `com_share_{mode}`. 분모는 해당 목적의 total이다. 단일 수단 11개와 복합수단을 합하면 100이다(반올림 오차 ±0.003).
- DT_1PA2001에서 가져온 열(명): `pop_12plus`(12세 이상 인구), `no_commute_12plus`(통근통학 안함).
- long 파일 열: `purpose`, `purpose_key`, `mode_code`(T000..T200), `mode`, `mode_key`, `mode_group`(total/single_total/single/multi), `value`, `unit`=명.

**유의사항**:
- **표본 추정치다.** 20% 표본조사를 가중해 추정한 값이다. 집계대상은 12세 이상 인구이며 일반가구, 집단가구, 집단시설가구를 포함한다. 외국인가구와 특별조사구는 빠지고, 내국인과 함께 사는 외국인은 포함된다(KOSIS 주석).
- **2020년 교통수단 분류가 요청 목록과 다르다.**
  - 단일 수단은 11개다: 걸어서, 자전거, 승용차, 승합차(밴)(합쳐져 있음), 트럭(따로 있음), 시내, 좌석, 마을버스, 통근통학차량(통근통학버스), 고속, 시외버스, 전철, 지하철, 기차, 택시, 기타.
  - 여기에 '복합수단'(수단 2개 이상 이용)이 더해진다. KOSIS는 복합수단을 수단별로 나누어 주지 않는다.
  - 승용차와 승합차를 따로 볼 수 없다. 오토바이도 공표 분류에 따로 없다. 조사표에서 어디로 들어가는지(예: '기타')는 확인하지 않았다.
  - 통근과 통학은 따로 제공된다(`com_*`, `sch_*`).
- **'-' 표시 셀(486개)은 0으로 넣었다.** 예: 제주의 전철과 기차. '통계부호' 옵션을 켜고 다시 받아 봐도 '-' 말고 다른 부호(비공개 등)는 없었다.
- **일반구 처리**
  - 일반구가 있는 시 11곳(수원, 성남, 안양, 안산, 고양, 용인, 청주, 천안, 전주, 포항, 창원)은 본 파일에서 시 전체 행을 빼고 일반구 행 32개를 남겼다. 시 전체 행은 검증에만 썼다.
  - 부천시(31050)는 시 행을 남겼다. 2020년에는 일반구가 없었다. KOSIS 분류 목록에 원미, 소사, 오정구가 있지만 데이터 행은 오지 않았다. map_note는 `parent_si: 부천시 has 일반구 since 2024-01-01`이다.
  - 화성시도 시 행을 남겼고 map_note는 `parent_si ... since 2026-02-01`이다.
- **코드와 2026년 개편 영향**: `sggmap`에 ref_date=2020-11-01을 넣어 매핑했고, 이름 매칭에 실패한 행은 0개다.
  - 강원 42→51, 전북 45→52로 recode했다.
  - 광주 29와 전남 46은 12xxx(전남광주통합특별시, 2026-07-01)로 recode했다.
  - 군위군은 2020년 기준 경북이다. 47720→27720으로 recode했다.
  - 인천 중구(28110), 동구(28140), 서구(28260)는 2026-07-01 분할로 1:1 후속 코드가 없다. 그래서 sgg_cd에 2020년 코드를 그대로 두었고 map_note에 split을 적었다.
  - map_note 집계: 없음 184, recoded 61, split 3, parent_si 2.
- **검증 결과(모두 통과)**
  - T100 + T200 = T000이고, 단일 수단 11개의 합 = T100이다(모든 행).
  - 통근 + 통학 = 계다(모든 수단).
  - 일반구 합 = 시 전체다(11개 시).
  - 250개 단위 합 = 시도다. 17개 시도 x 목적 3개 x 항목 14개에서 최대 차이는 0이다.
  - 250개 단위 합 = 전국이고 시도 합 = 전국이다. 동부 + 읍부 + 면부 = 전국이다.
  - DT_1PA2003의 T000 = DT_1PA2001의 통근통학 계, 통근 계, 통학 계다(모든 지역).
  - 공표된 전국값: 통근통학 인구 28,012,287명, 승용차, 승합차 12,228,703명, 시내, 좌석, 마을버스 3,750,677명, 전철, 지하철 2,645,111명, 걸어서 5,122,567명, 복합수단 1,541,895명. 통근은 23,285,254명, 통학은 4,727,033명이다.
- **받지 않은 관련 2020 표본 통계표** (필요하면 같은 스크립트로 받을 수 있다):
  - DT_1PA2004: 소요시간별/이용 교통수단별 통근 통학 인구, 시군구.
  - DT_1PA2002: 성별/연령별/통근 통학 유형별 인구, 시군구.
  - DT_1PA2013/2014/2015: 산업, 직업, 종사상지위별 이용 교통수단별 통근 인구(15세 이상), 시도.
  - DT_1PA2016: 각급 학교별 이용 교통수단별 통학 인구, 시도.
  - DT_1PA2018/2019: 통근통학 유형, 시군구.
  - DT_1PA2005~2012 및 2021: 현 거주지별/통근통학지별 OD, 시군구.
  - DT_1PA2003에는 성별(남/여)과 연령(5세 계급) 구분도 있다. 이번에는 계와 합계만 받았다.

## B. 2025 (not obtainable yet)

- **2026-09-24 현재, 2025 인구주택총조사 표본(20%) 결과는 공표되지 않았다.** 통근통학 교통수단도 여기에 포함된다.
  - 국가데이터처 인구총조사 보도자료 게시판(https://mods.go.kr/board.es?mid=a10301020200&bid=203)의 최근 글은 두 건뿐이다: 2026-07-28 「2025년 인구주택총조사 등록센서스 방식 결과」(전수), 2026-08-20 「2025 인구주택총조사 100세 이상 고령자조사 집계 결과」.
  - KOSIS 목록 '총조사인구(2015년 이후)'에는 '표본(20%)부문 (2020년)'과 '(2015년)'만 있다.
- **예정 공표일은 2026년 11월 말이다.** 2025 등록센서스 보도자료 p.4에 "※ 2025 인구주택총조사 표본(20%) 공표일정: 2026년 11월말 예정"이라고 적혀 있다.
  - 보도자료 URL: https://mods.go.kr/board.es?mid=a10301020200&bid=203&act=view&list_no=446219 (첨부 PDF: `boardDownload.es?bid=203&list_no=446219&seq=11`)
- **공표된 뒤에 할 일**:
  1. KOSIS 목록에서 새 '표본(20%)부문 (2025년) > 통근통학' 통계표 ID를 확인한다. 2020년 DT_1PA20xx 체계를 따르면 DT_1PA25xx일 가능성이 있지만 확인되지 않았다. DT_1PA2501/2503/2504는 현재 존재하지 않는다.
  2. `_scripts/download_2020.py`를 기간 '2025'로 바꿔 다시 실행한다.
  3. ref_date=2025-11-01로 정제한다. 2025년 코드체계에는 강원 51, 전북 52, 군위 27720, 부천 일반구가 반영되어 있다.
- **대안**: 2025 전수(등록센서스)에는 교통수단 항목이 없다. 그 전까지는 2020 표본이 가장 최근의 시군구 단위 통근통학 수단 자료다.

---

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

---

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

---

# 08 시군구 면적 (지적통계) + 인구감소지역, 인구감소관심지역

---------------------------------------------------------------------------------------------------
## (8a) 시군구별 면적: 지적통계, 2025-12-31 기준

### 주 원천
- 데이터명: 국토교통부_지적기본통계집계_20251231 (지적통계, 국가승인통계)
- 제공기관: 국토교통부 (국가공간정보센터) / 출처 플랫폼: 공공데이터포털 파일데이터 15063997
- 페이지: https://www.data.go.kr/data/15063997/fileData.do (등록 2026-08-18, 수정 2026-08-31, 차기 등록 예정 2027-08-20)
- 다운로드 URL: https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003808480&fileDetailSn=1&insertDataPrcus=N
  (서버 파일명 `20260818-국토교통부_지적기본통계집계.csv`), 수집 2026-09-24, 로그인 불필요
- 기준일: 2025-12-31 (통계 기준일자 열). 공표: 국토교통부 '2026년 지적통계' 2026-03-31 공표 (지적통계연보; 통계누리, KOSIS 게재)
- 원본: 08_area_depopulation/20260818-국토교통부_지적기본통계집계.csv (CP949, 89,908행; 열: 통계 기준일자, 행정구역, 대장 구분[토지/임야],
  축척[9], 소유구분[11], 지목[28], 지번수[필지], 면적[㎡])
- 이용조건: 공공데이터포털 '이용허락범위 제한 없음'

### 검증용 원천 (공식 통계표)
- 국토교통 통계누리 (stat.molit.go.kr) 지적통계 「행정구역별, 지목별 국토이용현황_시군구 (2007~2025)」 (hRsId=24, hFormId=2300, 양식2)
  화면: https://stat.molit.go.kr/portal/cate/statView.do?hRsId=24&hFormId=2300 . 화면의 '파일 다운로드'는 브라우저 측 IBSheet 내보내기이므로,
  화면이 표를 그릴 때 호출하는 공개 JSON을 그대로 저장:
  https://stat.molit.go.kr/portal/stat/data.do?formId=2300&styleNum=2&apprYn=Y&startDate=2025&endDate=2025 ,
  열 정의 https://stat.molit.go.kr/portal/stat/columns.do?formId=2300&styleNum=2
- 원본: 08_area_depopulation/국토교통통계누리_지적통계_행정구역별지목별국토이용현황_시군구_2025_data.json (282행: 전국, 시도, 시(계), 일반구, 시군구),
  08_area_depopulation/국토교통통계누리_지적통계_행정구역별지목별국토이용현황_시군구_columns.json
- 이용조건: 국토교통 통계누리 저작권보호정책, 공공누리 제1유형(출처표시)

### Tidy
- tidy/area_sgg_2025.csv: 253행 × 39열. 열: sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note, ref_date(2025-12-31), src_name,
  area_m2 (㎡), area_km2 (km²), parcels (필지 수), area_km2_<지목> 28개 (전, 답, 과수원, 목장용지, 임야, 광천지, 염전, 대, 공장용지, 학교용지,
  주차장, 주유소용지, 창고용지, 도로, 철도용지, 제방, 하천, 구거, 유지, 양어장, 수도용지, 공원, 체육용지, 유원지, 종교용지, 사적지, 묘지, 잡종지; km²),
  area_km2_public_owned (소유구분 국유지+시도유지+군유지, km²)
- tidy/area_sgg_2025_long.csv: 50,657행: sgg × register(토지/임야) × ownership(11) × jimok(28), 값 area_m2(㎡), parcels (축척은 합산)

### 유의사항 / 검증
- 단위 체계: data.go.kr 파일은 기준일이 2025-12-31이지만 행정구역명이 2026-07-01 이후 체계로 집계되어 있음(전남광주통합특별시 27개, 인천 제물포구, 영종구, 서해구, 검단구).
  통계누리 표(2025)는 기준일 당시 체계(인천 중구, 동구, 서구, 광주, 전남 분리). 대조 결과: 제물포구+영종구 = 통계누리 중구+동구 (147.7196 km²),
  서해구+검단구 = 서구 (119.0193 km²) 정확히 일치; 나머지 249개 단위 모두 0.1 ㎡ 이내 일치 → 제공기관의 재집계이며 임의 분할 아님.
  신설 인천 4개 구 행 map_note = 'source_reaggregated…'. 코드 매핑은 원자료 명칭 체계(2026-08) 기준 → sgg_cd_ref = sgg_cd.
- 화성시 일반구(만세, 효행, 병점, 동탄, 41591/41593/41595/41597; 2026-02-01 설치)는 원자료에 없음 → 화성시 전체 1행(41590, 706.4998 km²),
  map_note 'parent_si… 화성 일반구 not available in source'. 분할값을 만들지 않음. (253행 = 분석단위 256 − 화성 일반구 4 + 화성시 1)
- 그 밖의 일반구(수원, 성남, 안양, 부천, 안산, 고양, 용인, 청주, 천안, 전주, 포항, 창원)는 일반구 단위로 제공됨(모 시 행 없음). 세종 36110, 군위 27720(대구).
- 검증: 이름 미매칭 0. 시군구 합 100,472.3966 km² = 통계누리 전국 100,472,396,606.8 ㎡ (차이 0.1 ㎡); 필지 39,843,292 = 전국; 16개 시도 합 = 통계누리 시도값
  (전남광주 = 광주+전남) 불일치 0; 28개 지목별 전국 합 일치(최대 차 6.6e-6 km²). 최소 부산 중구 3.05 km², 최대 강원 홍천군 1,820.47 km².
- 정의: 지적공부(토지대장+임야대장) 등록면적. 행정안전부 「지방자치단체 행정구역 및 인구현황」의 면적과 반올림, 시점 차이가 있을 수 있음.

---------------------------------------------------------------------------------------------------
## (8b) 인구감소지역 89 + 인구감소관심지역 18

### 원천 (모두 행정안전부 누리집; 첨부 다운로드 https://www.mois.go.kr/cmm/fms/FileDown.do?atchFileId=<ID>&fileSn=<n>, 수집 2026-09-24)
훈령, 예규, 고시 게시판 bbsId=BBSMSTR_000000000016 (https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000016&nttId=<nttId>)
1. 「인구감소지역 지정 고시」 행정안전부 고시 제2021-66호, 2021-10-19 (근거: 국가균형발전 특별법 시행령 제2조의3): nttId=90651, atchFileId=FILE_00107440fxvgD8E, fileSn=0
   → 08_area_depopulation/인구감소지역 지정 고시(행정안전부 고시 제2021-66호, 2021.10.19.).hwp
2. 「인구감소지역 지정 변경 고시」 행정안전부 고시 제2024-15호, 2024-02-27 시행, 변경 기준일 2023-07-01 (경북 군위군 → 대구 군위군): nttId=107400,
   FILE_001252705dfaL-K, fileSn=0 → 08_area_depopulation/행정안전부고시제2024-15호(인구감소지역 지정 변경 고시).pdf
3. 「인구감소관심지역 지정 고시」 행정안전부 고시 제2025-78호 (고시 2025-12-24, 시행 2026-01-01, 유효기간 2026-10-19까지; 근거: 지방자치분권 및
   지역균형발전에 관한 특별법 시행령 제3조제2항): nttId=122812, FILE_00141660nMwObtZ, fileSn=0
   → 08_area_depopulation/인구감소관심지역 지정고시(안)_행정안전부 고시 제2025-78호(2026.1.1. 시행).hwpx
4. (검증) 「지방소멸대응기금 배분 등에 관한 기준」 행정안전부고시 제2026-53호 (2026-08-18, 일부개정) 별표1 '관심지역': nttId=128876, FILE_00148321n1cTmf0
   → 08_area_depopulation/지방소멸대응기금 배분 등에 관한 기준(행정안전부고시 제2026-53호 2026.8.18.).hwpx
5. (경위) 행정안전부고시 제2022-11호 「지방소멸대응기금 배분 등에 관한 기준」(2022-02-11): '관심지역' 최초 정의(별표1; 첨부 PDF에는 별표 쪽 없음): nttId=90649,
   FILE_001074382Z12ua- → 08_area_depopulation/행정안전부고시제2022-11호(지방소멸대응기금 배분 등에 관한 기준).pdf
6. (경위) 보도자료 2021-10-18 「‘인구감소지역’89곳 지정, 지방 살리기 본격 나선다!」: 보도자료 게시판 bbsId=BBSMSTR_000000000008, nttId=87782,
   FILE_001044640hZWR2q fileSn=1 → 08_area_depopulation/211018 (석간) 인구감소지역 89곳 지정 지방 살리기 본격 나선다(지역균형발전과).pdf
7. (현황 스냅샷) https://www.mois.go.kr/frt/sub/a06/b06/populationDecline/screen.do → 08_area_depopulation/행정안전부_인구감소지역지정_안내페이지_20260924.html
- 서버의 Content-Disposition 파일명이 깨져(UTF-16 하위바이트) 게시판 표시 파일명으로 저장. 파일 내용은 수정 없음.
- 이용조건: 고시, 공고는 저작권법 제7조에 따른 비보호 저작물; 보도자료, 누리집은 공공누리 제1유형(출처표시).

### Tidy
- tidy/depopulation_area_2021.csv: 107행 × 17열 (인구감소지역 89 + 인구감소관심지역 18). 명단은 고시 원문(HWP/HWPX)에서 직접 파싱.
- 열: sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note, ref_date(2021-10-19; sgg_cd_ref 기준 시점), category(인구감소지역/인구감소관심지역),
  sido_src, sgg_src (고시 표기), designation_date, gosi_no, gosi_date, effective_from, valid_until, first_listed, amendment, status_20260924

### 유의사항 / 검증
- 89개 = 고시 제2021-66호 명단 (부산3, 대구2, 인천2, 경기2, 강원12, 충북6, 충남9, 전북10, 전남16, 경북16, 경남11). 고시 제2024-15호로 군위군이 대구 소속으로
  변경(대구3, 경북15, 합계 89 유지) → tidy: sgg_cd_ref 47720(경상북도 군위군) → sgg_cd 27720, amendment 열에 기재.
- 관심지역 18개는 고시 제2021-66호 본문에 없음. 2021년 인구감소지수로 산정된 목록이 고시 제2022-11호(기금 배분 기준) 별표1로 처음 고시되었고,
  고시 제2025-78호로 '인구감소관심지역'으로 정식 지정(2026-01-01 시행). 따라서 관심지역 designation_date = 2026-01-01 (gosi_date 2025-12-24),
  first_listed 열에 경위 기재. 명단은 고시 2025-78 = 기금 기준 2026-53 별표1 = 행안부 안내페이지(2026-09-24)로 동일(18개).
- 재지정 여부: 지정주기 5년(고시 2021-66 부칙 제2조) → 2026-10-19 도래 예정. 2026-09-24 현재 행안부 고시 게시판에 재지정 고시 없음
  (관련 최신: 2025-78, 기금 기준 2026-53[2026-08-18]), 안내페이지는 여전히 89/18 명단, 2026-07-31 보도자료도 '89개 인구감소지역' 표기.
  관심지역 고시 유효기간이 2026-10-19까지이므로 10월 재지정 후 갱신 필요. (웹 요약에서 89개를 우대지원 49/특별지원 40으로 나눈 지원 구분 언급이
  있었으나 공식 문서로 확인하지 못해 미반영; 웹검색 한도 소진)
- 코드: sgg_cd_ref = 2021-10-19 당시 코드(강원 42xxx, 전북 45xxx, 광주 29xxx, 전남 46xxx, 군위 47720), sgg_cd = 2026 현행 코드(51xxx, 52xxx, 12xxx, 27720);
  45행 'recoded'. 이름 미매칭 0, 코드 중복 0, 두 명단 간 중복 0.
- 2026 개편 영향: 관심지역 '인천 동구'(28140)는 2026-07-01 폐지 → 1:1 승계코드 없음이므로 sgg_cd=28140 유지(map_note: split). 옛 동구 법정동 7개
  (금곡, 만석, 송림, 송현, 창영, 화수, 화평동) 전부 제물포구(28125)에 속함(법정동코드 파일로 확인). 제물포구가 관심지역 지위를 승계하는지는 고시로 확인되지 않음.
  전남 16개 인구감소지역과 관심지역 광주 동구는 전남광주통합특별시 코드(12xxx)로 표기. 화성시 무관.

---

# 09 K-패스, 모두의 카드: 지역유형, 시도별 가입, 환급, 시군구 지역유형

- **2026년 1분기 지역유형별 이용, 환급 실적** (`tidy/kpass_regiontype_20260331.csv`)
  - 출처: 국회예산정책처(2026.7). 「2025회계연도 결산 위원회별 분석[국토교통위원회]」 p.172, 표 [2026년 1분기 지역유형별 모두의 카드(K-패스) 이용 및 환급 실적] (자료: 국토교통부).
  - 원문: `09_kpass/nabo_reports/국회예산정책처_2025회계연도 결산 위원회별 분석[국토교통위원회]_2026-07.pdf` (nabo.go.kr 발간물).
  - 주의: 우대지원지역은 월평균 환급대상자(137,863)가 가입자(54,828)보다 많아 원자료 불일치: 보고서에서는 참고값으로만 표기.
- **2025년 시도별 이용, 환급 실적** (`tidy/kpass_sido_20251231.csv`)
  - 출처: 같은 보고서 p.169, 표 [2025년 연간 시도별 모두의 카드(K-패스) 이용 및 환급 실적] (자료: 국토교통부).
- **시군구별 모두의 카드 지역유형, 기준금액, 참여 현황** (`tidy/kpass_sgg_20260924.csv`)
  - 출처: K-패스 누리집(korea-pass.kr, 참여 지자체 목록 2026-09-24 조회) + 국회예산정책처 「2026년도 예산안 위원회별 분석[국토위]」(2025.10) p.80 참여 지자체 현황, 기준금액은 정책브리핑(2026.3.17) 표.
- 이용조건: 국회예산정책처 발간물, 국토교통부 보도자료(공공저작물, 출처표시).

---

# 10 버스 운행(TS-BIS): 노선, 시간표, 정류소

- 자료: 한국교통안전공단_버스노선정보(15105964), 버스 노선 및 시간표 정보(15150451), 버스정류장정보(15106249): 공공데이터포털 파일데이터(2026-07-15~21, 이용허락범위 제한 없음).
- 범위: 한국교통안전공단 통합 BIS(TS-BIS)를 쓰는 52개 시군(주로 농어촌), 시간표는 26개 시군 1,962개 평일 노선.
- 용도: ① TAGO 전국 정류장 파일에서 누락된 시군(강원 영동 등) 정류장 보완(30m 이상 떨어진 9,204개), ② 농촌 노선의 일일 운행횟수 분포.
- 정제본: `tidy/bus_service_tsbis_by_sgg_20260716.csv`(시군별 노선, 운행 요약), 원본은 `data/raw/geo/tsbis/`.

---

