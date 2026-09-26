"""07. 필요와 혜택의 불일치(정책 사각지대), 결과 지표 비교

(1) 자동차 필수 거주 비율 5분위(인구가중) × 1인당 승용차 주행, CO2, 대중교통 통근분담, 고령운전자 사망, 전기차 보급
(2) 모두의 카드 지역유형 4구분(수도권/일반지방권/우대지원/특별지원) × 필요(자동차 필수 거주)와 혜택(가입, 환급, 2026 1분기)
(3) 시도별 K-패스 가입, 환급(2025) × 자동차 필수 거주 비율
(4) '이동 고립 위험' 고령자: 자동차 필수 거주 75세 이상 중 운전면허가 없는 인구(시도별 연령별 면허보유율 적용)
(5) 농촌 버스 운행 빈도(TS-BIS 시간표)
(6) 검증용 가설: 자동차 필수 지역에서 차량 보유의 소득 탄력성이 다른가(통제 변수별 강건성)
"""
import json
import math

import numpy as np
import pandas as pd

from config import RAW, PROC, TAB
from units import to_unit

ST = RAW / "stats" / "tidy"
EF = 142.5  # gCO2eq/km


def wq(df, col, w, q=5):
    """인구가중 분위: 누적 인구 비율로 5등분."""
    d = df.sort_values(col)
    cw = d[w].cumsum() / d[w].sum()
    return pd.Series(np.minimum((cw * q).apply(np.ceil).astype(int), q), index=d.index).reindex(df.index)


