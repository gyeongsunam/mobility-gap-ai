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
