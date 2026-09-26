"""보고서 빌드: 분석 산출물(JSON/CSV) → 수치 사전 N → HTML(Jinja2) → PDF(Chrome)

사용법:  python report/build_report.py
출력:    report/report.html, report/build/ 아래 분석보고서 PDF
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader

REPORT = Path(__file__).resolve().parent
ROOT = REPORT.parent
TAB = ROOT / "outputs" / "tables"
PROC = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "src"))


def man(x, d=0):
    """명 → 만 명 문자열."""
    v = x / 1e4
    return f"{v:,.{d}f}"


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


def load():
    J = lambda f: json.load(open(TAB / f))
    return (J("incidence_summary.json"), J("model_summary.json"), J("typology_meta.json"), J("policy_summary.json"))


def build_numbers():
    inc, mod, typ, pol = load()
    h = inc["headline"]
    N = {}
    hx = pd.read_parquet(PROC / "hex_access.parquet")
    N["n_hex_man"] = man(hx["h3"].nunique(), 1)
    N["car_man"] = man(h["pop_car_ess"])
    N["car65_man"] = man(h["pop65_car_ess"])
    N["car65_half"] = man(h["pop65_car_ess"] / 2)
    N["uncov_man"] = man(h["pop_uncov"])
    N["uncov_pct"] = pct(h["pop_uncov"] / h["pop_total"])
    N["car_pct"] = pct(h["share_car_ess"])
    N["car65_pct"] = pct(h["share65_car_ess"])
    al = pd.read_csv(TAB / "sensitivity_allocation.csv")
    N["car_range"] = f"{man(al['pop_car_ess'].min())}~{man(al['pop_car_ess'].max())}"
    ws = pd.read_csv(TAB / "sensitivity_walk_threshold.csv").set_index("walk_threshold_m")
    N["walk_range"] = f"{man(ws.loc[1200, 'pop_car_ess'])}~{man(ws.loc[800, 'pop_car_ess'])}"
    cs = pd.read_csv(TAB / "sensitivity_circuity.csv").set_index("circuity")
    N["circ_range"] = f"{cs['share_pop_uncov'].min()*100:.1f}~{cs['share_pop_uncov'].max()*100:.1f}%"
    N["car_kon_man"] = man(4133855)          # 첫 계산(Kontur 가중, 격자중심 배정, 동=400m 일괄) 결과. 검증 후 교체
    N["iso_man"] = man(inc["isolation"]["pop75_car_ess_no_license"])
    bus = pd.read_parquet(PROC / "bus_stops.parquet")
    N["n_stops_man"] = man(len(bus), 1)
    fac = pd.read_parquet(PROC / "facilities.parquet")
    N["n_imputed"] = f"{int(fac['imputed'].sum()):,}"
    N["n_fac_man"] = man(len(fac), 1)
    pv = pd.read_csv(TAB / "population_grid_validation.csv").set_index("source")
    g, k = pv.loc["GHS-POP 2025", "median_abs_log_err"], pv.loc["Kontur 2023", "median_abs_log_err"]
    N["pop_err_ghs"], N["pop_err_kon"], N["pop_err_gain"] = f"{g:.2f}", f"{k:.2f}", f"{(1 - g / k) * 100:.0f}"
    iv = pd.read_csv(TAB / "imputation_validation.csv")
    N["imp_err_lo"] = f"{iv['pop_weighted_mean_abs_err_m'].min():.0f}"
    N["imp_err_hi"] = f"{iv['pop_weighted_mean_abs_err_m'].max():.0f}"

    # 시도
    hx["sido_2025"] = hx["unit"].str[:2]
    s = hx.groupby("sido_2025").agg(pop=("pop", "sum"), car=("pop_car_ess", "sum"))
    s["share"] = s["car"] / s["pop"]
    names = {"50": "제주", "46": "전남", "51": "강원", "47": "경북", "44": "충남", "48": "경남", "43": "충북",
             "31": "울산", "52": "전북", "11": "서울"}
    top = s.sort_values("share", ascending=False).head(3)
    N["top3"] = ", ".join(f"{names.get(i, i)}({pct(v)})" for i, v in top["share"].items())
    N["seoul_pct"] = pct(s.loc["11", "share"])
    N["jeju_pct"] = pct(s.loc["50", "share"])
    N["gj_pct"] = pct(s.loc["29", "share"]); N["jn_pct"] = pct(s.loc["46", "share"])
    N["jn65_man"] = man(hx.loc[hx["sido_2025"] == "46", "pop_65p_car_ess"].sum(), 1)
    ad = pd.read_csv(PROC / "admdong_access.csv")
    N["jm_pct"] = pct(ad.loc[ad["adm_nm"] == "경기도 연천군 중면", "share_car_ess"].iloc[0], 0)   # 한겨레 현장 기사(삼곶리) 대조
    k = pd.read_csv(ROOT / "data" / "raw" / "kotsa_ptc2025" / "kotsa_minservice_sido_2025.csv",
                    dtype={"sido_2025": str}).set_index("sido_2025").fillna(0)
    k["short"] = (k.dong_short + k.ri_short) / (k.dong_secured + k.dong_short + k.ri_secured + k.ri_short)
    d = s.join(k["short"])
    N["kotsa_rho_ex"] = f"{d.drop('50')[['share', 'short']].corr('spearman').iloc[0, 1]:.2f}"
    N["kotsa_rho_all"] = f"{d[['share', 'short']].corr('spearman').iloc[0, 1]:.2f}"

    # TS-BIS
    ts = inc["tsbis"]
    N["ts_n"], N["ts_med"], N["ts_le2"] = f"{ts['n_routes_weekday']:,}", f"{ts['median_runs']:.0f}", pct(ts["share_le2"])

    # 5분위
    q = pd.read_csv(TAB / "quintile_outcomes.csv", index_col=0)
    N["q1_co2"], N["q5_co2"] = f"{q.loc[1, 'co2_pc_t']:.2f}", f"{q.loc[5, 'co2_pc_t']:.2f}"
    N["co2_ratio"] = f"{q.loc[5, 'co2_pc_t'] / q.loc[1, 'co2_pc_t']:.1f}"
    N["q1_death"], N["q5_death"] = f"{q.loc[1, 'death65_per_100k65']:.1f}", f"{q.loc[5, 'death65_per_100k65']:.1f}"
    N["death_ratio"] = f"{q.loc[5, 'death65_per_100k65'] / q.loc[1, 'death65_per_100k65']:.1f}"
    N["q1_transit"], N["q5_transit"] = pct(q.loc[1, "transit_commute"], 0), pct(q.loc[5, "transit_commute"], 0)
    N["ev_q1"], N["ev_q5"] = f"{q.loc[1, 'ev_per_1k_car']:.0f}", f"{q.loc[5, 'ev_per_1k_car']:.0f}"
    N["top2_pop_man"] = man(pol["p3c"]["top2q_pop"])
    N["excess_mt"] = f"{pol['p3c']['excess_mt'] * 100:,.0f}"       # 백만 t → 만 t
    N["excess_share"] = pct(pol["p3c"]["excess_mt"] / 94.59)        # 2025 수송 잠정배출 9,459만 t 대비

    # 모두의 카드
    g = pd.DataFrame(inc["modu_regiontype"]).T
    cap, sp = g.loc["수도권"], g.loc["특별지원지역"]
    N["cap_need"], N["sp_need"] = pct(cap["share_car_ess"]), pct(sp["share_car_ess"])
    N["sp_need_ratio"] = f"{sp['share_car_ess'] / cap['share_car_ess']:.1f}"
    N["cap_mem"], N["sp_mem"] = f"{cap['members_per_100']:.1f}", f"{sp['members_per_100']:.2f}"
    N["cap_ref"], N["sp_ref"] = f"{cap['refund_per_capita_year_krw']:,.0f}", f"{sp['refund_per_capita_year_krw']:,.0f}"
    N["ref_gap"] = f"{cap['refund_per_capita_year_krw'] / sp['refund_per_capita_year_krw']:.0f}"
    N["rho_mem"] = f"{inc['kpass_sido_spearman']['members']:.2f}".replace("-", "−")

    # 모델
    N["r2_transit"] = f"{mod['shap']['share_transit_commute']['cv_r2_spatial_gbm']:.2f}"
    N["r2_vkt"] = f"{mod['shap']['vkt_pc']['cv_r2_spatial_gbm']:.2f}"
    imp = mod["shap"]["share_transit_commute"]["shap_importance"]
    order = list(imp)
    N["shap_top"] = ", ".join(order[:3])
    N["shap_income_rank"] = str(order.index("1인당 근로소득") + 1)
    dv = mod["dml"]["vkt_pc"]
    N["dml_vkt"] = f"{dv['theta']:,.0f}"
    N["dml_vkt_ci"] = f"{dv['ci_low']:,.0f}~{dv['ci_high']:,.0f}".replace("-", "−")
    ie = pd.read_csv(TAB / "income_car_elasticity.csv").set_index("spec")
    N["ie_hi"] = f"{ie.loc['A_none', 'elasticity_car_ess_top3']:.2f}"
    N["ie_lo"] = f"{abs(ie.loc['A_none', 'elasticity_others']):.2f}"
    N["ie_p"], N["ie_p_ctrl"] = f"{ie.loc['A_none', 'p_diff']:.3f}", f"{ie.loc['B_density_aging', 'p_diff']:.2f}"
    N["bike_man"] = man(h["pop_car_ess_bikeable"])
    N["bike_pct"] = pct(h["pop_car_ess_bikeable"] / h["pop_car_ess"], 0)

    # 유형
    N["n_target_dong"] = f"{typ['n_target_dong']:,}"
    N["cover300"] = pct(typ["cover_top_n"]["300"], 0)
    prof = pd.read_csv(TAB / "typology_profile.csv", index_col=0)
    rx = {"초고령 산간 오지형": "예약형(택시) DRT와 찾아가는 의료, 장보기(서비스가 사람에게)",
          "농촌 생활권 외곽형": "소재지 순환 DRT, 3km 안전 자전거길과 전기자전거",
          "도시 외곽 도농복합형": "마을버스 신설과 증편, 도시형 DRT, 보행로 연결",
          "역세권 라스트마일형": "역 연계 수요응답 셔틀, 공공자전거와 환승할인"}
    N["types"] = []
    for c in typ["order"]:
        r = prof.loc[c]
        N["types"].append({"name": r["name"], "n": int(r["n"]), "car": man(r["pop_car_ess"], 1),
                           "car65": man(r["pop65_car_ess"], 1), "old": pct(r["share_65p"], 0),
                           "dpc": f"{r['d_pc'] / 1000:.1f}", "dshop": f"{r['d_shop'] / 1000:.1f}", "rx": rx[r["name"]]})
    t = pd.read_csv(TAB / "typology_admdong.csv", dtype={"unit": str})
    jn = t[(t["unit"].str[:2] == "46") & t["adm_nm"].str.contains(r"[읍면]$")].head(3)
    N["jn_top"] = ", ".join(jn["adm_nm"].str.replace("전남광주통합특별시 ", "", regex=False).tolist())
    m = pd.read_csv(PROC / "master_units.csv", dtype={"unit": str})
    fl = m[m["flag_stop_data"]].sort_values("share_far2km", ascending=False)
    N["flag_units"] = ", ".join(fl["unit_nm"].str.split().str[-1].str.replace(r"(군|시)$", "", regex=True))
    N["n_flag"] = str(len(fl))
    N["flag_pop_car"] = man(hx.loc[hx["unit"].isin(fl["unit"]), "pop_car_ess"].sum())

    # 정책
    p1 = pol["p1"]
    N["p1_t1"] = f"{p1['tier1_cost_eok']:,.0f}"
    N["p1_t2"] = f"{p1['tier2_cost_eok_50pct']:,.0f}"
    N["p1_t1_share"] = pct(p1["tier1_cost_eok"] / 3072, 0)
    N["p1_t2_share"] = pct(p1["tier2_cost_eok_50pct"] / 3072, 0)
    N["sp_after"] = f"{round(p1['special_after'], -2):,.0f}"
    N["gap_after"] = f"{p1['gap_after']:.1f}"
    b = pol["p3b"]
    N["bike_co2"] = f"{b['co2_kt_10pct']:.0f}~{b['co2_kt_20pct']:.0f}"
    a = pol["p3a"]
    N["lic_man"] = man(a["holders_75p_car_ess"], 1)
    N["ret"] = f"{a['extra_returns_per_year']:,.0f}"
    N["crash"] = f"{a['crashes_avoided']:,.0f}"
    N["cost"] = f"{a['social_cost_saved_eok']:,.0f}"
    N["ret_co2"] = f"{a['co2_kt_if_scrapped']:.1f}"
    return N


def render(team, repo_url):
    N = build_numbers()
    env = Environment(loader=FileSystemLoader(str(REPORT)), autoescape=False)
    html = env.get_template("template.html.j2").render(N=N, team=team, repo_url=repo_url)
    out = REPORT / "report.html"          # 상대경로(style.css, fonts/, assets/, ../outputs) 유지를 위해 report/에 둠
    out.write_text(html, encoding="utf-8")
    json.dump(N, open(REPORT / "build_numbers.json", "w"), ensure_ascii=False, indent=1)
    return out


def to_pdf(html_path, pdf_path):
    from playwright.sync_api import sync_playwright
    footer = ('<div style="width:100%;font-size:8px;color:#555;text-align:center;font-family:sans-serif;">'
              '- <span class="pageNumber"></span> -</div>')
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        pg = br.new_page()
        pg.goto(html_path.as_uri(), wait_until="networkidle")
        pg.pdf(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True,
               display_header_footer=True, header_template="<div></div>", footer_template=footer,
               margin={"top": "13mm", "bottom": "14mm", "left": "14mm", "right": "14mm"})
        br.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", default="모두의이동")
    ap.add_argument("--repo-url", default="https://github.com/gyeongsunam/mobility-gap-ai")
    args = ap.parse_args()
    html = render(args.team, args.repo_url)
    pdf = REPORT / "build" / f"{args.team}_분석보고서.pdf"
    pdf.parent.mkdir(exist_ok=True)
    to_pdf(html, pdf)
    import fitz
    print(f"PDF: {pdf} ({fitz.open(pdf).page_count}쪽)")


if __name__ == "__main__":
    main()