def ols_hc3(y, X):
    """OLS 계수와 HC3 강건 공분산."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    xtx_inv = np.linalg.pinv(X.T @ X)
    b = xtx_inv @ X.T @ y
    e = y - X @ b
    h = np.einsum("ij,jk,ik->i", X, xtx_inv, X)
    meat = (X * (e / (1 - h))[:, None] ** 2).T @ X
    return b, xtx_inv @ meat @ xtx_inv, 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))


def income_elasticity(d):
    """성인 1천 명당 승용차(로그) ~ 근로소득(로그) × 자동차 필수 상위 1/3. 통제 변수를 늘려 가며 강건성 확인."""
    d = d.dropna(subset=["cars_per_1k_adult", "wage_per_filer_mn", "share_car_ess", "nbls_rate", "pw_density"]).copy()
    d["hi"] = (wq(d, "share_car_ess", "pop", q=3) == 3).astype(float)
    d["lcar"] = np.log(d["cars_per_1k_adult"]); d["lwage"] = np.log(d["wage_per_filer_mn"])
    d["ldens"] = np.log(d["pw_density"]); d["lwage_hi"] = d["lwage"] * d["hi"]
    fe = pd.get_dummies(d["sido_2025"], prefix="s", drop_first=True, dtype=float)
    specs = {"A_none": [], "B_density_aging": ["ldens", "share_65p"],
             "C_plus_poverty": ["ldens", "share_65p", "nbls_rate"],
             "D_plus_sido_fe": ["ldens", "share_65p", "nbls_rate", "FE"]}
    rows = []
    for name, ctrl in specs.items():
        cols = ["lwage", "hi", "lwage_hi"] + [c for c in ctrl if c != "FE"]
        X = d[cols].assign(const=1.0)
        if "FE" in ctrl:
            X = pd.concat([X, fe], axis=1)
        b, V, r2 = ols_hc3(d["lcar"], X)
        i0, i1 = 0, 2
        e_hi = b[i0] + b[i1]; se_hi = math.sqrt(V[i0, i0] + V[i1, i1] + 2 * V[i0, i1])
        rows.append({"spec": name, "n": len(d), "elasticity_others": b[i0], "se_others": math.sqrt(V[i0, i0]),
                     "elasticity_car_ess_top3": e_hi, "se_car_ess_top3": se_hi,
                     "diff": b[i1], "p_diff": math.erfc(abs(b[i1] / math.sqrt(V[i1, i1])) / math.sqrt(2)), "r2": r2})
    return pd.DataFrame(rows)


def main():
    m = pd.read_csv(PROC / "master_units.csv", dtype={"unit": str, "sido_2025": str}).set_index("unit")
    m["sido_2025"] = m["sido_2025"].str.zfill(2)
    ok = ~m["flag_stop_data"] & ~m["flag_reg_outlier"]
    out = {}

    # (1) 5분위 비교
    d = m[ok].copy()
    d["q"] = wq(d, "share_car_ess", "pop")
    d["co2_pc_t"] = d["vkt_pc"] * EF / 1e6
    agg = d.groupby("q").apply(lambda g: pd.Series({
        "n_units": len(g), "pop": g["pop"].sum(),
        "share_car_ess": g["pop_car_ess"].sum() / g["pop"].sum(),
        "vkt_pc": np.average(g["vkt_pc"], weights=g["pop"]),
        "co2_pc_t": np.average(g["co2_pc_t"], weights=g["pop"]),
        "daily_km_car": np.average(g["daily_km_car"], weights=g["car_nonbusiness"]),
        "transit_commute": np.average(g["share_transit_commute"], weights=g["pop"]),
        "active_commute": np.average(g["share_active_commute"], weights=g["pop"]),
        "death65_per_100k65": g["death_65p_2y"].sum() / 2 / g["pop_65p"].sum() * 1e5,
        "ev_per_1k_car": g["ev_car_nonbusiness"].sum() / g["car_nonbusiness"].sum() * 1000,
        "wage_mn": np.average(g["wage_per_filer_mn"], weights=g["filers"]),
        "share_65p": g["pop_65p"].sum() / g["pop"].sum(),
    }), include_groups=False)
    agg.to_csv(TAB / "quintile_outcomes.csv", encoding="utf-8-sig")
    out["quintiles"] = agg.round(4).to_dict(orient="index")
    print(agg.round(3).to_string())

    # (2) 모두의 카드 지역유형별 필요 vs 혜택
    kp = pd.read_csv(ST / "kpass_regiontype_20260331.csv")
    g = m.groupby("modu_region_type").agg(pop=("pop", "sum"), pop_65p=("pop_65p", "sum"),
                                          pop_car_ess=("pop_car_ess", "sum"), pop65_car_ess=("pop_65p_car_ess", "sum"),
                                          n_units=("unit_nm", "size"))
    g = g.join(kp.set_index("region_type")[["members_q1end", "refund_recipients_month_avg", "refund_amount_q1_mil_krw",
                                            "usage_amount_q1_mil_krw"]])
    g["share_car_ess"] = g["pop_car_ess"] / g["pop"]
    g["members_per_100"] = g["members_q1end"] / g["pop"] * 100
    g["refund_per_capita_year_krw"] = g["refund_amount_q1_mil_krw"] * 1e6 * 4 / g["pop"]
    g = g.loc[["수도권", "일반지방권", "우대지원지역", "특별지원지역"]]
    g.to_csv(TAB / "modu_regiontype_incidence.csv", encoding="utf-8-sig")
    out["modu_regiontype"] = g.round(4).to_dict(orient="index")
    print(g.round(3).to_string())

    # (3) 시도별 K-패스(2025) × 자동차 필수 거주 비율
    ks = pd.read_csv(ST / "kpass_sido_20251231.csv", dtype={"sido_cd_ref": str})
    ks["sido_2025"] = ks["sido_cd_ref"].str[:2]
    s = m.groupby("sido_2025").agg(pop=("pop", "sum"), pop_car_ess=("pop_car_ess", "sum"),
                                   sidonm=("sidonm_2025", "first"))
    s = s.join(ks.set_index("sido_2025")[["members_2025end", "refund_amount_mil_krw"]])
    s["share_car_ess"] = s["pop_car_ess"] / s["pop"]
    s["members_per_100"] = s["members_2025end"] / s["pop"] * 100
    s["refund_per_capita_krw"] = s["refund_amount_mil_krw"] * 1e6 / s["pop"]
    rho = s[["share_car_ess", "members_per_100", "refund_per_capita_krw"]].corr("spearman")
    s.to_csv(TAB / "kpass_sido_vs_access.csv", encoding="utf-8-sig")
    out["kpass_sido_spearman"] = {"members": float(rho.loc["share_car_ess", "members_per_100"]),
                                  "refund": float(rho.loc["share_car_ess", "refund_per_capita_krw"])}
    print(s.sort_values("share_car_ess").round(3).to_string())

    # (4) 이동 고립 위험 고령자
    lic = pd.read_csv(ST / "driver_license_by_age_2025.csv")
    pa = pd.read_csv(ST / "population_age_202608.csv", dtype={"sgg_cd": str})
    pa["unit"] = [to_unit(c, n) for c, n in zip(pa["sgg_cd"], pa["sgg_nm"])]
    pa["sido_2025"] = pa["unit"].str[:2]
    p75 = pa.groupby("sido_2025")[["age_75_79", "age_80_84", "age_85_89", "age_90_94", "age_95_99", "age_100p"]].sum()
    p75 = p75.sum(axis=1)
    lic["sido_2025"] = lic["sido_cd"].astype(str).str.zfill(2)
    lic = lic.set_index("sido_2025")
    rate75 = (lic["lic_75_79"] + lic["lic_80p"]) / p75
    hx = pd.read_parquet(PROC / "hex_access.parquet")
    hx["sido_2025"] = hx["unit"].str[:2]
    hx["lic75"] = hx["sido_2025"].map(rate75)
    iso = (hx["pop_75p_car_ess"] * (1 - hx["lic75"])).sum()
    out["isolation"] = {"pop75_car_ess": float(hx["pop_75p_car_ess"].sum()),
                        "pop75_car_ess_no_license": float(iso),
                        "license_rate_75p_national": float((lic["lic_75_79"] + lic["lic_80p"]).sum() / p75.sum()),
                        "license_rate_75p_by_sido": rate75.round(3).to_dict()}
    print("이동 고립 위험 고령자(75+, 면허 없음):", round(iso), "/ 75+ 필수거주:", round(hx['pop_75p_car_ess'].sum()))

    # (5) 농촌 버스 운행 빈도(TS-BIS)
    tt = pd.read_csv(RAW / "geo" / "tsbis" / "tsbis_timetable_20260721.csv", encoding="cp949")
    rt = pd.read_csv(RAW / "geo" / "tsbis" / "tsbis_routes_20260715.csv", encoding="cp949")
    wk = tt[tt["요일"] == "평일"].merge(rt[["노선 아이디", "지자체명"]], on="노선 아이디", how="left")
    r = wk["일일운행횟수"]
    out["tsbis"] = {"n_routes_weekday": int(len(wk)), "n_localgov": int(wk["지자체명"].nunique()),
                    "median_runs": float(r.median()), "share_le2": float((r <= 2).mean()),
                    "share_le4": float((r <= 4).mean())}
    print(out["tsbis"])

    # 헤드라인 수치
    ok_units = m.index[ok]
    hx_ok = hx[hx["unit"].isin(ok_units)]
    out["headline"] = {
        "pop_total": float(hx["pop"].sum()),
        "pop_uncov": float(hx["pop_uncov"].sum()), "pop65_uncov": float(hx["pop_65p_uncov"].sum()),
        "pop_car_ess": float(hx["pop_car_ess"].sum()), "pop65_car_ess": float(hx["pop_65p_car_ess"].sum()),
        "pop75_car_ess": float(hx["pop_75p_car_ess"].sum()),
        "share_car_ess": float(hx["pop_car_ess"].sum() / hx["pop"].sum()),
        "share65_car_ess": float(hx["pop_65p_car_ess"].sum() / hx["pop_65p"].sum()),
        "pop_car_ess_excl_flag": float(hx_ok["pop_car_ess"].sum()),
        "n_hex": int(len(hx)), "n_hex_car_ess_gt50": int((hx["car_ess_share"] > 0.5).sum()),
        "pop_bikeable_not_walkable": float((hx["pop"] * hx["ess_bikeable"]).sum()),
        "pop_car_ess_bikeable": float((hx["pop_car_ess"] * hx["ess_bikeable"]).sum()),
    }
    # 필수시설 보행 기준거리 민감도(0.8~1.5km)
    sens = []
    for thr in (800, 1000, 1200, 1500):
        walk = (hx["d_primary_care_m"] <= thr) & (hx["d_daily_shop_m"] <= thr)
        sens.append({"walk_threshold_m": thr, "pop_car_ess": float((hx["pop"] * hx["uncov"] * ~walk).sum()),
                     "pop65_car_ess": float((hx["pop_65p"] * hx["uncov"] * ~walk).sum())})
    pd.DataFrame(sens).to_csv(TAB / "sensitivity_walk_threshold.csv", index=False)

    # (6) 검증용 가설: 소득-차량 보유 탄력성의 지역 차이(통제 시 유지되는가)
    ie = income_elasticity(m[ok])
    ie.to_csv(TAB / "income_car_elasticity.csv", index=False)
    out["income_elasticity"] = ie.set_index("spec").round(4).to_dict(orient="index")
    print(ie.round(3).to_string(index=False))
    print(json.dumps(out["headline"], indent=1))
    json.dump(out, open(TAB / "incidence_summary.json", "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main()
