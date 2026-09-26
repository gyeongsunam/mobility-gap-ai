"""프로젝트 공통 설정: 경로, 좌표계, 접근성 기준값.

기준값 출처
- 버스정류장 기준거리 동(도시) 400m / 읍면(농어촌) 800m, 도시철도, 광역철도 800m:
  한국교통안전공단(2026), 「2025년 대중교통 현황조사 - 대중교통 시설 및 수단」 <표 3-2>
- 우회계수(circuity) 1.3: 직선거리를 보행 네트워크 거리로 환산(민감도 1.2, 1.4 병행)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
FIG = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
for p in (PROC, FIG, TAB):
    p.mkdir(parents=True, exist_ok=True)

BOUNDARY_2026 = RAW / "geo" / "HangJeongDong_ver20260701.geojson"
KONTUR = RAW / "geo" / "kontur_population_KR_20231101.gpkg"

CRS_WGS = 4326
CRS_KOR = 5179          # UTM-K (m)
CRS_LOCALDATA = 5174    # 지방행정 인허가 좌표계 (보정계수 없는 Bessel 중부원점 TM)

H3_RES = 8              # Kontur 400m 육각격자
H3_CHILD_RES = 10       # 격자 내부 커버리지 계산용 하위격자(격자당 49점)

CIRCUITY = 1.3
BUS_URBAN_M = 400       # 도시지역(주거, 상업, 공업) 기준
BUS_RURAL_M = 800       # 녹지, 비도시 기준
RAIL_M = 800
# 용도지역 자료(로그인 필요) 대신 격자 인구밀도로 근사: 동이라도 저밀(<1,000인/㎢) 격자는 녹지, 비도시 기준 800m,
# 읍면이라도 고밀(≥3,000인/㎢) 격자는 도시 주거, 상업 기준 400m 적용
DENS_LO = 1000
DENS_HI = 3000
HEX_AREA_KM2 = 0.737

# 생활필수시설 '걸어서 닿는' 기준(보행 네트워크 1km ≈ 도보 15분, 고령자 기준 약 20분)
WALK_ESSENTIAL_M = 1000

EARTH_R = 6_371_008.8
