# _ref: 시군구 code reference (built 2026-09-24)

- 법정동코드_전체자료_20260924.zip / 법정동코드_전체자료.txt : 행정안전부 행정표준코드관리시스템 (https://www.code.go.kr/stdcode/regCodeL.do -> '법정동 코드 전체자료'), file dated 2026-09-17. Tab-separated: 법정동코드(10) / 법정동명 / 폐지여부.
- sgg_master_2026.csv : all existing (존재) 5-digit 시군구 codes as of 2026-09-17 (269 codes; 256 analysis units = 일반구 used instead of their parent 시; is_unit flag).
- sgg_crosswalk_2020_2026.csv : codes valid at any time 2020-2026 -> 2026 successor (1:1) or split note.
- sggmap.py : helper. `m = sggmap.Mapper(); m.lookup(sido, sgg, ref_date='YYYY-MM-DD')` / `m.attach(df, sido_col, sgg_col, ref_date)`.

Code-system events relevant for 2020-2026 data:
| date | event | old -> new |
|---|---|---|
| 2023-06-11 | 강원특별자치도 출범 | 42xxx -> 51xxx (same suffix) |
| 2023-07-01 | 군위군 경북 -> 대구 편입 | 47720 -> 27720 |
| 2024-01-01 | 부천시 일반구 재설치 | 41190 -> 41192 원미구/41194 소사구/41196 오정구 |
| 2024-01-18 | 전북특별자치도 출범 | 45xxx -> 52xxx (same suffix) |
| 2026-02-01 | 화성시 일반구 설치 | 41590 -> 41591 만세구/41593 효행구/41595 병점구/41597 동탄구 |
| 2026-07-01 | 인천 행정체제 개편 | 중구 28110 + 동구 28140 -> 제물포구 28125 + 영종구 28155; 서구 28260 -> 서해구 28275 + 검단구 28290 |
| 2026-07-01 | 전남광주통합특별시 출범 | 광주 29xxx, 전남 46xxx -> 12xxx (suffixes renumbered, e.g. 46230 광양 -> 12190) |

Standard columns in every tidy CSV:
sgg_cd (5-digit, harmonised to 2026-09 codes when 1:1), sgg_nm (2026 full name), sgg_cd_ref / sgg_nm_ref (code & name valid at the source's reference date), map_note.
