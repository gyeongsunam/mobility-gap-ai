"""04. 400m 육각격자(H3 res 8) 단위 '사람 중심' 접근성 지표 산출

격자 인구: p02에서 GHS-POP 2025 가중치로 재배분한 2026.8 행정동 주민등록인구(민감도: Kontur, 혼합)
대중교통 공간 커버리지: 격자당 49개 하위점(res 10) 중 기준거리 이내 비율
  - 버스: 도시지역(주거, 상업, 공업) 400m, 녹지, 비도시 800m / 철도: 800m  (보행거리 = 직선거리 × 우회계수 1.3)
  - 용도지역 근사: 동 400m, 읍면 800m를 기본으로, 저밀(<1,000인/㎢) 격자 800m, 고밀(≥3,000인/㎢) 격자 400m
생활필수시설 보행 접근: 1차 의료(의원, 보건기관)와 생활편의점(편의점, 대규모점포)이 모두 보행 1km 이내
'차 없이는 생활이 불가능한 거주지'(자동차 필수 거주지) = 대중교통 커버 밖 × 필수시설 보행권 밖
"""
import geopandas as gpd
import h3
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from config import (PROC, TAB, H3_CHILD_RES, DENS_LO, DENS_HI, HEX_AREA_KM2, CIRCUITY, BUS_URBAN_M, BUS_RURAL_M,
                    RAIL_M, WALK_ESSENTIAL_M, EARTH_R)

FTYPES = ["primary_care", "pharmacy", "hospital", "daily_shop"]


def tree(df):
    return BallTree(np.radians(df[["lat", "lon"]].to_numpy()), metric="haversine")


def qdist(t, latlon):
    d, _ = t.query(np.radians(latlon), k=1)
    return d[:, 0] * EARTH_R


def transit_coverage(hx, bus, rail, circuity=CIRCUITY):
    tb, tr = tree(bus), tree(rail)
    kids = [h3.cell_to_children(c, H3_CHILD_RES) for c in hx["h3"]]
    n = np.array([len(k) for k in kids])
    flat = np.array([h3.cell_to_latlng(c) for ks in kids for c in ks])
    parent = np.repeat(np.arange(len(hx)), n)
    d_bus = qdist(tb, flat)
    d_rail = qdist(tr, flat)
    dens = (hx["pop"] / HEX_AREA_KM2).to_numpy()
    urban_std = np.where(dens >= DENS_HI, True, np.where(dens < DENS_LO, False, hx["urban"].to_numpy().astype(bool)))
    thr_bus = np.where(urban_std, BUS_URBAN_M, BUS_RURAL_M)[parent] / circuity
    cov_bus = d_bus <= thr_bus
    cov_rail = d_rail <= RAIL_M / circuity
    cov = cov_bus | cov_rail
    agg = lambda x: np.bincount(parent, weights=x.astype(float), minlength=len(hx)) / n
    return pd.DataFrame({"cov_bus": agg(cov_bus), "cov_rail": agg(cov_rail), "cov_transit": agg(cov),
                         "d_bus_m": agg(d_bus) * circuity, "d_rail_m": agg(d_rail) * circuity})


def facility_access(hx, fac, circuity=CIRCUITY):
    out = {}
    pts = hx[["lat", "lon"]].to_numpy()
    for t in FTYPES:
        f = fac[fac["ftype"] == t]
        out[f"d_{t}_m"] = qdist(tree(f), pts) * circuity
        # 보행 1km(직선 환산) 이내 시설 수
        cnt = tree(f).query_radius(np.radians(pts), r=(WALK_ESSENTIAL_M / circuity) / EARTH_R, count_only=True)
        out[f"n_{t}_1km"] = cnt
    return pd.DataFrame(out)


def classify(hx):
    walk = (hx["d_primary_care_m"] <= WALK_ESSENTIAL_M) & (hx["d_daily_shop_m"] <= WALK_ESSENTIAL_M)
    bike = (hx["d_primary_care_m"] <= 3000) & (hx["d_daily_shop_m"] <= 3000)
    hx["ess_walkable"] = walk
    hx["ess_bikeable"] = bike & ~walk          # 걸어서는 멀지만 자전거(3km≈15분)로는 닿는 곳
    hx["uncov"] = 1 - hx["cov_transit"]
    # 자동차 필수 거주 인구(연속형): 대중교통 비커버 비율 × 필수시설 보행권 밖
    hx["car_ess_share"] = hx["uncov"] * (~walk)
    for c in ["pop", "pop_65p", "pop_75p", "pop_80p"]:
        hx[f"{c}_uncov"] = hx[c] * hx["uncov"]
        hx[f"{c}_car_ess"] = hx[c] * hx["car_ess_share"]
    return hx


