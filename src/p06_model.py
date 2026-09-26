"""05. AI 모델: 대중교통, 생활서비스 결핍은 자동차 의존, 탄소, 고령운전 위험을 얼마나 키우는가?

(1) 이중 머신러닝(Double/Debiased ML, Chernozhukov et al. 2018): 부분선형모형 Y = θ, D + g(X) + ε
    D = 자동차 필수 거주 인구 비율, X = 체감밀도, 고령화, 소득, 빈곤, 재정, 수도권, 철도, 시도 효과
    g(X), m(X)=E[D|X]를 LightGBM으로 교차적합(5-fold × 30회 반복) → θ의 점추정, 95% 신뢰구간
    → '밀도, 소득, 고령화가 같아도' 접근성 결핍이 결과를 얼마나 바꾸는지(교란 통제된 연관 효과)
(2) 설명가능 AI: LightGBM + TreeSHAP: 전역 중요도, 비선형 의존(임계점) 확인, 시도 단위 공간 교차검증
(3) 반사실 시뮬레이션: DML θ로 '자동차 필수 거주 비율 절반 감축' 시 주행거리, CO2, 고령운전 사망 변화
※ 횡단면 관측자료이므로 인과효과로 단정하지 않고 '교란요인을 통제한 효과 크기'로 해석한다.
"""
import json

import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from config import PROC, TAB

EF_G_PER_KM = 142.5      # 승용차 평균 배출계수(gCO2eq/km) = 2024 승용 도로배출 37,126천t ÷ 2024 승용 총주행 2,605억km
SEED = 7

CONTROLS = ["log_density", "share_65p", "wage_per_filer_mn", "nbls_rate", "fiscal_indep", "capital",
            "pw_cov_rail"]
TREAT = "share_car_ess"
OUTCOMES = {
    "vkt_pc": "1인당 승용차 연간 주행거리(km)",
    "cars_per_1k_adult": "성인 1천명당 자가용 승용차(대)",
    "share_car_commute": "승용차 통근·통학 분담률(2020)",
    "share_transit_commute": "대중교통 통근·통학 분담률(2020)",
    "death65_per_100k65": "65세+ 운전자 사고 사망자(고령인구 10만명당, 2024-25 평균)",
}
SHAP_FEATURES = [TREAT] + CONTROLS
LABELS = {"share_car_ess": "자동차 필수 거주 비율", "log_density": "체감 인구밀도(log)",
          "share_65p": "65세 이상 비율", "wage_per_filer_mn": "1인당 근로소득", "nbls_rate": "기초수급 비율",
          "fiscal_indep": "재정자립도", "capital": "수도권", "pw_cov_rail": "철도역 보행권 비율"}


def load():
    m = pd.read_csv(PROC / "master_units.csv", dtype={"unit": str}).set_index("unit")
    m["capital"] = m["capital"].astype(int)
    m["log_density"] = np.log10(m["pw_density"])
    return m[~m["flag_stop_data"] & ~m["flag_reg_outlier"]]


def gbm(n=400):
    return lgb.LGBMRegressor(n_estimators=n, learning_rate=0.03, num_leaves=7, max_depth=3, min_child_samples=12,
                             subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=2.0,
                             random_state=SEED, verbose=-1)


def dml_plr(d, y, treat, controls, reps=30, folds=5):
    """부분선형모형 DML(교차적합). 시도 더미를 통제변수에 추가."""
    X = pd.concat([d[controls], pd.get_dummies(d["sido_2025"].astype(str), prefix="sd", drop_first=True,
                                               dtype=float)], axis=1)
    Y, D = d[y].to_numpy(float), d[treat].to_numpy(float)
    thetas, ses = [], []
    for r in range(reps):
        kf = KFold(folds, shuffle=True, random_state=100 + r)
        ry, rd = np.zeros_like(Y), np.zeros_like(D)
        for tr, te in kf.split(X):
            my = gbm().fit(X.iloc[tr], Y[tr]); md = gbm().fit(X.iloc[tr], D[tr])
            ry[te] = Y[te] - my.predict(X.iloc[te]); rd[te] = D[te] - md.predict(X.iloc[te])
        theta = np.sum(rd * ry) / np.sum(rd * rd)
        psi = (ry - theta * rd) * rd
        se = np.sqrt(np.mean(psi ** 2) / (np.mean(rd * rd) ** 2) / len(Y))
        thetas.append(theta); ses.append(se)
    thetas, ses = np.array(thetas), np.array(ses)
    theta = float(np.median(thetas))
    se = float(np.median(np.sqrt(ses ** 2 + (thetas - theta) ** 2)))   # 반복 분할 보정(Chernozhukov et al.)
    # 비교용 OLS(동일 통제 + 시도 더미)
    ols = LinearRegression().fit(pd.concat([d[[treat]], X], axis=1), Y)
    return {"theta": theta, "se": se, "ci_low": theta - 1.96 * se, "ci_high": theta + 1.96 * se,
            "ols_coef": float(ols.coef_[0]), "n": int(len(Y)), "y_mean": float(Y.mean())}


