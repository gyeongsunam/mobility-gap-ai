"""06. 행정동(읍면동) 유형화와 우선 개입지역 선정

대상: 자동차 필수 거주 인구가 있는 행정동 중 비율 20% 이상(또는 65세 이상 필수거주 300명 이상)
특성: 자동차 필수 비율, 65세 이상 비율, 체감밀도(log), 1차의료, 생활편의 거리(log), 자전거권(3km) 비율, 철도 접근
방법: 표준화 → K-means(k=2~7 실루엣 비교, 해석가능성 고려해 k=4) → 군집별 처방 메뉴 매칭
우선순위: 65세 이상 자동차 필수 거주 인구(명) × 자동차 필수 비율 → 상위 읍면 목록
"""
import json

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from config import PROC, TAB

SEED = 11
FEATS = ["share_car_ess", "share_65p", "log_density", "log_d_primary_care", "log_d_daily_shop",
         "pw_ess_bikeable", "pw_cov_rail"]


def main():
    a = pd.read_csv(PROC / "admdong_access.csv", dtype={"adm_cd2": str, "unit": str})
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")[["adm_cd2", "pop_65p"]]
    a["share_65p"] = a["pop_65p"] / a["pop"]
    a["log_density"] = np.log10(a["pw_density"].clip(lower=1))
    a["log_d_primary_care"] = np.log10(a["pw_d_primary_care_m"].clip(lower=50))
    a["log_d_daily_shop"] = np.log10(a["pw_d_daily_shop_m"].clip(lower=50))
    m = pd.read_csv(PROC / "master_units.csv", dtype={"unit": str}).set_index("unit")
    a["flag_stop_data"] = a["unit"].map(m["flag_stop_data"]).fillna(False).astype(bool)
    tgt = a[((a["share_car_ess"] >= 0.20) | (a["pop_65p_car_ess"] >= 300)) & ~a["flag_stop_data"]].copy()
    X = StandardScaler().fit_transform(tgt[FEATS])
    sil = {}
    for k in range(2, 8):
        lab = KMeans(k, n_init=20, random_state=SEED).fit_predict(X)
        sil[k] = float(silhouette_score(X, lab))
    k = 4
    km = KMeans(k, n_init=50, random_state=SEED).fit(X)
    tgt["cluster"] = km.labels_
    prof = tgt.groupby("cluster").agg(n=("adm_cd2", "size"), pop=("pop", "sum"), pop_car_ess=("pop_car_ess", "sum"),
                                      pop65_car_ess=("pop_65p_car_ess", "sum"),
                                      share_car_ess=("share_car_ess", "median"), share_65p=("share_65p", "median"),
                                      density=("pw_density", "median"), d_pc=("pw_d_primary_care_m", "median"),
                                      d_shop=("pw_d_daily_shop_m", "median"), bike=("pw_ess_bikeable", "median"),
                                      rail=("pw_cov_rail", "median"), urban=("urban", "mean"))
    # 규칙 기반 이름 부여(군집 번호는 임의이므로 특성으로 식별)
    names, rest = {}, list(prof.index)
    c_rail = prof.loc[rest, "rail"].idxmax(); names[c_rail] = "역세권 라스트마일형"; rest.remove(c_rail)
    c_old = prof.loc[rest, "share_65p"].idxmax(); names[c_old] = "초고령 산간 오지형"; rest.remove(c_old)
    c_urb = prof.loc[rest, "urban"].idxmax(); names[c_urb] = "도시 외곽 도농복합형"; rest.remove(c_urb)
    names[rest[0]] = "농촌 생활권 외곽형"
    order = [c_old, rest[0], c_urb, c_rail]
    prof["name"] = prof.index.map(names)
    tgt["type_name"] = tgt["cluster"].map(names)
    print("실루엣:", {k: round(v, 3) for k, v in sil.items()})
    print(prof.round(3).to_string())
    tgt["priority_score"] = tgt["pop_65p_car_ess"] * tgt["share_car_ess"]
    tgt = tgt.sort_values("pop_65p_car_ess", ascending=False)
    tgt.to_csv(TAB / "typology_admdong.csv", index=False, encoding="utf-8-sig")
    prof.to_csv(TAB / "typology_profile.csv", encoding="utf-8-sig")
    # 우선순위 집중도: 65세+ 자동차 필수 거주 인구 기준 상위 N개 읍면동의 포괄률(전국 대비)
    tot65 = a.loc[~a["flag_stop_data"], "pop_65p_car_ess"].sum()
    cum = tgt["pop_65p_car_ess"].cumsum() / tot65
    cover = {int(n): float(cum.iloc[min(n, len(cum)) - 1]) for n in (100, 200, 300, 500)}
    json.dump({"silhouette": sil, "k": k, "n_target_dong": int(len(tgt)), "names": {str(k2): v for k2, v in names.items()},
               "order": [int(o) for o in order], "cover_top_n": cover,
               "target_pop65_car_ess_share": float(tgt["pop_65p_car_ess"].sum() / tot65)},
              open(TAB / "typology_meta.json", "w"), ensure_ascii=False, indent=1)
    print("상위 N 포괄률:", cover)


if __name__ == "__main__":
    main()
