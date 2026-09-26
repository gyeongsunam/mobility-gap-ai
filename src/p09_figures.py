"""09. 보고서 그림(인쇄용 300dpi PNG)

F1 전국 400m 격자 '자동차 필수 거주 인구' 지도 + 시도별 비율
F2 전남광주통합특별시 확대: 하나의 특별시, 두 개의 이동권
F3 필요 vs 혜택: 모두의 카드 지역유형별 자동차 필수 거주 비율과 1인당 환급액, 시도 산점도
F4 자동차 필수 거주 5분위별 결과(1인당 승용차 CO2, 대중교통 통근, 고령운전자 사고 사망)
F5 AI 해석: 대중교통 통근분담 모델 SHAP 요약
F6 유형화 4종 소형 다중지도 + 특성 요약
"""
import json

import geopandas as gpd
import h3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from matplotlib.collections import PolyCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import viz_style as vs
from config import PROC, TAB, FIG

vs.setup()
TYPE_NAMES = {}   # p07 결과로 채움


def hex_polys(cells):
    return [np.array([(lng, lat) for lat, lng in h3.cell_to_boundary(c)]) for c in cells]


def sido_boundaries():
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")
    s = adm.dissolve(by="sidonm")[["geometry"]].reset_index()
    s["geometry"] = s.geometry.simplify(0.002)
    return s


def draw_hexes(ax, hx, values, bins, colors, zero_color=None):
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bins, cmap.N)
    polys = hex_polys(hx["h3"].tolist())
    fc = cmap(norm(values))
    if zero_color is not None:
        fc[values < bins[0]] = mpl_color(zero_color)
    pc = PolyCollection(polys, facecolors=fc, edgecolors="none", linewidths=0)
    ax.add_collection(pc)


def mpl_color(c):
    from matplotlib.colors import to_rgba
    return to_rgba(c)


def base_ax(ax, extent):
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
    ax.set_aspect(1 / np.cos(np.radians((extent[2] + extent[3]) / 2)))
    ax.axis("off")


# ------------------------------------------------------------------ F1
def unique_hex(hx):
    u = hx.groupby("h3", as_index=False).agg(pop=("pop", "sum"), pop_car_ess=("pop_car_ess", "sum"),
                                             pop_65p_car_ess=("pop_65p_car_ess", "sum"), unit=("unit", "first"))
    u["car_ess_share"] = np.where(u["pop"] > 0, u["pop_car_ess"] / u["pop"], 0)
    return u


SIDO25 = {"11": "서울", "26": "부산", "27": "대구", "28": "인천", "29": "광주", "30": "대전", "31": "울산",
          "36": "세종", "41": "경기", "43": "충북", "44": "충남", "46": "전남", "47": "경북", "48": "경남",
          "50": "제주", "51": "강원", "52": "전북"}
_M = pd.read_csv(PROC / "master_units.csv", dtype={"unit": str})
FLAG_UNITS = _M.loc[_M["flag_stop_data"], "unit"].tolist()   # 정류장 원자료 확인 필요 시군(지도에서 빗금 처리)


def draw_flagged(ax, hu):
    f = hu[hu["unit"].isin(FLAG_UNITS)]
    if len(f):
        pc = PolyCollection(hex_polys(f["h3"].tolist()), facecolors="#e4e3de", edgecolors="#9c9b96",
                            linewidths=0.0, hatch="////")
        ax.add_collection(pc)


def count_map(ax, hu, col, bins, labels_zero):
    v = hu[col].to_numpy()
    ok = ~hu["unit"].isin(FLAG_UNITS).to_numpy()
    low = (v < bins[0]) & ok
    draw_hexes(ax, hu[low], np.zeros(low.sum()), [-1, 1e9], [vs.ZERO])
    hi = (v >= bins[0]) & ok
    draw_hexes(ax, hu[hi], v[hi], bins, vs.BURDEN_5)
    draw_flagged(ax, hu)


