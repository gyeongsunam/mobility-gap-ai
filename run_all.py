"""전체 재현: 원자료 내려받기 → 격자 인구 → 접근성 → 시군구 결합 → AI 모델 → 유형화 → 정책 산정 → 그림 → 보고서(PDF)

  python run_all.py                 # 전체(내려받기 포함)
  python run_all.py --skip-download # 원자료가 이미 있을 때
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = ["p00_ghspop_to_h3.py", "p01_prepare_base.py", "p02_hex_population.py", "p03_transit_facilities.py",
         "p04_hex_accessibility.py", "p05_build_master.py", "p07_typology.py", "p08_incidence.py", "p06_model.py",
         "p10_policy.py", "p09_figures.py"]


def run(cmd, cwd):
    t = time.time()
    print(f"\n▶ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)
    print(f"  ({time.time() - t:.0f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-download", action="store_true")
    a = ap.parse_args()
    if not a.skip_download:
        run([sys.executable, "scripts/download_data.py"], ROOT)
    for s in STEPS:
        run([sys.executable, s], ROOT / "src")
    run([sys.executable, "report/build_report.py"], ROOT)


if __name__ == "__main__":
    main()
