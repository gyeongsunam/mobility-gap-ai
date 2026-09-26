"""02. 대중교통 거점(버스정류장, 철도역)과 생활필수시설 위치 정제

버스정류장: 국토교통부 전국 버스정류장 위치정보(2025.10.31, TAGO 수집) 기본
  → TAGO 수집이 누락, 과소한 시군(강원 영동, 영서 일부, 전북 익산, 전남 강진, 영광 등)은
    ① 한국교통안전공단 TS-BIS 정류소정보(2026.7.15)로 1차 보완
    ② 그래도 OSM 대비 60% 미만인 시군은 OpenStreetMap 정류장으로 2차 보완(기존 정류장과 30m 이내 중복 제거)
철도역: OpenStreetMap 여객역(도시철도, 광역철도, 일반철도, 경전철) + 국가철도공단 철도역 정보
시설: 지방행정 인허가(LOCALDATA, 2026.9 내려받기) 영업 중 사업장
  - 1차 의료: 의원 + 보건소, 보건지소, 보건진료소, 보건의료원
  - 병원급: 병원, 종합병원
  - 약국, 생활편의점(안전상비의약품 판매업소=편의점 등), 대규모점포
  좌표 결측(제주, 전남광주, 인천에 집중)은 지번주소의 읍면동을 파싱해 해당 행정동 격자로 대체
  (동 지역은 인구 비례 계통추출로 분산, 읍면은 소재지 격자): 좌표 완전 4개 시도에서 대체 오차를 검증
"""
import glob
import json
import re

import geopandas as gpd
import h3
import numpy as np
import pandas as pd
from pyproj import Transformer
from sklearn.neighbors import BallTree

from config import RAW, PROC, TAB, CRS_LOCALDATA, EARTH_R

rng = np.random.default_rng(42)


# ---------------------------------------------------------------- 공통
def to_points(df, lon="lon", lat="lat"):
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon], df[lat]), crs=4326)


def nearest_m(src_latlon, dst_latlon):
    tree = BallTree(np.radians(dst_latlon), metric="haversine")
    d, i = tree.query(np.radians(src_latlon), k=1)
    return d[:, 0] * EARTH_R, i[:, 0]


def dedupe(df, radius_m=30):
    """radius 이내 중복 점 제거(먼저 나온 점 유지)."""
    xy = np.radians(df[["lat", "lon"]].to_numpy())
    tree = BallTree(xy, metric="haversine")
    nb = tree.query_radius(xy, r=radius_m / EARTH_R)
    keep = np.ones(len(df), bool)
    for i, js in enumerate(nb):
        if keep[i]:
            for j in js:
                if j > i:
                    keep[j] = False
    return df[keep]