def shap_model(d, y):
    X = d[SHAP_FEATURES]
    grp = d["sido_2025"].astype(str)
    pred_sp, pred_rand = np.zeros(len(d)), np.zeros(len(d))
    for tr, te in GroupKFold(len(grp.unique())).split(X, d[y], grp):
        pred_sp[te] = gbm().fit(X.iloc[tr], d[y].iloc[tr]).predict(X.iloc[te])
    for tr, te in KFold(10, shuffle=True, random_state=SEED).split(X):
        pred_rand[te] = gbm().fit(X.iloc[tr], d[y].iloc[tr]).predict(X.iloc[te])
    lin = np.zeros(len(d))
    for tr, te in GroupKFold(len(grp.unique())).split(X, d[y], grp):
        lin[te] = make_pipeline(StandardScaler(), LinearRegression()).fit(X.iloc[tr], d[y].iloc[tr]).predict(X.iloc[te])
    model = gbm().fit(X, d[y])
    ex = shap.TreeExplainer(model)
    sv = ex.shap_values(X)
    imp = pd.Series(np.abs(sv).mean(0), index=X.columns).sort_values(ascending=False)
    return model, X, sv, {"cv_r2_spatial_gbm": float(r2_score(d[y], pred_sp)),
                          "cv_r2_random10_gbm": float(r2_score(d[y], pred_rand)),
                          "cv_r2_spatial_ols": float(r2_score(d[y], lin)),
                          "cv_mae_spatial_gbm": float(mean_absolute_error(d[y], pred_sp)),
                          "shap_importance": {LABELS[k]: float(v) for k, v in imp.items()}}


def main():
    m = load()
    out = {"dml": {}, "shap": {}}
    for y, lab in OUTCOMES.items():
        d = m.dropna(subset=CONTROLS + [TREAT, y])
        r = dml_plr(d, y, TREAT, CONTROLS)
        r["label"] = lab
        r["effect_per_10pp"] = r["theta"] * 0.10
        r["effect_per_10pp_pct_of_mean"] = r["theta"] * 0.10 / r["y_mean"]
        out["dml"][y] = r
        print(f"[DML] {lab}: θ={r['theta']:.3f} (95% CI {r['ci_low']:.3f}~{r['ci_high']:.3f}), "
              f"+10%p → {r['effect_per_10pp']:.3f} ({r['effect_per_10pp_pct_of_mean']:+.1%} of mean), OLS {r['ols_coef']:.3f}")
    models = {}
    for y in ["vkt_pc", "share_transit_commute", "death65_per_100k65"]:
        d = m.dropna(subset=SHAP_FEATURES + [y])
        model, X, sv, res = shap_model(d, y)
        out["shap"][y] = res
        models[y] = (model, X, sv)
        print(f"[SHAP] {OUTCOMES[y]}: spatialCV R2 GBM {res['cv_r2_spatial_gbm']:.2f} / OLS {res['cv_r2_spatial_ols']:.2f}"
              f" / random10 GBM {res['cv_r2_random10_gbm']:.2f}; top: {list(res['shap_importance'])[:4]}")
    pd.to_pickle(models, PROC / "shap_models.pkl")

    # 반사실 시뮬레이션: 전국 평균(인구가중)보다 높은 시군구의 '자동차 필수 거주 비율'을 절반으로 낮춤
    full = pd.read_csv(PROC / "master_units.csv", dtype={"unit": str}).set_index("unit")
    nat = float(full["pop_car_ess"].sum() / full["pop"].sum())
    tgt = full[full["share_car_ess"] > nat].copy()
    tgt["d_share"] = -0.5 * tgt["share_car_ess"]
    th_v = out["dml"]["vkt_pc"]
    th_d = out["dml"]["death65_per_100k65"]
    d_vkt = (tgt["d_share"] * tgt["pop"]).sum()
    sim = {"national_share_car_ess": nat, "n_units": int(len(tgt)), "pop_units": float(tgt["pop"].sum()),
           "pop_car_ess_units": float(tgt["pop_car_ess"].sum()),
           "people_lifted": float(0.5 * tgt["pop_car_ess"].sum()),
           "elderly_lifted": float(0.5 * tgt["pop_65p_car_ess"].sum())}
    for k, th in [("central", th_v["theta"]), ("low", th_v["ci_low"]), ("high", th_v["ci_high"])]:
        vkt = th * d_vkt
        sim[f"d_vkt_bn_km_{k}"] = float(vkt / 1e9)
        sim[f"d_co2_kt_{k}"] = float(vkt * EF_G_PER_KM / 1e9)
    sim["d_deaths65_per_year"] = float((th_d["theta"] * tgt["d_share"] * tgt["pop_65p"] / 1e5).sum())
    sim["d_deaths65_per_year_ci"] = [float((th_d[c] * tgt["d_share"] * tgt["pop_65p"] / 1e5).sum())
                                     for c in ("ci_low", "ci_high")]
    out["simulation_halve"] = sim
    json.dump(out, open(TAB / "model_summary.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(sim, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
