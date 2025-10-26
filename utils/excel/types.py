from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CleaningStats:
    original_rows: int
    rows_removed: int
    rows_remaining: int
    detected_name_column: Optional[str]
    detected_month_columns: List[str]