# ---------------------------------------------------------------- 버스정류장
def build_bus_stops(adm):
    f = glob.glob(str(RAW / "geo" / "busstop" / "*.csv"))[0]
    bs = pd.read_csv(f, encoding="cp949").rename(columns={"위도": "lat", "경도": "lon", "정류장번호": "stop_id",
                                                        "정류장명": "name"})
    sw = (bs.lat > 100) & (bs.lon < 50)
    bs.loc[sw, ["lat", "lon"]] = bs.loc[sw, ["lon", "lat"]].to_numpy()
    bs = bs[bs.lat.between(33, 38.7) & bs.lon.between(124.5, 131.9)]
    bs = dedupe(bs[["stop_id", "name", "lat", "lon"]].assign(src="TAGO"), 5)

    # 한국교통안전공단 TS-BIS 정류소(2026.7.15): 강원 영동, 전남 일부 등 TAGO 누락 시군을 공식 자료로 보완
    ts = pd.read_csv(RAW / "geo" / "tsbis" / "tsbis_stops_20260715.csv", encoding="cp949")
    ts = ts.rename(columns={"정류소노드 아이디": "stop_id", "정류소명": "name", "위도": "lat", "경도": "lon"})
    ts = ts[ts.lat.between(33, 38.7) & ts.lon.between(124.5, 131.9)][["stop_id", "name", "lat", "lon"]]
    ts["stop_id"] = "ts" + ts["stop_id"].astype(str)
    d_ts, _ = nearest_m(ts[["lat", "lon"]].to_numpy(), bs[["lat", "lon"]].to_numpy())
    ts_add = dedupe(ts[d_ts > 30].assign(src="TSBIS"), 5)
    print(f"  TS-BIS 정류소 {len(ts):,}개 중 신규 {len(ts_add):,}개 추가")
    bs = pd.concat([bs, ts_add], ignore_index=True)

    osm = json.load(open(RAW / "osm" / "osm_busstops_kr.json"))["elements"]
    osm = pd.DataFrame([{"stop_id": f"osm{e['id']}", "name": e.get("tags", {}).get("name"),
                         "lat": e["lat"], "lon": e["lon"]} for e in osm]).assign(src="OSM")

    # 시군구별 TAGO, OSM 정류장 수 비교 → TAGO가 OSM의 60% 미만인 단위는 OSM으로 보완
    j_t = gpd.sjoin(to_points(bs), adm[["unit", "geometry"]], predicate="within")
    j_o = gpd.sjoin(to_points(osm), adm[["unit", "geometry"]], predicate="within")
    cmp_ = pd.concat([j_t.groupby("unit").size().rename("tago"), j_o.groupby("unit").size().rename("osm")],
                     axis=1).fillna(0)
    cmp_["ratio"] = cmp_["tago"] / cmp_["osm"].replace(0, np.nan)
    gap_units = cmp_[(cmp_["ratio"] < 0.6) & (cmp_["osm"] >= 30)].index.tolist()
    add = j_o[j_o["unit"].isin(gap_units)].drop(columns=["index_right", "geometry"])
    if len(add):
        d, _ = nearest_m(add[["lat", "lon"]].to_numpy(), bs[["lat", "lon"]].to_numpy())
        add = add[d > 30]
    out = pd.concat([bs, add[["stop_id", "name", "lat", "lon", "src"]]], ignore_index=True)
    cmp_.loc[gap_units].assign(added=add.groupby("unit").size()).to_csv(TAB / "busstop_gapfill.csv",
                                                                         encoding="utf-8-sig")
    print(f"  버스정류장: TAGO+TS-BIS {len(bs):,} + OSM 보완 {len(add):,} (보완 시군 {len(gap_units)}개: {gap_units})")
    return out


# ---------------------------------------------------------------- 철도역
def build_rail():
    els = json.load(open(RAW / "osm" / "osm_rail_kr.json"))["elements"]
    rows = []
    for e in els:
        t = e.get("tags", {})
        if t.get("railway") not in ("station", "halt") and t.get("public_transport") != "station":
            continue
        if t.get("railway") == "construction" or t.get("disused") == "yes" or t.get("station") == "stop_position":
            continue
        if any(k.startswith(("disused", "abandoned", "construction")) for k in t):
            continue
        if t.get("usage") == "freight" or t.get("railway:traffic_mode") == "freight":
            continue
        lat = e.get("lat", e.get("center", {}).get("lat"))
        lon = e.get("lon", e.get("center", {}).get("lon"))
        rows.append({"name": t.get("name"), "kind": t.get("station", "train"), "lat": lat, "lon": lon, "src": "OSM"})
    osm = pd.DataFrame(rows).dropna(subset=["lat"])
    kr = pd.read_csv(glob.glob(str(RAW / "facilities" / "15067652" / "*.csv"))[0], encoding="cp949")
    kr = pd.DataFrame({"name": kr["역이름"], "kind": "train", "lat": kr["위도좌표"], "lon": kr["경도좌표"],
                       "src": "국가철도공단"}).dropna()
    kr = kr[kr.lat.between(33, 39) & kr.lon.between(124, 132)]
    rail = dedupe(pd.concat([osm, kr], ignore_index=True), 150)
    print(f"  철도역: {len(rail):,}개 (OSM {len(osm):,}, 국가철도공단 {len(kr):,}, 150m 중복 제거)")
    return rail


# ---------------------------------------------------------------- 생활필수시설
def read_localdata(name):
    f = glob.glob(str(RAW / "localdata" / f"{name}__*.csv"))[0]
    df = pd.read_csv(f, encoding="cp949", low_memory=False)
    return df[df["영업상태명"] == "영업/정상"].copy()


