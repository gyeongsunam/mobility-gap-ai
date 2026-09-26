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