def fig1_national(hx, sido, head):
    hu = unique_hex(hx)
    fig = plt.figure(figsize=(7.2, 4.15))
    ax = fig.add_axes([0.0, 0.0, 0.60, 1.0])
    bins = [10, 30, 100, 300, 1000, 1e9]
    count_map(ax, hu, "pop_car_ess", bins, True)
    sido.boundary.plot(ax=ax, color="#8a8984", linewidth=0.35)
    base_ax(ax, (124.55, 131.0, 33.05, 38.65))
    handles = [Patch(color=vs.ZERO, label="10명 미만(없음 포함)")] + \
        [Patch(color=c, label=l) for c, l in zip(vs.BURDEN_5, ["10~30명", "30~100명", "100~300명", "300~1,000명",
                                                                "1,000명 이상"])] + \
        [Patch(facecolor="#e4e3de", edgecolor="#9c9b96", hatch="////", label="정류장 원자료 확인 필요 시군")]
    ax.legend(handles=handles, loc="lower right", fontsize=6.4, title="격자(0.74㎢)당 자동차 필수 거주 인구",
              title_fontsize=6.7, handlelength=1.1, borderaxespad=0.2)
    # 시도별(2025 시도 체계: 광주와 전남 구분) 막대
    bx = fig.add_axes([0.69, 0.10, 0.29, 0.84])
    hx = hx.assign(sd=hx["unit"].str[:2])
    s = hx.groupby("sd").agg(pop=("pop", "sum"), car=("pop_car_ess", "sum"))
    s["share"] = s["car"] / s["pop"] * 100
    s = s.sort_values("share")
    y = np.arange(len(s))
    bx.barh(y, s["share"], color=vs.BURDEN, height=0.64)
    for i, (sh, c) in enumerate(zip(s["share"], s["car"])):
        bx.text(sh + 0.3, i, f"{sh:.1f}% ({c/1e4:.0f}만)", va="center", fontsize=6.4, color=vs.INK2)
    bx.set_yticks(y, [SIDO25[i] for i in s.index], fontsize=7)
    bx.set_xlim(0, s["share"].max() * 1.6)
    bx.set_xlabel("인구 대비 자동차 필수 거주 비율(%)", fontsize=7)
    bx.grid(axis="y", visible=False)
    bx.set_title("시도별(괄호: 인원)", fontsize=8.2, loc="left")
    fig.savefig(FIG / "F1_national_car_essential.png")
    plt.close(fig)


