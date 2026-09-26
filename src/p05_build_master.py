"""04. 분석 시군구(228개) 마스터 테이블 구축

접근성(격자 집계) + 자동차 등록(2026.8) + 주행거리(2025) + 소득(2024 귀속) + 기초생활수급(2025)
+ 재정자립도(2026) + 통근통학 수단(2020 센서스) + 고령운전자 사고(2025) + 전기차(2025.4)
+ 모두의 카드 지역유형 + 인구감소지역 + TS-BIS 버스 운행(2026.7)
"""
import numpy as np
import pandas as pd

from config import RAW, PROC, TAB
from units import to_unit

ST = RAW / "stats" / "tidy"
S = lambda f: pd.read_csv(ST / f, dtype={"sgg_cd": str, "sgg_cd_ref": str})


def by_unit(df, cols, how="sum", code="sgg_cd", name="sgg_nm"):
    df = df.copy()
    df["unit"] = [to_unit(c, n) for c, n in zip(df[code], df[name])]
    return df.groupby("unit")[cols].agg(how)


def main():
    u = pd.read_csv(PROC / "units.csv", dtype={"unit": str}).set_index("unit")
    acc = pd.read_csv(PROC / "unit_access.csv", dtype={"unit": str}).set_index("unit")
    acc = acc.drop(columns=[c for c in acc.columns if c in u.columns and c != "unit_nm"] + ["unit_nm"])
    m = u.join(acc, how="left")

    # 1) 자동차 등록 2026.8: 자가용 승용(가구 보유 차량의 근사), 비사업용 전체
    vr = S("vehicle_registration_202608.csv")
    m = m.join(by_unit(vr, ["car_private", "car_nonbusiness", "total_private", "car_all"]))

    # 2) 주행거리 2025: 비사업용 승용차 1대당 일평균 주행거리(km/일)
    mi = S("vehicle_mileage_2025.csv")
    mi24 = S("vehicle_mileage_2024.csv")
    # 인천 중, 동구처럼 합쳐지는 단위는 2024 대수 가중 평균
    mi = mi.merge(mi24[["sgg_cd", "implied_reg_veh_nonbiz_passenger_car", "annual_vkt_1000km_nonbiz_passenger_car",
                        "annual_vkt_1000km_all_passenger_car"]], on="sgg_cd", how="left")
    mi["w"] = mi["implied_reg_veh_nonbiz_passenger_car"].fillna(1)
    mi["km_w"] = mi["daily_km_nonbiz_passenger_car"] * mi["w"]
    g = by_unit(mi, ["km_w", "w", "annual_vkt_1000km_nonbiz_passenger_car", "annual_vkt_1000km_all_passenger_car"])
    m["daily_km_car"] = g["km_w"] / g["w"]
    m["vkt24_nonbiz_car_1000km"] = g["annual_vkt_1000km_nonbiz_passenger_car"]
    m["vkt24_all_car_1000km"] = g["annual_vkt_1000km_all_passenger_car"]

    # 3) 소득(국세청 근로소득 연말정산, 2024 귀속, 주소지 기준)
    inc = by_unit(S("earned_income_nts_2024.csv"), ["total_wage_mn", "n_filers"])
    m["wage_per_filer_mn"] = inc["total_wage_mn"] / inc["n_filers"]          # 백만원/인
    m["filers"] = inc["n_filers"]

    # 4) 기초생활보장 수급자(2025.12, 한국사회보장정보원 시군구별 수급권자 현황: 이용허락범위 제한 없음)
    bl = by_unit(S("basic_livelihood_ssis_2025.csv"), ["n_nbls_total_persons"])
    m["nbls_persons"] = bl["n_nbls_total_persons"]

    # 5) 재정자립도(2026 당초, 일반회계): 자체수입/예산 합산 비율
    fi = S("fiscal_independence_2026.csv")
    fi = fi[fi["sgg_cd"].notna()]
    g = by_unit(fi, ["own_revenue_thou_krw", "gen_acct_budget_thou_krw"])
    m["fiscal_indep"] = g["own_revenue_thou_krw"] / g["gen_acct_budget_thou_krw"] * 100
    # 제주시, 서귀포시는 행정시(독자 예산 없음) → 제주특별자치도 재정자립도 적용
    fs = S("fiscal_independence_2026_sido.csv")
    jeju = fs.loc[fs["sido"].astype(str).str.contains("제주"), "fiscal_independence_pct"]
    if len(jeju):
        m.loc[["50110", "50130"], "fiscal_indep"] = float(jeju.iloc[0])

    # 6) 통근통학 수단(2020 인구주택총조사 20% 표본)
    cm = S("census_commute_mode_2020.csv")
    cols = ["all_single_total", "all_walk", "all_bicycle", "all_car_van", "all_bus_local", "all_bus_intercity",
            "all_subway", "all_train", "all_shuttle_bus", "all_taxi", "com_single_total", "com_car_van",
            "com_bus_local", "com_subway", "com_train", "com_bus_intercity", "com_walk", "com_bicycle"]
    cm = cm[cm["sgg_cd"].notna()]
    g = by_unit(cm, cols)
    m["share_car_commute"] = g["all_car_van"] / g["all_single_total"]
    m["share_transit_commute"] = (g["all_bus_local"] + g["all_bus_intercity"] + g["all_subway"] + g["all_train"]) \
        / g["all_single_total"]
    m["share_active_commute"] = (g["all_walk"] + g["all_bicycle"]) / g["all_single_total"]
    m["share_bike_commute"] = g["all_bicycle"] / g["all_single_total"]

    # 7) 가해운전자 연령별 교통사고(2025, TAAS)
    ac = by_unit(S("accidents_by_driver_age_2025.csv"), ["acc_total", "acc_65p", "death_total", "death_65p"])
    m = m.join(ac)
    ac24 = by_unit(S("accidents_by_driver_age_2024.csv"), ["acc_65p", "death_65p"])
    m["acc_65p_2y"] = m["acc_65p"] + ac24["acc_65p"]
    m["death_65p_2y"] = m["death_65p"] + ac24["death_65p"]

    # 8) 전기차(한국교통안전공단, 2025.4.7 운행차량 기준)
    ev = S("vehicle_fuel_ev_sgg_20250407.csv")
    ev = ev[ev["row_type"] == "unit"]
    m = m.join(by_unit(ev, ["ev_car_nonbusiness"]))

    # 9) 모두의 카드 지역유형(수도권/일반지방권/우대지원지역/특별지원지역)
    kp = S("kpass_sgg_20260924.csv")
    kp["unit"] = [to_unit(c, n) for c, n in zip(kp["sgg_cd"], kp["sgg_nm"])]
    m["modu_region_type"] = kp.groupby("unit")["modu_region_type"].first()

    # 10) 인구감소지역(89), 관심지역(18)
    dp = S("depopulation_area_2021.csv")
    dp["unit"] = [to_unit(c, n) for c, n in zip(dp["sgg_cd"], dp["sgg_nm"])]
    m["depop"] = m.index.isin(dp.loc[dp["category"].str.contains("인구감소지역") &
                                      ~dp["category"].str.contains("관심"), "unit"])
    m["depop_interest"] = m.index.isin(dp.loc[dp["category"].str.contains("관심"), "unit"])

    # 11) 면적
    ar = S("area_sgg_2025.csv")
    ar = ar[ar["sgg_cd"].notna()]
    m["area_km2"] = by_unit(ar, ["area_km2"])["area_km2"]

    # 12) TS-BIS 버스 운행(52개 시군, 2026.7)
    bs = S("bus_service_tsbis_by_sgg_20260716.csv")
    m = m.join(by_unit(bs, ["n_routes", "n_routes_weekday_service", "weekday_runs_total", "n_routes_weekday_le2",
                            "n_routes_weekday_ge10"]))

    # ---------------- 파생 지표
    m["adult"] = m["pop_20_64"] + m["pop_65p"]
    m["cars_per_1k"] = m["car_private"] / m["pop"] * 1000
    m["cars_per_1k_adult"] = m["car_private"] / m["adult"] * 1000
    m["vkt_pc"] = m["car_nonbusiness"] * m["daily_km_car"] * 365 / m["pop"]           # km/인/년
    m["share_65p"] = m["pop_65p"] / m["pop"]
    m["share_75p"] = m["pop_75p"] / m["pop"]
    m["nbls_rate"] = m["nbls_persons"] / m["pop"]
    m["filer_rate"] = m["filers"] / m["pop_20_64"]
    m["acc65_per_1k65"] = m["acc_65p_2y"] / 2 / m["pop_65p"] * 1000
    m["death65_per_100k65"] = m["death_65p_2y"] / 2 / m["pop_65p"] * 1e5
    m["share_acc_by65"] = m["acc_65p"] / m["acc_total"]
    m["ev_per_1k_car"] = m["ev_car_nonbusiness"] / m["car_nonbusiness"] * 1000
    m["capital"] = m["sido_2025"].isin(["11", "28", "41"])
    m["metro"] = m["sido_2025"].isin(["11", "26", "27", "28", "29", "30", "31"])
    m["gun"] = m["unit_nm"].str.endswith("군")
    m["pop_density"] = m["pop"] / m["area_km2"]
    m["tsbis_share_routes_le2"] = m["n_routes_weekday_le2"] / m["n_routes_weekday_service"]
    m["tsbis_runs_per_1k"] = m["weekday_runs_total"] / m["pop"] * 1000

    # 자료 결함 플래그: 버스정류장 밀도가 동급 대비 비정상적으로 낮은 단위(정류장 원자료 누락 의심)
    bus = pd.read_parquet(PROC / "bus_stops.parquet")
    import geopandas as gpd
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")
    pts = gpd.GeoDataFrame(bus, geometry=gpd.points_from_xy(bus.lon, bus.lat), crs=4326)
    m["n_bus_stops"] = gpd.sjoin(pts, adm[["unit", "geometry"]], predicate="within").groupby("unit").size()
    m["stops_per_1k"] = m["n_bus_stops"] / m["pop"] * 1000
    # 정류장 원자료 완결성 점검: 주민의 10% 이상이 가장 가까운 정류장에서 2km 넘게 떨어진 시군(전국 중앙값 0.1%)
    #   → 도서, 산간의 실제 공백과 정류장 원자료 누락이 섞여 있어 시군구 비교, 모델, 우선순위 목록에서 제외
    hx = pd.read_parquet(PROC / "hex_access.parquet", columns=["unit", "pop", "d_bus_m"])
    far2 = (hx["pop"] * (hx["d_bus_m"] > 2000)).groupby(hx["unit"]).sum() / hx.groupby("unit")["pop"].sum()
    m["share_far2km"] = far2
    m["flag_stop_data"] = m["share_far2km"] > 0.10
    # 등록지 왜곡(리스, 법인 차량이 특정 주소지에 집중) 의심: 성인 1천명당 자가용 승용차가 Q3+3, IQR 초과
    q1, q3 = m["cars_per_1k_adult"].quantile([0.25, 0.75])
    m["flag_reg_outlier"] = m["cars_per_1k_adult"] > q3 + 3 * (q3 - q1)
    m.to_csv(PROC / "master_units.csv", encoding="utf-8-sig")
    print(f"마스터 테이블 {m.shape}, 정류장 자료 결함 의심 {int(m['flag_stop_data'].sum())}곳:",
          m.index[m["flag_stop_data"]].map(m["unit_nm"]).tolist(),
          "/ 등록지 왜곡 의심:", m.index[m["flag_reg_outlier"]].map(m["unit_nm"]).tolist())
    miss = m.isna().sum()
    print("결측 있는 열:\n", miss[miss > 0].to_string())


if __name__ == "__main__":
    main()