def build_facilities():
    tr = Transformer.from_crs(CRS_LOCALDATA, 4326, always_xy=True)
    parts = []
    c = read_localdata("clinics")
    c["ftype"] = np.select([c["의료기관종별명"].eq("의원"),
                            c["의료기관종별명"].isin(["보건소", "보건지소", "보건진료소", "보건의료원"])],
                           ["primary_care", "primary_care"], default="other")
    c["subtype"] = c["의료기관종별명"]
    parts.append(c[c.ftype != "other"])
    h = read_localdata("hospitals")
    kind = h["의료기관종별명"].fillna(h["업태구분명"])
    h = h[kind.isin(["병원", "종합병원"]) | h["업태구분명"].isin(["병원", "종합병원"])].copy()
    h["ftype"], h["subtype"] = "hospital", h["업태구분명"]
    parts.append(h)
    p = read_localdata("pharmacies"); p["ftype"], p["subtype"] = "pharmacy", "약국"; parts.append(p)
    o = read_localdata("over_the_counter_medicine_stores"); o["ftype"], o["subtype"] = "daily_shop", "편의점등"
    parts.append(o)
    lg = read_localdata("large_scale_retail_stores"); lg["ftype"], lg["subtype"] = "daily_shop", lg["업태구분명"]
    parts.append(lg)
    f = pd.concat(parts, ignore_index=True)
    f = f[["ftype", "subtype", "사업장명", "지번주소", "도로명주소", "좌표정보(X)", "좌표정보(Y)"]].rename(
        columns={"사업장명": "name", "지번주소": "addr_jibun", "도로명주소": "addr_road",
                 "좌표정보(X)": "x", "좌표정보(Y)": "y"})
    ok = f["x"].notna() & f["y"].notna() & (f["x"] > 0) & (f["y"] > 0)
    lon, lat = tr.transform(f.loc[ok, "x"].to_numpy(), f.loc[ok, "y"].to_numpy())
    f["lon"], f["lat"] = np.nan, np.nan
    f.loc[ok, "lon"], f.loc[ok, "lat"] = lon, lat
    bad = ~(f["lat"].between(33, 38.7) & f["lon"].between(124.5, 131.9))
    f.loc[bad, ["lon", "lat"]] = np.nan
    return f


def parse_emd(addr):
    """주소 문자열에서 (시군구 후보 토큰들, 읍면동 토큰) 추출."""
    if not isinstance(addr, str):
        return None, None
    toks = addr.replace(",", " ").split()
    emd = next((t for t in toks if re.fullmatch(r".+[읍면동가]", t) and not t.endswith(("시", "군", "구"))), None)
    sgg_toks = [t for t in toks[:4] if t.endswith(("시", "군", "구"))]
    return sgg_toks, emd


def _target_dong(addr, adm2):
    """주소 → (대상 행정동 코드, 수준 'emd'|'sgg'|None)."""
    sgg_toks, emd = parse_emd(addr)
    if not sgg_toks:
        return None, None
    cand = adm2[adm2["sggnm"].isin(sgg_toks) | adm2["sgg_short"].isin(sgg_toks)
                | adm2["sggnm"].isin(["".join(sgg_toks[:2])])]
    if cand["unit"].nunique() > 1:          # 동명 시군구(예: 동구, 서구) → 시도명으로 한정
        c2 = cand[cand["sidonm"].str[:2] == addr.split()[0][:2]]
        cand = c2 if len(c2) else cand
    if cand.empty:
        return None, None
    hit = cand[cand["emd"] == emd] if emd else cand.iloc[0:0]
    if hit.empty and emd:
        stem = re.sub(r"\d*[읍면동가]$", "", emd)
        hit = cand[cand["emd"].str.startswith(stem)] if len(stem) >= 1 else hit
    if len(hit):
        return hit.sort_values("pop", ascending=False).iloc[0]["adm_cd2"], "emd"
    return cand.sort_values("pop", ascending=False).iloc[0]["adm_cd2"], "sgg"


