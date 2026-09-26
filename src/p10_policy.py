"""10. 정책 시나리오 산정(가정은 모두 명시; 보수적 값 사용)

P1 이동권 크레딧(모두의 카드 '이동권형'): 자동차 필수 거주 65세+에게 DRT, 공공형택시, 농어촌/시외버스용 월 2만 원
    - 1순위: 면허 없는 75세+ 자동차 필수 거주자(100% 지급 가정) / 2순위: 65세+ 전체(이용률 50% 가정)
P2 교통서비스개선지역 지정, DRT 예산 배분: 65세+ 자동차 필수 거주 인구 기준 상위 N개 읍면동 포괄률
P3 탄소, 안전 공동편익
    (a) 운전대 교환: 자동차 필수 거주 75세+ 면허 보유자의 연간 반납률 2.51%→7.5% 가정
        반납 1건당 사고 −0.0118건, 사회적 비용 −42만 원(최재훈, 염윤호, 2024), 폐차 시 승용 1대 연 주행×배출계수
    (b) 3km 자전거 생활권: 자동차 필수 거주자 중 의원, 생활편의시설이 3km 이내인 인구의 필수시설 차량통행
        (주 2회 왕복, 편도 평균 2km 가정 = 연 416km/인) 중 10~20%를 (전기)자전거로 전환
    (c) 구조적 초과배출: 자동차 필수 거주 상위 2개 5분위(약 2천만 명)의 1인당 승용 CO2가 전국 평균을 넘는 부분
"""
import json

import numpy as np
import pandas as pd

from config import RAW, PROC, TAB

EF = 142.5            # gCO2eq/km
CREDIT_MONTH = 20000  # 원
ST = RAW / "stats" / "tidy"


def main():
    inc = json.load(open(TAB / "incidence_summary.json"))
    typ = json.load(open(TAB / "typology_meta.json"))
    m = pd.read_csv(PROC / "master_units.csv", dtype={"unit": str}).set_index("unit")
    hx = pd.read_parquet(PROC / "hex_access.parquet")
    h = inc["headline"]
    out = {}

    # P1 크레딧
    iso = inc["isolation"]["pop75_car_ess_no_license"]
    p65 = h["pop65_car_ess"]
    annual = CREDIT_MONTH * 12
    out["p1"] = {"tier1_people": iso, "tier1_cost_eok": iso * annual / 1e8,
                 "tier2_people": p65, "tier2_cost_eok_50pct": p65 * annual * 0.5 / 1e8,
                 "budget_2027_increase_eok": 3072, "budget_2027_total_eok": 8652}
    g = pd.DataFrame(inc["modu_regiontype"]).T
    sp = g.loc["특별지원지역"]
    add = float(sp["pop65_car_ess"]) * annual * 0.5 / float(sp["pop"])
    out["p1"]["special_refund_now"] = float(sp["refund_per_capita_year_krw"])
    out["p1"]["special_after"] = float(sp["refund_per_capita_year_krw"]) + add
    out["p1"]["capital_refund"] = float(g.loc["수도권", "refund_per_capita_year_krw"])
    out["p1"]["gap_now"] = out["p1"]["capital_refund"] / out["p1"]["special_refund_now"]
    out["p1"]["gap_after"] = out["p1"]["capital_refund"] / out["p1"]["special_after"]

    # P2 우선지역
    out["p2"] = {"n_target_dong": typ["n_target_dong"], "cover_top_n": typ["cover_top_n"],
                 "target_share": typ["target_pop65_car_ess_share"], "drt_budget_2027_eok": 2000,
                 "driverless_drt_eok": 322}

    # P3(a) 운전대 교환
    lic = pd.read_csv(ST / "driver_license_by_age_2025.csv")
    pa = pd.read_csv(ST / "population_age_202608.csv", dtype={"sgg_cd": str})
    from units import to_unit
    pa["sido_2025"] = [to_unit(c, n)[:2] for c, n in zip(pa["sgg_cd"], pa["sgg_nm"])]
    p75 = pa.groupby("sido_2025")[["age_75_79", "age_80_84", "age_85_89", "age_90_94", "age_95_99",
                                   "age_100p"]].sum().sum(axis=1)
    lic["sido_2025"] = lic["sido_cd"].astype(str).str.zfill(2)
    rate = (lic.set_index("sido_2025")["lic_75_79"] + lic.set_index("sido_2025")["lic_80p"]) / p75
    holders = float((hx["pop_75p_car_ess"] * hx["unit"].str[:2].map(rate)).sum())
    extra_returns = holders * (0.075 - 0.0251)
    veh_km = 11300 * 0.6           # 비사업용 승용 1대 연 주행(2024, 11,300km)의 60%(고령운전자 보수 가정)
    out["p3a"] = {"holders_75p_car_ess": holders, "extra_returns_per_year": extra_returns,
                  "crashes_avoided": extra_returns * 0.0118, "social_cost_saved_eok": extra_returns * 42 / 1e4,
                  "co2_kt_if_scrapped": extra_returns * veh_km * EF / 1e9}

    # P3(b) 3km 자전거 생활권
    bike_pop = h["pop_car_ess_bikeable"]
    km = 2 * 2 * 2 * 52            # 주 2회 왕복 × 편도 2km × 52주 = 416km
    out["p3b"] = {"bike_pop": bike_pop, "km_per_person": km,
                  "co2_kt_10pct": bike_pop * km * 0.10 * EF / 1e9, "co2_kt_20pct": bike_pop * km * 0.20 * EF / 1e9}

    # P3(c) 구조적 초과배출
    q = pd.read_csv(TAB / "quintile_outcomes.csv", index_col=0)
    ok = m[~m["flag_stop_data"] & ~m["flag_reg_outlier"]]
    nat = float(np.average(ok["vkt_pc"], weights=ok["pop"]) * EF / 1e6)
    top = q.loc[q.index >= 4]
    excess = float(((top["co2_pc_t"] - nat) * top["pop"]).sum() / 1e6)
    out["p3c"] = {"national_co2_pc_t": nat, "top2q_pop": float(top["pop"].sum()), "excess_mt": excess,
                  "q1_co2": float(q.loc[1, "co2_pc_t"]), "q5_co2": float(q.loc[5, "co2_pc_t"])}
    json.dump(out, open(TAB / "policy_summary.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
