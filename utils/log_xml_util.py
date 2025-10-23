import os
import re
from typing import List, Tuple


class LogXmlUtil:
    def __init__(self, path: str, required_tags: List[str]):
        self._group_pattern = None
        self.required_tags = None
        self.path = path
        self.set_required_tags(required_tags)

    def set_required_tags(self, tags: List[str]) -> None:
        self.required_tags = tags
        # Build a dynamic pattern that captures each <Tag>...</Tag> in order, with line breaks.
        parts = [fr"<{t}>(.*?)</{t}>" for t in tags]
        pattern_str = r".*?".join(parts)
        self._group_pattern = re.compile(pattern_str, re.DOTALL)

    def _extract_rows(self, data: str) -> List[Tuple[str, ...]]:
        """
        Extract rows (tuples) in the order of self.required tags from a block of text.
        Supports multiple occurrences and line breaks between tags.
        """
        rows = []
        for m in self._group_pattern.finditer(data):
            values = tuple((m.group(i + 1) or "").strip() for i in range(len(self.required_tags)))
            rows.append(values)
        return rows

    def extract_required_data(self, data: str, output_file: str):
        """
        Reads all files within the specified directory (no subfolders) and extracts the data
        :param data: to be extracted
        :param output_file: output file
        :return: None
        """
        rows = self._extract_rows(data)

    def extract_dir_to_csv(self, output_file: str) -> None:
        """
        Reads ALL files in the root directory (no subfolders) and writes ALL matches to CSV (includes duplicates).
        """
        all_rows = []
        for name in os.listdir(self.path):
            p = os.path.join(self.path, name)
            if os.path.isfile(p):
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                        all_rows.extend(self._extract_rows(fh.read()))
                except Exception as e:
                    print(f"⚠️ No se pudo leer: {p} ({e})")

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(self.required_tags)
            writer.writerows(all_rows)

        print(f"✅ {len(all_rows)} filas escritas en {output_file}")