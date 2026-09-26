"""00. GHS-POP 2025(100m, JRC R2023A) → H3 res 8 격자 합산 (격자 내 인구 배분 가중치 개선용)."""
import glob

import h3
import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer

from config import RAW, PROC


def main():
    f = glob.glob(str(RAW / "geo" / "ghspop" / "GHS_POP_E2025*R5_C30.tif"))[0]
    with rasterio.open(f) as r:
        a = r.read(1)
        tr = r.transform
        crs = r.crs
    a = np.where(a > 0, a, 0).astype("float64")
    rows, cols = np.nonzero(a)
    xs = tr.c + (cols + 0.5) * tr.a
    ys = tr.f + (rows + 0.5) * tr.e
    lon, lat = Transformer.from_crs(crs, 4326, always_xy=True).transform(xs, ys)
    keep = (lat > 32.9) & (lat < 38.8) & (lon > 124.3) & (lon < 131.95)
    lat, lon, pop = lat[keep], lon[keep], a[rows[keep], cols[keep]]
    cells = np.fromiter((h3.latlng_to_cell(y, x, 8) for y, x in zip(lat, lon)), dtype=object, count=len(lat))
    s = pd.DataFrame({"h3": cells, "ghs_pop": pop}).groupby("h3", as_index=False)["ghs_pop"].sum()
    s.to_parquet(PROC / "ghspop2025_h3r8.parquet", index=False)
    print(f"GHS-POP 2025 픽셀 {len(pop):,}개 → H3 {len(s):,}개, 합계 {s['ghs_pop'].sum():,.0f}")


if __name__ == "__main__":
    main()
