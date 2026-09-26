"""01. 행정경계, 인구 기초자료 구축

- 행정동 경계(2026.7 기준, SGIS 원자료/vuski 가공)와 주민등록 인구(2026.8, 행정동, 성, 연령)를 결합
- 출장소 인구는 모(母) 읍면에 합산
- 2026년 행정구역 개편(전남광주통합특별시, 인천 제물포, 영종, 서해, 검단구, 화성시 일반구)을
  2025년 통계와 연결하기 위한 '분석 시군구(unit)' 코드 체계를 만든다., 일반구는 시로 통합, 인천 중구, 동구(→제물포, 영종구)는 하나의 단위로 통합, 전남광주통합특별시 시군구는 2025년 광주(29), 전남(46) 코드로 역매핑
"""
import glob
import re

import geopandas as gpd
import numpy as np
import pandas as pd

from config import RAW, PROC, BOUNDARY_2026

OLD_GWANGJU = {"동구": "29110", "서구": "29140", "남구": "29155", "북구": "29170", "광산구": "29200"}
OLD_JEONNAM = {"목포시": "46110", "여수시": "46130", "순천시": "46150", "나주시": "46170", "광양시": "46230",
               "담양군": "46710", "곡성군": "46720", "구례군": "46730", "고흥군": "46770", "보성군": "46780",
               "화순군": "46790", "장흥군": "46800", "강진군": "46810", "해남군": "46820", "영암군": "46830",
               "무안군": "46840", "함평군": "46860", "영광군": "46870", "장성군": "46880", "완도군": "46890",
               "진도군": "46900", "신안군": "46910"}
SIDO_OLD_NAME = {"29": "광주광역시", "46": "전라남도"}


def unit_code(sgg: str, sggnm: str) -> str:
    """2026 시군구 코드 → 분석 단위(2025 기준, 일반구는 시로 통합) 코드."""
    if sgg.startswith("12"):
        if sggnm in OLD_GWANGJU:
            return OLD_GWANGJU[sggnm]
        return OLD_JEONNAM[sggnm]
    if sgg in ("28125", "28155", "28110", "28140"):
        return "28110"          # 인천 중구+동구(=2026 제물포구+영종구)
    if sgg in ("28275", "28290"):
        return "28260"          # 인천 서구(=2026 서해구+검단구)
    # 일반구(시 아래 구): 시군구명에 '시'와 '구'가 함께 있는 경우 → 시 코드(4자리+0)
    if re.match(r"^.+시.+구$", sggnm):
        return sgg[:4] + "0"
    return sgg


def unit_name(row) -> str:
    sido = row["sidonm_2025"]
    nm = row["sggnm"]
    m = re.match(r"^(.+시).+구$", nm)
    if m:
        nm = m.group(1)
    if row["unit"] == "28110":
        nm = "중구·동구"
    if row["unit"] == "28260":
        nm = "서구"
    return f"{sido} {nm}"


def load_boundary() -> gpd.GeoDataFrame:
    g = gpd.read_file(BOUNDARY_2026)
    g["adm_cd2"] = g["adm_cd2"].astype(str)
    g["emd"] = g["adm_nm"].str.split().str[-1]
    g["urban"] = g["emd"].str.endswith("동") & ~g["emd"].str.endswith(("읍", "면"))
    g["unit"] = [unit_code(s, n) for s, n in zip(g["sgg"], g["sggnm"])]
    g["sido_2025"] = g["unit"].str[:2]
    g["sidonm_2025"] = g.apply(lambda r: SIDO_OLD_NAME.get(r["sido_2025"], r["sidonm"]), axis=1)
    g["unit_nm"] = g.apply(unit_name, axis=1)
    return g


