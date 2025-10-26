from __future__ import annotations
from typing import List, Optional, Tuple
import pandas as pd
from .months import detect_month_columns
from .types import CleaningStats

class ExcelCleaner:
    """Single-responsibility class to clean financial Excel sheets."""

    def __init__(self, name_candidates: Optional[List[str]] = None) -> None:
        self.name_candidates = name_candidates or [
            "name", "nombre", "nombres", "account_name", "cliente", "razon_social"
        ]

    def process_file(self, src_path: str, out_path: str, sheet_name: str = "cleaned", name_column: Optional[str] = None) -> CleaningStats:
        df = self._load(src_path)
        original = len(df)

        # Normalize name column
        detected_name_col = name_column or self._auto_detect_name_column(df.columns)
        if detected_name_col and detected_name_col in df.columns:
            df[detected_name_col] = self._capitalize_first(df[detected_name_col])

        # Detect months
        month_cols = detect_month_columns(list(df.columns))

        # Remove rows where all months are zero or null
        removed = 0
        if month_cols:
            df, removed = self._drop_all_zero_rows(df, month_cols)

        # Save
        self._save(df, out_path, sheet_name=sheet_name)

        return CleaningStats(
            original_rows=original,
            rows_removed=removed,
            rows_remaining=len(df),
            detected_name_column=detected_name_col,
            detected_month_columns=month_cols,
        )

    # ---- Helpers ----
    def _load(self, path: str) -> pd.DataFrame:
        return pd.read_excel(path)

    def _save(self, df: pd.DataFrame, path: str, sheet_name: str = "cleaned") -> None:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)

    def _auto_detect_name_column(self, columns) -> Optional[str]:
        lower_map = {str(c).lower(): c for c in columns}
        for cand in self.name_candidates:
            if cand in lower_map:
                return lower_map[cand]
        for c in columns:
            if str(c).strip().lower() in {"name", "nombre"}:
                return c
        return None

    @staticmethod
    def _capitalize_first(series: pd.Series) -> pd.Series:
        return series.astype("string").str.strip().str.lower().str.capitalize()

    @staticmethod
    def _drop_all_zero_rows(df: pd.DataFrame, month_cols: List[str]) -> Tuple[pd.DataFrame, int]:
        numeric = df[month_cols].apply(pd.to_numeric, errors="coerce")
        mask = (numeric.fillna(0) == 0).all(axis=1)
        removed = int(mask.sum())
        return df.loc[~mask].reset_index(drop=True), removed
