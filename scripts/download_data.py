"""원자료 내려받기(로그인, API 키 불필요한 공개 경로만 사용). 재실행 시 이미 있는 파일은 건너뜀.

  python scripts/download_data.py

시군구 통계표(자동차 등록, 주행거리, 소득, 수급, 재정, 통근, 사고, K-패스 등)는 정제본(CSV, 수 MB)을
data/raw/stats/tidy/ 에 함께 배포한다(원자료 출처, 내려받기 방법은 data/raw/stats/_manifest_parts/*.md).
"""
import gzip
import json
import shutil
import sys
import time
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
sys.path.insert(0, str(ROOT / "src"))
from datagokr import datagokr_download  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0 Safari/537.36", "Accept-Language": "ko-KR,ko;q=0.9"}


def get(url, dest, **kw):
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        print("  (있음)", dest.name); return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=UA, stream=True, timeout=900, **kw) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
    print("  받음", dest.name, dest.stat().st_size)
    return dest


def main():
    geo = RAW / "geo"
    # 1) 행정동 경계(2026.7): SGIS 원자료, vuski/admdongkor 가공(CC BY 4.0)
    get("https://raw.githubusercontent.com/vuski/admdongkor/master/ver20260701/HangJeongDong_ver20260701.geojson",
        geo / "HangJeongDong_ver20260701.geojson")
    # 2) Kontur 인구(2023.11, H3 400m, CC BY): HDX
    gz = get("https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/"
             "kontur_population_KR_20231101.gpkg.gz", geo / "kontur_population_KR_20231101.gpkg.gz")
    out = geo / "kontur_population_KR_20231101.gpkg"
    if not out.exists():
        with gzip.open(gz, "rb") as fi, open(out, "wb") as fo:
            shutil.copyfileobj(fi, fo)
    # 3) GHS-POP 2025 100m(EU JRC R2023A, CC BY 4.0): 한반도 남부 타일 R5_C30
    z = get("https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/"
            "GHS_POP_E2025_GLOBE_R2023A_54009_100/V1-0/tiles/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R5_C30.zip",
            geo / "ghspop" / "GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R5_C30.zip")
    if not list((geo / "ghspop").glob("*.tif")):
        zipfile.ZipFile(z).extractall(geo / "ghspop")
    # 4) 공공데이터포털 파일데이터(버스정류장, 주민등록인구, 철도역, TS-BIS)
    for pk, d in [("15067528", geo / "busstop"), ("15097972", RAW / "population" / "15097972"),
                  ("15067652", RAW / "facilities" / "15067652"), ("15106249", geo / "tsbis" / "stops"),
                  ("15105964", geo / "tsbis" / "routes"), ("15150451", geo / "tsbis" / "timetable")]:
        if d.exists() and any(d.glob("*.csv")):
            print("  (있음)", pk); continue
        try:
            print("  받음", datagokr_download(pk, str(d)))
        except Exception as e:
            print("  [실패]", pk, e)
    # TS-BIS 파일명 표준화(분석 코드가 쓰는 이름)
    for sub, name in [("stops", "tsbis_stops_20260715.csv"), ("routes", "tsbis_routes_20260715.csv"),
                      ("timetable", "tsbis_timetable_20260721.csv")]:
        src = list((geo / "tsbis" / sub).glob("*.csv"))
        if src and not (geo / "tsbis" / name).exists():
            shutil.copy(src[0], geo / "tsbis" / name)
    # 5) 지방행정 인허가(LOCALDATA): 의원, 병원, 약국, 안전상비의약품 판매업소, 대규모점포
    s = requests.Session(); s.headers.update(UA)
    for ds in ["clinics", "hospitals", "pharmacies", "large_scale_retail_stores", "over_the_counter_medicine_stores"]:
        d = RAW / "localdata"
        if list(d.glob(f"{ds}__*.csv")):
            print("  (있음)", ds); continue
        d.mkdir(parents=True, exist_ok=True)
        s.get(f"https://file.localdata.go.kr/file/{ds}/info", timeout=60)
        s.get("https://file.localdata.go.kr/file/validate/download-count", timeout=60)
        r = s.get(f"https://file.localdata.go.kr/file/download/{ds}/info",
                  headers={"Referer": f"https://file.localdata.go.kr/file/{ds}/info"}, timeout=900)
        (d / f"{ds}__{ds}.csv").write_bytes(r.content)
        print("  받음", ds, len(r.content)); time.sleep(5)
    # 6) OpenStreetMap(ODbL): 버스정류장, 철도역(Overpass API)
    q = {"osm_busstops_kr.json": '[out:json][timeout:500];area["ISO3166-1"="KR"][admin_level=2]->.kr;'
                                 '(node["highway"="bus_stop"](area.kr);node["public_transport"="platform"]["bus"="yes"]'
                                 '(area.kr););out body;',
         "osm_rail_kr.json": '[out:json][timeout:300];area["ISO3166-1"="KR"][admin_level=2]->.kr;'
                             '(node["railway"~"^(station|halt)$"](area.kr);way["railway"="station"](area.kr);'
                             'node["public_transport"="station"]["train"="yes"](area.kr);'
                             'node["public_transport"="station"]["subway"="yes"](area.kr);'
                             'node["public_transport"="station"]["light_rail"="yes"](area.kr););out center tags;'}
    for fn, qq in q.items():
        dest = RAW / "osm" / fn
        if dest.exists():
            print("  (있음)", fn); continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(5):
            r = requests.post("https://overpass-api.de/api/interpreter", data={"data": qq},
                              headers={"User-Agent": "mobility-gap-ai research"}, timeout=600)
            if r.status_code == 200 and r.text.lstrip().startswith("{"):
                dest.write_text(r.text); print("  받음", fn); break
            time.sleep(30)
    print("완료. 시군구 통계 정제본은 data/raw/stats/tidy/ 에 포함되어 있습니다.")


if __name__ == "__main__":
    main()