def load_population() -> pd.DataFrame:
    f = glob.glob(str(RAW / "population" / "15097972" / "*.csv"))[0]
    p = pd.read_csv(f, encoding="cp949", dtype={"행정기관코드": str})
    ages = {}
    for a in range(0, 100):
        cols = [c for c in p.columns if re.fullmatch(fr"{a}세(남자|여자)", c)]
        ages[a] = p[cols].sum(axis=1)
    # 100세 이상(100~109세 + '110세이상')은 하나의 구간으로 묶는다
    cols100 = [c for c in p.columns
               if (m := re.fullmatch(r"(\d+)세(남자|여자)", c)) and int(m.group(1)) >= 100]
    cols100 += [c for c in p.columns if c.startswith("110세이상")]
    ages[100] = p[cols100].sum(axis=1)
    age = pd.DataFrame(ages)
    out = pd.DataFrame({
        "adm_cd2": p["행정기관코드"], "sidonm": p["시도명"], "sggnm": p["시군구명"], "emd": p["읍면동명"],
        "pop": p["계"],
        "pop_0_14": age.loc[:, 0:14].sum(axis=1),
        "pop_65p": age.loc[:, 65:100].sum(axis=1),
        "pop_75p": age.loc[:, 75:100].sum(axis=1),
        "pop_80p": age.loc[:, 80:100].sum(axis=1),
        "pop_20_64": age.loc[:, 20:64].sum(axis=1),
    })
    assert (abs(age.sum(axis=1) - out["pop"]) <= 2).mean() > 0.99, "연령 합계 불일치"
    return out


def attach_branch_offices(pop: pd.DataFrame, g: gpd.GeoDataFrame) -> pd.DataFrame:
    """출장소 행을 같은 시군구의 모 읍면(이름 접두어 일치)에 합산."""
    known = set(g["adm_cd2"])
    is_branch = ~pop["adm_cd2"].isin(known)
    base = pop[~is_branch].copy()
    br = pop[is_branch].copy()
    num = ["pop", "pop_0_14", "pop_65p", "pop_75p", "pop_80p", "pop_20_64"]
    moved = 0
    for _, r in br.iterrows():
        same_sgg = base[base["adm_cd2"].str[:5] == r["adm_cd2"][:5]]
        parent_nm = re.split(r"(?<=[읍면동])", r["emd"], maxsplit=1)[0]
        cand = same_sgg[same_sgg["emd"] == parent_nm]
        if len(cand) != 1:
            # 접두어가 가장 길게 겹치는 읍면동(예: '삼랑진임천출장소' → '삼랑진읍')
            def overlap(nm):
                k = 0
                while k < min(len(nm), len(r["emd"])) and nm[k] == r["emd"][k]:
                    k += 1
                return k
            ov = same_sgg["emd"].map(overlap)
            cand = same_sgg[ov == ov.max()] if len(ov) and ov.max() >= 2 else same_sgg.iloc[0:0]
        if len(cand) >= 1:
            base.loc[cand.index[0], num] += r[num].values
            moved += 1
        elif len(same_sgg):
            # 최후 수단: 같은 시군구의 최대 인구 읍면동에 합산(전체 인구의 0.01% 미만)
            base.loc[same_sgg["pop"].idxmax(), num] += r[num].values
            moved += 1
            print("  [참고] 출장소를 시군구 최대 읍면동에 합산:", r["sggnm"], r["emd"], int(r["pop"]))
        else:
            print("  [경고] 출장소 모 읍면 미확인:", r["sggnm"], r["emd"])
    print(f"  출장소 {moved}/{len(br)}개 모 읍면에 합산")
    return base


def main():
    g = load_boundary()
    pop = attach_branch_offices(load_population(), g)
    g = g.merge(pop[["adm_cd2", "pop", "pop_0_14", "pop_65p", "pop_75p", "pop_80p", "pop_20_64"]],
                on="adm_cd2", how="left")
    assert g["pop"].notna().all()
    g.to_file(PROC / "admdong_2026.gpkg", driver="GPKG")
    units = (g.groupby(["unit", "unit_nm", "sido_2025", "sidonm_2025"], as_index=False)
               [["pop", "pop_65p", "pop_75p", "pop_80p", "pop_0_14", "pop_20_64"]].sum())
    units.to_csv(PROC / "units.csv", index=False, encoding="utf-8-sig")
    print(f"행정동 {len(g):,}개 / 분석 시군구 {len(units)}개 / 인구 {g['pop'].sum():,.0f}명 "
          f"(65+ {g['pop_65p'].sum()/g['pop'].sum():.1%})")


if __name__ == "__main__":
    main()
