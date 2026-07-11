from pathlib import Path


class TestSettings:
    watch_interval: int = 2
    db_path: Path = Path("data/deepmindly_database.db")


settings = TestSettings()