"""02. 400m 육각격자(H3 res 8) 인구 배분: 행정동 주민등록인구(2026.8)를 (행정동×격자) 조각으로 재배분

- 100m GHS-POP 2025 픽셀(EU JRC R2023A, 건물 '부피' 기반)을 픽셀 중심 기준으로 행정동, H3 격자에 동시에 배정
  → 행정동이 격자보다 작거나 경계가 격자를 가로질러도 인구가 실제 거주 픽셀 위치로 배분됨
- 행정동 인구를 그 행정동 안의 (격자) 조각에 GHS 인구 비례로 배분(dasymetric)
- 민감도: Kontur Population(2023, 400m H3) 가중치 / 두 가중치 평균
- 검증: 행정동별 주민등록인구 재현도(GHS vs Kontur)
"""
import glob

import geopandas as gpd
import h3
import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer

from config import RAW, PROC, TAB, KONTUR, CRS_KOR

AGE_COLS = ["pop", "pop_65p", "pop_75p", "pop_80p", "pop_0_14", "pop_20_64"]


def ghs_pixels():
    f = glob.glob(str(RAW / "geo" / "ghspop" / "GHS_POP_E2025*R5_C30.tif"))[0]
    with rasterio.open(f) as r:
        a, tr, crs = r.read(1), r.transform, r.crs
    rows, cols = np.nonzero(a > 0)
    xs = tr.c + (cols + 0.5) * tr.a
    ys = tr.f + (rows + 0.5) * tr.e
    lon, lat = Transformer.from_crs(crs, 4326, always_xy=True).transform(xs, ys)
    keep = (lat > 32.9) & (lat < 38.8) & (lon > 124.3) & (lon < 131.95)
    return pd.DataFrame({"lat": lat[keep], "lon": lon[keep], "gpop": a[rows[keep], cols[keep]].astype(float)})


def to_dong(df, adm, lat="lat", lon="lon"):
    pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon], df[lat]), crs=4326)
    j = gpd.sjoin(pts, adm[["adm_cd2", "geometry"]], predicate="within", how="inner")
    return pd.DataFrame(j.drop(columns=["geometry", "index_right"]))


def main():
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")
    adm["adm_cd2"] = adm["adm_cd2"].astype(str)
    a = adm.set_index("adm_cd2")

    # 1) GHS 픽셀 → (행정동, 격자)
    px = to_dong(ghs_pixels(), adm)
    px["h3"] = [h3.latlng_to_cell(y, x, 8) for y, x in zip(px["lat"], px["lon"])]
    pairs = px.groupby(["adm_cd2", "h3"], as_index=False)["gpop"].sum()

    # 2) Kontur 격자 → 격자 안 GHS 조각 비율로 분할(GHS가 없는 격자는 중심점 행정동)
    k = gpd.read_file(KONTUR)[["h3", "population"]].rename(columns={"population": "kpop"})
    share = pairs.assign(s=pairs["gpop"] / pairs.groupby("h3")["gpop"].transform("sum"))[["adm_cd2", "h3", "s"]]
    kk = k.merge(share, on="h3", how="left")
    k_in = kk[kk["s"].notna()].assign(kpop=lambda d: d["kpop"] * d["s"])[["adm_cd2", "h3", "kpop"]]
    k_out = kk[kk["s"].isna()][["h3", "kpop"]]
    ll = np.array([h3.cell_to_latlng(c) for c in k_out["h3"]]) if len(k_out) else np.zeros((0, 2))
    k_out = to_dong(k_out.assign(lat=ll[:, 0], lon=ll[:, 1]), adm)[["adm_cd2", "h3", "kpop"]]
    pairs = pairs.merge(pd.concat([k_in, k_out]).groupby(["adm_cd2", "h3"], as_index=False)["kpop"].sum(),
                        on=["adm_cd2", "h3"], how="outer").fillna({"gpop": 0.0, "kpop": 0.0})

    # 3) 행정동별 가중치
    for src in ("kpop", "gpop"):
        s = pairs.groupby("adm_cd2")[src].transform("sum")
        pairs[f"w_{src}"] = np.where(s > 0, pairs[src] / s, np.nan)
    pairs["w_main"] = pairs["w_gpop"].fillna(pairs["w_kpop"])
    pairs["w_kontur"] = pairs["w_kpop"].fillna(pairs["w_gpop"])
    pairs["w_blend"] = pairs[["w_gpop", "w_kpop"]].mean(axis=1)
    has = pairs.groupby("adm_cd2")["w_main"].sum()
    missing = a.index.difference(has[has > 0].index)
    extra = []
    for cd in missing:   # 두 자료 모두 인구가 없는 행정동 → 대표점 격자
        rp = a.loc[cd, "geometry"].representative_point()
        extra.append({"adm_cd2": cd, "h3": h3.latlng_to_cell(rp.y, rp.x, 8), "gpop": 0.0, "kpop": 0.0,
                      "w_main": 1.0, "w_kontur": 1.0, "w_blend": 1.0})
    if extra:
        pairs = pd.concat([pairs[~pairs["adm_cd2"].isin(missing)], pd.DataFrame(extra)], ignore_index=True)
    pairs = pairs[pairs[["w_main", "w_kontur", "w_blend"]].fillna(0).sum(axis=1) > 0].copy()
    for c in AGE_COLS:
        tot = pairs["adm_cd2"].map(a[c])
        pairs[c] = pairs["w_main"].fillna(0) * tot
        if c in ("pop", "pop_65p"):
            pairs[f"{c}_kontur"] = pairs["w_kontur"].fillna(0) * tot
            pairs[f"{c}_blend"] = pairs["w_blend"].fillna(0) * tot
    ll = np.array([h3.cell_to_latlng(c) for c in pairs["h3"]])
    pairs["lat"], pairs["lon"] = ll[:, 0], ll[:, 1]
    pairs = pairs.merge(adm[["adm_cd2", "adm_nm", "sgg", "sggnm", "sidonm", "unit", "unit_nm", "urban", "emd"]],
                        on="adm_cd2", how="left")
    pairs.to_parquet(PROC / "hex_pop.parquet", index=False)

    # 검증표: 행정동 단위 재현도(격자 인구 합계를 전국 총량에 맞춘 뒤 비교)
    d = a[["pop"]].join(pairs.groupby("adm_cd2")[["kpop", "gpop"]].sum())
    rows = []
    for src, nm in (("gpop", "GHS-POP 2025"), ("kpop", "Kontur 2023")):
        s = d[src].fillna(0) * d["pop"].sum() / d[src].sum()
        lr = np.log((s + 1) / (d["pop"] + 1))
        rows.append({"source": nm, "median_abs_log_err": float(np.median(np.abs(lr))),
                     "share_within_25pct": float((np.abs(np.exp(lr) - 1) < 0.25).mean()),
                     "share_under_half": float((np.exp(lr) < 0.5).mean())})
    pd.DataFrame(rows).to_csv(TAB / "population_grid_validation.csv", index=False, encoding="utf-8-sig")
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print(f"(행정동×격자) 조각 {len(pairs):,}개, 고유 격자 {pairs['h3'].nunique():,}개, 인구 {pairs['pop'].sum():,.0f}, "
          f"대표점 보정 행정동 {len(missing)}개")


if __name__ == "__main__":
    main()