# ------------------------------------------------------------------ F2
def fig2_jeonnam_gwangju(hx, adm):
    sub = unique_hex(hx[hx["unit"].str[:2].isin(["29", "46"])])
    a = adm[adm["sidonm"] == "전남광주통합특별시"]
    gj = a[a["sgg"].isin(["12210", "12240", "12270", "12300", "12330"])].dissolve()
    sg = a.dissolve(by="sggnm")[["geometry"]].reset_index()
    fig, ax = plt.subplots(figsize=(4.6, 4.1))
    count_map(ax, sub, "pop_car_ess", [10, 30, 100, 300, 1000, 1e9], True)
    sg.boundary.plot(ax=ax, color="#a9a8a2", linewidth=0.3)
    gj.boundary.plot(ax=ax, color=vs.BLUE, linewidth=1.2)
    for nm, (la, lo) in {"광주": (35.16, 126.85), "목포": (34.80, 126.40), "순천": (34.95, 127.49),
                         "여수": (34.76, 127.66), "나주": (35.02, 126.71), "고흥": (34.61, 127.28)}.items():
        ax.text(lo, la, nm, fontsize=7, fontweight="bold", color=vs.INK, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
    b = a.total_bounds
    base_ax(ax, (b[0] - 0.02, b[2] + 0.02, b[1] - 0.02, b[3] + 0.02))
    handles = [Patch(color=vs.ZERO, label="10명 미만")] + [Patch(color=c, label=l) for c, l in
                zip(vs.BURDEN_5, ["10~30명", "30~100명", "100~300명", "300~1,000명", "1,000명+"])]
    handles += [Patch(facecolor="#e4e3de", edgecolor="#9c9b96", hatch="////", label="정류장 자료 확인 필요"),
                Line2D([0], [0], color=vs.BLUE, lw=1.2, label="(구)광주광역시")]
    ax.legend(handles=handles, loc="lower left", fontsize=6.1, title="격자당 자동차 필수 거주 인구",
              title_fontsize=6.4, handlelength=1.1)
    fig.savefig(FIG / "F2_jeonnam_gwangju.png")
    plt.close(fig)


# ------------------------------------------------------------------ F3
def fig3_need_vs_benefit(inc):
    g = pd.DataFrame(inc["modu_regiontype"]).T.loc[["수도권", "일반지방권", "우대지원지역", "특별지원지역"]]
    s = pd.read_csv(TAB / "kpass_sido_vs_access.csv", dtype={"sido_2025": str})
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.2), gridspec_kw={"width_ratios": [1, 1, 1.25]})
    x = np.arange(4)
    lab = ["수도권", "일반\n지방권", "우대\n지원지역", "특별\n지원지역"]
    ax = axes[0]
    ax.bar(x, g["share_car_ess"] * 100, color=vs.BURDEN, width=0.62)
    for i, v in enumerate(g["share_car_ess"] * 100):
        ax.text(i, v + 0.4, f"{v:.1f}%", ha="center", fontsize=7.2, color=vs.INK)
    ax.set_xticks(x, lab, fontsize=7); ax.set_title("필요: 자동차 필수 거주 비율", fontsize=8.5, loc="left")
    ax.set_ylim(0, 25); ax.grid(axis="x", visible=False)
    ax = axes[1]
    vals = g["refund_per_capita_year_krw"].to_numpy(dtype=float)
    cols = [vs.BLUE, vs.BLUE, vs.GRAY, vs.BLUE]
    ax.bar(x, vals / 1000, color=cols, width=0.62)
    for i, v in enumerate(vals / 1000):
        ax.text(i, v + 0.4, f"{v:,.1f}천원" if i != 2 else f"{v:,.1f}천원*", ha="center", fontsize=7.2, color=vs.INK)
    ax.set_xticks(x, lab, fontsize=7); ax.set_title("혜택: 주민 1인당 연 환급액", fontsize=8.5, loc="left")
    ax.set_ylim(0, 25); ax.grid(axis="x", visible=False)
    ax = axes[2]
    s = s.dropna(subset=["members_per_100"])
    ax.scatter(s["share_car_ess"] * 100, s["members_per_100"], s=s["pop"] / 6e4, color=vs.BLUE, alpha=0.75,
               edgecolor="white", linewidth=0.6, zorder=3)
    for _, r in s.iterrows():
        nm = str(r["sidonm"]).replace("특별자치도", "").replace("특별자치시", "").replace("광역시", "") \
            .replace("특별시", "").replace("경기도", "경기").replace("충청북도", "충북").replace("충청남도", "충남") \
            .replace("경상북도", "경북").replace("경상남도", "경남").replace("전라남도", "전남")
        ax.annotate(nm, (r["share_car_ess"] * 100, r["members_per_100"]), fontsize=6.2, color=vs.INK2,
                    xytext=(3, 2), textcoords="offset points")
    rho = inc["kpass_sido_spearman"]["members"]
    ax.set_xlabel("자동차 필수 거주 비율(%)", fontsize=7); ax.set_ylabel("주민 100명당 가입자(명)", fontsize=7)
    ax.set_title(f"시도별 자동차 필수 비율과 가입률(ρ={rho:.2f})".replace("-", "−"), fontsize=8.5, loc="left")
    fig.tight_layout(w_pad=1.2)
    vs.note(axes[1], "* 우대지원지역 원자료는 환급대상자>가입자로 불일치(참고값). 환급액=2026년 1분기×4, 인구 2026.8", y=-0.28)
    fig.savefig(FIG / "F3_need_vs_benefit.png")
    plt.close(fig)


