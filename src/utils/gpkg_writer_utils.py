from typing import List

import geopandas as gpd
import pandas as pd

from src.config.config import DataConfig


def write_to_gpkg(config: DataConfig, data: List[any], crs="EPSG:4326") -> None:
    df = pd.DataFrame(data, columns=config.columns)
    gdf = gpd.GeoDataFrame(data=df, geometry=df.geometry, crs=crs)
    gdf.to_file(config.filename, driver="GPKG")
