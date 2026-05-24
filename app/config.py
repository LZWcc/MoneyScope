"""项目配置常量。"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "moneyscope.db"
SAMPLE_DATA_PATH = DATA_DIR / "sample_transactions.csv"
