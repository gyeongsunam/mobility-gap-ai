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
