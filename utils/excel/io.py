from typing import Any
import pandas as pd

class ExcelIO:
    def __init__(self, read_kwargs: dict[str, Any] | None = None, write_engine: str = "openpyxl"):
        self.read_kwargs = read_kwargs or {}
        self.write_engine = write_engine

    def read(self, path: str) -> pd.DataFrame:
        return pd.read_excel(path, **self.read_kwargs)

    def write(self, df: pd.DataFrame, path: str, sheet_name: str = "cleaned") -> None:
        with pd.ExcelWriter(path, engine=self.write_engine) as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)