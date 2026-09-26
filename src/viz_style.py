"""그림 공통 스타일(인쇄용 PDF 보고서 기준)과 팔레트.

- 글꼴: Pretendard(SIL OFL 1.1): report/fonts
- 색 역할: 부담(자동차 필수 거주)은 자주(claret) 단일색상, 혜택, 서비스, 접근은 파랑 단일색상, 해당 없음은 중립 회색
- 두 색 모두 dataviz 검증 스크립트 통과(서수형 램프: 단일 색상, 명도 단조, 밝은 끝 2:1 이상, 자주↔파랑 색각이상 ΔE 20.9)
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "report" / "fonts"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
INK3 = "#8a8984"
GRID = "#e6e5e0"
BLUE = "#2a78d6"
BURDEN = "#b42f56"             # 부담(필요) 막대, 강조
AQUA = "#1baf7a"
GRAY = "#b9b8b2"
GREEN_ORG = "#6aa84f"          # 주최측 양식 녹색 띠와 조화
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
BURDEN_RAMP = ["#fbe0e4", "#f4bdc6", "#e593a2", "#d3627b", "#b53559", "#8b173d", "#5a0c26"]
# 지도 단계구분(서수형) 5단계: dataviz 검증 스크립트 통과(밝은 끝 2:1 이상, 단일 색상, 명도 단조)
BURDEN_5 = ["#e1909f", "#d25d78", "#b42f56", "#8b173d", "#5d1028"]
BLUE_5 = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
ZERO = "#ecebe6"               # '해당 없음' 단계(중립)

CMAP_BURDEN = LinearSegmentedColormap.from_list("burden", BURDEN_RAMP)
CMAP_ACCESS = LinearSegmentedColormap.from_list("access", BLUE_RAMP)


def setup():
    for f in FONT_DIR.glob("Pretendard-*.otf"):
        font_manager.fontManager.addfont(str(f))
    mpl.rcParams.update({
        "font.family": "Pretendard",
        "font.size": 9,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 9,
        "axes.labelcolor": INK2,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.facecolor": SURFACE,
        "figure.facecolor": "white",
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.unicode_minus": False,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
    })


def note(ax, text, y=-0.16):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=6.8, color=INK3, va="top")