def impute_locations(f, adm, hexp):
    """좌표 결측 시설 → 주소의 행정동 안 격자로 대체.
    - 동(도시) 지역: 행정동 내 격자에 '인구 비례 계통추출'로 분산 배치(시설은 사람을 따라 분포)
    - 읍면 지역 및 시군구 수준 대체: 인구 최대 격자(소재지)에 배치
    """
    adm2 = adm[["adm_cd2", "sggnm", "sidonm", "emd", "unit", "urban", "pop"]].copy()
    adm2["sgg_short"] = adm2["sggnm"].str.replace(r"^(.+시)(.+구)$", r"\2", regex=True)
    hx = hexp[["adm_cd2", "lat", "lon", "pop"]].sort_values(["adm_cd2", "pop"], ascending=[True, False])
    groups = {k: g for k, g in hx.groupby("adm_cd2")}
    miss = f["lat"].isna()
    tgt = []
    for idx in f.index[miss]:
        addr = f.at[idx, "addr_jibun"] if isinstance(f.at[idx, "addr_jibun"], str) else f.at[idx, "addr_road"]
        cd, lvl = _target_dong(addr, adm2) if isinstance(addr, str) else (None, None)
        tgt.append((idx, cd, lvl))
    t = pd.DataFrame(tgt, columns=["idx", "adm_cd2", "level"]).dropna(subset=["adm_cd2"])
    urban = adm2.set_index("adm_cd2")["urban"]
    for (cd, lvl), g in t.groupby(["adm_cd2", "level"]):
        h = groups.get(cd)
        if h is None or h.empty:
            continue
        if lvl == "emd" and bool(urban.get(cd, False)) and len(h) > 1 and h["pop"].sum() > 0:
            cw = (h["pop"].cumsum() / h["pop"].sum()).to_numpy()
            u = (np.arange(len(g)) + 0.5) / len(g)
            pick = np.searchsorted(cw, u)
            pick = np.minimum(pick, len(h) - 1)
            f.loc[g["idx"].to_numpy(), "lat"] = h["lat"].to_numpy()[pick]
            f.loc[g["idx"].to_numpy(), "lon"] = h["lon"].to_numpy()[pick]
        else:
            f.loc[g["idx"].to_numpy(), "lat"] = h["lat"].iloc[0]
            f.loc[g["idx"].to_numpy(), "lon"] = h["lon"].iloc[0]
    f["imputed"] = miss
    s = t["level"].value_counts()
    print(f"  시설 좌표 결측 {miss.sum():,}건 → 대체 {f.loc[miss, 'lat'].notna().sum():,}건 "
          f"(읍면동 {s.get('emd', 0):,} / 시군구 {s.get('sgg', 0):,} / 실패 {miss.sum() - len(t):,})")
    return f.dropna(subset=["lat"])


def validate_imputation(f, adm, hexc, sido="경상북도", share=0.45, ftype="primary_care"):
    """좌표 완전 지역에서 좌표를 인위적으로 제거→대체했을 때 격자별 최근접 거리 오차를 측정."""
    sub = f[(~f["imputed"]) & (f["ftype"] == ftype) & f["addr_jibun"].fillna("").str.startswith(sido)].copy()
    drop = rng.random(len(sub)) < share
    test = sub.copy()
    test.loc[drop, ["lat", "lon"]] = np.nan
    test = impute_locations(test, adm, hexc)
    hx = hexc[hexc["sidonm"] == sido]
    d_true, _ = nearest_m(hx[["lat", "lon"]].to_numpy(), sub[["lat", "lon"]].to_numpy())
    d_imp, _ = nearest_m(hx[["lat", "lon"]].to_numpy(), test[["lat", "lon"]].to_numpy())
    w = hx["pop"].to_numpy()
    err = np.abs(d_imp - d_true)
    res = {"sido": sido, "ftype": ftype, "drop_share": share, "n_fac": len(sub),
           "pop_weighted_mean_abs_err_m": float(np.average(err, weights=w)),
           "pop_weighted_median_abs_err_m": float(np.median(np.repeat(err, np.maximum(1, (w / w.mean()).round().astype(int))))),
           "share_hex_err_lt_500m": float((err < 500).mean()),
           "mean_true_m": float(np.average(d_true, weights=w)), "mean_imputed_m": float(np.average(d_imp, weights=w))}
    print("  대체 검증:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()})
    return res


def main():
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")
    adm["adm_cd2"] = adm["adm_cd2"].astype(str)
    bus = build_bus_stops(adm)
    bus.to_parquet(PROC / "bus_stops.parquet", index=False)
    rail = build_rail()
    rail.to_parquet(PROC / "rail_stations.parquet", index=False)
    hexc = pd.read_parquet(PROC / "hex_pop.parquet")
    f = build_facilities()
    f = impute_locations(f, adm, hexc)
    f.to_parquet(PROC / "facilities.parquet", index=False)
    print(f.groupby("ftype").agg(n=("name", "size"), imputed=("imputed", "mean")).to_string())
    val = [validate_imputation(f, adm, hexc, s, 0.45, t)
           for s in ["경상북도", "충청남도", "대구광역시", "대전광역시"] for t in ["primary_care", "pharmacy"]]
    pd.DataFrame(val).to_csv(TAB / "imputation_validation.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