# ------------------------------------------------------------------ F4
def fig4_quintiles(inc):
    q = pd.DataFrame(inc["quintiles"]).T
    q.index = q.index.astype(int)
    q = q.sort_index()
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 1.95))
    specs = [("co2_pc_t", "1인당 승용차 CO₂(t/년)", "{:.2f}"),
             ("transit_commute", "대중교통 통근통학 분담률(%)", "{:.0%}"),
             ("death65_per_100k65", "고령운전자 사고 사망(65세+ 10만명당/년)", "{:.1f}")]
    x = np.arange(1, 6)
    for ax, (col, title, fmt) in zip(axes, specs):
        v = q[col].to_numpy(dtype=float)
        col_bar = vs.BURDEN_5                      # 분위 = 자동차 필수 비율의 크기(서수형)
        ax.bar(x, v, color=col_bar, width=0.66)
        for xi, vi in zip(x, v):
            ax.text(xi, vi * 1.02, fmt.format(vi), ha="center", va="bottom", fontsize=6.8, color=vs.INK)
        ax.set_xticks(x, ["1분위\n(낮음)", "2", "3", "4", "5분위\n(높음)"], fontsize=6.8)
        ax.set_title(title, fontsize=8, loc="left")
        ax.set_ylim(0, v.max() * 1.22)
        ax.grid(axis="x", visible=False)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    axes[0].set_xlabel("시군구 자동차 필수 거주 비율 5분위(인구 각 약 1천만 명)", fontsize=6.8, loc="left")
    fig.tight_layout(w_pad=1.0)
    fig.savefig(FIG / "F4_quintile_outcomes.png")
    plt.close(fig)


# ------------------------------------------------------------------ F5
def fig5_shap():
    models = pd.read_pickle(PROC / "shap_models.pkl")
    model, X, sv = models["share_transit_commute"]
    lab = {"share_car_ess": "자동차 필수 거주 비율", "log_density": "체감 인구밀도(log)", "share_65p": "65세 이상 비율",
           "wage_per_filer_mn": "1인당 근로소득", "nbls_rate": "기초수급 비율", "fiscal_indep": "재정자립도",
           "capital": "수도권", "pw_cov_rail": "철도역 보행권 인구 비율"}
    keep = [c for c in X.columns if c != "capital"]
    Xl = X[keep].rename(columns=lab)
    sv = sv[:, [list(X.columns).index(c) for c in keep]]
    plt.figure(figsize=(4.6, 2.45))
    shap.summary_plot(sv * 100, Xl, show=False, plot_size=None, color_bar_label="변수값",
                      max_display=7, cmap=vs.CMAP_ACCESS)
    fig = plt.gcf()
    ax = fig.axes[0]
    ax.set_xlabel("SHAP 값: 대중교통 통근분담률 예측 기여(%p)", fontsize=7.5)
    ax.tick_params(labelsize=7)
    cb = fig.axes[-1]
    cb.set_yticks(cb.get_yticks()[[0, -1]] if len(cb.get_yticks()) > 1 else cb.get_yticks())
    cb.set_yticklabels(["낮음", "높음"], fontsize=7)
    cb.set_ylabel("변수값", fontsize=7)
    plt.tight_layout()
    plt.savefig(FIG / "F5_shap_transit.png")
    plt.close()


