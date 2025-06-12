# core/controller.py

import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

STATION_FILE = "data/stations.csv"

class AppController:
    def __init__(self):
        self.station_data = self._load_station_data()

    def _load_station_data(self) -> pd.DataFrame:
        """โหลดข้อมูลสถานีจาก CSV"""
        try:
            path = Path(STATION_FILE)
            if not path.exists():
                logger.warning("stations.csv not found.")
                return pd.DataFrame()

            df = pd.read_csv(path)
            logger.info(f"Loaded {len(df)} stations.")
            return df
        except Exception as e:
            logger.exception("Failed to load station data.")
            return pd.DataFrame()

    def get_station_list(self) -> list:
        """คืนชื่อสถานีทั้งหมด"""
        if self.station_data.empty:
            return []
        return self.station_data["name"].tolist()

    def find_station_by_name(self, name: str) -> dict:
        """ค้นหาสถานีตามชื่อ"""
        matches = self.station_data[self.station_data["name"].str.contains(name, case=False)]
        return matches.to_dict(orient="records")[0] if not matches.empty else {}