def aggregate(hx, key):
    num = ["pop", "pop_65p", "pop_75p", "pop_80p", "pop_uncov", "pop_65p_uncov", "pop_75p_uncov",
           "pop_car_ess", "pop_65p_car_ess", "pop_75p_car_ess", "pop_80p_car_ess"]
    g = hx.groupby(key)
    a = g[num].sum()
    w = hx["pop"]
    for c in ["cov_transit", "cov_bus", "cov_rail", "d_bus_m", "d_rail_m"] + [f"d_{t}_m" for t in FTYPES]:
        a[f"pw_{c}"] = (hx[c] * w).groupby(hx[key]).sum() / a["pop"]
    a["pw_ess_walkable"] = (hx["ess_walkable"] * w).groupby(hx[key]).sum() / a["pop"]
    a["pw_ess_bikeable"] = (hx["ess_bikeable"] * w).groupby(hx[key]).sum() / a["pop"]
    # 인구가중 밀도(체감 밀도): 격자 인구밀도의 인구가중 평균(명/km²)
    hex_area_km2 = 0.737
    a["pw_density"] = ((hx["pop"] / hex_area_km2) * w).groupby(hx[key]).sum() / a["pop"]
    a["share_uncov"] = a["pop_uncov"] / a["pop"]
    a["share_car_ess"] = a["pop_car_ess"] / a["pop"]
    a["share65_car_ess"] = a["pop_65p_car_ess"] / a["pop_65p"]
    a["n_hex"] = g.size()
    return a.reset_index()


def main():
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")
    adm["adm_cd2"] = adm["adm_cd2"].astype(str)
    bus = pd.read_parquet(PROC / "bus_stops.parquet")
    rail = pd.read_parquet(PROC / "rail_stations.parquet")
    fac = pd.read_parquet(PROC / "facilities.parquet")
    hx = pd.read_parquet(PROC / "hex_pop.parquet").reset_index(drop=True)
    # 접근성은 고유 격자 단위로 계산(격자 총인구 밀도, 인구 다수 행정동의 동/읍면 구분) 후 (행정동×격자) 조각에 결합
    hu = hx.groupby("h3").agg(lat=("lat", "first"), lon=("lon", "first"), pop=("pop", "sum")).reset_index()
    maj = hx.sort_values("pop", ascending=False).drop_duplicates("h3").set_index("h3")["urban"]
    hu["urban"] = hu["h3"].map(maj).fillna(False).astype(bool)
    hu = pd.concat([hu, transit_coverage(hu, bus, rail)], axis=1)
    hu = pd.concat([hu, facility_access(hu, fac)], axis=1)
    hu.drop(columns=["lat", "lon", "pop", "urban"]).to_parquet(PROC / "hex_unique_access.parquet", index=False)
    hx = hx.merge(hu.drop(columns=["lat", "lon", "pop", "urban"]), on="h3", how="left")
    hx = classify(hx)
    hx.to_parquet(PROC / "hex_access.parquet", index=False)
    # 우회계수 민감도
    sens = []
    p65u = hx.groupby("h3")["pop_65p"].sum().reindex(hu["h3"]).to_numpy()
    for c in (1.0, 1.2, 1.3, 1.4):
        cv = transit_coverage(hu, bus, rail, circuity=c)["cov_transit"].to_numpy()
        sens.append({"circuity": c, "share_pop_uncov": float(((1 - cv) * hu["pop"]).sum() / hu["pop"].sum()),
                     "share_65p_uncov": float(((1 - cv) * p65u).sum() / p65u.sum())})
    pd.DataFrame(sens).to_csv(TAB / "sensitivity_circuity.csv", index=False)
    print(pd.DataFrame(sens).to_string(index=False))
    # 인구 배분 방식 민감도(GHS-POP 주 / 혼합 / Kontur)
    alloc = []
    for suf, nm in (("", "GHS-POP 2025(주)"), ("_blend", "GHS·Kontur 평균"), ("_kontur", "Kontur 2023")):
        p, p65 = hx[f"pop{suf}"], hx[f"pop_65p{suf}"]
        alloc.append({"allocation": nm, "pop_uncov": float((p * hx["uncov"]).sum()),
                      "pop_car_ess": float((p * hx["car_ess_share"]).sum()),
                      "pop65_car_ess": float((p65 * hx["car_ess_share"]).sum())})
    pd.DataFrame(alloc).to_csv(TAB / "sensitivity_allocation.csv", index=False, encoding="utf-8-sig")
    print(pd.DataFrame(alloc).round(0).to_string(index=False))
    for key, fn in [("unit", "unit_access.csv"), ("adm_cd2", "admdong_access.csv")]:
        ag = aggregate(hx, key)
        if key == "unit":
            ag = ag.merge(hx[["unit", "unit_nm"]].drop_duplicates("unit"), on="unit")
        else:
            ag = ag.merge(adm[["adm_cd2", "adm_nm", "unit", "unit_nm", "urban"]], on="adm_cd2")
        ag.to_csv(PROC / fn, index=False, encoding="utf-8-sig")
    tot = hx[["pop", "pop_65p", "pop_uncov", "pop_65p_uncov", "pop_car_ess", "pop_65p_car_ess",
              "pop_75p", "pop_75p_car_ess"]].sum()
    print(f"  대중교통 공간커버 밖 인구 {tot.pop_uncov:,.0f} ({tot.pop_uncov/tot['pop']:.1%}), "
          f"65+ {tot.pop_65p_uncov:,.0f} ({tot.pop_65p_uncov/tot.pop_65p:.1%})")
    print(f"  자동차 필수 거주 인구 {tot.pop_car_ess:,.0f} ({tot.pop_car_ess/tot['pop']:.1%}), "
          f"65+ {tot.pop_65p_car_ess:,.0f} ({tot.pop_65p_car_ess/tot.pop_65p:.1%}), "
          f"75+ {tot.pop_75p_car_ess:,.0f} ({tot.pop_75p_car_ess/tot.pop_75p:.1%})")


if __name__ == "__main__":
    main()