# ------------------------------------------------------------------ F6
def fig6_typology(hx, sido):
    t = pd.read_csv(TAB / "typology_admdong.csv", dtype={"adm_cd2": str})
    meta = json.load(open(TAB / "typology_meta.json"))
    names = meta.get("names", {})
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")[["adm_cd2", "geometry"]]
    adm["adm_cd2"] = adm["adm_cd2"].astype(str)
    g = adm.merge(t[["adm_cd2", "cluster"]], on="adm_cd2")
    g["geometry"] = g.geometry.simplify(0.001)
    order = meta.get("order", sorted(t["cluster"].unique()))
    cols = [vs.BURDEN] * 4                      # 작은 배수 지도: 유형은 패널 제목이 구분
    fig, axes = plt.subplots(1, 4, figsize=(7.4, 2.9))
    for ax, c, col in zip(axes, order, cols):
        sido.boundary.plot(ax=ax, color="#c9c8c2", linewidth=0.3)
        g[g["cluster"] == c].plot(ax=ax, color=col, linewidth=0)
        base_ax(ax, (124.55, 131.0, 33.05, 38.65))
        prof = t[t["cluster"] == c]
        ax.set_title(names.get(str(c), f"유형 {c}"), fontsize=7.8, loc="left")
        ax.text(0.0, -0.02, f"{len(prof)}개 읍면동\n자동차 필수 {prof['pop_car_ess'].sum()/1e4:.0f}만 명"
                            f"(65+ {prof['pop_65p_car_ess'].sum()/1e4:.0f}만)",
                transform=ax.transAxes, va="top", fontsize=6.6, color=vs.INK2)
    fig.subplots_adjust(wspace=0.05, bottom=0.14)
    fig.savefig(FIG / "F6_typology.png")
    plt.close(fig)


# ------------------------------------------------------------------ F7
def fig7_info_map(hx, sido):
    hu = unique_hex(hx)
    fig, ax = plt.subplots(figsize=(3.6, 4.6))
    count_map(ax, hu, "pop_65p_car_ess", [5, 10, 30, 100, 300, 1e9], True)
    sido.boundary.plot(ax=ax, color="#8a8984", linewidth=0.3)
    base_ax(ax, (124.55, 131.0, 33.05, 38.65))
    handles = [Patch(color=c, label=l) for c, l in zip(vs.BURDEN_5, ["5~10", "10~30", "30~100", "100~300", "300+"])]
    ax.legend(handles=handles, loc="lower right", fontsize=5.8, title="격자당 65세+\n자동차 필수 거주(명)",
              title_fontsize=6, handlelength=1.0, borderaxespad=0.1)
    fig.savefig(FIG / "F7_infographic_map.png")
    plt.close(fig)


# ------------------------------------------------------------------ F8
def fig8_info_bars(inc):
    g = pd.DataFrame(inc["modu_regiontype"]).T.loc[["수도권", "일반지방권", "특별지원지역"]]
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 1.45))
    lab = ["수도권", "일반지방", "특별지원"]
    y = np.arange(3)[::-1]
    for ax, col, color, fmt, title in [
        (axes[0], g["share_car_ess"] * 100, vs.BURDEN, "{:.1f}%", "필요: 자동차 필수"),
        (axes[1], g["refund_per_capita_year_krw"].astype(float) / 1000, vs.BLUE, "{:.1f}천원", "혜택: 1인당 환급")]:
        v = col.to_numpy(dtype=float)
        ax.barh(y, v, color=color, height=0.62)
        for yi, vi in zip(y, v):
            ax.text(vi + v.max() * 0.03, yi, fmt.format(vi), va="center", fontsize=6.3, color=vs.INK)
        ax.set_yticks(y, lab, fontsize=6.3)
        ax.set_xlim(0, v.max() * 1.55)
        ax.set_xticks([]); ax.grid(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_title(title, fontsize=7, loc="left")
    axes[1].set_yticks(y, [""] * 3)
    fig.tight_layout(w_pad=0.6)
    fig.savefig(FIG / "F8_info_bars.png")
    plt.close(fig)


def main():
    hx = pd.read_parquet(PROC / "hex_access.parquet")
    inc = json.load(open(TAB / "incidence_summary.json"))
    sido = sido_boundaries()
    adm = gpd.read_file(PROC / "admdong_2026.gpkg")
    fig1_national(hx, sido, inc["headline"])
    fig2_jeonnam_gwangju(hx, adm)
    fig3_need_vs_benefit(inc)
    fig4_quintiles(inc)
    fig5_shap()
    fig6_typology(hx, sido)
    fig7_info_map(hx, sido)
    fig8_info_bars(inc)
    print("그림 저장:", sorted(p.name for p in FIG.glob("F*.png")))


if __name__ == "__main__":
    main()
